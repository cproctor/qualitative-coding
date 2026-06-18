from pathlib import Path
from collections import defaultdict
import bisect
import json
import numpy as np
import structlog
from tqdm import tqdm
from qualitative_coding.exceptions import QCError

log = structlog.get_logger()

AUTOCODE_DEFAULTS = {
    "autocode_embeddings_dir": "embeddings",
    "autocode_window": [2, 2],
    "autocode_api_base": "http://localhost:1234/v1",
    "autocode_api_key": "",
    "autocode_api_model": "text-embedding-nomic-embed-text-v1.5",
}

BATCH_SIZE = 100


class CorpusEmbedder:
    """Embeds corpus documents using an OpenAI-compatible embedding API.

    The unit of analysis (line/paragraph/document) is read from settings
    and determines how each document is chunked before embedding:

    - line:      one embedding per non-blank line, optionally windowed with
                 surrounding context (autocode_window setting).
    - paragraph: one embedding per paragraph (delimited by blank lines).
    - document:  one embedding per document.

    Embeddings are cached on disk as .npy files with .json sidecars. The
    cache is whole-document: a document is either fully cached or absent.
    Changing unit, model, or (for line unit) window invalidates the cache.
    """

    def __init__(self, corpus):
        self.corpus = corpus
        settings = corpus.settings
        self.embeddings_dir = corpus.resolve_path(
            settings.get("autocode_embeddings_dir",
                         AUTOCODE_DEFAULTS["autocode_embeddings_dir"])
        )
        window = settings.get("autocode_window", AUTOCODE_DEFAULTS["autocode_window"])
        self.window_before, self.window_after = window[0], window[1]
        self.api_base = settings.get("autocode_api_base",
                                     AUTOCODE_DEFAULTS["autocode_api_base"])
        self.api_key = settings.get("autocode_api_key",
                                    AUTOCODE_DEFAULTS["autocode_api_key"])
        self.model = settings.get("autocode_api_model",
                                  AUTOCODE_DEFAULTS["autocode_api_model"])
        self.unit = settings.get("unit", "line")

    def _client(self):
        from openai import OpenAI
        return OpenAI(base_url=self.api_base, api_key=self.api_key or "no-key")

    def embed_corpus(self, force=False, pattern=None, file_list=None):
        """Embed all matching corpus documents, caching results on disk."""
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        with self.corpus.session():
            documents = self.corpus.get_documents(pattern=pattern, file_list=file_list)
        total_units = 0
        for doc in tqdm(documents, desc="Embedding documents"):
            if not force and self.is_cache_valid(doc.file_path):
                continue
            n = self._embed_document(doc.file_path)
            total_units += n
        log.info("autocode embed", total_units=total_units,
                 unit=self.unit, embeddings_dir=str(self.embeddings_dir))
        return total_units

    def ensure_embedded(self, document_id):
        """Embed a single document on demand if its cache is missing or stale."""
        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])
            if not doc:
                return
        if not self.is_cache_valid(document_id):
            self._embed_document(document_id)

    def _embed_document(self, document_id):
        """Embed a document according to the current unit of analysis."""
        corpus_path = self.corpus.corpus_dir / document_id
        lines = corpus_path.read_text().splitlines()

        if self.unit == "document":
            texts, line_numbers = self._chunks_document(lines)
        elif self.unit == "paragraph":
            texts, line_numbers = self._chunks_paragraph(corpus_path, lines)
        else:
            texts, line_numbers = self._chunks_line(lines)

        if not texts:
            return 0

        client = self._client()
        all_vectors = []
        for batch_start in range(0, len(texts), BATCH_SIZE):
            batch = texts[batch_start:batch_start + BATCH_SIZE]
            response = client.embeddings.create(model=self.model, input=batch)
            all_vectors.extend(item.embedding for item in response.data)

        matrix = np.array(all_vectors, dtype=np.float32)
        np.save(self.cache_path(document_id), matrix)

        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])[0]
            file_hash = doc.file_hash

        sidecar = {
            "model": self.model,
            "unit": self.unit,
            "window": [self.window_before, self.window_after],
            "hash": file_hash,
            "lines": line_numbers,
        }
        self.sidecar_path(document_id).write_text(json.dumps(sidecar))
        log.debug("autocode embed document", document_id=document_id,
                  unit=self.unit, n_units=len(line_numbers))
        return len(line_numbers)

    def _chunks_line(self, lines):
        """One embedding per non-blank line, with windowed context."""
        texts, line_numbers = [], []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            start = max(0, i - self.window_before)
            end = min(len(lines), i + self.window_after + 1)
            texts.append("\n".join(lines[start:end]))
            line_numbers.append(i)
        return texts, line_numbers

    def _chunks_paragraph(self, corpus_path, lines):
        """One embedding per paragraph, indexed by paragraph start line."""
        from qualitative_coding.helpers import iter_paragraph_lines
        texts, line_numbers = [], []
        with open(corpus_path) as fh:
            for p_start, p_end in iter_paragraph_lines(fh):
                text = "\n".join(lines[p_start:p_end])
                if not text.strip():
                    continue
                texts.append(text)
                line_numbers.append(p_start)
        return texts, line_numbers

    def _chunks_document(self, lines):
        """One embedding for the whole document, indexed at line 0."""
        text = "\n".join(lines)
        if not text.strip():
            return [], []
        return [text], [0]

    def get_embeddings(self, document_id) -> tuple:
        """Load cached embeddings for a document.

        Returns (matrix of shape [n_units, n_dims], list of representative line numbers).
        For line unit: line numbers of non-blank lines.
        For paragraph unit: start lines of paragraphs.
        For document unit: [0].
        """
        if not self.is_cache_valid(document_id):
            reason = self._cache_invalidity_reason(document_id)
            raise QCError(
                f"Embeddings for {document_id} are missing or stale ({reason}). "
                "Run `qc autocode embed` first."
            )
        matrix = np.load(self.cache_path(document_id))
        sidecar = json.loads(self.sidecar_path(document_id).read_text())
        return matrix, sidecar["lines"]

    def embedding_key_for_line(self, line, line_numbers):
        """Return the matrix row index for a corpus line number.

        For line unit:      exact match (or None if line was blank/skipped).
        For paragraph unit: finds the paragraph whose start_line <= line.
        For document unit:  always 0.

        line_numbers must be sorted ascending (as returned by get_embeddings).
        """
        if self.unit == "document":
            return 0 if line_numbers else None
        elif self.unit == "paragraph":
            idx = bisect.bisect_right(line_numbers, line) - 1
            return idx if idx >= 0 else None
        else:  # line
            idx = bisect.bisect_left(line_numbers, line)
            if idx < len(line_numbers) and line_numbers[idx] == line:
                return idx
            return None

    def cache_path(self, document_id) -> Path:
        """Returns path to .npy cache file for a document."""
        safe_name = document_id.replace("/", "_").replace("\\", "_")
        if safe_name.endswith(".txt"):
            safe_name = safe_name[:-4]
        return self.embeddings_dir / f"{safe_name}.npy"

    def sidecar_path(self, document_id) -> Path:
        """Returns path to .json sidecar for a document."""
        return self.cache_path(document_id).with_suffix(".json")

    def is_cache_valid(self, document_id) -> bool:
        """True if cache exists and matches current settings.

        Checks: file hash, model, unit. For line unit also checks window.
        """
        sidecar_p = self.sidecar_path(document_id)
        npy_p = self.cache_path(document_id)
        if not sidecar_p.exists() or not npy_p.exists():
            return False
        sidecar = json.loads(sidecar_p.read_text())
        if sidecar.get("model") != self.model:
            return False
        if sidecar.get("unit", "line") != self.unit:
            return False
        if self.unit == "line":
            if sidecar.get("window") != [self.window_before, self.window_after]:
                return False
        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])
            if not doc:
                return False
            return doc[0].file_hash == sidecar.get("hash")

    def _cache_invalidity_reason(self, document_id) -> str:
        """Diagnoses why is_cache_valid returned False, for error messages."""
        sidecar_p = self.sidecar_path(document_id)
        npy_p = self.cache_path(document_id)
        if not sidecar_p.exists() or not npy_p.exists():
            return "no cached embeddings found"
        sidecar = json.loads(sidecar_p.read_text())
        if sidecar.get("model") != self.model:
            return f"embedded with model '{sidecar.get('model')}', settings now specify '{self.model}'"
        sidecar_unit = sidecar.get("unit", "line")
        if sidecar_unit != self.unit:
            return (
                f"embedded at unit '{sidecar_unit}', but settings now specify "
                f"unit '{self.unit}'; re-embed after changing 'unit' in settings"
            )
        if self.unit == "line":
            window = [self.window_before, self.window_after]
            if sidecar.get("window") != window:
                return f"embedded with window {sidecar.get('window')}, settings now specify {window}"
        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])
            if not doc:
                return "document no longer exists in corpus"
        return "document content has changed since embedding"

    def invalidate(self, document_id):
        """Delete cached embeddings for a document (called after corpus update)."""
        for p in [self.cache_path(document_id), self.sidecar_path(document_id)]:
            if p.exists():
                p.unlink()

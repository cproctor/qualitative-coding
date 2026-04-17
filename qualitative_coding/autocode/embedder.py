from pathlib import Path
from collections import defaultdict
import json
import numpy as np
import structlog
from tqdm import tqdm

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
    """Embeds corpus lines using an OpenAI-compatible embedding API.

    Embeddings are cached on disk as .npy files (one per document) with
    .json sidecars recording the model, window, and document hash. The
    cache is always whole-document: a document is either fully cached or
    absent — there is no partial state.
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

    def _client(self):
        from openai import OpenAI
        return OpenAI(base_url=self.api_base, api_key=self.api_key or "no-key")

    def embed_corpus(self, force=False, pattern=None, file_list=None):
        """Embed all matching corpus documents, caching results on disk."""
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
        with self.corpus.session():
            documents = self.corpus.get_documents(pattern=pattern, file_list=file_list)
        total_lines = 0
        for doc in tqdm(documents, desc="Embedding documents"):
            if not force and self.is_cache_valid(doc.file_path):
                continue
            n = self._embed_document(doc.file_path)
            total_lines += n
        log.info("autocode embed", total_lines=total_lines,
                 embeddings_dir=str(self.embeddings_dir))
        return total_lines

    def ensure_embedded(self, document_id):
        """Embed a single document on demand if its cache is missing or stale."""
        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])
            if not doc:
                return
        if not self.is_cache_valid(document_id):
            self._embed_document(document_id)

    def _embed_document(self, document_id):
        """Embed all lines of a document and write cache files."""
        corpus_path = self.corpus.corpus_dir / document_id
        lines = corpus_path.read_text().splitlines()
        windowed_texts = []
        line_numbers = []
        for i, line in enumerate(lines):
            # Skip completely blank lines
            if not line.strip():
                continue
            start = max(0, i - self.window_before)
            end = min(len(lines), i + self.window_after + 1)
            context = "\n".join(lines[start:end])
            windowed_texts.append(context)
            line_numbers.append(i)

        if not windowed_texts:
            return 0

        # Embed in batches
        client = self._client()
        all_vectors = []
        for batch_start in range(0, len(windowed_texts), BATCH_SIZE):
            batch = windowed_texts[batch_start:batch_start + BATCH_SIZE]
            response = client.embeddings.create(model=self.model, input=batch)
            batch_vectors = [item.embedding for item in response.data]
            all_vectors.extend(batch_vectors)

        matrix = np.array(all_vectors, dtype=np.float32)
        npy_path = self.cache_path(document_id)
        np.save(npy_path, matrix)

        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])[0]
            file_hash = doc.file_hash

        sidecar = {
            "model": self.model,
            "window": [self.window_before, self.window_after],
            "hash": file_hash,
            "lines": line_numbers,
        }
        self.sidecar_path(document_id).write_text(json.dumps(sidecar))
        log.debug("autocode embed document", document_id=document_id,
                  n_lines=len(line_numbers))
        return len(line_numbers)

    def get_embeddings(self, document_id) -> tuple:
        """Load cached embeddings for a document.

        Returns (matrix of shape [n_lines, n_dims], list of line numbers).
        Raises RuntimeError if cache is missing or stale.
        """
        if not self.is_cache_valid(document_id):
            raise RuntimeError(
                f"Embeddings for {document_id} are missing or stale. "
                "Run `qc autocode embed` first."
            )
        matrix = np.load(self.cache_path(document_id))
        sidecar = json.loads(self.sidecar_path(document_id).read_text())
        return matrix, sidecar["lines"]

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
        """True if sidecar exists and its hash matches Document.file_hash.

        Cache entries are always whole-document; there is no partial state.
        """
        sidecar_p = self.sidecar_path(document_id)
        npy_p = self.cache_path(document_id)
        if not sidecar_p.exists() or not npy_p.exists():
            return False
        sidecar = json.loads(sidecar_p.read_text())
        # Also check model and window match current settings
        if sidecar.get("model") != self.model:
            return False
        if sidecar.get("window") != [self.window_before, self.window_after]:
            return False
        with self.corpus.session():
            doc = self.corpus.get_documents(file_list=[document_id])
            if not doc:
                return False
            return doc[0].file_hash == sidecar.get("hash")

    def invalidate(self, document_id):
        """Delete cached embeddings for a document (called after corpus update)."""
        for p in [self.cache_path(document_id), self.sidecar_path(document_id)]:
            if p.exists():
                p.unlink()

from pathlib import Path
import bisect
import structlog

log = structlog.get_logger()


class UncertaintySampler:
    """Ranks corpus units by classifier uncertainty for active learning.

    Uses margin sampling: margin = P(top code) - P(second code).
    Lower margin = higher uncertainty = higher priority for human review.
    """

    def __init__(self, corpus, predictor):
        self.corpus = corpus
        self.predictor = predictor

    def rank_by_margin(self, codes=None, pattern=None, file_list=None,
                       exclude_coded_by=None):
        """Return [(document_id, line, margin), ...] sorted ascending by margin.

        Args:
            codes: restrict uncertainty to this subset of codes
            pattern/file_list: corpus filter
            exclude_coded_by: skip units already coded by any of these coders
        """
        all_scores = self.predictor.score_all_lines(
            pattern=pattern, file_list=file_list
        )

        # Get already-coded lines to exclude
        excluded_lines = set()
        if exclude_coded_by:
            with self.corpus.session():
                for cl in self.corpus.get_coded_lines(
                    coders=list(exclude_coded_by),
                    pattern=pattern,
                    file_list=file_list,
                ):
                    excluded_lines.add((cl[3], cl[2]))  # (doc_id, line)

        # Group scores by (doc_id, line)
        by_unit = {}
        for doc_id, line, code, conf in all_scores:
            if codes and code not in codes:
                continue
            if (doc_id, line) in excluded_lines:
                continue
            key = (doc_id, line)
            if key not in by_unit:
                by_unit[key] = []
            by_unit[key].append(conf)

        # Compute margin = P(top) - P(second) per unit; lower = more uncertain
        ranked = []
        for (doc_id, line), confs in by_unit.items():
            sorted_confs = sorted(confs, reverse=True)
            top = sorted_confs[0]
            second = sorted_confs[1] if len(sorted_confs) > 1 else 0.0
            margin = top - second
            ranked.append((doc_id, line, margin))

        ranked.sort(key=lambda x: x[2])  # ascending: most uncertain first
        return ranked

    def get_context(self, document_id, line, context_lines=3):
        """Return a list of (line_number, text, is_target) tuples for display.

        For paragraph unit: shows the full paragraph containing `line`.
        For document unit: shows a window around line 0.
        For line unit: shows ±context_lines around `line`.
        """
        corpus_path = self.corpus.corpus_dir / document_id
        all_lines = corpus_path.read_text().splitlines()
        unit = self.predictor.embedder.unit

        if unit == "paragraph":
            # line is a paragraph start_line; find the paragraph's end from sidecar
            _, para_starts = self.predictor.embedder.get_embeddings(document_id)
            idx = bisect.bisect_left(para_starts, line)
            para_end = (para_starts[idx + 1]
                        if idx + 1 < len(para_starts)
                        else len(all_lines))
            return [(i, all_lines[i], i == line) for i in range(line, para_end)]
        else:
            start = max(0, line - context_lines)
            end = min(len(all_lines), line + context_lines + 1)
            return [(i, all_lines[i], i == line) for i in range(start, end)]

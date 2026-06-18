import click
import os
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger
from qualitative_coding.exceptions import QCError

@click.command(name="interactive")
@click.argument("coder")
@click.argument("codes", nargs=-1)
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-c", "--train-coders", "train_coders", multiple=True,
              help="Coders whose coding to use for training")
@click.option("--context", "context_lines", default=3, type=int,
              help="Lines of context to show around each target line")
@click.option("--uncertainty-threshold", "uncertainty_threshold", default=0.1,
              type=float,
              help="Stop when all remaining margins exceed this threshold")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames")
@click.option("-f", "--filenames", help="File path containing a list of filenames")
@handle_qc_errors
def autocode_interactive(coder, codes, settings, train_coders, context_lines,
                         uncertainty_threshold, pattern, filenames):
    "Interactively code the most uncertain lines using active learning"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("autocode interactive", coder=coder, train_coders=train_coders)
    corpus = QCCorpus(settings_path)

    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.trainer import AutocodeTrainer
    from qualitative_coding.autocode.predictor import AutocodePredictor
    from qualitative_coding.autocode.active import UncertaintySampler

    embedder = CorpusEmbedder(corpus)
    file_list = read_file_list(filenames)
    code_filter = list(codes) if codes else None

    def build_predictor():
        trainer = AutocodeTrainer(corpus, embedder)
        classifiers = trainer.train(
            coders=list(train_coders) if train_coders else None,
            pattern=pattern,
            file_list=file_list,
        )
        if not classifiers:
            raise QCError(
                "No classifiers could be trained. Ensure enough lines are "
                "hand-coded and embeddings are generated with `qc autocode embed`."
            )
        return AutocodePredictor(corpus, embedder, classifiers)

    predictor = build_predictor()
    sampler = UncertaintySampler(corpus, predictor)
    n_coded = 0

    click.echo(
        f"Active learning session — coding as '{coder}'. "
        "Enter codes (comma-separated), Enter to skip, 'q' to quit."
    )
    click.echo()

    try:
        while True:
            ranked = sampler.rank_by_margin(
                codes=code_filter,
                pattern=pattern,
                file_list=file_list,
                exclude_coded_by=[coder],
            )
            if not ranked:
                click.echo("No uncoded lines remain. Session complete.")
                break
            doc_id, line, margin = ranked[0]
            if margin > uncertainty_threshold:
                click.echo(
                    f"All remaining lines have margin > {uncertainty_threshold}. "
                    "Consider running `qc code CODER --auto --no-edit` to write "
                    "high-confidence predictions."
                )
                break

            # Display context
            context = sampler.get_context(doc_id, line, context_lines)
            width = 65
            click.echo("─" * width)
            click.echo(f"Document: {doc_id}  [Lines {context[0][0]}–{context[-1][0]}]")
            click.echo("─" * width)
            for ln, text, is_target in context:
                marker = "→" if is_target else " "
                click.echo(f"{marker} {ln:4d}  {text}")
            click.echo("─" * width)

            # Show candidate codes by confidence
            with corpus.session():
                raw = predictor.predict_line(
                    embedder.get_embeddings(doc_id)[0][
                        embedder.get_embeddings(doc_id)[1].index(line)
                    ]
                )
            candidates = sorted(raw.items(), key=lambda x: abs(x[1] - 0.5))
            click.echo("Candidate codes (most uncertain first):")
            for code_name, conf in candidates[:8]:
                marker = "← most uncertain" if code_name == candidates[0][0] else ""
                click.echo(f"  {code_name:<24s} {conf:.2f}  {marker}")
            click.echo()

            raw_input = click.prompt(
                "Enter codes (comma-separated), Enter to skip, 'q' to quit",
                default="",
                show_default=False,
            ).strip()

            if raw_input.lower() == "q":
                break
            if not raw_input:
                # Skip — mark as coded with empty (just advance past it)
                with corpus.session():
                    corpus.update_coded_lines(doc_id, coder, [])
                continue

            entered_codes = [c.strip() for c in raw_input.split(",") if c.strip()]
            with corpus.session():
                corpus.update_coded_lines(
                    doc_id, coder,
                    [{"line": line, "code_id": c} for c in entered_codes]
                )
            n_coded += 1
            click.echo(f"  Coded line {line}: {', '.join(entered_codes)}")
            click.echo()

            # Retrain after each annotation
            predictor = build_predictor()
            sampler = UncertaintySampler(corpus, predictor)

    except (KeyboardInterrupt, click.exceptions.Abort):
        click.echo()

    click.echo(f"\nSession ended. {n_coded} lines coded as '{coder}'.")
    log.info("autocode interactive session ended", coder=coder, n_coded=n_coded)

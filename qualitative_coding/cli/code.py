import click
import yaml
import os
from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import QCError, IncompatibleOptions
from qualitative_coding.views.viewer import QCCorpusViewer
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.helpers import read_file_list
from qualitative_coding.logs import configure_logger

@click.command()
@click.argument("coder")
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern",
        help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames",
        help="File path containing a list of filenames to use")
@click.option("-u", "--uncoded", is_flag=True, help="Select uncoded files")
@click.option("-1", "--first", is_flag=True, help="Select first uncoded file")
@click.option("-r", "--random", is_flag=True, help="Select random uncoded file")
@click.option("--recover", is_flag=True, help="Recover incomplete coding session")
@click.option("--abandon", is_flag=True, help="Abandon incomplete coding session")
@click.option("--auto", is_flag=True,
        help="Pre-populate codes from autocode predictions before opening editor")
@click.option("--no-edit", "no_edit", is_flag=True,
        help="Write autocode predictions directly without opening editor (requires --auto)")
@click.option("-c", "--train-coders", "train_coders", multiple=True,
        help="Coders whose coding to use for training (with --auto)")
@click.option("--threshold", type=float, default=None,
        help="Confidence threshold for predictions (with --auto)")
@click.option("--no-hierarchy", "no_hierarchy", is_flag=True,
        help="Disable tree-descent post-processing (with --auto)")
@click.option("--from-coder", "from_coder", default=None,
        help="Read predictions from this coder's existing DB entries (with --auto)")
@handle_qc_errors
def code(coder, settings, pattern, filenames, uncoded, first, random,
         recover, abandon, auto, no_edit, train_coders, threshold, no_hierarchy,
         from_coder):
    "Open a file for coding"
    if first and random:
        raise IncompatibleOptions("--first and --random cannot both be used.")
    if no_edit and not auto:
        raise IncompatibleOptions("--no-edit requires --auto.")

    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    log = configure_logger(settings_path)
    log.info("code", coder=coder, pattern=pattern, filenames=filenames,
             uncoded=uncoded, first=first, random=random, recover=recover,
             abandon=abandon, auto=auto, no_edit=no_edit)
    corpus = QCCorpus(settings_path)
    viewer = QCCorpusViewer(corpus)

    if recover:
        viewer.recover_incomplete_coding_session(coder)
        return
    if abandon:
        viewer.abandon_incomplete_coding_session()
        return

    if viewer.incomplete_coding_session_exists():
        raise QCError(
            "An incomplete coding session exists. "
            "Run qc code coder --recover to recover this coding session or "
            "qc code coder --abandon to abandon it."
        )

    if auto and no_edit:
        _run_auto_no_edit(corpus, coder, train_coders, threshold, no_hierarchy,
                          pattern, read_file_list(filenames), settings_path, log)
        return

    f = viewer.select_file(
        coder,
        pattern=pattern,
        file_list=read_file_list(filenames),
        uncoded=uncoded,
        first=first,
        random=random,
    )

    if auto:
        viewer.open_editor(f, coder, suggest_from=from_coder or coder,
                           train_coders=list(train_coders) if train_coders else None,
                           threshold=threshold, no_hierarchy=no_hierarchy)
    else:
        viewer.open_editor(f, coder)


def _run_auto_no_edit(corpus, coder, train_coders, threshold, no_hierarchy,
                      pattern, file_list, settings_path, log):
    """Bulk apply autocode predictions without opening an editor."""
    from qualitative_coding.autocode.embedder import CorpusEmbedder
    from qualitative_coding.autocode.trainer import AutocodeTrainer
    from qualitative_coding.autocode.predictor import AutocodePredictor

    embedder = CorpusEmbedder(corpus)
    trainer = AutocodeTrainer(corpus, embedder)
    if threshold is not None:
        corpus.settings["autocode_confidence_threshold"] = threshold

    classifiers = trainer.train(
        coders=list(train_coders) if train_coders else None,
        pattern=pattern,
        file_list=file_list,
    )
    if not classifiers:
        raise QCError(
            "No classifiers could be trained. Check that enough lines are "
            "hand-coded and that embeddings have been generated with "
            "`qc autocode embed`."
        )

    predictor = AutocodePredictor(corpus, embedder, classifiers)
    counts = predictor.apply(
        coder,
        pattern=pattern,
        file_list=file_list,
        only_uncoded=True,
        apply_hierarchy=not no_hierarchy,
    )
    total = sum(counts.values())
    click.echo(f"Wrote {total} predictions across {len(counts)} codes.")
    for code_name, n in sorted(counts.items()):
        click.echo(f"  {code_name}: {n}")
    log.info("code --auto --no-edit", coder=coder, counts=counts)

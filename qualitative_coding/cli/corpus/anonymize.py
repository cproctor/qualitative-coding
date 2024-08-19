import os
import click
import spacy
import yaml
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import QCError
from qualitative_coding.helpers import read_file_list
from qualitative_coding.cli.decorators import handle_qc_errors
from qualitative_coding.logs import configure_logger

LABELS = {
    "PERSON": "Person",
    "FAC": "Location",
    "ORG": "Organization",
    "GPE": "Location",
    "LOC": "Location",
}

@click.command()
@click.option("-s", "--settings", type=click.Path(exists=True), help="Settings file")
@click.option("-p", "--pattern", help="Pattern to filter corpus filenames (glob-style)")
@click.option("-f", "--filenames", help="File path containing a list of filenames to use")
@click.option("-k", "--key", default="key.yaml", help="Path to key file")
@click.option("-r", "--reverse", is_flag=True, help="Un-anonymize documents")
@click.option("-o", "--anon-dir", default="anonymized", help="location for anonymized documemts")
@click.option("-u", "--update", is_flag=True, help="Update documents in place")
@handle_qc_errors
def anonymize(settings, pattern, filenames, key, reverse, anon_dir, update):
    "Anonymize corpus files"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    key_file = Path(key)
    out_path = Path(anon_dir)
    log = configure_logger(settings_path)
    log.info("corpus anonymize", pattern=pattern, filenames=filenames, key=key, reverse=reverse, anon_dir=anon_dir, update=update)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        docs = corpus.get_documents(pattern=pattern, file_list=read_file_list(filenames))

    if key_file.exists():
        keys = yaml.safe_load(key_file.read_text())
        out_path.mkdir(exist_ok=True, parents=True)
        for doc in docs:
            source = corpus.corpus_dir / doc.file_path
            dest = out_path / doc.file_path
            replace_keys(keys, source, dest)
    else:
        doc_paths = [corpus.corpus_dir / doc.file_path for doc in docs]
        generate_key_file(key, doc_paths)

def replace_keys(keys, source, dest):
    text = source.read_text()
    for k, v in keys.items():
        text = text.replace(k, v)
    dest.write_text(text)

def generate_key_file(key, file_paths):
    """Generates a YAML file containing keys for anonymization.
    A key file is required to anonymize a corpus. 
    """
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        raise QCError(
            "A language model is required to run this task. Please run:\n" + 
            "python -m spacy download en_core_web_sm"
        )
    entities = defaultdict(set)
    for file_path in tqdm(file_paths, desc="Processing documents"):
        text = file_path.read_text()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in LABELS:
                entities[ent.label_].add(ent)
    placeholders = {}
    for label, ents in entities.items():
        placeholder = LABELS[label]
        terms = sorted(e.text for e in ents)
        for i, term in enumerate(terms):
            placeholders[term] = f"{placeholder}_{i+1}"
    Path(key).write_text(yaml.dump(placeholders))

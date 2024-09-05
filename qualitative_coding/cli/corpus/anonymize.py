import os
import click
import spacy
import yaml
from tqdm import tqdm
from pathlib import Path
from collections import defaultdict
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.exceptions import QCError, IncompatibleOptions
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
@click.option("-o", "--out-dir", default="anonymized", help="location for anonymized documemts")
@click.option("-u", "--update", is_flag=True, help="Update documents in place")
@click.option("-d", "--dryrun", is_flag=True, help="Show diff instead of performing update")
@handle_qc_errors
def anonymize(settings, pattern, filenames, key, reverse, out_dir, update, dryrun):
    "Anonymize corpus files"
    settings_path = settings or os.environ.get("QC_SETTINGS", "settings.yaml")
    key_file = Path(key)
    out_path = Path(out_dir)
    log = configure_logger(settings_path)
    log.info("corpus anonymize", pattern=pattern, filenames=filenames, key=key, 
             reverse=reverse, out_dir=out_dir, update=update, dryrun=dryrun)
    corpus = QCCorpus(settings_path)
    with corpus.session():
        docs = corpus.get_documents(pattern=pattern, file_list=read_file_list(filenames))

    if key_file.exists():
        keys = yaml.safe_load(key_file.read_text())
        if reverse:
            keys = reverse_keys(keys)
        out_path.mkdir(exist_ok=True, parents=True)
        with corpus.session():
            for doc in docs:
                source = corpus.corpus_dir / doc.file_path
                dest = out_path / doc.file_path
                replace_keys(keys, source, dest)
                if update:
                    corpus.update_document(source, dest, dryrun)
    else:
        if reverse:
            raise QCError("Cannot use --reverse unless key file exists")
        doc_paths = [corpus.corpus_dir / doc.file_path for doc in docs]
        generate_key_file(key, doc_paths, log)

def replace_keys(keys, source, dest):
    text = source.read_text()
    for k, v in keys.items():
        text = text.replace(k, v)
    dest.write_text(text)

def reverse_keys(keys):
    """Converts anonymization keys into de-anonymization keys.
    In a dict, each key has a single value, but there may be multiple 
    values with the same key. In this case, uses the first occurence. 
    """
    rkeys = {}
    for k, v in keys.items():
        if v not in rkeys:
            rkeys[v] = k
    return rkeys

def generate_key_file(key, file_paths, log):
    """Generates a YAML file containing keys for anonymization.
    A key file is required to anonymize a corpus. 
    """
    model_name = 'en_core_web_sm'
    if spacy.util.is_package(model_name):
        log.debug(f"Using spacy model {model_name}")
    else:
        log.info(f"Downloading spacy model {model_name}")
        spacy.cli.download(model_name)
    try:
        nlp = spacy.load('en_core_web_sm')
    except OSError:
        raise QCError(
            "A language model is required to run this task. " +
            f"Automatic downloading of spacy model {model_name} " +
            "failed. Please install the language model manually:\n" +
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

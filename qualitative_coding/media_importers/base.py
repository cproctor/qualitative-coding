
from qualitative_coding.corpus import QCCorpus

class BaseMediaImporter:
    """Base class for media importers.
    The API for MediaImporters is a single method, `import_media`, which 
    takes an input filename and an output filename. We use filenames instead
    of streams beacuse 
    """
    def __init__(self, settings):
        self.settings = settings
        self.corpus = QCCorpus(self.settings)

    def import_media(self, input_filename, output_filename):
        raise NotImplementedError("Subclasses of BaseMediaImporter should be used.")

    def register_media_in_database(self, corpus_path):
        with self.corpus.session():
            self.corpus.register_document(corpus_path)

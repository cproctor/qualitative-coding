class BaseMediaImporter:
    """Base class for media importers.
    The API for MediaImporters is a single method, `import_media`, which 
    takes an input filename and an output filename. We use filenames instead
    of streams beacuse 
    """
    def import_media(self, input_filename, output_filename):
        raise NotImplementedError("Subclasses of BaseMediaImporter should be used.")"

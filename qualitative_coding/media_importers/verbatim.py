import shutil
from qualitative_coding.media_importers.base import BaseMediaImporter

class VerbatimImporter(BaseMediaImporter):
    """Imports media without making any changes.
    """
    def import_media(self, input_filename, output_filename):
        if input_filename != output_filename:
            shutil.copyfile(input_filename, output_filename)

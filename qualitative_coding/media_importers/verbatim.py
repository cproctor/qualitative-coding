import shutil
from qualitative_coding.media_importers.base import BaseMediaImporter

class VerbatimImporter(BaseMediaImporter):
    def import_media(self, input_filename, output_filename):
        shutil.copyfile(input_filename, output_filename)
        self.register_media_in_database(output_filename)



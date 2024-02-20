from subprocess import run
from qualitative_coding.media_importers.base import BaseMediaImporter

class PandocImporter(BaseMediaImporter):
    def import_media(self, input_filename, output_filename):
        cmd = f'pandoc -i "{input_filename}" -o "{output_filename}" --to plain --columns 80'
        run(cmd, shell=True, check=True)


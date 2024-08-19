from subprocess import run, CalledProcessError
from qualitative_coding.media_importers.base import BaseMediaImporter
from qualitative_coding.exceptions import QCError

class PandocImporter(BaseMediaImporter):
    def import_media(self, input_filename, output_filename):
        self.check_for_pandoc()
        cmd = f'pandoc -i "{input_filename}" -o "{output_filename}" --to plain --columns 80'
        run(cmd, shell=True, check=True)

    def check_for_pandoc(self):
        try:
            run("which pandoc", shell=True, check=True)
        except CalledProcessError:
            raise QCError("pandoc is required but was not found. Please install pandoc.")


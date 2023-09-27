from subprocess import run

class PandocImporter:
    def import_media(self, input_filename, output_filename):
        cmd = f"pandoc -i {input_filename} -o {output_filename} --to plain --columns 80"
        run(cmd, shell=True, check=True)


from qualitative_coding.media_importers.base import BaseMediaImporter
from textwrap import fill
import webvtt

class VTTImporter(BaseMediaImporter):
    """Imports a VTT transcript file, stripping out timestamps and collapsing 
    adjacent talk turns from the same speaker.
    """
    def import_media(self, input_filename, output_filename):
        turns = []
        current_speaker = None
        current_speech = ""
        for caption in webvtt.read(input_filename):
            speaker, speech = caption.text.split(':', 1)
            if speaker == current_speaker: 
                current_speech += speech
            else:
                if current_speech: 
                    turns.append({'speaker': current_speaker, 'speech': current_speech})
                current_speaker = speaker
                current_speech = speech
        turns.append({'speaker': current_speaker, 'speech': current_speech})
        with open(output_filename, 'w') as fh:
            for i, turn in enumerate(turns):
                if i > 0:
                    fh.write('\n\n')
                fh.write(fill(turn['speaker'] + ': ' + turn['speech'], width=80))

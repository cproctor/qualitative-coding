# Next steps

# 2023

- qc cb mis-populates "$ROOT$" when there are no codes.

## Not yet implemented, but could be implemented

- cli import:
  - transcription
  - auto-fieldnotes?


## New API

- init
  - looks for settings.
  - create directories

I want to publish this tool. What's needed? 

- Add interrater reliability
  - Verbose mode: Gives language suitable for the methods section.
  - Just offer Krippendorff's alpha; this is all anyone really needs. 
    - Select which documents.
    - Select which coders.
    - Select which codes. (allow recursive inclusion)
    - Select which unit.
    - Is it multilabel? 
      - If so, we need a distance metric between sets. MASI is an option: https://stackoverflow.com/questions/32733510/nltk-agreement-with-distance-metric
        - Treat uncoded units as missing data (report this).
      - If not, 
        - then raise an error in cases where more than a single code is applied to a unit.
        - then if --blank, treat uncoded units as missing data. Otherwise, treat uncoded units as having no code applied.

- Add autocoding
  - Verbose mode: Gives language suitable for the methods section.

- Add import/export to standard format. 



# Next steps

What's the problem here? The problem is I'm thinking about where to create the interface
boundary on QCCorpus, specifically who should handle its sessions. This is an implementation
detail I can't really hide within methods, because that would mean that a session would be
scoped to that session, and I would lose many of the benefits of the ORM.

OK, so given that I need the client of QCCorpus to manage the session, shall I expose the 
context manager? This seems best.

# 2023

- qc cb mis-populates "$ROOT$" when there are no codes.

## Not yet implemented, but could be implemented

- cli import:
  - transcription
  - auto-fieldnotes?

- Why data structure as separate coder files? It's efficient, and 
  then you can also see who's coding in the git logs. Basically, 
  the data structure is compatible with the use case, while using 
  widely-used data formats.

## Storage mechanism

Storage is distributed across three locations: 
- courpus text files
- codes.yaml
- the sqlite database

For text files and the code tree, direct file access is the most graceful user interface. 
For coding, the relational database is designed for the kinds of queries we have.

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



# Next steps

- find should have --output options for csv
- rename not implemented for database. 
- Remove qc cb. The codebook should be automatically updated after coding.
- The min and max should targed different values depending on whether -a is present. 
  If -a, then we care about the recursive total codes. If not, then we care about that code
  exactly.

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

## Notes 2024-02-20

- Ensure that `import` is idempotent. Note files which already exist. 
- Provide `corpus remove` to remove a file. Warn about all the Coded lines which will be deleted.
- 'corpus rebase`

## Notes 2024-03-11

### What's the API for autocode?
I need to send across training and estimation data
- The codes only need to be specified for test data. Either the autocoder will 
  fit itself based on the given codes, or it'll do its own thing

qc autocode 
autocoder               Name of autocoder (either built in or specified in settings.py)
coder                   Name of coder to use
codes                   Codes to select for training set (If no codes given, send no training data)
-r, --recursive-codes   Include recursive codes
-v, --cross-validate    Cross-validate the estimator
-k, --folds x           Specify number of folds for cross-validation
-p, --pattern-train

AI tools to build in. All of these need to be able to be parameterized.
- suggest
- named_entities
- sentiment

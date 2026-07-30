import csv
import sys
from tabulate import tabulate, tabulate_formats

TABLE_FORMATS = tuple(tabulate_formats) + ("csv",)

def is_raw_output(format=None, outfile=None):
    "True when output should be unstyled data (CSV file or CSV to stdout)."
    return bool(outfile) or format == "csv"

def write_table(rows, cols, format=None, outfile=None, **tabulate_kwargs):
    """Writes tabular data as CSV (to outfile, or to stdout when format is "csv"),
    or otherwise renders it with tabulate.
    """
    if outfile:
        with open(outfile, 'w', newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(cols)
            writer.writerows(rows)
    elif format == "csv":
        writer = csv.writer(sys.stdout)
        writer.writerow(cols)
        writer.writerows(rows)
    else:
        print(tabulate(rows, cols, tablefmt=format, **tabulate_kwargs))

#!/usr/bin/env python3
"""Converts Morgan Stanley (MSSB) 1099-B PDFs to CSV."""

import collections
import csv
import datetime
import re
import subprocess
import sys

# Maps PDF category names to TXF codes.
# See the following for codes and structure:
# https://www.taxdataexchange.org/txf/txf-spec.html
CATEGORIES = {
    'Short Term – Noncovered Securities': '711',
    'Long Term – Noncovered Securities': '713',
}

# Match a section of sales for one sales category.
# The last line can say 'Total Short Term – Noncovered Securities' or
# 'Total Short Term Noncovered Securities' (without the hypen) so match
# only on "^Total".
CATEGORIES_PATTERN = '|'.join(CATEGORIES)
SECTION_EXPR = re.compile(r'(' + CATEGORIES_PATTERN + r')'
                          r'(.*?)'
                          r'^Total', re.DOTALL | re.MULTILINE)

# Matches a row.
#
# Example:
#   ALPHABET INC CL C
#   12345A678
#   1.000000 01/01/20 02/01/20 $2,000.00 $1,9999.00
#
# Example:
#   1234 R18 ALPHABET INC CL C
#   12345A678
#   1.000000 VARIOUS 02/01/20 $2,000.00 $1,9999.00
ROW_EXPR = re.compile(
    '^'
    r'(?:(\d+)\s+)?'  # RefNumber (optional)
    r'(?:([a-zA-Z]\d\d)\s+)?'  # PlanNumber (optional)
    r'([\w ]+)\s+'  # Description
    r'(\w+)\s+'  # CUSIP
    r'(\d+\.\d+)\s+'  # Quantity
    r'((?:\d+/\d+/\d+|\w+))\s+'  # DateAcquired
    r'(\d+/\d+/\d+)\s+'  # DateSold
    r'(\$[0-9,.]+)\s+'  # GrossProceeds
    r'(\$[0-9,.]+)\s',  # CostBasis
    re.MULTILINE)

# Fields of the output, suitable as a CSV header.
FIELDS = [
    'Category', 'RefNumber', 'PlanNumber', 'Description', 'CUSIP', 'Quantity',
    'DateAcquired', 'DateSold', 'GrossProceeds', 'CostBasis'
]

# Type of each row of output.
Row = collections.namedtuple('Row', FIELDS)


def _parseSection(section_text, section_name):
    return [
        Row(*((section_name, ) + row_match.groups()))
        for row_match in ROW_EXPR.finditer(section_text)
    ]


def parsePdf(path):
    """Returns a list of `Row` tuples."""
    text = subprocess.check_output(['pdftotext', '-raw', path, '-']).decode()
    return [
        row  #
        for section_match in SECTION_EXPR.finditer(text) for row in
        _parseSection(section_match.group(2), section_match.group(1))
    ]


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'Usage: {sys.argv[0]} <mssb_1099b_file.pdf>')
    rows = parsePdf(sys.argv[1])
    writer = csv.writer(sys.stdout)
    writer.writerow(FIELDS)
    writer.writerows(rows)

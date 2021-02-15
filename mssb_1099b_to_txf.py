#!/usr/bin/env python
"""mssb_1099b_to_txf converts simple Morgan Stanley (MSSB) 1099-B PDFs to TXF files."""

import datetime
import re
import subprocess
import sys

import mssb_1099b_to_csv


def parseAndPrintRow(row):
    entry_code = mssb_1099b_to_csv.CATEGORIES[row.Category]
    description = ' '.join(filter(None, [
        row.RefNumber,
        row.PlanNumber,
        row.Description,
    ]))
    print('TD')
    print('N' + entry_code)
    print('C1')
    print('L1')
    print('P' + description)
    print('D' + row.DateAcquired)
    print('D' + row.DateSold)
    # These have a leading dollar sign.
    print(row.CostBasis)
    print(row.GrossProceeds)
    print("$")  # Wash sale. Leaving blank. They aren't handled here.
    print('^')


def parseAndPrintPdf(path):
    rows = mssb_1099b_to_csv.parsePdf(path)
    print('V042')
    print('A mssb_1099b_to_txf')
    print('D ' + datetime.datetime.now().strftime('%m/%d/%Y'))
    print('^')
    for row in rows:
        parseAndPrintRow(row)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'Usage: {sys.argv[0]} path-to-1099b-pdf')
    parseAndPrintPdf(sys.argv[1])

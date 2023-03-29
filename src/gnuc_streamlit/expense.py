import sys

import gncxml
import pandas as pd

GNUFILE_PATH = "/home/isa/Documents/my-accounts/real.gnucash"

def main():
    try:
        book = gncxml.Book(GNUFILE_PATH)
    except OSError as err:
        sys.exit(err)
        

    splits = book.list_splits()
    ACCOUNT_TYPE = 'EXPENSE'

    # Filter based on BHD Expenses
    splits = splits.query(
        f"act_type == '{ACCOUNT_TYPE}' \
           and trn_crncy_id == 'BHD'").reset_index()

    splits.value = splits.value.astype('float64')

    # Only interested in some columns
    cols_of_interest = ['trn_date', 
                        'act_path',
                        'act_name',
                        'trn_description',
                        'value']
    splits = splits[cols_of_interest].sort_values('trn_date')


# Split Date into Year, Month, Day...
    _ = splits['trn_date'].dt
    splits['year'], splits['month'], splits['day'] = _.year, _.month, _.day

    print(splits.groupby(['year', 'month', 'day']).sum(numeric_only=True))




import sys

import gncxml
import pandas as pd
import streamlit as st

GNUFILE_PATH = "/home/isa/Documents/my-accounts/real.gnucash"

@st.cache_data
def get_expenses():
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
    cols_rename_mapper = dict(zip(cols_of_interest,
         ('Date', 'FullAccountName', 'Account', 'Desc', 'Amount')))
    splits = splits.rename(cols_rename_mapper, axis=1)


# Split Date into Year, Month, Day...
    print(splits['Date'])
    _ = splits['Date'].dt
    splits['Year'], splits['Month'], splits['Day'] = _.year, _.month, _.day
    return splits
        # .groupby(['trn_date', 'year', 'month', 'day'])\
        # .sum(numeric_only=True)\
        # .reset_index()



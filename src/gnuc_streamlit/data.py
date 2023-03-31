import sys

import gncxml
import streamlit as st

GNUFILE_PATH = "/home/isa/Documents/my-accounts/real.gnucash"

@st.cache_data
def get_expenses():
    try:
        book = gncxml.Book(GNUFILE_PATH)
    except OSError as err:
        sys.exit(err)
        

    splits = book.list_splits()
    old_column_names = ('trn_date',
                        'act_path',
                        'act_name',
                        'trn_description',
                        'value')
    new_columns_names = ('Date',
                         'FullAccountName',
                         'Account',
                         'Desc',
                         'Amount')
    cols_rename_mapper = dict(zip(old_column_names, new_columns_names))

    splits = splits\
        .query(f"act_type == 'EXPENSE' and trn_crncy_id == 'BHD'")\
        .reset_index()\
        .sort_values('trn_date')\
        .rename(cols_rename_mapper, axis=1)\
        .filter(new_columns_names)

    splits.Amount = splits.Amount.astype('float64')


    # Split Date into Year, Month, Day...
    _ = splits['Date'].dt
    splits['Year'], splits['Month'], splits['Day'] = _.year, _.month, _.day
    return splits



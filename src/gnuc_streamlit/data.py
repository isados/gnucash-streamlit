import sys

import streamlit as st
from piecash import open_book
import pandas as pd

GNUFILE_PATH = "/home/isa/Documents/my-accounts/real.gnucash"

def get_accounts_df(accounts):
    df_rows = []
    df_columns = ['account.fullname', 'account.shortname', 'account.guid', 'account_type']
    for acc in accounts:
        df_rows.append((acc.fullname, acc.name, acc.guid, acc.type))
    return pd.DataFrame(data=df_rows, columns=df_columns)

    

@st.cache_data
def get_expenses():
    try:
        with open_book(f"sqlite:///{GNUFILE_PATH}", readonly=True) as book:
            basic_splits = book.splits_df()
            accounts = get_accounts_df(book.accounts)
            
            splits = basic_splits.merge(accounts,
                 left_on='account.fullname',
                 right_on='account.fullname',
                 )
    except OSError as err:
        sys.exit(err)
        
    old_column_names = ('transaction.post_date',
                        'account.fullname',
                        'account.shortname',
                        'transaction.description',
                        'value',
                        )
    new_columns_names = ('Date',
                         'FullAccountName',
                         'Account',
                         'Desc',
                         'Amount',
                         )
    cols_rename_mapper = dict(zip(old_column_names, new_columns_names))

    splits = splits\
        .reset_index()\
        .rename(cols_rename_mapper, axis=1)\
        .query(f"account_type == 'EXPENSE'")\
        .filter(new_columns_names)\
        .sort_values('Date')
#  and transaction.currency.mnemonic == 'BHD'

    splits.Amount = splits.Amount.astype('float64')
    splits.Date = pd.to_datetime(splits.Date)


    # Split Date into Year, Month, Day...
    _ = splits['Date'].dt
    splits['Year'], splits['Month'], splits['Day'] = _.year, _.month, _.day
    splits, num_of_sublevels = create_sublevels_of_accounts(splits)
    return splits, num_of_sublevels

def _split_account_name_into_sublevels(full_account_name, max_levels):
    path_parts = full_account_name.split(':')
    level_names = []
    
    for i in range(len(path_parts)):
        level_names.append(':'.join(path_parts[0:i+1]))

    number_of_levels = len(level_names)
    remaining_levels_to_pad = max_levels - number_of_levels
    LAST_LEVEL = level_names[-1]
    level_names.extend([LAST_LEVEL]*remaining_levels_to_pad)
    return level_names

def create_sublevels_of_accounts(df):
    df = df.copy()
    MAX_LEVELS = df['FullAccountName']\
            .apply(lambda account_str: account_str.count(':')+1)\
            .max()

    levels_as_columns = [f'level{num}_account_name' for num in range(MAX_LEVELS)]
    df[levels_as_columns] = df['FullAccountName']\
        .apply(_split_account_name_into_sublevels, args=(MAX_LEVELS,))\
        .to_list()
    return df, MAX_LEVELS
    


if __name__ == "__main__":
    # print(_split_account_name_into_sublevels('Exp:Full:Hello', 4))
    df, max_levels = get_expenses()
    df.to_csv('out.csv', index=False)
    print(df)



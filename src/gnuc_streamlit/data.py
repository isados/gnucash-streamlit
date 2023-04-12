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
    depth_of_path = len(path_parts)
    padding_none_length = max_levels - depth_of_path
    path_parts += [None] * padding_none_length
    return path_parts

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
    
def convert_sub_levels_to_account_name(row, sub_level):
    path_parts = []
    for num in range(sub_level+1):

        path = row[f'level{num}_account_name']
        if not path: continue
        path_parts.append(path)
    return ":".join(path_parts)


if __name__ == "__main__":
    # print(_split_account_name_into_sublevels('Exp:Full:Hello', 4))
    df, max_levels = get_expenses()
    accounts = df[['level0_account_name',  'level1_account_name', 'level2_account_name',  'level3_account_name', ]]
    accounts.sort_values(list(accounts.columns)).drop_duplicates().to_csv('account.csv', index=False)
    df.to_csv('out.csv', index=False)
    print(df)



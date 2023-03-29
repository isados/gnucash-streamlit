import sqlite3
from pprint import pprint
import piecash as pc
import pandas as pd
from pandas import read_sql_query, read_sql_table
from piecash import Transaction, ledger, Split
from piecash.core.factories import single_transaction


def list_tables(dbfile):
    with sqlite3.connect(dbfile) as dbcon:
        tables = list(read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", dbcon)['name'])
    
        # out = {tbl : read_sql_query(f"SELECT * from {tbl}", dbcon) for tbl in tables}
    
    return tables

def read_table(table):
    """Returns The Requested table from the DB"""
    with sqlite3.connect(DB) as dbcon:
        df = pd.read_sql(f"select * from {table}", con=dbcon)
    return df

def find_sub_accounts(data_object: dict, accs_df: pd.DataFrame):
    for _, row in accs_df.iterrows():
        if row['parent_guid'] == data_object['id']:
            sub_account = {'name': row['name'], 'id': row['guid'], 'accs': []}
            find_sub_accounts(sub_account, accs_df)
            data_object['accs'].append(sub_account)
            
            
def build_heirarchy_of_accounts(accs_df: pd.DataFrame, root_id: str):
    # This data object will hold the heirarchy of accounts
    data_obj = {'name': 'Expenses', 'id': root_id, 'accs': []}
    find_sub_accounts(data_obj, accs_df)
    return data_obj

def list_full_names(acc, *, text='', collection):
    if isinstance(acc, dict): 
        text+=acc['name']
        if not acc.get('accs'):
            return collection.append((acc['id'], text))
        list_full_names(acc['accs'], text=text+':', collection=collection)
    if isinstance(acc, list):
        for sub_acc in acc:
            list_full_names(sub_acc, text=text, collection=collection)


if __name__ == '__main__':
    # GLOBAL VARIABLES HERE
    DB = 'sqlversion.gnucash'
    read_table('transactions')
    print(list_tables(DB))

    # Read Accounts Table Here
    expense_accs = read_table('accounts')

    ROOT_ACC = expense_accs.iloc[0].guid

    EXPENSE_ACCS = expense_accs.query("account_type == 'EXPENSE'")
    EXPENSE_ROOT_ACC = EXPENSE_ACCS.query(f"parent_guid == '{ROOT_ACC}'")
    EXPENSE_ROOT_ID = EXPENSE_ROOT_ACC.iloc[0]['guid']
    hierarchy = build_heirarchy_of_accounts(EXPENSE_ACCS, EXPENSE_ROOT_ID)
    collection = []
    list_full_names(hierarchy, collection=collection)
    print(pd.DataFrame(columns=['id', 'name'], data=collection))
    
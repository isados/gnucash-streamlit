"""Reporting Module"""
###########################################################################################################
###########################################################################################################
###########################################################################################################
######## author = Isa AlDoseri
######## website = https://www.linkedin.com/in/isadoseri/
######## version = 1.0
######## status = WIP
######## deployed at = 
######## layout inspired by https://share.streamlit.io/tylerjrichards/streamlit_goodreads_app/books.py
###########################################################################################################
###########################################################################################################
###########################################################################################################


import streamlit as st
from functools import partial
import plotly.express as px
import pandas as pd
import numpy as np

from gnuc_streamlit.data import get_expenses, convert_sub_levels_to_account_name
from gnuc_streamlit.core import dateutils



time_period_to_dtvalues = {
    'Current Month': partial(dateutils.get_month),
    'Previous Month': partial(dateutils.get_month, 1),
    '2 Months Ago': partial(dateutils.get_month, 2),
}

def main():
    """CLI Executable"""
    st.set_page_config(page_title='Finances',
                    page_icon=':bar_chart:',
                    layout='wide')
    left_col, right_col = st.columns((2/3, 1/3))
    left_col.title('Finances Overview :dollar:')
    right_col.subheader('Streamlit App by [Isa AlDoseri](https://www.linkedin.com/in/isadoseri/)')


    # Get Data
    df, sublevels = get_expenses()


    # --- SIDEBARD & Filtering --- #
    st.sidebar.header('Filter here:')
    sel_sublevel = st.sidebar.select_slider('Sub Levels',
                                        options=range(sublevels),
                                        value=1)
    period = st.sidebar.radio('Period:',
                              options=time_period_to_dtvalues.keys())
    start_date, end_date = time_period_to_dtvalues[period]()
    df_selection = df.query(
        'Date <= @end_date '
        'and Date >= @start_date').copy()

    df_selection.loc[:, 'Account'] = df_selection.apply(convert_sub_levels_to_account_name, args=[sel_sublevel,], axis=1)
    expense_type = st.sidebar.multiselect('Expense Types:',
                                options=df_selection['Account'].unique())
    if expense_type:
        df_selection = df_selection[df_selection.Account.isin(expense_type)]




    
    # TOP PAGE 
    budget = st.number_input('Budget (default is 300)', value=300)

    left_column, right_column = st.columns(2)
    with left_column:
        total = df_selection.Amount.sum()
        savings = budget-total
        under_or_over_budget = 'More' if savings > 0 else 'Less'
        st.metric(
            'Total Expenses',
            f"BHD {total:.2f}",
            f"{savings:.2f} {under_or_over_budget} in Savings",
        )
    with right_column:
        st.metric(
            'Number of Txns',
            df_selection.shape[0],
        )


    # fig_product_sales.update_layout(
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     xaxis=(dict(showgrid=False)),
    # )

    

    # --- EXPENSES BY WEEK ---- #
    expenses_by_week = df_selection\
        .groupby([pd.Grouper(key='Date', freq='W'), 'Account'])\
        .sum(numeric_only=True)[['Amount']]\
        .reset_index()
    fig_expenses_by_week = px.bar(
        expenses_by_week,
        y='Amount',
        x=expenses_by_week.Date,
        color='Account',
        title='<b>Expenses By Week</b>',
    #     orientation='h',
        # color_discrete_sequence=['#0083B8'] * len(expenses_by_day),
        template='plotly_white',
    )

    # --- EXPENSES BY DAY [BAR] --- #
    expenses_by_day = df_selection\
        .groupby(['Date', 'Account'])\
        .sum(numeric_only=True)[['Amount']]\
        .reset_index()
    fig_expenses_by_day = px.bar(
        expenses_by_day,
        y='Amount',
        x=expenses_by_day.Date,
        color='Account',
        title='<b>Expenses By Day</b>',
        # color_discrete_sequence=['#0083B8'] * len(expenses_by_day),
        template='plotly_white',
    )
    fig_expenses_by_day.update_layout(
        xaxis=dict(tickmode='linear'),
        yaxis=dict(showgrid=False)
    )

    # --- SUNBURST SPLIT UP OF EXPENSES
    lvl_cols_selected = [f'level{i}_account_name' for i in range(sel_sublevel+1)]
    df_sunburst = df_selection\
        .groupby(lvl_cols_selected, dropna=False)['Amount']\
        .sum()\
        .reset_index()
    fig_split_up_expenses = px.sunburst(
        df_sunburst,
        path=lvl_cols_selected,
        values='Amount',
    )

    # --- COMBINING ALL CHARTS ABOVE --- #
    left_column, right_column = st.columns(2)
    st.plotly_chart(fig_expenses_by_week, use_container_width=True)
    st.plotly_chart(fig_expenses_by_day, use_container_width=True)
    st.plotly_chart(fig_split_up_expenses, use_container_width=True)


    # --- HIDE STREAMLIT STYLE --- #
    hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

if __name__ == '__main__':
    main()

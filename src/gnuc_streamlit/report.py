"""Reporting Module"""

import streamlit as st
from functools import partial
import plotly.express as px

from gnuc_streamlit.data import get_expenses
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

    st.title(':bar_chart: Finances')
    st.markdown('##')

    df, sublevels = get_expenses()



    # --- SIDEBARD --- #
    st.sidebar.header('Filter here:')
    sel_sublevel = st.sidebar.select_slider('Sub Levels',
                                        options=range(sublevels),
                                        value=1)
    period = st.sidebar.radio('Period:',
                              options=time_period_to_dtvalues.keys())
    expense_type = st.sidebar.multiselect('Expense Types:',
                                options=df['Account'].unique())


    # FILTERING
    start_date, end_date = time_period_to_dtvalues[period]()

    df_selection = df.query(
        'Date <= @end_date '
        'and Date >= @start_date').copy()
    df_selection.loc[:, 'Account'] = df_selection.loc[:, f'level{sel_sublevel}_account_name']
    if expense_type:
        df_selection = df_selection[df_selection.Account.isin(expense_type)]





    # TOP KPIs
    num_trxns = df_selection.shape[0]
    expenses_total = round(df_selection.Amount.sum(), 3)
    high_expense = df_selection\
                    .sort_values('Amount', ascending=False)\
                    .iloc[0] if num_trxns else None
    
    


    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.subheader(f'{period} Expenses')
        st.subheader(f'BHD {expenses_total}')

    with middle_column:
        st.subheader('# Transactions')
        st.subheader(num_trxns)
        # st.subheader(':star:' * int(89) + str(89))

    if num_trxns:
        with right_column:
            st.subheader('Highest Expense')
            st.text(f'{high_expense.FullAccountName}')
            st.text(f'{high_expense.Desc}')
            st.subheader(f'BHD {high_expense.Amount}')

    # st.dataframe(df_selection)

    # --- SALES BY PRODUCT LINE [BAR] --- #
    # sales_by_product_line = df_selection\
    #     .groupby('Product line')\
    #     .sum(numeric_only=True)[['Total']]\
    #     .sort_values('Total')
    # fig_product_sales = px.bar(
    #     sales_by_product_line,
    #     x='Total',
    #     y=sales_by_product_line.index,
    #     orientation='h',
    #     title='<b>Sales by Product Line</b>',
    #     color_discrete_sequence=['#0083BB'] * len(sales_by_product_line),
    #     template='plotly_white',
    # )
    # fig_product_sales.update_layout(
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     xaxis=(dict(showgrid=False)),
    # )

    # --- SALES BY HOuR [BAR] --- #
    expenses_by_day = df_selection\
        .groupby(['Date', 'Account'])\
        .sum(numeric_only=True)[['Amount']]\
        .reset_index()
        # .sort_values('Total')
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
    # st.dataframe(df_selection)
    
    data = dict(
    character=["Eve", "Cain", "Seth", "Enos", "Noam", "Abel", "Awan", "Enoch", "Azura"],
    parent=["", "Eve", "Eve", "Seth", "Seth", "Eve", "Eve", "Awan", "Eve" ],
    value=[10, 14, 12, 10, 2, 6, 6, 4, 4])

    fig_split_up_expenses = px.sunburst(
        df_selection,
        path=[f'level{i}_account_name' for i in range(0,sublevels)],
        values='Amount',
        color='Account',
    )



    # --- COMBINING ALL CHARTS ABOVE --- #
    left_column, right_column = st.columns(2)
    # left_column.plotly_chart(fig_expenses_by_day, use_container_width=True)
    st.plotly_chart(fig_expenses_by_day, use_container_width=True)
    st.plotly_chart(fig_split_up_expenses, use_container_width=True)
    # right_column.plotly_chart(fig_hourly_sales, use_container_width=True)


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

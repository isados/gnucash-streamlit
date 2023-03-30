"""Reporting Module"""

import os
import pandas as pd
import streamlit as st
from functools import partial
import plotly.express as px
from datetime import datetime

from gnuc_streamlit.data import get_expenses
from gnuc_streamlit.core import dateutils


@st.cache_data
def get_data_from_csv():
    """Get Sales Data from CSV"""
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'supermarkt_sales.csv')
    data = pd.read_csv(filename)
    data['hour'] = pd.to_datetime(data['Time'], format='%H:%M').dt.hour
    return data

time_period_to_value = {
    'Current Month': partial(dateutils.get_month),
    'Previous Month': partial(dateutils.get_month, 1),
}

def main():
    """CLI Executable"""
    st.set_page_config(page_title='Finances',
                    page_icon=':bar_chart:',
                    layout='wide')

    st.title(':bar_chart: Finances')
    st.markdown('##')

    df = get_expenses()




    # --- SIDEBARD --- #
    st.sidebar.header('Please filter here:')
    default_period = 'Current Month'
    period = st.sidebar.radio('Period:',
                                options=time_period_to_value.keys(),
                                )


    # cust_type = st.sidebar.multiselect('Customer Type:',
    #                             options=df['Customer_type'].unique(),
    #                             default=df['Customer_type'].unique())

    # weeks_expenses = expenses\
    #             .query(f'Date >= "{current_week[0]}" and Date <= "{current_week[1]}"')\
    #             .Amount.sum()
    start_date, end_date = time_period_to_value[period]()
    print(start_date, end_date)
    df_selection = df\
                    .query('Date <= @end_date and Date >= @start_date')
    st.dataframe(df_selection)





    # TOP KPIs
    expenses_total = round(df_selection.Amount.sum(), 3)


    left_column, middle_column, right_column = st.columns(3)

    with left_column:
        st.subheader(f'{period} Expenses')
        st.subheader(f'BHD {expenses_total}')

    # with middle_column:
    #     st.subheader('Average Rating')
    #     st.subheader(':star:' * int(89) + str(89))

    with right_column:
        st.subheader('Average Sales for Transaction')
        st.subheader(f'US $ {900}')

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
    # sales_by_hour = df_selection\
    #     .groupby('hour')\
    #     .sum(numeric_only=True)[['Total']]\
    #     .sort_values('Total')
    # fig_hourly_sales = px.bar(
    #     sales_by_hour,
    #     y='Total',
    #     x=sales_by_hour.index,
    #     title='<b>Sales by Hour</b>',
    #     color_discrete_sequence=['#0083B8'] * len(sales_by_hour),
    #     template='plotly_white',
    # )
    # fig_hourly_sales.update_layout(
    #     xaxis=dict(tickmode='linear'),
    #     yaxis=dict(showgrid=False)
    # )


    # --- COMBINING ALL CHARTS ABOVE --- #
    # left_column, right_column = st.columns(2)
    # left_column.plotly_chart(fig_product_sales, use_container_width=True)
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

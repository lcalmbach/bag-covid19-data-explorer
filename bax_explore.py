from numpy import float64
import streamlit as st
import altair as alt
import pandas as pd
from st_aggrid import AgGrid
import const as cn
import tools

class App:
    """
    """

    def __init__(self):
        self.filename = ''

    
    def show_table(self, df):
        AgGrid(df)
        href = tools.download_link(df, f'{self.filename}.csv', f'Download data ({len(df)} rows)')
        st.markdown(href,unsafe_allow_html=True)

    def show_plots(self, df):
        def get_chart(df_chart, title, color_col):
            chart = alt.Chart(df_chart, title=title).mark_line().encode(
                    x=f'{date_col}:T',
                    y='value:Q',
                    tooltip=[date_col,'geoRegion','parameter','value'],
                    color=color_col,
                ).properties(
                    width=800,
                    height=300
                )
            return chart

        def melt_data(df):
            lst_felder =  [ x for x in list(df.columns) if (df[x].dtypes in ('int64','float64') ) ]
            df = pd.melt(df, id_vars=[date_col, 'geoRegion'], value_vars=lst_felder, var_name='parameter', value_name='value')
            return df

        df = melt_data(df)        
        group_plot_by = st.sidebar.selectbox('Group charts by', ['canton','parameter'])
        if  group_plot_by == 'canton':
            for region in df['geoRegion'].unique():
                df_filtered = df.query('geoRegion == @region')
                chart = get_chart(df_filtered, region, 'parameter')
                st.altair_chart(chart)
        else:
            for par in df['parameter'].unique():
                df_filtered = df.query('parameter == @par')
                chart = get_chart(df_filtered, par, 'geoRegion')
                st.altair_chart(chart)
            

    def show_menu(self):
        global date_col

        dataset_type_filter = st.sidebar.selectbox('Dataset-type', ['daily', 'weekly by age', 'weekly by sex'])

        datasets_dict, ok = tools.get_datasets_list(dataset_type_filter)
        self.filename = st.sidebar.selectbox("Select a dataset", list(datasets_dict.keys()))
        df, date_col = tools.get_data(datasets_dict[self.filename], dataset_type_filter)
        if 'weekly' in dataset_type_filter:
            df[date_col] = df[date_col].astype(str)
        df = tools.filter_regions(df)
        df = tools.filter_fields(df, date_col, False)
        
        view_as = tools.get_output_type()
        if view_as.lower() == 'table':
            self.show_table(df)
        else:
            self.show_plots(df)
        
    
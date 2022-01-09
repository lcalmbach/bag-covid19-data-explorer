import streamlit as st
import const as cn
import numpy as np
import altair as alt
import pandas as pd
from st_aggrid import AgGrid
from datetime import date

import tools
import const

W_DEV = const.WAVES

class App:
    """
    """

    def __init__(self, texts):
        self.texts = texts


    def get_wave_data(self, df, date_col):
        waves = {}
        W_DEV = const.WAVES
        cols = st.columns(3)
        waves['wave 1'] = {}
        waves['wave 2'] = {}
        waves['wave 3'] = {}
        waves['wave 4'] = {}
        waves['wave 5'] = {}
        waves['wave 1']['start'] = cols[0].date_input('Wave1 start',value=W_DEV['wave 1']['date_start'])
        waves['wave 2']['start'] = cols[0].date_input('Wave2 start',value=W_DEV['wave 2']['date_start'])
        waves['wave 3']['start'] = cols[0].date_input('Wave3 start',value=W_DEV['wave 3']['date_start'])
        waves['wave 4']['start'] = cols[0].date_input('Wave4 start',value=W_DEV['wave 4']['date_start'])
        waves['wave 5']['start'] = cols[0].date_input('Wave5 start',value=W_DEV['wave 5']['date_start'])
        
        waves['wave 1']['end'] = cols[1].date_input('Wave1 end',value=W_DEV['wave 1']['date_end'])
        waves['wave 2']['end'] = cols[1].date_input('Wave2 end',value=W_DEV['wave 2']['date_end'])
        waves['wave 3']['end'] = cols[1].date_input('Wave3 end',value=W_DEV['wave 3']['date_end'])
        waves['wave 4']['end'] = cols[1].date_input('Wave3 end',value=W_DEV['wave 4']['date_end'])
        waves['wave 5']['end'] = cols[1].date_input('Wave5 end', value = date.today())

        df['wave'] = ''
        for x in range(1,len(W_DEV)+1):
            key = f"wave {x}"
            waves[key]['start'] = np.datetime64(waves[key]['start'])
            waves[key]['end'] = np.datetime64(waves[key]['end'])
            df.loc[ (df[date_col] >= waves[key]['start']) & (df[date_col] <= waves[key]['end']), 'wave'] = key

        df = df.query("wave > ''")
        return df, waves


    def get_wave_stats(self, df, waves):
        sel_field = df.columns[3]
        df_stats = df.groupby(['wave', 'geoRegion'])[sel_field].agg(['sum','mean','max']).reset_index()
        df_stats.columns = ['wave', 'geoRegion', f"{sel_field}_sum",f"{sel_field}_mean",f"{sel_field}_max"]
        df_stats['duration'] = 0
        for x in range(1,len(W_DEV)+1):
            key = f"wave {x}"
            diff_days = (waves[key]['end'] - waves[key]['start']).astype(int)
            df_stats.loc[df_stats['wave'] == key, 'duration'] = diff_days
            df_stats.loc[df_stats['wave'] == key, 'start'] = waves[key]['start']
            df_stats.loc[df_stats['wave'] == key, 'end'] = waves[key]['end']
        return df_stats
        
    def show_wave_charts(self, df, waves, date_col):
        """
        shows a series of charts, grouped by either cantons or wave. instead of the date, a day number is used
        as the x axis starting from day 0 (start of wave) allowing the waves to be stacked.
        """
        def fill_days_col(df):
            """
            fills a wave start column then calculates a days column as days = date - start of wave in days
            """
            for x in range(1,len(W_DEV)+1):
                key = f"wave {x}"
                df.loc[df['wave'] == key, 'start'] = waves[key]['start']
            df['days'] = (df[date_col] - df['start']).astype('timedelta64[D]')
            return df
        
        df = fill_days_col(df)
        #st.write(df)
        chart_type = st.sidebar.selectbox('Chart type',['timeseries'])
        group_by = st.sidebar.selectbox('Group charts by',['canton', 'wave'])
        settings = {}
        if chart_type.lower() == 'timeseries':
            settings['x'] = alt.X('days:Q')
            settings['y'] = alt.Y(f"{df.columns[3]}:Q")
            if group_by == 'canton':
                for canton in df['geoRegion'].unique():
                    df_filtered = df.query('geoRegion == @canton')
                    settings['title'] = canton
                    settings['tooltip'] = list(df.columns) 
                    settings['color'] = 'wave:N'
                    chart = tools.get_line_chart(df_filtered, settings)  
                    st.altair_chart(chart)                  
            else:
                for wave in df['wave'].unique():
                    df_filtered = df.query('wave == @wave')
                    settings['title'] = wave
                    settings['tooltip'] = list(df.columns) 
                    settings['color'] = 'geoRegion:N'
                    chart = tools.get_line_chart(df_filtered, settings)
                    st.altair_chart(chart)


    def filter_waves(self, df):
        """
        todo: marry with region filter
        """
        lst_waves = list(df['wave'].unique())
        wave_filter = st.sidebar.multiselect('Wave', lst_waves)
        if len(wave_filter) > 0:
            df = df.query('wave.isin(@wave_filter)')
        return df


    def show_menu(self):
        """
        retrieves the common input for stats and charts and then calls either the stats or charts routine
        """

        datasets_dict, ok = tools.get_datasets_list('daily')
        key = st.sidebar.selectbox("Select dataset", list(datasets_dict.keys()))
        df, date_col = tools.get_data(datasets_dict[key], 'daily')
        field = tools.filter_field(df, True)
        df = tools.filter_regions(df)
        df, wave_interval_dict = self.get_wave_data(df, date_col)
        df = df[['wave', date_col, 'geoRegion',field]]
        df = self.filter_waves(df)
        output = tools.get_output_type()
        if output.lower() == 'table':
            df = self.get_wave_stats(df, wave_interval_dict)
            st.markdown(f"Dataset: {key}")
            AgGrid(df)
        else:
            self.show_wave_charts(df, wave_interval_dict, date_col)
        
        with st.expander("Description of method", expanded=False):
            st.markdown(self.texts['method'])
            
        


            
    
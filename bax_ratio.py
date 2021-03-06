from typing import Text
import streamlit as st
import const as cn
import pandas as pd
import altair as alt
from datetime import timedelta
import json

import const
import tools

class App:
    """
    """

    def __init__(self, texts):
        self.texts = texts
    

    def calc_ratio(self,df):
        df = df.query('sum7d_y > 0')
        df['ratio'] = df['sum7d_x'] / df['sum7d_y']
        return df
    
    def get_ratio_chart(self, df, settings):
        if 'color' in settings:
            chart = alt.Chart(df, title=settings['title']).mark_line().encode(
                    x=settings['x'],
                    y=settings['y'],
                    tooltip=settings['tooltip'],
                    color = settings['color']
            )
        elif settings['rolling_average_window'] > 0:
            rad = int(settings['rolling_average_window']/2)
            chart = alt.Chart(df, title=settings['title']).mark_line(color = 'red', size=2
            ).transform_window(
                rolling_mean=settings['rolling_avg'],
                frame=[-rad, rad]
            ).encode(
                x='date:T',
                y='rolling_mean:Q'
            )

            chart += alt.Chart(df).mark_point(size = 3, opacity=0.4, clip=True).encode(
                    x=settings['x'],
                    y=settings['y'],
                    tooltip=settings['tooltip']
            )
        else:
            chart = alt.Chart(df, title=settings['title']).mark_line().encode(
                    x=settings['x'],
                    y=settings['y'],
                    tooltip=settings['tooltip'],
            )    
        
        chart = chart.properties(
            width=800,
            height=300
        )

        return chart


    def show_menu(self):
        options_dict = {
                'cases':{'short': 'cases', 'long': 'number of cases', 'file':'cases', 'numerator_text':'number of cases', 'denominator_text':'number of cases'}, 
                'hospitalized': {'short':'hospitalized','long':'number of hospital entries', 'file':'hosp', 'numerator_text':'number of hospitalized', 'denominator_text':'be hospitalized'}, 
                'deseased': {'short':'deseased','long':'number of deseased','file':'death', 'numerator_text':'number of deseased', 'denominator_text':'die'}, 
            }

        datasets_dict, ok = tools.get_datasets_list('daily')
        numerator = st.sidebar.selectbox("Numerator", ['cases', 'hospitalized'])
        lst_denominator = ['hospitalized', 'deseased']
        if numerator in lst_denominator:
            lst_denominator.remove(numerator)  
        denominator = st.sidebar.selectbox("Denominator", lst_denominator)
        
        avg_timelag = st.sidebar.number_input("Average time lag in days", 0, 31, cn.DEFAULT_LAG)
        
        df, date_cases_col = tools.get_data(datasets_dict[options_dict[numerator]['file']], 'daily')
        df_numerator = df.copy() # dont mutate the cached data
        
        df_numerator['date_x'] = df_numerator[date_cases_col] + pd.to_timedelta(avg_timelag, unit="D")
        df, date_hosp_col = tools.get_data(datasets_dict[options_dict[denominator]['file']], 'daily')
        df_denominator = df.copy() # dont mutate the cached data
        # remove last 2 days as most recent hospitalisations are seldomly complete
        max_date = df_denominator[date_cases_col].max() + timedelta(-1)
        df_denominator = df_denominator[df_denominator[date_cases_col] < max_date]
        df = pd.merge(df_numerator, df_denominator, left_on=('date_x','geoRegion'), right_on=(date_hosp_col,'geoRegion'))
        df = df.query('sum7d_y.notna()')
        df = tools.filter_regions(df)
        
        df = self.calc_ratio(df)
        df = df[['date_x','geoRegion','sum7d_x','sum7d_y','ratio']]
        df = df.rename(columns={
                'date_x':'date',
                'geoRegion':'canton', 
                'sum7d_x': f"sum {options_dict[numerator]['short']} 7 days", 
                'sum7d_y': f"sum {options_dict[denominator]['short']} 7 days", 
                'ratio': f"ratio {options_dict[numerator]['short']} per {options_dict[denominator]['short']}"
            })
        group_by_canton = st.sidebar.checkbox('Group charts by canton')
        if group_by_canton:
            rolling_average_window = st.sidebar.number_input("Rolling average window in days (0 for none)", 0,100,30)
            common_y_axis = st.sidebar.number_input("Common y axis (0 for none)", 0,1000,0)
            for region in df['canton'].unique():
                df_filtered = df.query('canton == @region')
                settings = {
                    'x': alt.X('date:T', axis = alt.Axis(title = '', format = ("%b %Y"), labelAngle=45)), 
                    'y': alt.Y(f"ratio {options_dict[numerator]['short']} per {options_dict[denominator]['short']}:Q", 
                        axis = alt.Axis(title = f"{options_dict[numerator]['short']} / {options_dict[denominator]['short']}")), 
                    'title': region
                    }
                settings['tooltip'] = list(df.columns)
                settings['rolling_avg'] = f"mean(ratio {options_dict[numerator]['short']} per {options_dict[denominator]['short']})"
                settings['rolling_average_window'] = rolling_average_window
                if common_y_axis:
                    settings['y'] = alt.Y(f"ratio {options_dict[numerator]['short']} per {options_dict[denominator]['short']}:Q", 
                        axis = alt.Axis(title = f"{options_dict[numerator]['short']} / {options_dict[denominator]['short']}"),
                        scale=alt.Scale(domain=[0, common_y_axis])
                    )
                chart = self.get_ratio_chart(df_filtered, settings)
                st.altair_chart(chart)
        else:
            settings = {
                'x': alt.X('date:T'), 'y': alt.Y(f"ratio {options_dict[numerator]['short']} per {options_dict[denominator]['short']}:Q"), 
                'title':f"ratio {options_dict[numerator]['long']}/{options_dict[denominator]['long']}"
                }
            settings['color'] = 'canton'
            settings['tooltip'] = list(df.columns)
            
            chart = self.get_ratio_chart(df, settings)
            st.altair_chart(chart)
        
        with st.expander("Description of method", expanded=False):
            st.markdown(self.texts['method'].format(options_dict[numerator]['short'], options_dict[denominator]['short']))
            
        with st.expander("Interpretation", expanded=False):
            st.markdown(self.texts['interpretation'])
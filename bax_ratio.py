from typing import Text
import streamlit as st
import const as cn
import pandas as pd
import altair as alt
from datetime import timedelta

import const
import tools

class App:
    """
    """

    def __init__(self):
        pass

    def get_description(self,numerator, denominator):
        text = f"""
The timeline for the ratio {numerator['short']}/{denominator['short']} allows to verify, if over time, fewer people require hospitalisation or die for a given number of infections. The desired trend is therefore towards a lower ratio. Such a trend may be influenced by better treatment techniques, less aggressive variants, more vaccinated people, more infections in age classes reacting less less severely to the virus or any combination of these. An increase in ratio may indicate the spread of more aggressive variants or the shift in infections towards more vulnerable groups. 
        
Since the transition from infection to hospitalization and - in the worst case - from hospitalization to death requires time, nominator and denominator groups are taken from different time intervals separated by a time lag. As described in a study by [Faes, C. et al.](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7589278/), the time between symptoms onset and hospitalization lies approximately between 3 and 10.4 days, the time from hospitalization to death between 5.7 to 12.1 days. The durations highly depend on the patient's age and preconditions, which are not available in the used daily dataset. The results must be considered with extreme care. However, the user may calculate various scenarios based on different time lags. The most plausible time lag is the one causing less variation in the calculated ratios. 
"""
        return text
    
    def get_interpretation(self):
        text = f"""
The timeline for ratios shows a high variability for most cantons. Several factors may be responsible for this unexpected behavior. First, the assumption of a constant time lag between first symptoms and hospitalization poorly reflects the actual time lag. Time lags may vary considerably, depending on the patient's age and preconditions. Also, some hospital entry data are missing for patients in long-term care, as they often stay in their current facility and are not counted as new hospital entries. However, they are counted as laboratory-confirmed cases and therefore increase the ratio cases/hospitalizations. Cantons with many hospital beds accept patients from cantons or other countries where hospital capacity is exceeded. Except for the laboratory-confirmed cases dataset, the origin of patients (e.g., hospitalized or deceased) is not available. For this reason, ratio cases/hospitalizations increase artificially for receiving cantons and decrease for cantons, forwarding their patients. This effect attenuates with larger cantons or with the CH-dataset. In general, as can be observed when filtering the data for CH, an overall tendency towards higher cases/hospitalizations ratios can be observed over time. This tendency seems to accelerate starting in April 2021.
"""
        return text

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
        denominator = st.sidebar.selectbox("Denominator", ['hospitalized', 'deseased'])
        avg_timelag = st.sidebar.number_input("Average time lag in days", 0, 31, 4)
        
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
            for region in df['canton'].unique():
                df_filtered = df.query('canton == @region')
                settings = {
                    'x': alt.X('date:T', axis = alt.Axis(title = '', format = ("%b %Y"), labelAngle=45)), 
                    'y': alt.Y(f"ratio {options_dict[numerator]['short']} per {options_dict[denominator]['short']}:Q"), 
                    'title': region
                    }
                settings['tooltip'] = list(df.columns)
                
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
        
        description = st.expander("Description of method", expanded=False)
        with description:
            st.markdown(self.get_description(options_dict[numerator],options_dict[denominator]))
            
        interpretation = st.expander("Description of method", expanded=False)
        with interpretation:
            st.markdown(self.get_interpretation())
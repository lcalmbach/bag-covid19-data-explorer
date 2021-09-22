"""
Diese App unterstützt die Prozesse rund um das Erstellen des Covid-19 Lageberichts mails der Medizinischen Dienste
des Kantons Basel-Stadt.

Kontakt: lukas.calmbach@bs.ch
"""

import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime, timedelta, date
import logging
from st_aggrid import AgGrid
import numpy as np

import tools
import const as cn
import bax_info
import bax_explore
import bax_ratio
import bax_wave

STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

__author__ = 'lukas calmbach'
__author_email__ = 'lukas.calmbach@bs.ch'
__version__ = '0.1.46'
version_date = '2021-09-05'
LOGGING_LEVEL = logging.DEBUG
logger = {}
my_name = 'covid-lagebericht'
date_col = ''


def main():
    """
    Initialisiert das Session state Objekt und führt die Streamlit Applikation aus.
    """

    # starting from version 71
    st.set_page_config(
        page_title="BAG-covid-data-Explorer",
        # page_icon="🦠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(STYLE, unsafe_allow_html=True)
    st.sidebar.markdown(f"### 🦠 BAG-COVID-19 Data Explorer")
    
    menu_action = st.sidebar.selectbox('Menu', cn.MENU_OPTIONS)
    if menu_action=='Info':
        app = bax_info.App() 
    elif menu_action=='Discover datasets':
        app = bax_explore.App() 
    elif menu_action == 'Analysis of case ratios':
        app = bax_ratio.App() 
    elif menu_action == 'Analysis of waves':
        app = bax_wave.App() 
    app.show_menu()
    
if __name__ == '__main__':
    main()
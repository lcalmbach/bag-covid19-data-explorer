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
import json

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

__version__ = '0.0.1' 
__author__ = 'Lukas Calmbach'
__author_email__ = 'lcalmbach@gmail.com'
VERSION_DATE = '2021-09-25'
my_icon = "🔭"
my_name = 'FOPH-Covid19-Data-Explorer'
GIT_REPO = 'https://github.com/lcalmbach/bag-covid19-data-explorer'
APP_INFO = f"""<div style="background-color:powderblue; padding: 10px;border-radius: 15px;">
    <small>App created by <a href="mailto:{__author_email__}">{__author__}</a><br>
    version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}">git-repo</a>
    """

@st.cache()
def get_texts():
    return json.loads(open(cn.TEXTS).read())
        
def main():
    """
    shows the  main menu and calls the selected menu item
    """

    st.set_page_config(
        page_title=my_name,
        page_icon=my_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    texts = get_texts()
    st.markdown(STYLE, unsafe_allow_html=True)
    st.sidebar.markdown(f"### {my_icon} {my_name}")
    
    menu_action = st.sidebar.selectbox('Menu', cn.MENU_OPTIONS)
    if menu_action=='Info':
        app = bax_info.App(texts['info']) 
    elif menu_action=='Discover datasets':
        app = bax_explore.App(texts['explore']) 
    elif menu_action == 'Analysis of case ratios':
        app = bax_ratio.App(texts['ratio']) 
    elif menu_action == 'Analysis of waves':
        app = bax_wave.App(texts['wave']) 
    app.show_menu()
    st.sidebar.markdown(APP_INFO,unsafe_allow_html=True)
    
if __name__ == '__main__':
    main()
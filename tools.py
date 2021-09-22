import pandas as pd
import altair as alt
import base64
import streamlit as st
import requests
import io
import const as cn

def error_message(ex: Exception) -> str:
    """
    Gibt den String eines error Objekts zurück
    """

    if hasattr(ex, 'message'):
        return ex.message
    else:
        return ex
    
def left(s, amount):
    return s[:amount]

def right(s, amount):
    return s[-amount:]

def mid(s, offset, amount):
    return s[offset:offset+amount]

def parse_list_of_objects(obj_list:list, field:str, value_list:list):
    output = []
    for x in obj_list:
        if x[field] in value_list:
            output.add(x) 
            
    return output

def download_file(df:pd.DataFrame, text: str):
    csv = df.to_csv(index=False, sep=";")
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">{text}</a> (Rechtsklick, dann: Link speichern unter und <Dateiname>.csv angeben)'
    return href


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False, sep=';', encoding='iso-8859-1')

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode('Windows-1252')).decode('utf-8')

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

@st.cache
def get_datasets_list(type: str):
    ok = True
    ds_dict = {}
    try:
        #urlData = requests.get(url, proxies=PROXY_DICT) # create HTTP response object 
        urlData = requests.get(cn.CONTEXT_URL) # create HTTP response object 
        files_metadata = urlData.json()
        if type == 'daily':
            ds_dict = files_metadata['sources']['individual']['csv']['daily']
        elif type == 'weekly by age':
            ds_dict = files_metadata['sources']['individual']['csv']['weekly']['byAge']
        else:
            ds_dict = files_metadata['sources']['individual']['csv']['weekly']['bySex']
    except Exception as ex:
        st.warning(f"Beim Einlesen der Fallzahlen der Schweiz ist ein Fehler aufgetreten: {ex}")
        ok = False
    return ds_dict, ok

@st.cache(allow_output_mutation=True)
def get_data(url: str, type: str):
    #urlData = requests.get(url,proxies=PROXY_DICT).content # create HTTP response object 
    urlData = requests.get(url).content # create HTTP response object 
    df = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    if 'datum' in list(df.columns):
        date_col = 'datum'
    else:
       date_col = 'date'
    if 'weekly' not in type:
        df[date_col] = pd.to_datetime(df[date_col])
    return df, date_col


def filter_fields(df, date_col, numeric_only):
    if numeric_only:
        lst_felder =  [ x for x in list(df.columns) if (df[x].dtypes in ('int64','float64') ) ]
        lst_default = ['entries'] if 'entries' in lst_felder else []
    else:
        lst_felder =  list(df.columns)
        lst_default = []
    selected_fields = st.sidebar.multiselect('Fields', lst_felder, lst_default)
    if len(selected_fields) > 0:
        df = df[['geoRegion',date_col] + selected_fields]
    return df

def filter_field(df, numeric_only):
    if numeric_only:
        lst_felder =  [ x for x in list(df.columns) if (df[x].dtypes in ('int64','float64') ) ]
    else:
        lst_felder =  list(df.columns)
    selected_field = st.sidebar.selectbox('Fields', lst_felder)
    return selected_field


def filter_regions(df):
    lst_regions = list(df['geoRegion'].unique())
    region_filter = st.sidebar.multiselect('Canton', lst_regions)
    if len(region_filter) > 0:
        df = df.query('geoRegion.isin(@region_filter)')
    return df

def get_output_type():
    return st.sidebar.selectbox('Show', ["table", "chart"])

def get_line_chart(df, settings):
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

    if not 'width' in settings.keys():
        settings['width'] = 800 
        settings['height'] = 300 
    chart = chart.properties(
        width=settings['width'],
        height=settings['height']
    )

    return chart
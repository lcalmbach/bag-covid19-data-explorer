from datetime import date

MENU_OPTIONS=['Info', 'Discover datasets', 'Analysis of case ratios', 'Analysis of waves']

CONTEXT_URL = 'https://www.covid19.admin.ch/api/data/context'

WAVES = { 
    "wave 1": {'date_start': date(2020, 2, 29), 'date_end': date(2020, 5, 2)},
    "wave 2": {'date_start': date(2020, 9, 27), 'date_end': date(2021, 2, 14)},
    "wave 3": {'date_start': date(2021, 2, 14), 'date_end': date(2021, 6, 11)},
    "wave 4": {'date_start': date(2021, 7, 11), 'date_end': date(2021, 8, 10)},
    "wave 5": {'date_start': date(2021, 10, 20), 'date_end': date.today()}

}

INFO = """## FOPH Covid19-Data-Explorer
The Federal Office of Public Health FOPH compiles a large dataset of Covid19 data from various sources. The FOPH presents this data in a commented [Dashboard](https://www.covid19.admin.ch/de/overview). The source data for this dashboard is published on its own API site accessible e.g. through the index https://www.covid19.admin.ch/api/data/context. The weekly data is also publised as opendata on [opendata.swiss.ch](https://opendata.swiss/de/dataset/covid-19-schweiz). 

The FOPH Covid-19 dataset is extensive, and the usual initial approach for exploring such a dataset using tools such as MS Excel and eventually plotting the extracted data is time-consuming. The current app facilitates this process by providing several analysis tools that allow to quickly preview and plot the data by parameter or canton and then download only the required data.

In addition to the pure data exploration, this tool also provides two analyses based on the currently selected datafile:
- calculation of ratios, e.g. hospitalization/cases, deaths/cases, deaths/hospitalizations etc.
- statistics and graphical analysis of cases, hospitalizations, icu-hospitalizations and deaths per wave (wave temporal delineations are estimated graphically based on the daily cases time series in Basel)

Additional ressources:
- FOPH [data documentation](https://www.covid19.admin.ch/api/data/documentation/)
"""

FIELD_METADATA = 'https://www.covid19.admin.ch/api/data/documentation/models/sources-definitions-{}incomingdata.md#{}'

TEXTS = 'texts.json'

DEFAULT_LAG = 9
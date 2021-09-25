# FOPH-Covid19-Data-Explorer

The Federal Office of Public Health FOPH compiles a large dataset of Covid19 data from various sources. The FOPH presents this data in a commented [Dashboard](https://www.covid19.admin.ch/de/overview). The source data for this dashboard is published on its API accessible e.g., through the index https://www.covid19.admin.ch/api/data/context. The weekly data is also published as open data on [opendata.swiss.ch](https://opendata.swiss/de/dataset/covid-19-schweiz). The FOPH Covid-19 dataset is very extensive, and the usual initial approach for exploring such a dataset consisting of downloading the data, viewing and filtering it using tools such as MS Excel, and eventually plotting the extracted data is time-consuming. The current app facilitates the exploration of the dataset by providing several tools allowing to quickly preview and plot the data by parameter or canton and then download only the required data.

In addition to the pure data exploration, the tools also provides two analysis based on selected datafile:
- calculation of ratios for hospitalization/cases, deaths/cases, deaths/hospitalizations etc.
- statistics and graphical analyses of infections, hospitalizations, icu-hospitalizations and deaths per wave.

[Open the app](https://foph-covid19-data-explorer.herokuapp.com/)

Install and run app locally
prerequisites: Python Python < version 3.9 ist installed on your machine
required steps:
```
> https://github.com/lcalmbach/bag-covid19-data-explorer.git
> cd bag-covid19-data-explorer
> python -m venv env
> env\scripts\activate
> pip install -r requirements.txt
> streamlit run app.py
```

If you discover errors in the app or have questions/comments please feel free to contact lcalmbach@gmail.com.


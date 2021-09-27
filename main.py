import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mlt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

#import requests
#from bs4 import BeautifulSoup

# COVID-19 Data Repository by the Center for Systems Science and Engineering (CSSE) at Johns Hopkins University (https://github.com/CSSEGISandData/COVID-19)
url_confirmed = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
url_deaths = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
url_recovered = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"

url_vaccine = "https://raw.githubusercontent.com/govex/COVID-19/master/data_tables/vaccine_data/global_data/vaccine_data_global.csv"

# reading COVID-19 data in pandas table
raw_data = pd.read_csv(url_confirmed)
raw_data_deaths = pd.read_csv(url_deaths)
raw_data_recovered = pd.read_csv(url_recovered)

# Converting COVID-19 data in more readable data (convert headers with Date in 1 column)
data_confirmed_cases = raw_data.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"],
                                     var_name="Date",
                                     value_name="Confirmed_cases")
data_confirmed_deaths = raw_data_deaths.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"],
                                             var_name="Date",
                                             value_name="Confirmed_deaths")
data_confirmed_recovered = raw_data_recovered.melt(id_vars=["Province/State", "Country/Region", "Lat", "Long"],
                                                   var_name="Date",
                                                   value_name="Confirmed_recovered")

# Merging 3 tables in 1 table, that contains data on all COVID-19 cases, new cases of deaths and recovers
data_confirmed_cases = data_confirmed_cases.merge(data_confirmed_deaths, how="outer", left_on=["Country/Region", "Date", "Province/State", "Lat", "Long"], right_on=["Country/Region", "Date", "Province/State", "Lat", "Long"])
data_confirmed_cases = data_confirmed_cases.merge(data_confirmed_recovered, how="outer", left_on=["Country/Region", "Date", "Province/State", "Lat", "Long"], right_on=["Country/Region", "Date", "Province/State", "Lat", "Long"])

# Formatting Date
data_confirmed_cases["Date"] = pd.to_datetime(data_confirmed_cases["Date"])

data_confirmed_cases = pd.DataFrame(data=data_confirmed_cases)

# Deleting unnecessary columns
data_confirmed_cases = data_confirmed_cases.drop(["Province/State", "Lat", "Long"], axis=1)

# Group by Country and date
data_confirmed_cases = data_confirmed_cases.groupby(["Country/Region", "Date"]).sum()

# Receiving columns with daily data on new cases of COVID and deaths from COVID
data_confirmed_cases["Cases_per_day"] = data_confirmed_cases.groupby(["Country/Region"])["Confirmed_cases"].diff()
data_confirmed_cases["Deaths_per_day"] = data_confirmed_cases.groupby(["Country/Region"])["Confirmed_deaths"].diff()

# Saving table to csv file. Then reading data from saved dile
data_confirmed_cases.reset_index().to_csv("Data1.csv", index=False)
data_confirmed_cases = pd.read_csv("Data1.csv")

# Create table that contains data for Russia
cases_Russia = data_confirmed_cases[data_confirmed_cases["Country/Region"] == "Russia"]
cases_Russia["Date"] = pd.to_datetime(cases_Russia["Date"])


def cases_country(data, country):
#    figure.set_facecolor("#282633")
#    plt.style.use(['dark_background', 'presentation'])
    with plt.style.context(('dark_background')):
        figure, (axs1, axs2) = plt.subplots(2, 1)
        figure.set_size_inches(10, 7)
        figure.tight_layout()
        # Figure 1 - total cases of COVID-19 in Russia
        axs1.plot(data["Date"], data["Confirmed_cases"], label="Confirmed cases of Coronavirus", color="yellow", fillstyle="full")
        axs1.fill_between(data["Date"], data["Confirmed_cases"])
        axs1.plot(data["Date"], data["Confirmed_deaths"], label="Confirmed cases of deaths", color="red", fillstyle="full")
        axs1.fill_between(data["Date"], data["Confirmed_deaths"], color="red")
        axs1.set_title(f"Total cases of COVID-19 in {country}", fontweight="bold", fontsize="large")
        axs1.set(ylabel="Confirmed cases")
        axs1.tick_params(labelsize=8)
        axs1.yaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        axs1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axs1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
        legend1 = axs1.legend(loc="upper left", fontsize="medium")
        legend1.get_frame()
        plt.setp(axs1.get_xticklabels(), rotation=15, ha="right")
     #   figure.autofmt_xdate()
        axs1.grid(True)

        # Figure 2 - New cases of COVID-19 and deaths from COVID-19 since the previous day
        axs2.plot(data["Date"], data["Cases_per_day"], label="Confirmed cases of Coronavirus", color="yellow", fillstyle="full")
        axs2.fill_between(data["Date"], data["Cases_per_day"])
        axs2.plot(data["Date"], data["Deaths_per_day"], label="Confirmed cases of Deaths", color="red")
        axs2.fill_between(data["Date"], data["Deaths_per_day"], color="red")
        axs2.set(ylabel="Confirmed cases")
        axs2.tick_params(labelsize=8)
        axs2.set_title("New cases of COVID-19 and new deaths", fontweight="bold", fontsize="large")
        axs2.yaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        axs2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axs2.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
        legend2 = axs2.legend(loc="upper left", fontsize="medium")
        legend2.get_frame()
        plt.setp(axs2.get_xticklabels(), rotation=15, ha="right")
       # figure.autofmt_xdate()
        axs2.grid(True)
        plt.subplots_adjust(left=0.1, bottom=0.055, right=0.974, top=0.96, wspace=0.198, hspace=0.214)
        plt.savefig(f"Covid_{country}.png")
        plt.subplot_tool()
    plt.show()

cases_country(cases_Russia, "Russia")

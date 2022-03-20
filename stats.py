import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mlt
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter
from config import IMG_PATH
import plotly as py
import plotly.express as px
import json

#import requests
#from bs4 import BeautifulSoup

def get_stats(country):
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

    # Saving table to csv file. Then reading data from saved file
    data_confirmed_cases.reset_index().to_csv("Data1.csv", index=False)
    data_confirmed_cases = pd.read_csv("Data1.csv")
    print(data_confirmed_cases['Country/Region'])

        # Create table that contains data for specified country
    if (country != 'World'):
        data_country = data_confirmed_cases[data_confirmed_cases["Country/Region"] == country]
        data_country["Date"] = pd.to_datetime(data_country["Date"])
        cases_country(data_country, country)

        total_cases = data_country['Confirmed_cases'].iloc[-1]
        total_deaths = data_country['Confirmed_deaths'].iloc[-1]
        daily_cases = data_country['Cases_per_day'].iloc[-1]
        daily_deaths = data_country['Deaths_per_day'].iloc[-1]

        return (total_cases, total_deaths, daily_cases, daily_deaths)

    if (country == 'World'):
        #Create table with totals
        Top_10_cases_total = data_confirmed_cases.sort_values(by=['Date', 'Confirmed_cases'], ascending=[False, False]).head(10).sort_values(by="Confirmed_cases").replace('United Kingdom', 'UK')
        Top_10_deaths_total = data_confirmed_cases.sort_values(by=['Date', 'Confirmed_deaths'], ascending=[False, False]).head(10).sort_values(by="Confirmed_deaths").replace('United Kingdom', 'UK')
        Top_10_cases_today = data_confirmed_cases.sort_values(by=['Date', 'Cases_per_day'], ascending=[False, False]).head(10).rename(index={"United Kingdom" : "UK"})
        Top_10_deaths_today = data_confirmed_cases.sort_values(by=['Date', 'Deaths_per_day'], ascending=[False, False]).head(10).rename(index={"United Kingdom" : "UK"})
        top_cases(Top_10_cases_total, Top_10_deaths_total, Top_10_cases_today, Top_10_deaths_today)

        last_date = data_confirmed_cases.sort_values(by=['Date'], ascending=[True])['Date'].iloc[-1]

        total_cases = data_confirmed_cases[data_confirmed_cases['Date'] == last_date]['Confirmed_cases'].sum()
        total_deaths = data_confirmed_cases[data_confirmed_cases['Date'] == last_date]['Confirmed_deaths'].sum()
        daily_cases = data_confirmed_cases[data_confirmed_cases['Date'] == last_date]['Cases_per_day'].sum()
        daily_deaths = data_confirmed_cases[data_confirmed_cases['Date'] == last_date]['Deaths_per_day'].sum()

        graphJSON = draw_map(data_confirmed_cases, last_date)

        return (total_cases, total_deaths, daily_cases, daily_deaths, graphJSON)


# locations - Values from this column or array_like are to be interpreted
# according to locationmode and mapped to longitude/latitude.
# locationmode - Determines the set of locations used to match entries in locations to regions on the map.
# color - Values from this column or array_like are used to assign color to marks.
# hover_name - Values from this column or array_like appear in bold in the hover tooltip.
# color_continuous_scale
def draw_map(data_confirmed_cases, last_date):
    group_by_country_date = data_confirmed_cases.groupby(['Country/Region', 'Date'])
    covid_confirmed = group_by_country_date.sum().reset_index().sort_values(['Date'], ascending=False)

    fig = px.choropleth(
        covid_confirmed[::-1],  # Dataframe
        locations='Country/Region',
        locationmode='country names',
        color='Confirmed_cases',
        hover_name='Country/Region',  # Text to be displayed in Bold upon hover
        hover_data=['Confirmed_cases'],  # Extra text to be displayed in Hover tip
        animation_frame='Date',  # Data for animation, time-series data
        color_continuous_scale=px.colors.diverging.RdYlGn[::-1]
    )

    fig.update_layout(
        title_text=f"COVID-19 Spread in the World up to {last_date}",
        title_x=0.5,
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular'
        )
    )

    graphJSON = json.dumps(fig, cls=py.utils.PlotlyJSONEncoder)

    return (graphJSON)


def top_cases(Top_10_cases_total, Top_10_deaths_total, Top_10_cases_today, Top_10_deaths_today):
    with plt.style.context(('dark_background')):
        figure, axs = plt.subplots(1, 2, figsize=(10.2, 4))
        Top_10_cases_total["Confirmed_cases"] = (Top_10_cases_total["Confirmed_cases"] / 1000000).apply(lambda x: round(x, 2))
        axs[0].barh(Top_10_cases_total["Country/Region"], Top_10_cases_total["Confirmed_cases"])
        #axs[0].set_xticks(Top_10_cases_total["Confirmed_cases"])
        axs[0].set_yticks(Top_10_cases_total["Country/Region"])
        axs[0].set_title("Top 10 countries by total COVID-19 cases\n(mln people)", fontweight="bold", fontsize="large")
        axs[0].xaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        for container in axs[0].containers:
            axs[0].bar_label(container, padding=-28, color="black")
        plt.setp(axs[0].get_xticklabels(), rotation=15, ha="right")

        axs[1].barh(Top_10_deaths_total["Country/Region"], Top_10_deaths_total["Confirmed_deaths"])
        #axs[1].set_xticks(Top_10_deaths_total["Confirmed_deaths"])
        axs[1].set_yticks(Top_10_deaths_total["Country/Region"])
        axs[1].set_title("Top 10 countries by total deaths from COVID-19\n(people)", fontweight="bold", fontsize="large")
        axs[1].xaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x: 10,.2f}'))
        for container in axs[1].containers:
            axs[1].bar_label(container, padding=-40, color="black")
        plt.setp(axs[1].get_xticklabels(), rotation=15, ha="right")
        plt.subplots_adjust(left=0.083, bottom=0.11, right=0.955, top=0.88, wspace=0.255, hspace=0.2)
        plt.subplot_tool()
        plt.savefig(IMG_PATH + "Top 10 counties.png")
        plt.close(figure)

    plt.show()


def total_cases_country(data, country):
    with plt.style.context(('dark_background')):
        figure, (axs1, axs2) = plt.subplots(2, 1)
        figure.set_size_inches(10, 7)
        figure.tight_layout()
        # Figure 1 - total cases of COVID-19 in in specified country
        axs1.plot(data["Date"], data["Confirmed_cases"], label="Confirmed cases of Coronavirus", color="yellow", fillstyle="full")
        axs1.fill_between(data["Date"], data["Confirmed_cases"])
        axs1.set_title(f"Total cases of COVID-19 in {country}", fontweight="bold", fontsize="large")
        axs1.set(ylabel="Confirmed cases")
        axs1.tick_params(labelsize=8)
        axs1.yaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        axs1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axs1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
        legend1 = axs1.legend(loc="upper left", fontsize="medium")
        legend1.get_frame()
        plt.setp(axs1.get_xticklabels(), rotation=25, ha="right")
     #   figure.autofmt_xdate()
        axs1.grid(True)
        # Figure 2 - total cases of deaths from COVID-19 in specified country
        axs2.plot(data["Date"], data["Confirmed_deaths"], label="Confirmed cases of deaths", color="red",
                  fillstyle="full")
        axs2.fill_between(data["Date"], data["Confirmed_deaths"], color="red")
        axs2.set_title(f"Total deaths from COVID-19 in {country}", fontweight="bold", fontsize="large")
        axs2.set(ylabel="Confirmed cases")
        axs2.tick_params(labelsize=8)
        axs2.yaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        axs2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axs2.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
        legend1 = axs1.legend(loc="upper left", fontsize="medium")
        legend1.get_frame()
        plt.setp(axs2.get_xticklabels(), rotation=25, ha="right")
        #   figure.autofmt_xdate()
        axs1.grid(True)

        plt.subplots_adjust(left=0.1, bottom=0.055, right=0.974, top=0.96, wspace=0.198, hspace=0.214)
        plt.savefig(IMG_PATH + "Covid_country_total.png")
        plt.close(figure)
    plt.show()


def daily_cases_country(data, country):
    with plt.style.context(('dark_background')):
        figure, (axs1, axs2) = plt.subplots(2, 1)
        figure.set_size_inches(10, 7)
        figure.tight_layout()
        # Figure 1 - daily cases of COVID-19 in in specified country
        axs1.plot(data["Date"], data["Cases_per_day"], label="Confirmed cases of Coronavirus", color="yellow",
                  fillstyle="full")
        axs1.fill_between(data["Date"], data["Cases_per_day"])
        axs1.set_title(f"Daily cases of COVID-19 in {country}", fontweight="bold", fontsize="large")
        axs1.set(ylabel="Confirmed cases")
        axs1.tick_params(labelsize=8)
        axs1.yaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        axs1.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axs1.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
        legend1 = axs1.legend(loc="upper left", fontsize="medium")
        legend1.get_frame()
        plt.setp(axs1.get_xticklabels(), rotation=25, ha="right")
     #   figure.autofmt_xdate()
        axs1.grid(True)
        # Figure 2 - Daily cases of deaths from COVID-19 in specified country
        axs2.plot(data["Date"], data["Deaths_per_day"], label="Confirmed cases of Deaths", color="red")
        axs2.fill_between(data["Date"], data["Deaths_per_day"], color="red")
        axs2.set_title(f"Daily deaths from COVID-19 in {country}", fontweight="bold", fontsize="large")
        axs2.set(ylabel="Confirmed cases")
        axs2.tick_params(labelsize=8)
        axs2.yaxis.set_major_formatter(mlt.ticker.StrMethodFormatter('{x:,.0f}'))
        axs2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        axs2.xaxis.set_major_formatter(DateFormatter('%b-%Y'))
        legend1 = axs1.legend(loc="upper left", fontsize="medium")
        legend1.get_frame()
        plt.setp(axs2.get_xticklabels(), rotation=25, ha="right")
        #   figure.autofmt_xdate()
        axs1.grid(True)

        plt.subplots_adjust(left=0.1, bottom=0.055, right=0.974, top=0.96, wspace=0.198, hspace=0.214)
        plt.savefig(IMG_PATH + "Covid_country_daily.png")
        plt.close(figure)
    plt.show()


def cases_country(data, country):
    total_cases_country(data, country)
    daily_cases_country(data, country)

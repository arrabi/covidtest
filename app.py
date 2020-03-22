import datetime
import streamlit as st
from streamlit import caching
import pandas as pd
import altair as alt
import os
import numpy as np
 

APP_LOG_FILE = f"log_{os.path.basename(__file__)}.log"
def log(ss):
    with open (file=APP_LOG_FILE, mode="a+") as f:
        f.write(str(datetime.datetime.now()) + ": " + ss + "\n")


# get countries populations from csv file, and cache it.
# csv file obtained from UN: population.un.org/wpp/Download/Standard/CSV/
@st.cache
def read_population_data(parent="World"):
    """ return a dictionary of country name -> population in millions """
    df = pd.read_csv("countries_pop_2020.csv", index_col=0, header=0, 
        dtype={'country':str, 'population':np.float64, 'parent':str})
    df = df[df['parent'] == parent]
    return df.T.to_dict("records")[0]

inhabitants = read_population_data()
inhabitants_us = read_population_data(parent="US")

@st.cache
def read_data():
    BASEURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"    
    url_confirmed = f"{BASEURL}/time_series_19-covid-Confirmed.csv"
    url_deaths = f"{BASEURL}/time_series_19-covid-Deaths.csv"
    url_recovered = f"{BASEURL}/time_series_19-covid-Recovered.csv"

    confirmed = pd.read_csv(url_confirmed)#, index_col=0)
    deaths = pd.read_csv(url_deaths)#, index_col=0)
    recovered = pd.read_csv(url_recovered)#, index_col=0)

    #ignore where State/Province has ,, because that's city stats, and they shouldn't be added to country
    #to avoid duplication.

    confirmed = confirmed[~ confirmed['Province/State'].str.contains(",", na=False)]
    deaths = deaths[~ deaths['Province/State'].str.contains(",", na=False)]
    recovered = recovered[~ recovered['Province/State'].str.contains(",", na=False)]

    # sum over potentially duplicate rows (France and their territories)
    confirmed = confirmed.groupby("Country/Region").sum().reset_index()
    deaths = deaths.groupby("Country/Region").sum().reset_index()
    recovered = recovered.groupby("Country/Region").sum().reset_index()

    # # data bug, discard 03/13
    # confirmed = confirmed.drop('3/13/20', axis=1)
    # deaths = deaths.drop('3/13/20', axis=1)
    # recovered = recovered.drop('3/13/20', axis=1)
    # try:
    #     confirmed = confirmed.drop('3/14/20', axis=1)
    #     deaths = deaths.drop('3/14/20', axis=1)
    #     recovered = recovered.drop('3/14/20', axis=1)
    # except:
    #     pass

    return (confirmed, deaths, recovered)

@st.cache
def read_data_bystate():
    BASEURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series"    
    url_confirmed = f"{BASEURL}/time_series_19-covid-Confirmed.csv"
    url_deaths = f"{BASEURL}/time_series_19-covid-Deaths.csv"
    url_recovered = f"{BASEURL}/time_series_19-covid-Recovered.csv"

    confirmed = pd.read_csv(url_confirmed)
    deaths = pd.read_csv(url_deaths)
    recovered = pd.read_csv(url_recovered)

    confirmed = confirmed[confirmed['Country/Region'] == "US"]
    deaths = deaths[deaths['Country/Region'] == "US"]
    recovered = recovered[recovered['Country/Region'] == "US"]

    confirmed = confirmed[~ confirmed['Province/State'].str.contains(",")]
    deaths = deaths[~ deaths['Province/State'].str.contains(",")]
    recovered = recovered[~ recovered['Province/State'].str.contains(",")]

    confirmed = confirmed[~ confirmed['Province/State'].str.contains("Princess")]
    deaths = deaths[~ deaths['Province/State'].str.contains("Princess")]
    recovered = recovered[~ recovered['Province/State'].str.contains("Princess")]

    # sum over potentially duplicate rows (France and their territories)
    confirmed = confirmed.groupby("Province/State").sum().reset_index()
    deaths = deaths.groupby("Province/State").sum().reset_index()
    recovered = recovered.groupby("Province/State").sum().reset_index()

    # # data bug, discard 03/13
    # confirmed = confirmed.drop('3/13/20', axis=1)
    # deaths = deaths.drop('3/13/20', axis=1)
    # recovered = recovered.drop('3/13/20', axis=1)
    # try:
    #     confirmed = confirmed.drop('3/14/20', axis=1)
    #     deaths = deaths.drop('3/14/20', axis=1)
    #     recovered = recovered.drop('3/14/20', axis=1)
    # except:
    #     pass

    return (confirmed, deaths, recovered)


def transform(df, collabel='confirmed'):
    dfm = pd.melt(df)
    dfm["date"] = pd.to_datetime(dfm.variable, infer_datetime_format=True)
    dfm = dfm.set_index("date")
    dfm = dfm[["value"]]
    dfm.columns = [collabel]
    return dfm

def transform2(df, collabel='confirmed'):
    dfm = pd.melt(df, id_vars=["Country/Region"])
    dfm["date"] = pd.to_datetime(dfm.variable, infer_datetime_format=True)
    dfm = dfm.set_index("date")
    dfm = dfm[["Country/Region","value"]]
    dfm.columns = ["country", collabel]
    return dfm


def transform2bystate(df, collabel='confirmed'):
    dfm = pd.melt(df, id_vars=["Province/State"])
    dfm["date"] = pd.to_datetime(dfm.variable, infer_datetime_format=True)
    dfm = dfm.set_index("date")
    dfm = dfm[["Province/State","value"]]
    dfm.columns = ["state", collabel]
    return dfm

ISDEBUG = os.path.isfile("__debug__")

def main():
    st.title("Simple Covid-19 Data Explorer")

    if ISDEBUG:
        st.sidebar.button("reload")

    pages = {
        "MiddleEast & North Africa": 1,
        "South Asia & Neighbors":5,
        "US States": 2,
        "Europe": 3,
        "World": 4,
    }
    chosen = st.sidebar.radio("Select page", list(pages.keys()), index=0)
    chosen = pages[chosen]
    if chosen == 1:
#        arabcountries()
        arab_countries = ["Algeria", "Bahrain", "Egypt", "Iraq", "Jordan", "Kuwait",
            "Lebanon", "Morocco", "Mauritania", "Oman", "Qatar", "Saudi Arabia", "Somalia", 
            "Sudan", "Tunisia", "United Arab Emirates", "Djibouti", "Comores", "Libya", "Palestine", 
            "Syria", "Yemen", "Iran", "Turkey", "Greece", "Cypress", "Ethiopia", "Eritrea", "South Sudan",
            "Chad", "Niger", "Mali", "Senegal", "Malta", "Cote d'Ivoire"]
        generalList(title="MENA Region", countries=arab_countries)
    elif chosen == 2: 
        usstates()
    elif chosen == 3: 
        eu_countries = ["Germany", "Austria", "Belgium", "Denmark", "France", "Greece", "Italy", \
                 "Netherlands", "Norway", "Poland", "Romania", "Spain", "Sweden", \
                 "Switzerland", "United Kingdom"]
        generalList(title="Select EU countries", countries=eu_countries)
#        europe()
    elif chosen == 4:
        confirmed, _, _ = read_data()
        all_countries = list(confirmed['Country/Region'].unique()) 
        generalList(title="World", countries=all_countries)
    elif chosen == 5:
#        arabcountries()
        sa_countries = ["India", "Pakistan", "Bangladesh", "Afghanistan", "Tajikistan", "Nepal", 
            "Bhutan", "Myanmar", "Laos"]
        generalList(title="South Asia & Neighbors", countries=sa_countries)
    else:
        st.write("not implemented yet")

    st.info("""\
          
        by: Muhammad Arrabi (https://twitter.com/mrarrabi) |
        Source [GitHub](https://github.com/arrabi/covidtest) |
        Based on code from C. Werner's beautiful project here [GitHub](https://www.github.com/cwerner/covid19)
        | data source: [Johns Hopkins Univerity (GitHub)](https://github.com/CSSEGISandData/COVID-19). 
    """)


def usstates():
    st.markdown("""\
        This app illustrates the spread of COVID-19 in Arab Region (where data is available) over time.
    """)

    #st.error("⚠️ There is currently an issue in the datasource of JHU. Data for 03/13 is invalid and thus removed!")


    analysis = st.sidebar.selectbox("Choose Analysis", ["Overview", "By State"])

    confirmed, deaths, recovered = read_data_bystate()

    #keep only dates where there were confirmed cases
    cols_to_remove = []
    for c in confirmed.columns:
        if c[0].isdigit():
            if confirmed[c].sum() == 0:
                cols_to_remove += [c]
    confirmed = confirmed.drop(cols_to_remove, axis=1)
    deaths = deaths.drop(cols_to_remove, axis=1)
    recovered = recovered.drop(cols_to_remove, axis=1)

    #list of states 
    states_list = list(confirmed['Province/State'].unique()) 

    #keep top 10 states by default + 3 states with high per capita confirmed
    sorted_conf = confirmed.sort_values(by=confirmed.columns[-1], ascending=False)
    def_states_list = list(sorted_conf.iloc[0:10,0].unique()) + ['Guam', 'District of Columbia', 'Colorado']

    if analysis == "Overview":

        st.header("COVID-19 cases and fatality rate in US by state")
        st.markdown("""\
            These are the reported case numbers for a selection of US state"""
            + """The case fatality rate (CFR) is calculated as:  
            $$
            CFR[\%] = \\frac{fatalities}{\\textit{all cases}}
            $$

            ℹ️ You can select/ deselect states and switch between linear and log scales.
            """)

        if st.checkbox("select all"):
            multiselection = st.multiselect("Select states:", states_list, default=states_list)
        else:
            multiselection = st.multiselect("Select states:", states_list, default=def_states_list)
        log(f"US_multiselection {str(multiselection)}")

        logscale = st.checkbox("Log scale", True)

        confirmed = confirmed[confirmed["Province/State"].isin(multiselection)]
        confirmed = confirmed.drop(["Lat", "Long"],axis=1)
        confirmed = transform2bystate(confirmed, collabel="confirmed")

        deaths = deaths[deaths["Province/State"].isin(multiselection)]
        deaths = deaths.drop(["Lat", "Long"],axis=1)
        deaths = transform2bystate(deaths, collabel="deaths")

        frate = confirmed[["state"]]
        frate["frate"] = (deaths.deaths / confirmed.confirmed)*100
        frate["deaths"] = deaths.deaths
        frate["confirmed"] = confirmed.confirmed

        # saveguard for empty selection 
        if len(multiselection) == 0:
            return 

        SCALE = alt.Scale(type='linear')
        if logscale:
            confirmed["confirmed"] += 0.00001

            confirmed = confirmed[confirmed.index > '2020-02-16']
            frate = frate[frate.index > '2020-02-16']
            
            SCALE = alt.Scale(type='log', domain=[10, int(max(confirmed.confirmed))], clamp=True)

        c2 = alt.Chart(confirmed.reset_index()).properties(height=150).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("confirmed:Q", title="Cases", scale=SCALE),
            color=alt.Color('state:N', title="State"),
            tooltip=[alt.Tooltip('state:N', title='State'), 
                     alt.Tooltip('confirmed:Q', title='Total cases')]
        )

        # case fatality rate...
        c3 = alt.Chart(frate.reset_index()).properties(height=100).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("frate:Q", title="Fatality rate [%]", scale=alt.Scale(type='linear')),
            color=alt.Color('state:N', title="State"),
            tooltip=[alt.Tooltip('state:N', title='State'), 
                     alt.Tooltip('frate:Q', title='Fatality rate'),
                     alt.Tooltip('deaths:Q', title='Total deaths'),
                     alt.Tooltip('confirmed:Q', title='Total cases')]
        )

        per100k = confirmed.loc[[confirmed.index.max()]].copy()
        per100k.loc[:,'inhabitants'] = per100k.apply(lambda x: inhabitants_us[x['state']], axis=1)
        per100k.loc[:,'per100k'] = per100k.confirmed / (per100k.inhabitants * 1_000_000) * 100_000
        per100k.loc[:,'totalc'] = round(per100k.confirmed,0)
        per100k = per100k.set_index("state")
        per100k = per100k.sort_values(ascending=False, by='per100k')
        per100k.loc[:,'per100k'] = per100k.per100k.round(2)

        c4 = alt.Chart(per100k.reset_index()).properties(width=75).mark_bar().encode(
            x=alt.X("per100k:Q", title="Cases per 100k inhabitants"),
            y=alt.Y("state:N", title="States", sort=None),
            color=alt.Color('state:N', title="State"),
            tooltip=[alt.Tooltip('state:N', title='State'), 
                     alt.Tooltip('per100k:Q', title='Cases per 100k'),
                     alt.Tooltip('inhabitants:Q', title='Inhabitants [mio]'),
                     alt.Tooltip('totalc:Q', title='Total cases')]
        )

        st.altair_chart(alt.hconcat(c4, alt.vconcat(c2, c3)), use_container_width=True)



    elif analysis == "By State":        

        st.header("State statistics")
        st.markdown("""\
            The reported number of active, recovered and deceased COVID-19 cases by state """
            """  
            ℹ️ You can select state and plot data as cummulative counts or new active cases per day. 
            """)

        # selections
        selection = st.selectbox("Select state:", states_list)
        cummulative = st.radio("Display type:", ["total", "new cases"])
        #scaletransform = st.radio("Plot y-axis", ["linear", "pow"])
        log(f"selection: {selection}, cummulative: {cummulative}")
        
        confirmed = confirmed[confirmed["Province/State"] == selection].iloc[:,3:]
        confirmed = transform(confirmed, collabel="confirmed")

        deaths = deaths[deaths["Province/State"] == selection].iloc[:,3:]
        deaths = transform(deaths, collabel="deaths")

        recovered = recovered[recovered["Province/State"] == selection].iloc[:,3:]
        recovered = transform(recovered, collabel="recovered")

        variables = ["active", "deaths", "recovered"]

        df = pd.concat([confirmed, deaths, recovered], axis=1)
        df["active"] = df.confirmed - df.deaths - df.recovered

        colors = ["orange", "purple", "gray"]

        value_vars = variables
        SCALE = alt.Scale(domain=variables, range=colors)
        if cummulative == 'new cases':
            value_vars = ['active']
            df = df[value_vars]
            df = df.diff()
            df["active"][df.active < 0] = 0
            SCALE = alt.Scale(domain=variables[0:1], range=colors[0:1]) 

        dfm = pd.melt(df.reset_index(), id_vars=["date"], value_vars=value_vars)
      
        c = alt.Chart(dfm.reset_index()).properties(height=200, title=selection).mark_bar(size=10).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Cases", scale=alt.Scale(type='linear')),
            color=alt.Color('variable:N', title="Category", scale=SCALE),
            tooltip=[alt.Tooltip('value:Q', title='Value')]
        )
        st.altair_chart(c, use_container_width=True)

        st.markdown(f"### Data for {selection}")
        st.write(df)


def europe():
    st.markdown("""\
        This app illustrates the spread of COVID-19 in Europe (where data is available) over time.
    """)

    #st.error("⚠️ There is currently an issue in the datasource of JHU. Data for 03/13 is invalid and thus removed!")

    countries = ["Germany", "Austria", "Belgium", "Denmark", "France", "Greece", "Italy", \
                 "Netherlands", "Norway", "Poland", "Romania", "Spain", "Sweden", \
                 "Switzerland", "United Kingdom"]

    confirmed, deaths, recovered = read_data()

    #keep only arab countries
    confirmed = confirmed[confirmed['Country/Region'].isin(countries)]
    deaths = deaths[deaths['Country/Region'].isin(countries)]
    recovered = recovered[recovered['Country/Region'].isin(countries)]

    #keep only dates where there were confirmed cases
    cols_to_remove = []
    for c in confirmed.columns:
        if c[0].isdigit():
            if confirmed[c].sum() == 0:
                cols_to_remove += [c]
    confirmed = confirmed.drop(cols_to_remove, axis=1)
    deaths = deaths.drop(cols_to_remove, axis=1)
    recovered = recovered.drop(cols_to_remove, axis=1)


    analysis = st.sidebar.selectbox("Choose Analysis", ["Overview", "By Country"])

    if analysis == "Overview":

        st.header("COVID-19 cases and fatality rate in Europe")
        st.markdown("""\
            These are the reported case numbers for a selection of European countries"""
            f""" (currently only {', '.join(countries)}). """
            """The case fatality rate (CFR) is calculated as:  
            $$
            CFR[\%] = \\frac{fatalities}{\\textit{all cases}}
            $$

            ℹ️ You can select/ deselect countries and switch between linear and log scales.
            """)

        multiselection = st.multiselect("Select countries:", countries, default=countries)
        logscale = st.checkbox("Log scale", True)

        confirmed = confirmed[confirmed["Country/Region"].isin(multiselection)]
        confirmed = confirmed.drop(["Lat", "Long"],axis=1)
        confirmed = transform2(confirmed, collabel="confirmed")

        deaths = deaths[deaths["Country/Region"].isin(multiselection)]
        deaths = deaths.drop(["Lat", "Long"],axis=1)
        deaths = transform2(deaths, collabel="deaths")

        frate = confirmed[["country"]]
        frate["frate"] = (deaths.deaths / confirmed.confirmed)*100

        # saveguard for empty selection 
        if len(multiselection) == 0:
            return 

        SCALE = alt.Scale(type='linear')
        if logscale:
            confirmed["confirmed"] += 0.00001

            confirmed = confirmed[confirmed.index > '2020-02-16']
            frate = frate[frate.index > '2020-02-16']
            
            SCALE = alt.Scale(type='log', domain=[10, int(max(confirmed.confirmed))], clamp=True)


        c2 = alt.Chart(confirmed.reset_index()).properties(height=150).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("confirmed:Q", title="Cases", scale=SCALE),
            color=alt.Color('country:N', title="Country")
        )

        # case fatality rate...
        c3 = alt.Chart(frate.reset_index()).properties(height=100).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("frate:Q", title="Fatality rate [%]", scale=alt.Scale(type='linear')),
            color=alt.Color('country:N', title="Country")
        )

        per100k = confirmed.loc[[confirmed.index.max()]].copy()
        per100k.loc[:,'inhabitants'] = per100k.apply(lambda x: inhabitants[x['country']], axis=1)
        per100k.loc[:,'per100k'] = per100k.confirmed / (per100k.inhabitants * 1_000_000) * 100_000
        per100k = per100k.set_index("country")
        per100k = per100k.sort_values(ascending=False, by='per100k')
        per100k.loc[:,'per100k'] = per100k.per100k.round(2)

        c4 = alt.Chart(per100k.reset_index()).properties(width=75).mark_bar().encode(
            x=alt.X("per100k:Q", title="Cases per 100k inhabitants"),
            y=alt.Y("country:N", title="Countries", sort=None),
            color=alt.Color('country:N', title="Country"),
            tooltip=[alt.Tooltip('country:N', title='Country'), 
                     alt.Tooltip('per100k:Q', title='Cases per 100k'),
                     alt.Tooltip('inhabitants:Q', title='Inhabitants [mio]')]
        )

        st.altair_chart(alt.hconcat(c4, alt.vconcat(c2, c3)), use_container_width=True)


    elif analysis == "By Country":        

        st.header("Country statistics")
        st.markdown("""\
            The reported number of active, recovered and deceased COVID-19 cases by country """
            f""" (currently only {', '.join(countries)}).  
            """
            """  
            ℹ️ You can select countries and plot data as cummulative counts or new active cases per day. 
            """)

        # selections
        selection = st.selectbox("Select country:", countries)
        cummulative = st.radio("Display type:", ["total", "new cases"])
        #scaletransform = st.radio("Plot y-axis", ["linear", "pow"])
        
        confirmed = confirmed[confirmed["Country/Region"] == selection].iloc[:,3:]
        confirmed = transform(confirmed, collabel="confirmed")

        deaths = deaths[deaths["Country/Region"] == selection].iloc[:,3:]
        deaths = transform(deaths, collabel="deaths")

        recovered = recovered[recovered["Country/Region"] == selection].iloc[:,3:]
        recovered = transform(recovered, collabel="recovered")

        variables = ["active", "deaths", "recovered"]

        df = pd.concat([confirmed, deaths, recovered], axis=1)
        df["active"] = df.confirmed - df.deaths - df.recovered

        colors = ["orange", "purple", "gray"]

        value_vars = variables
        SCALE = alt.Scale(domain=variables, range=colors)
        if cummulative == 'new cases':
            value_vars = ['active']
            df = df[value_vars]
            df = df.diff()
            df["active"][df.active < 0] = 0
            SCALE = alt.Scale(domain=variables[0:1], range=colors[0:1]) 

        dfm = pd.melt(df.reset_index(), id_vars=["date"], value_vars=value_vars)
      
        c = alt.Chart(dfm.reset_index()).properties(height=200, title=selection).mark_bar(size=10).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Cases", scale=alt.Scale(type='linear')),
            color=alt.Color('variable:N', title="Category", scale=SCALE),
        )
        st.altair_chart(c, use_container_width=True)
        st.markdown(f"### Data for {selection}")
        st.write(df)


def arabcountries():
    st.markdown("""\
        This app illustrates the spread of COVID-19 in Arab Region (where data is available) over time.
    """)

    #st.error("⚠️ There is currently an issue in the datasource of JHU. Data for 03/13 is invalid and thus removed!")

    countries = ["Algeria", "Bahrain", "Egypt", "Iraq", "Jordan", "Kuwait",
                "Lebanon", "Morocco", "Mauritania", "Oman", "Qatar", "Saudi Arabia", "Somalia", 
                "Sudan", "Tunisia", "United Arab Emirates", "Djibouti", "Comores", "Libya", "Palestine", 
                "Syria", "Yemen", "Iran", "Turkey", "Greece", "Cypress", "Ethiopia", "Eritrea", "South Sudan",
                "Chad", "Niger", "Mali", "Senegal", "Malta"]

    #get data
    confirmed, deaths, recovered = read_data()

    #keep only arab countries
    confirmed = confirmed[confirmed['Country/Region'].isin(countries)]
    deaths = deaths[deaths['Country/Region'].isin(countries)]
    recovered = recovered[recovered['Country/Region'].isin(countries)]

    #keep only dates where there were confirmed cases
    cols_to_remove = []
    for c in confirmed.columns:
        if c[0].isdigit():
            if confirmed[c].sum() == 0:
                cols_to_remove += [c]
    confirmed = confirmed.drop(cols_to_remove, axis=1)
    deaths = deaths.drop(cols_to_remove, axis=1)
    recovered = recovered.drop(cols_to_remove, axis=1)

    #list of countries 
    countries = list(confirmed['Country/Region'].unique()) 

    #keep top 10 states by default 
    sorted_conf = confirmed.sort_values(by=confirmed.columns[-1], ascending=False)
    def_countries = list(sorted_conf.iloc[0:10,0].unique()) 

    analysis = st.sidebar.selectbox("Choose Analysis", ["Overview", "By Country"])

    if analysis == "Overview":

        st.header("COVID-19 cases and fatality rate in Arab Region")
        st.markdown("""\
            These are the reported case numbers for a selection of Arab countries"""
            f""" (currently only {', '.join(countries)}). """
            """The case fatality rate (CFR) is calculated as:  
            $$
            CFR[\%] = \\frac{fatalities}{\\textit{all cases}}
            $$

            ℹ️ You can select/ deselect countries and switch between linear and log scales.
            """)

        if st.checkbox("select all"):
            multiselection = st.multiselect("Select countries:", countries, default=countries)
        else:
            multiselection = st.multiselect("Select countries:", countries, default=def_countries)

        logscale = st.checkbox("Log scale", True)

        confirmed = confirmed[confirmed["Country/Region"].isin(multiselection)]
        confirmed = confirmed.drop(["Lat", "Long"],axis=1)
        confirmed = transform2(confirmed, collabel="confirmed")

        deaths = deaths[deaths["Country/Region"].isin(multiselection)]
        deaths = deaths.drop(["Lat", "Long"],axis=1)
        deaths = transform2(deaths, collabel="deaths")

        frate = confirmed[["country"]]
        frate["frate"] = (deaths.deaths / confirmed.confirmed)*100

        # saveguard for empty selection 
        if len(multiselection) == 0:
            return 

        SCALE = alt.Scale(type='linear')
        if logscale:
            confirmed["confirmed"] += 0.00001

            confirmed = confirmed[confirmed.index > '2020-02-16']
            frate = frate[frate.index > '2020-02-16']
            
            SCALE = alt.Scale(type='log', domain=[10, int(max(confirmed.confirmed))], clamp=True)


        c2 = alt.Chart(confirmed.reset_index()).properties(height=150).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("confirmed:Q", title="Cases", scale=SCALE),
            color=alt.Color('country:N', title="Country")
        )

        # case fatality rate...
        c3 = alt.Chart(frate.reset_index()).properties(height=100).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("frate:Q", title="Fatality rate [%]", scale=alt.Scale(type='linear')),
            color=alt.Color('country:N', title="Country")
        )

        per100k = confirmed.loc[[confirmed.index.max()]].copy()
        per100k.loc[:,'inhabitants'] = per100k.apply(lambda x: inhabitants[x['country']], axis=1)
        per100k.loc[:,'per100k'] = per100k.confirmed / (per100k.inhabitants * 1_000_000) * 100_000
        per100k = per100k.set_index("country")
        per100k = per100k.sort_values(ascending=False, by='per100k')
        per100k.loc[:,'per100k'] = per100k.per100k.round(2)

        c4 = alt.Chart(per100k.reset_index()).properties(width=75).mark_bar().encode(
            x=alt.X("per100k:Q", title="Cases per 100k inhabitants"),
            y=alt.Y("country:N", title="Countries", sort=None),
            color=alt.Color('country:N', title="Country"),
            tooltip=[alt.Tooltip('country:N', title='Country'), 
                     alt.Tooltip('per100k:Q', title='Cases per 100k'),
                     alt.Tooltip('inhabitants:Q', title='Inhabitants [mio]')]
        )

        st.altair_chart(alt.hconcat(c4, alt.vconcat(c2, c3)), use_container_width=True)


    elif analysis == "By Country":        

        st.header("Country statistics")
        st.markdown("""\
            The reported number of active, recovered and deceased COVID-19 cases by country """
            f""" (currently only {', '.join(countries)}).  
            """
            """  
            ℹ️ You can select countries and plot data as cummulative counts or new active cases per day. 
            """)

        # selections
        selection = st.selectbox("Select country:", countries)
        cummulative = st.radio("Display type:", ["total", "new cases"])
        #scaletransform = st.radio("Plot y-axis", ["linear", "pow"])
        
        confirmed = confirmed[confirmed["Country/Region"] == selection].iloc[:,3:]
        confirmed = transform(confirmed, collabel="confirmed")

        deaths = deaths[deaths["Country/Region"] == selection].iloc[:,3:]
        deaths = transform(deaths, collabel="deaths")

        recovered = recovered[recovered["Country/Region"] == selection].iloc[:,3:]
        recovered = transform(recovered, collabel="recovered")

        variables = ["active", "deaths", "recovered"]

        df = pd.concat([confirmed, deaths, recovered], axis=1)
        df["active"] = df.confirmed - df.deaths - df.recovered


        colors = ["orange", "purple", "gray"]

        value_vars = variables
        SCALE = alt.Scale(domain=variables, range=colors)
        if cummulative == 'new cases':
            value_vars = ['active']
            df = df[value_vars]
            df = df.diff()
            df["active"][df.active < 0] = 0
            SCALE = alt.Scale(domain=variables[0:1], range=colors[0:1]) 

        dfm = pd.melt(df.reset_index(), id_vars=["date"], value_vars=value_vars)
      
        c = alt.Chart(dfm.reset_index()).properties(height=200, title=selection).mark_bar(size=10).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Cases", scale=alt.Scale(type='linear')),
            color=alt.Color('variable:N', title="Category", scale=SCALE),
        )
        st.altair_chart(c, use_container_width=True)
        st.markdown(f"### Data for {selection}")
        st.write(df)



def get_pop(country):
    try:
        return inhabitants[country]
    except:
        log(f"Can't get pop of {country}, assuming 1m")
        return 1

def generalList(title, countries, unit_name="Country", unit_plural="Countries", 
        column_name ="Country/Region", num_def_selected = 10):
    st.markdown(f"""\
        This app illustrates the spread of COVID-19 in {title} (where data is available) over time.
        You can choose other regions from the left sidebar (on mobile, click the top left button).
    """)

    #st.error("⚠️ There is currently an issue in the datasource of JHU. Data for 03/13 is invalid and thus removed!")

    #get data
    confirmed, deaths, recovered = read_data()

    #keep only arab countries
    confirmed = confirmed[confirmed[column_name].isin(countries)]
    deaths = deaths[deaths[column_name].isin(countries)]
    recovered = recovered[recovered[column_name].isin(countries)]

    #keep only dates where there were confirmed cases
    cols_to_remove = []
    for c in confirmed.columns:
        if c[0].isdigit():
            if confirmed[c].sum() == 0:
                cols_to_remove += [c]
    confirmed = confirmed.drop(cols_to_remove, axis=1)
    deaths = deaths.drop(cols_to_remove, axis=1)
    recovered = recovered.drop(cols_to_remove, axis=1)

    #list of countries 
    countries = list(confirmed[column_name].unique()) 

    #keep top 10 (num_def_selected) states by default 
    sorted_conf = confirmed.sort_values(by=confirmed.columns[-1], ascending=False)
    def_countries = list(sorted_conf.iloc[0:num_def_selected,0].unique()) 

    analysis = st.sidebar.selectbox("Choose Analysis", ["Overview", f"By {unit_name}"])

    if analysis == "Overview":

        st.header(f"COVID-19 cases and fatality rate in {title}")
        st.markdown(f"""\
            These are the reported case numbers for a selection of {unit_plural}"""
            """The case fatality rate (CFR) is calculated as:  
            $$
            CFR[\%] = \\frac{fatalities}{\\textit{all cases}}
            $$"""
            f"""
            ℹ️ You can select/ deselect {unit_plural} and switch between linear and log scales.
            """)

        if len(countries) < 30 and st.checkbox("select all"):
            multiselection = st.multiselect(f"Select {unit_plural}:", countries, default=countries)
        else:
            multiselection = st.multiselect(f"Select {unit_plural}:", countries, default=def_countries)
        log(f"multiselection {str(multiselection)}")

        logscale = st.checkbox("Log scale", True)

        confirmed = confirmed[confirmed[column_name].isin(multiselection)]
        confirmed = confirmed.drop(["Lat", "Long"],axis=1)
        confirmed = transform2(confirmed, collabel="confirmed")

        deaths = deaths[deaths[column_name].isin(multiselection)]
        deaths = deaths.drop(["Lat", "Long"],axis=1)
        deaths = transform2(deaths, collabel="deaths")

        frate = confirmed[["country"]]
        frate["frate"] = (deaths.deaths / confirmed.confirmed)*100
        frate["deaths"] = deaths.deaths
        frate["confirmed"] = confirmed.confirmed

        # saveguard for empty selection 
        if len(multiselection) == 0:
            return 

        SCALE = alt.Scale(type='linear')
        if logscale:
            confirmed["confirmed"] += 0.00001

            confirmed = confirmed[confirmed.index > '2020-02-16']
            frate = frate[frate.index > '2020-02-16']
            
            SCALE = alt.Scale(type='log', domain=[10, int(max(confirmed.confirmed))], clamp=True)


        c2 = alt.Chart(confirmed.reset_index()).properties(height=150).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("confirmed:Q", title="Cases", scale=SCALE),
            color=alt.Color('country:N', title="Country"),
            tooltip=[alt.Tooltip('country:N', title='Country'), 
                     alt.Tooltip('confirmed:Q', title='Total cases')]
        )

        # case fatality rate...
        c3 = alt.Chart(frate.reset_index()).properties(height=100).mark_line().encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("frate:Q", title="Fatality rate [%]", scale=alt.Scale(type='linear')),
            color=alt.Color('country:N', title="Country"),
            tooltip=[alt.Tooltip('country:N', title='Country'), 
                     alt.Tooltip('frate:Q', title='Fatality rate'),
                     alt.Tooltip('deaths:Q', title='Total deaths'),
                     alt.Tooltip('confirmed:Q', title='Total cases')]
        )

        per100k = confirmed.loc[[confirmed.index.max()]].copy()
        per100k.loc[:,'inhabitants'] = per100k.apply(lambda x: get_pop(x['country']), axis=1)
        per100k.loc[:,'per100k'] = per100k.confirmed / (per100k.inhabitants * 1_000_000) * 100_000
        per100k.loc[:,'totalc'] = round(per100k.confirmed,0)
        per100k = per100k.set_index("country")
        per100k = per100k.sort_values(ascending=False, by='per100k')
        per100k.loc[:,'per100k'] = per100k.per100k.round(2)

        c4 = alt.Chart(per100k.reset_index()).properties(width=75).mark_bar().encode(
            x=alt.X("per100k:Q", title="Cases per 100k inhabitants"),
            y=alt.Y("country:N", title="Countries", sort=None),
            color=alt.Color('country:N', title="Country"),
            tooltip=[alt.Tooltip('country:N', title='Country'), 
                     alt.Tooltip('per100k:Q', title='Cases per 100k'),
                     alt.Tooltip('inhabitants:Q', title='Inhabitants [mio]'),
                     alt.Tooltip('totalc:Q', title='Total Cases')]
        )

        st.altair_chart(alt.hconcat(c4, alt.vconcat(c2, c3)), use_container_width=True)


    elif analysis == f"By {unit_name}":        

        st.header(f"{unit_name} statistics")
        st.markdown(f"""\
            The reported number of active, recovered and deceased COVID-19 cases by {unit_name} """
            """  
            ℹ️ You can select countries and plot data as cummulative counts or new active cases per day. 
            """)

        # selections
        selection = st.selectbox(f"Select {unit_name}:", countries)
        cummulative = st.radio("Display type:", ["total", "new cases"])
        log(f"selection: {selection}, cummulative: {cummulative}")

        #scaletransform = st.radio("Plot y-axis", ["linear", "pow"])
        
        confirmed = confirmed[confirmed[column_name] == selection].iloc[:,3:]
        confirmed = transform(confirmed, collabel="confirmed")

        deaths = deaths[deaths[column_name] == selection].iloc[:,3:]
        deaths = transform(deaths, collabel="deaths")

        recovered = recovered[recovered[column_name] == selection].iloc[:,3:]
        recovered = transform(recovered, collabel="recovered")

        variables = ["active", "deaths", "recovered"]

        df = pd.concat([confirmed, deaths, recovered], axis=1)
        df["active"] = df.confirmed - df.deaths - df.recovered


        colors = ["orange", "purple", "gray"]

        value_vars = variables
        SCALE = alt.Scale(domain=variables, range=colors)
        if cummulative == 'new cases':
            value_vars = ['active']
            df = df[value_vars]
            df = df.diff()
            df["active"][df.active < 0] = 0
            SCALE = alt.Scale(domain=variables[0:1], range=colors[0:1]) 

        dfm = pd.melt(df.reset_index(), id_vars=["date"], value_vars=value_vars)
      
        c = alt.Chart(dfm.reset_index()).properties(height=200, title=selection).mark_bar(size=10).encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("value:Q", title="Cases", scale=alt.Scale(type='linear')),
            color=alt.Color('variable:N', title="Category", scale=SCALE),
            tooltip=[alt.Tooltip('value:Q', title='Value')]
        )
        st.altair_chart(c, use_container_width=True)
        st.markdown(f"### Data for {selection}")
        st.write(df)

import traceback

if __name__ == "__main__":
    retry = 0
    while retry < 3:
        try:
            main()
            break
        except Exception as e:
            log(f"Exception: {type(e)}")
            log(str(e))
            log(str(e.args))      # arguments stored in .args
            log(str(vars(e)))
            log(''.join(traceback.format_stack()))
            retry += 1
            log(f"#### Restarting, retry: {retry} ####")
            if ISDEBUG:
                raise e
    if retry >= 3:
        st.write("Server error, please visit the site later.")
        log(f"#### Giving Up - quitting, retry: {retry} ####")


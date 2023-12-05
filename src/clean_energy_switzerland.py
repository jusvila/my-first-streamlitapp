import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
from copy import deepcopy

# Add title and header
st.set_page_config(page_title="Clean Energy Sources in Switzerland", # page title, displayed on the window/tab bar
                   page_icon="apple", # favicon: icon that shows on the window/tab bar 
                   #layout="wide", # use full width of the page
                   #menu_items={
                   #    'About': "WRITE WHAT YOUR PAGE IS ABOUT"
                   #}
)
st.title("Clean Energy Sources in Switzerland")

# First some Data Exploration
@st.cache
def load_data(path):
    df = pd.read_csv(path)
    return df

clean_energy_ch_raw = load_data("../data/raw/renewable_power_plants_CH.csv")
clean_energy_ch = deepcopy(clean_energy_ch_raw)

# Getting the coordinates of the Cantons 
# File downloaded from here: https://data.opendatasoft.com/explore/dataset/georef-switzerland-kanton%40public/export/?disjunctive.kan_code&disjunctive.kan_name&sort=year&location=8,46.82242,8.22403&basemap=jawg.streets&dataChart=eyJxdWVyaWVzIjpbeyJjb25maWciOnsiZGF0YXNldCI6Imdlb3JlZi1zd2l0emVybGFuZC1rYW50b25AcHVibGljIiwib3B0aW9ucyI6eyJkaXNqdW5jdGl2ZS5rYW5fY29kZSI6dHJ1ZSwiZGlzanVuY3RpdmUua2FuX25hbWUiOnRydWUsInNvcnQiOiJ5ZWFyIn19LCJjaGFydHMiOlt7ImFsaWduTW9udGgiOnRydWUsInR5cGUiOiJsaW5lIiwiZnVuYyI6IkNPVU5UIiwic2NpZW50aWZpY0Rpc3BsYXkiOnRydWUsImNvbG9yIjoiIzE0MkU3QiJ9XSwieEF4aXMiOiJ5ZWFyIiwibWF4cG9pbnRzIjoiIiwidGltZXNjYWxlIjoieWVhciIsInNvcnQiOiIifV0sImRpc3BsYXlMZWdlbmQiOnRydWUsImFsaWduTW9udGgiOnRydWV9
with open("../data/raw/georef-switzerland-kanton.geojson") as response:
    cantons = json.load(response)

# Need to find a way to match the canton code from the df with the canton name in the json
cantons_dict = {'TG':'Thurgau', 'GR':'Graubünden', 'LU':'Luzern', 'BE':'Bern', 'VS':'Valais', 
                'BL':'Basel-Landschaft', 'SO':'Solothurn', 'VD':'Vaud', 'SH':'Schaffhausen', 'ZH':'Zürich', 
                'AG':'Aargau', 'UR':'Uri', 'NE':'Neuchâtel', 'TI':'Ticino', 'SG':'St. Gallen', 'GE':'Genève', 
                'GL':'Glarus', 'JU':'Jura', 'ZG':'Zug', 'OW':'Obwalden', 'FR':'Fribourg', 'SZ':'Schwyz', 
                'AR':'Appenzell Ausserrhoden', 'AI':'Appenzell Innerrhoden', 'NW':'Nidwalden', 'BS':'Basel-Stadt'}

clean_energy_ch["canton_name"] = clean_energy_ch["canton"].map(cantons_dict)

# Setting up columns
left_column, middle_column, right_column  = st.columns([3, 1, 1])

# Widgets: selectbox
options = ["Number of sources", "Total electrical capacity", "Total production"]
choice = left_column.selectbox("Quantity:", options)

# Widgets: selectbox
select_list = ["All"]+sorted(pd.unique(clean_energy_ch['energy_source_level_2']))
type = middle_column.radio(label="Energy type:", options=select_list)

# Widgets: radio buttons
##show_means = middle_column.radio(
##    label='Show Class Means', options=['Yes', 'No'])

##plot_types = ["Matplotlib", "Plotly"]
##plot_type = right_column.radio("Choose Plot Type", plot_types)

# Flow control and plotting
if choice == "Number of sources":
    st.header("Number of sources per Canton")
    if type == 'All':
        df_plot = clean_energy_ch.groupby("canton_name").size().reset_index(name="count")
    else:
        df_plot = clean_energy_ch[clean_energy_ch['energy_source_level_2'] == type].groupby(
            "canton_name").size().reset_index(name="count")
    clr = "count"
    
elif choice == "Total electrical capacity":
    st.header("Total electrical capacity per Canton")
    if type == 'All':
        df_plot = clean_energy_ch.groupby("canton_name")["electrical_capacity"].sum().reset_index(name="sum")
    else:
        df_plot = clean_energy_ch[clean_energy_ch['energy_source_level_2'] == type].groupby(
            "canton_name")["electrical_capacity"].sum().reset_index(name="sum")
    clr = "sum"

elif choice == "Total production":
    st.header("Total production per Canton")
    if type == 'All':
        df_plot = clean_energy_ch.groupby("canton_name")["production"].sum().reset_index(name="sum")
    else:
        df_plot = clean_energy_ch[clean_energy_ch['energy_source_level_2'] == type].groupby(
            "canton_name")["production"].sum().reset_index(name="sum")
    clr = "sum"

else:
    df_plot = clean_energy_ch.groupby("canton_name").size().reset_index(name="count")


# Plotly visualization
fig = px.choropleth_mapbox(
    df_plot, 
    color=clr,
    geojson=cantons, 
    locations="canton_name", 
    featureidkey="properties.kan_name",
    center={"lat": 46.8, "lon": 8.3},
    mapbox_style="open-street-map", 
    zoom=6.3,
    opacity=0.8,
    width=900,
    height=500,
    labels={"canton_name":"Canton",
           clr:choice},
    #title="<b>Number of Clean Energy Sources per Canton</b>",
    color_continuous_scale="ylgn",
)
fig.update_layout(margin={"r":0,"t":35,"l":0,"b":0},
                  #font={"family":"Sans",
                  #     "color":"maroon"},
                  hoverlabel={"bgcolor":"white", 
                              "font_size":12,
                             "font_family":"Sans"},
                  title={"font_size":20,
                        "xanchor":"left", "x":0.01,
                        "yanchor":"bottom", "y":0.95}
                 )
fig.show()

st.plotly_chart(fig)

# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show dataframe"):
    st.subheader("Original data:")
    st.dataframe(data=df_plot)
    # st.table(data=df_plot)
import numpy as np
import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px


st.title("Motor Vehicle Collisions in New York City")
st.markdown("### A Streamlit Dashboard that used to Analyse vehicle collision in NYC ")

DATA_URL = "https://raw.githubusercontent.com/devsTudu/StreamlitAccident/main/chunks/part_0.csv"

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL,nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'}, inplace=True)
    return data

data = load_data(100000)

st.header("Where are the most people injured in NYC")
injured_people = st.slider("Number of persons injured in vehicle Collisions :",6,19)
st.map(data.query("injured_persons >= @injured_people")[["latitude","longitude"]].dropna(how="any"))

st.header("How many collisions occur during a given time of a day ?")
hour = st.slider("Hour to look at", 0,24)
data = data[data['date/time'].dt.hour == hour]

midpoint = (np.average(data['latitude']),np.average(data['longitude']))

st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=midpoint[0],
        longitude = midpoint[1],
        zoom=11
    ),
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time','latitude','longitude']],
            get_position=['longitude','latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0,1000],
        ),
    ]
 )
)

st.markdown("Vehicle Collisions between %i:00 and %i:00" %(hour,(hour+1)%24))


st.subheader("Breakdown by minutes between %i:00 and %i:00" %(hour,(hour+1)%24))

filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour<hour+1)
]

hist = np.histogram(filtered['date/time'].dt.minute, bins=60,range=(0,60))[0]
chrt_data = pd.DataFrame({'minute': range(0,60), 'crashes':hist})
fig = px.bar(chrt_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
st.write(fig)

original_data = data

st.header("Top 5 Dangerous streets by affected type")
select = st.selectbox('Affected type of people', ['Pedestrians','Cyclists','Motorists'])

showtop = lambda colname: st.write(original_data.
    query(colname +" >= 1")[["on_street_name",colname]].
    sort_values(by=[colname],ascending=False).dropna(how='any')[:5])

if select == 'Pedestrians':
    showtop("injured_pedestrians")

elif select == 'Cyclists':
    colname = "injured_cyclists"
    showtop(colname)

elif select == 'Motorists':
    colname = "injured_motorists"
    showtop(colname)

if st.checkbox("Show Raw Data", False):
    st.subheader("Raw Data")
    st.write(data)

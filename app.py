import streamlit as s
import pandas as pd
import numpy as np
import pydeck as pdk
import datetime as dt
import plotly.express as p

s.title("Motor vehical collsion")

@s.cache(persist=True)
def load_data(nrows):
    data=pd.read_csv('Motor_Vehicle_Collisions_-_Crashes.csv',nrows=nrows,parse_dates=[['CRASH_DATE','CRASH_TIME']])
    data.dropna(subset=['LATITUDE','LONGITUDE'],inplace=True)
    lowercase=lambda x:str(x).lower()
    data.rename(lowercase,axis='columns',inplace=True)
    data.rename(columns={'crash_date_crash_time':'date/time'},inplace=True)
    return data


data=load_data(100000)


s.header('Most injured people?')
injured=s.slider('number of people injured',0,19)
s.map(data.query("injured_persons >= @injured")[['latitude','longitude']].dropna(how='any'))



s.header("day time : collision , select hour")
hour=s.slider('select hour here',0,23)
#subset data 
original_data = data
data=data[data['date/time'].dt.hour==hour]

midpoint_initial=(np.average(data['latitude']),np.average(data['longitude']))

#3d map data
s.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude":midpoint_initial[0],
        "longitude":midpoint_initial[1],
        "zoom":11,
        "pitch":50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time','latitude','longitude']],
            get_position=['longitude','latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[1,1000],

        ),
    ],

    
))

s.subheader("breakdown by hour and hour+1")
#subset data
dfil=data[
    (data['date/time'].dt.hour>=hour )& ( data['date/time'].dt.hour< (hour+1))
]
hist=np.histogram(dfil['date/time'].dt.minute, bins=60,range=(0,60))[0]
chart_data=pd.DataFrame({'minute':range(60),'crashes':hist})
figure=p.bar(chart_data,x='minute',y='crashes',hover_data=['minute','crashes'],height=400)
s.write(figure)

s.header("Top 5 dangerous streets by affected class")
select = s.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    s.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
    s.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

else:
    s.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])
#raw data
if s.checkbox("show raw data",False):
    s.subheader('Raw data')
    s.write(data)
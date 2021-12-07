# -*- coding: utf-8 -*-
"""
Created on Mon Dec  6 08:47:30 2021

@author: usuario
"""

import streamlit as st
import pandas as pd
import json
import plotly.express as px
import geopandas as gdp
import plotly.graph_objs as go


df = pd.read_csv('C:/Users/usuario/TAE/Incidentesviales/geoloca.csv', encoding = 'utf-8')

with open('limites.geojson') as limite:
    mapa = json.load(limite)

# locat = list(zip(df.LONGITUD,df.ALTITUD))
# fig = px.choropleth_mapbox(df, geojson = mapa, locations = locat,color = 'cluster',mapbox_style = 'carto-positron, zoom = 3)

# st.plotly_chart(fig)
# print('ok')

# mapa = gdp.read_file('C:\Users\usuario\TAE\Aplicacion incidentes viales\limites_.shp')

i=1
for feature in mapa["features"]:
   feature ['id'] = str(i).zfill(2)
   i += 1

df['Accidentes'] = df['Accidentes'].apply(lambda x: round(x))
mapboxt = 'MapBox Token'
choro = go.Choroplethmapbox(z=df['cluster'], locations =  df.BARRIO,
                            colorscale = 'Viridis', geojson = mapa, text = df['Accidentes'], marker_line_width=0.1)

scatt = go.Scattermapbox(lat=df['ALTITUD'], lon=df['LONGITUD'],mode='markers+text', below='False', marker=dict( size=6, color = df.cluster),
                         hovertext = df[['BARRIO','Accidentes','cluster']],hoverinfo = 'text')


layer1 = st.multiselect('Layer Selection', [choro, scatt], 
         format_func=lambda x: 'Polygon' if x==choro else 'Points')
layout = go.Layout(title_text ='Barrios Medellin', title_x =0.5,  
         width=950, height=700,mapbox = dict(center= dict(lat=6.25184,  
         lon=-75.56359),accesstoken= mapboxt, zoom=11,style="stamen-terrain"))


fig = go.Figure(data=scatt, layout=layout)
st.plotly_chart(fig)
print('ok')
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import datetime as dte
import joblib 
import plotly.graph_objs as go
import json
import sklearn
#from streamlit_player import st_player

header = st.container()
Dataset = st.container()
Features = st.container()
mode_training = st.container()

st.markdown(
    '''
    <style>
    .main{
        background-color: #F5F5F5;
    }
    </style>    
    ''',
    unsafe_allow_html=True
    )

def quincena(f):
    z = []
    for i,j in zip(f['DayMo'],f['Dayw']):
        if (i in [15,30,31] and j in ['Monday','Tuesday', 'Thursday', 'Friday','Wednesday']):
            z.append(1)
        else:
            z.append(0)
    return z

@st.cache
def get_data(finename):
    txi_data = pd.read_csv(finename, encoding = 'utf-8')
    return txi_data

with header:
    st.title('Crashapp')
    #st_player('https://youtu.be/K-YZjpwqD_Q')
    


with Dataset:
    st.header('MEdata: Datos accidente Medellín')
    st.text('''Esta base de datos corresponde a los accidentes  de transito registrados en la 
ciudad de Medellín. Según la ley 769 de 2002 - códgio nacional de Tránsito, se 
entiende por accidente de transito: evento, generalmente involuntario, generado
al menos por un un vehículo en movimiento, que causa daños a personas y bienes
involucrados en él, e igualmente afecta la normal circulación de los vehículos 
que se movilizan por la vía o vías comprendidas en el lugar o dentro de la zona 
de influencia del hecho''')
    #st.text('Base de datos original[Medata](http://medata.gov.co/dataset/incidentes-viales)')
    Data = get_data(r'Dataaplica.csv')
    DataLost = get_data(r'Datalost.csv')
    st.write(Data.head(8))
    st.subheader('Comparación datos no recuperados contra los datos completos')
    DataLostchart = DataLost.groupby(['MES'])[['Data perdida','Datos completos']].sum()
    DataLostchart = DataLostchart.reset_index()
    DataLostchart = DataLostchart.set_index('MES')
    st.bar_chart(DataLostchart) 
    
    
    
with Features:
    
    st.header('Clustering de los barrios de Medellín')
    st.text('''Según los datos recolectados los barrios de Medellín se pueden agrupar en 
tres categórias, según su riesgo de accidente : Alto, Medio, Bajo''')

    st.markdown('* **Alto ** Son los barrios que presentan un alto riesgo de accidentes, en el mapa se represetan con el color rosado')
    st.markdown('* **Medio** Son los barrios que presentan un  riesgo medio de accidentes, en el mapa se represetan con el color Amarillo')
    st.markdown('* **Bajo** Son los barrios que presentan un  riesgo bajo de accidentes, en el mapa se represetan con el color Azul')
    st.text('A continuación se presenta la agrupación de los barrios por su accidentalidad')
    
    st.text('''Cada punto tiene el nombre del barrio y la cantidad de accidentes en promedio
por mes [Nombre del barrio, Accidentes por mes]''')
    
    df = pd.read_csv(r'geoloca.csv', encoding = 'utf-8')
    with open('limites.geojson') as limite:
        mapa = json.load(limite)
    df['Accidentes'] = df['Accidentes'].apply(lambda x: round(x))
    scatt = go.Scattermapbox(lat=df['ALTITUD'], lon=df['LONGITUD'],mode='markers+text', below='False', marker=dict( size=6, color = df.cluster),
                             hovertext = df[['BARRIO','Accidentes']],hoverinfo = 'text')
    mapboxt = 'MapBox Token'
    layout = go.Layout(title_text ='Barrios Medellin', title_x =0.5,  
             width=950, height=700,mapbox = dict(center= dict(lat=6.25184,  
             lon=-75.56359),accesstoken= mapboxt, zoom=11,style="stamen-terrain"))
    
    fig = go.Figure(data=scatt, layout=layout)
    st.plotly_chart(fig)
    
    
with mode_training:
    
    st.header('Predicción')
    st.text('')
    
    sel_col, col2, col3 = st.columns(3)
    
    boton = col3.button('Predecir')
    
    intervalperiod = sel_col.selectbox('Para que período de tiempo desea hacer la predicción',
                                       options = ['Día','Semana','Mes'], index = 0)
    
    Fecha_inicial = sel_col.date_input('Inicio')
    
    if (intervalperiod != 'Día'):
        Fecha_final = sel_col.date_input('Final')
    else:
        Fecha_final = Fecha_inicial
                                           
    if(intervalperiod != 'Día' and Fecha_final < Fecha_inicial):
        
        sel_col.text('Revisa las fechas ingresadas')
        
    Df_festivos = pd.read_csv('festivosproximos.csv', encoding = 'utf-8', header = None)
    Df_festivos.rename({Df_festivos.columns[0]:'Fecha'},axis =1, inplace = True)
    Df_festivos['Fecha'] = pd.to_datetime(Df_festivos['Fecha'], format="%d/%m/%Y")
        
      
    
    Daymonth =[]
    Month = []
    year = []
    Dayweek = []
    
    filldf = []
    
    # i = pd.to_datetime (Fecha_inicial,format="%Y/%m/%d")
    i = Fecha_inicial
    
    
    
    if boton:
        z = Df_festivos['Fecha'].unique()
        
        if (Fecha_final - i).days < 6:
            # Fecha_final = pd.to_datetime (Fecha_final,format="%Y/%m/%d")
            k = Fecha_final + dte.timedelta(days=6)
        else:
            k = Fecha_final
        
        while i <= k:
            i = pd.to_datetime(i,format="%Y/%m/%d")
            Day = i.strftime('%d')
            Day = int(Day)
            Daymonth.append(Day)
            
            Dweek = i.strftime('%A')
            Dayweek.append(Dweek)
            
            
            numbermonth = i.strftime('%m')
            numbermonth = int(numbermonth)
            Month.append(numbermonth)
            
            yeardate = i.strftime('%Y')
            yeardate = int(yeardate)
            year.append(yeardate)
            
            
            
            if i in z:
                festivo = 1
            else:
                festivo = 0
            
            filldf.append([Day,numbermonth,yeardate,festivo,Dweek])
            
            
            i = i + dte.timedelta(days=1)
            
        
        
        column = ['DayMo','Month','year','festivo','Dayw']
        Df = pd.DataFrame(filldf, columns = column)
        Df['Quincena'] = quincena(Df)
        
        Df = pd.get_dummies(Df)
        Df = Df[['DayMo', 'Month', 'year', 'festivo', 'Quincena', 'Dayw_Friday',
           'Dayw_Monday', 'Dayw_Saturday', 'Dayw_Sunday', 'Dayw_Thursday',
           'Dayw_Tuesday', 'Dayw_Wednesday']]
        
        if (intervalperiod == 'Día'):
            Df = Df.iloc[[0]]
        elif (intervalperiod == 'Semana'):
            Ff = pd.to_datetime (Fecha_final,format="%Y/%m/%d")
            Fi = pd.to_datetime (Fecha_inicial,format="%Y/%m/%d")
            Aux =(Ff - Fi).days
            Aux = int(Aux)
            Df = Df.head(Aux)
        else:
            Df = Df
        
        choquemodel = joblib.load('modelo_choque_entrenado.pkl')
        atropellomodel = joblib.load('modelo_Atropello_entrenado.pkl')
        caidamodel = joblib.load('modelo_Caida_entrenado.pkl')
        otromodel = joblib.load('modelo_Otro_entrenado.pkl')
        volcamientomodel = joblib.load('modelo_Volcamiento_entrenado.pkl')
        
        ychoque = choquemodel.predict(Df)
        yatropello = atropellomodel.predict(Df)
        ycaida =caidamodel.predict(Df)
        yotro = otromodel.predict(Df)
        yvolcamient = volcamientomodel.predict(Df)
        
        ychoque = round(sum(ychoque))
        yatropello = round(sum(yatropello))
        ycaida = round(sum(ycaida))
        yotro = round(sum(yotro))
        yvolcamient = round(sum(yvolcamient))
        
        
        
        Predic = [['Choque', ychoque],['Atropello',yatropello],['Caída',ycaida],
                  ['Volcamiento',yvolcamient],['Otro tipo',yotro]]
        
        preDf = pd.DataFrame(Predic,columns =['Tipo', 'Total'])
        preDf = preDf.set_index('Tipo')
        st.bar_chart(preDf)
    
    
    print('ok')
        
    
            
    



    
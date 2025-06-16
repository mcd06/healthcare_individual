import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("Lebanese Currency Exchange Rate to USD Over the Years")
st.write("The data represents the fluctuation of the Lebanese currency exchange rate to the US Dollar (USD) over time, with points distributed between actual local currency units per USD and standardized local currency units per USD, highlighting key trends in currency volatility and value changes")
path = "https://linked.aub.edu.lb/pkgcube/data/c788a60a4bccd0b261d0204f9f9e281b_20240905_152400.csv"
df = pd.read_csv(path)
st.subheader("Figure 1: Scatterplot using plotly.express")
fig = px.scatter(data_frame = df, x = 'Year', y = 'Value', hover_data = ['Currency'], hover_name = 'Item',
                 color = 'Item Code', size = 'Value')
trend_annotation = {'x':2021.5, 'y':7000, 'text':"Upward trend (SLC)", 'arrowhead':3,
                   'showarrow':True, 'font':{'size':10, 'color':'black'}}
multiple_annotation = {'x':1992, 'y':4000, 'text':"Fluctuations observed (LCU)",
                       'arrowhead':3,'showarrow':True, 'font':{'size':10, 'color':'black'}}
spike_annotation = {'x':2023, 'y':17000, 'text':"Spike observed (LCU)",
                       'arrowhead':3,'showarrow':True, 'font':{'size':10, 'color':'black'}}
fig.update_layout({'title':{'text': 'Lebanese Currency Exchange Rate to USD Over the Years'}}) 
fig.update_layout({'annotations':[trend_annotation, multiple_annotation, spike_annotation]})
fig.update_layout({'xaxis':{'range':[1985,2026]}})
fig.update_yaxes(title_text = 'Lebanese Currency Rate to USD')
st.plotly_chart(fig)

st.subheader("Figure 2: Bar chart using plotly.graph_objects")
df_LCU = df[df['Item'] == 'Local currency units per USD']
df_SLC = df[df['Item'] == 'Standard local currency units per USD']
df_LCU_max_per_year = df_LCU.groupby('Year')['Value'].max().reset_index()    
df_SLC_max_per_year = df_SLC.groupby('Year')['Value'].max().reset_index()    
fig = go.Figure()
fig.add_trace(go.Bar(x = df_LCU_max_per_year['Year'], y = df_LCU_max_per_year['Value'], name = 'Local currency units per USD',
                      hovertext = df_LCU_max_per_year['Value'], hoverinfo = 'text'))
fig.add_trace(go.Bar(x = df_SLC_max_per_year['Year'], y = df_SLC_max_per_year['Value'], name = 'Standard local currency units per USD',
                    hovertext = df_LCU_max_per_year['Value'], hoverinfo = 'text'))
fig.update_layout(title = 'Lebanese Currency Exchange Rate to USD (Max Value per Year)', xaxis_title = 'Year', 
                  yaxis_title = 'Lebanese Currency Rate to USD', height = 800, hovermode = "x")
fig.update_layout({'xaxis': {'range': [1985, 2024]}})
trend_annotation = {'x':2021, 'y':5800, 'text':"Upward trend (SLC)", 'arrowhead':3,
                   'showarrow':True, 'font':{'size':10, 'color':'black'}}
multiple_annotation = {'x':1992, 'y':2530, 'text':"Fluctuations observed (LCU)",
                       'arrowhead':3,'showarrow':True, 'font':{'size':10, 'color':'black'}}
spike_annotation = {'x':2023, 'y':15000, 'text':"Spike observed (LCU)",
                       'arrowhead':3,'showarrow':True, 'font':{'size':10, 'color':'black'}} 
fig.update_layout({'annotations':[trend_annotation, multiple_annotation, spike_annotation]})
st.plotly_chart(fig)

st.subheader("Figure 3: Scatterplot using plotly.graph_objects")
df_filtered = df[(df['Year'] >= 1985) & (df['Year'] <= 2024)]
fig = px.scatter(data_frame = df_filtered, x = 'Year', y = 'Value', size = 'Value', color = 'Item', hover_name = 'Item', 
    animation_frame = 'Year', title = 'Lebanese Currency Exchange Rate to USD (1985-2024)', range_x = [1985, 2024], 
    range_y = [0, 16000], size_max = 30)
fig.update_layout(xaxis_title="Year", yaxis_title="Lebanese Currency Rate to USD", height=800)
st.plotly_chart(fig)

st.subheader("Figure 4: Line chart using plotly.graph_objects")
df_SLC = df[df['Item'] == 'Standard local currency units per USD']
fig = go.Figure()
fig.add_trace(go.Scatter(x = df_SLC['Year'], y = df_SLC['Value'], mode = 'lines', name = 'Standard local currency units per USD'))
latest_year = df_SLC['Year'].max()
fig.update_layout(title = 'Lebanese Currency Exchange Rate to USD (Standard Local Currency Units)', height = 800,
    xaxis_title = "Year", yaxis_title = "Lebanese Currency Rate to USD",
    updatemenus = [{'buttons': [{'args': [{'xaxis.range': [latest_year - 3, latest_year]}], 'label': '3 Years Before', 'method': 'relayout'},
                {'args': [{'xaxis.range': [latest_year - 10, latest_year]}], 'label': '10 Years Before', 'method': 'relayout'},
                {'args': [{'xaxis.range': [latest_year - 40, latest_year]}], 'label': '40 Years Before', 'method': 'relayout'}],
            'direction': 'down', 'showactive': True, 'x': 1.1, 'xanchor': 'left', 'y': 1, 'yanchor': 'middle'}])
st.plotly_chart(fig)

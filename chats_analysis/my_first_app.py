from numpy.lib.arraysetops import unique
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from PIL import Image
import os, datetime
import pydeck as pdk
from urllib.error import URLError
import altair as alt
import plotly.graph_objects as go
import json

primary_color = "#00A5DE"
st.set_page_config(
        page_title='Digital Clinical Trial Assistant - Analysis',
        page_icon="🧊",
        layout= "wide")


st.header('DL04 Trial')
st.subheader('Initial Study')


# ----------    READ CSV -------------------------------------
full_chats_csv_name = os.path.abspath('new_214.csv')

df = pd.read_csv(full_chats_csv_name)

# -------------- DATA PREPRATION ----------------------------
initial = True

for j in df.data:
    a = json.loads(j)
    
    if a['event'] == 'user':

        if 'intent_ranking' in a['parse_data']:

            df1 = pd.DataFrame(a['parse_data']['intent_ranking']).T
            df1.columns = df1.loc['name']
            df1 = df1.drop(['name'],axis=0)
            df1.insert(0,'text', a['text'])
            df1.reset_index(inplace=True)

            df2 = pd.DataFrame(a['parse_data']['entities'])

            df2.insert(0,'message_id', a['parse_data']['message_id'])

            if len(df1) == 2:

                df1.drop([0],inplace=True)
                df1.reset_index(inplace=True)
                df1 = df1.join(df2)
                if initial == True:
                    dfx1 = df1
                    initial = False
                else:
                    dfx1 = dfx1.append(df1)
df1 = dfx1

new_columns = ['text', 'inform_protocol', 'SOA_C1', 'character',
       'target_group', 'treatment_history', 'message_id', 'entity',
       'confidence_entity', 'value', 'extractor', 'processors','inquiry_protocol']

df1 = pd.DataFrame(df1,columns = new_columns)
df1.set_index('message_id',inplace=True)


# ------------------ START DISPLACY ------------------------------------------------
st.title("Digital Clinical Trial Assistant Analsyis ")

st.write("Display user text, intent, entities")

df1



# df = pd.DataFrame({
#     'first column:': [1,2,3,4],
#     'second column:': [10,20,30,40],
# })

# chart_data = pd.DataFrame(
#     np.random.randn(20,3),
#     columns=['a','b','c']
# )

# # chart_data

# st.line_chart(chart_data)

# map_data = pd.DataFrame(
#     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#     columns=['lat', 'lon']
# )

# st.map(map_data)

if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
        np.random.rand(20,3), 
        columns=['a','b','c']
    )
    df1

option = st.sidebar.selectbox(
    'Which number do you like the best"',
    df['first column:'])

'You selected: ', option

left_column, right_column = st.columns(2)
pressed = left_column.button('Press me?')
if pressed:
  right_column.write("Woohoo!")

expander = st.expander("FAQ")
expander.write("Here you could put in some really, really long explanations...")

'Starting a long computation...'

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
  # Update the progress bar with each iteration.
  latest_iteration.text(f'Iteration {i+1}')
  bar.progress(i + 1)
  time.sleep(0.1)

'...and now we\'re done!'
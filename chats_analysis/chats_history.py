# Streamlit Timeline Component Example

import os, sys, subprocess
import streamlit as st
from streamlit_timeline import timeline
import subprocess
from datetime import datetime

# get current data and time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# use full page width
st.set_page_config(page_title="Timeline Example", layout="wide")

# hide manul and footnote
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

# refresh
if st.button('refesh'):
     st.write(current_time)
     subprocess.run(["bash", "History_chats.sh"])

# load data
charts_result_name = os.path.abspath('chats_result.json')
with open(charts_result_name, "r",encoding='utf-8') as f:
    data = f.read()

# render timeline
timeline(data, height=800)
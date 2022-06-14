# Streamlit Timeline Component Example

import os
import streamlit as st
from streamlit_timeline import timeline


# use full page width
st.set_page_config(page_title="Timeline Example", layout="wide")

# load data
charts_result_name = os.path.abspath('chats_result.json')
with open(charts_result_name, "r",encoding='utf-8') as f:
    data = f.read()

# render timeline
timeline(data, height=800)
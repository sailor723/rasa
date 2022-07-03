import streamlit as st

import pandas as pd
import numpy as np
import pymysql, json, os,re
from datetime import datetime
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, FactorRange
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral5


chat_full_name  = os.path.join(os.getcwd(),'chats_df.csv')


#----------------------------------------------read sql to df----------------------------------------------------------------------------#
# @st.cache
def read_csv_to_df(csv_file_name,sep):

    df = pd.read_csv(csv_file_name,sep=sep)

    if 'user_time' in df.columns:
        df['user_time'] = pd.to_datetime(df['user_time'])

    return (df)


df = read_csv_to_df(chat_full_name,',')

select_col_target = ['message_id','text','site_id','site_name', 'sender_name','csp_item', 'section_item', 'qa_item', 'non_answer','user_time']
select_col = [item for item in df.columns if item in select_col_target]
if 'non_answer' in select_col:  
        non_answer_col = ['message_id','user_time','sender_name', 'text', 'non_answer']
else:
        non_answer_col = []

df= df[select_col]
df = df.drop_duplicates()

df['short'] = [int(re.compile(r'\d+').findall(item)[0]) for item in df['csp_item'].fillna('0')]

inclusion_items = [('入选标准第' + str(i) +  '条') for i in range (1,18)]
exclusion_items = [('排除标准第' + str(i) +  '条') for i in range (1,26)]

base_series = pd.Series([0] * 17, list(range(1,18)))

# exclusion_order = [('第' + str(i) +  '条') for i in range (1,26)]

# filter inclusion csp
  

df_inclusion = df[df['csp_item'].isin(inclusion_items)]
df_inclusion.drop_duplicates()
df_inclusion.loc[1,'sender_name'] = 'weiping'




 senders  = list(df_inclusion.sender_name.unique())
 sections = list(df_inclusion.section_item.unique())

x = [ (section, sender) for section in sections for sender in senders ]

data = df_inclusion.groupby(['section_item'])['sender_name'].value_counts()

data = {}
data['sections'] = sections


# pattern = re.compile(r'\d+') 

# inclusion_order = [int(pattern.findall(item)[0]) for item in df_inclusion['csp_item']]

# inclusion_order.sort()

item_series = df_inclusion['short'].value_counts()
item_series = item_series.sort_index()

combine_series = (base_series + item_series).fillna(0).astype(int)
#


factors = [
    ("知情同意", "1"), ("知情同意", "2"), ("知情同意", "3"),
    ("年龄", "4"), ("受试者类型和疾病特征", "5"), ("受试者类型和疾病特征", "6"), ("受试者类型和疾病特征", "7"), ("受试者类型和疾病特征", "8"),
    ("受试者类型和疾病特征", "9"), ("受试者类型和疾病特征", "10"), ("受试者类型和疾病特征", "11"), ("受试者类型和疾病特征", "12"),
     ("受试者类型和疾病特征", "13"), ("受试者类型和疾病特征", "14"),
    ("生殖方面", "15"),("生殖方面", "16"),("生殖方面", "17")

]

regions = ['CSP']

source = ColumnDataSource(data=dict(
    x=factors,
    CSP=list(combine_series),
    
))

# index_cmap = factor_cmap('cyl_mfr', palette=Spectral5, factors=sorted(df.sender_name.unique()), end=1)

p = figure(x_range=FactorRange(*factors), height=250,
           toolbar_location=None, tools="")

p.vbar_stack(regions, x='x', width=0.9, alpha=0.5, color=["blue"], source=source,
             legend_label=regions)

p.y_range.start = 0
p.y_range.end = 18
p.x_range.range_padding = 0.1
p.xaxis.major_label_orientation = 1
p.xgrid.grid_line_color = None
p.legend.location = "top_center"
p.legend.orientation = "horizontal"

st.bokeh_chart(p, use_container_width=True)
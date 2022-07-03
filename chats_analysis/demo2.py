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

def get_num(item):
    
    result = re.compile(r'\d+').findall(item)[0]
    if len(result) <= 1:
        result = item[:2] + '0' + result
    else:
        result = item[:2] +  result
    return(result)


df = read_csv_to_df(chat_full_name,',')

select_col_target = ['message_id','text','site_id','site_name', 'sender_name','csp_item', 'section_item', 'qa_item', 'non_answer','user_time']
select_col = [item for item in df.columns if item in select_col_target]
if 'non_answer' in select_col:  
        non_answer_col = ['message_id','user_time','sender_name', 'text', 'non_answer']
else:
        non_answer_col = []

df= df[select_col]
df = df.drop_duplicates()

inclusion_items = [('入选标准第' + str(i) +  '条') for i in range (1,18)]
exclusion_items = [('排除标准第' + str(i) +  '条') for i in range (1,26)]

df_inclusion = df[df['csp_item'].isin(inclusion_items)].copy()
df_inclusion.drop_duplicates()

list1 = [get_num(string) for string in df_inclusion['csp_item']]
df_inclusion['csp_item'] = list1


df_inclusion.loc[13,'site_name'] = '广东省人民医院'

group = df_inclusion.groupby(['site_name','section_item','csp_item'])


# df_inclusion.pivot_table(index=['section', 'csp_item'], columns=['sender'], values=['sender'])

index_cmap = factor_cmap('site_name_section_item_csp_item', palette=Spectral5, factors=sorted(df_inclusion.site_name.unique()), end=1)


p = figure(width=800, height=300, title="Inclusion by CSP and Q&A Log",x_range=group,
            toolbar_location=None, tooltips=[("count", "@site_id_count"), ("section, csp,site_name", "@section_item_csp_item_site_name")])


p.vbar(x='site_name_section_item_csp_item', top='site_id_count', width=1, source=group,
       line_color="white", fill_color=index_cmap, )

p.y_range.start = 0
p.x_range.range_padding = 0.05
p.xgrid.grid_line_color = None
p.xaxis.axis_label = "CSP Inqury by SManufacturer grouped by # Cylinders"
p.xaxis.major_label_orientation = 1.2
p.outline_line_color = None

st.bokeh_chart(p, use_container_width=True)
from email import header
import streamlit as st
import pandas as pd
import numpy as np
import os, json, csv, sys, subprocess
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# from sqlalchemy import create_engine

st.set_page_config(page_title='SWAST - Handover Delays',  layout='wide', page_icon=':ambulance:')

t1, t2 = st.columns((0.07,1)) 

t1.image('az_log.jpg', width = 80)
t2.title("Digital Clinical Trial Assistant  - Conversational Report")

t2.markdown(" **tel:** +86 21 6030 2288 **| website:** https://www.astrazeneca.com.cn/zh/ **| email:** mailto:data.science@swast.nhs.uk")

# get current data and time
now = datetime.now()
current_time = now.strftime("%H:%M:%S")

# hide manu and footer
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
     subprocess.run(["bash", "BI_dashboard.sh"])

# setting
# SUB_COL= ['sub_entity', 'sub_confidence_entity', 'sub_value', 'sub_extractor', 'sub_processors']

# entities_file_name  = os.path.join(os.getcwd(),'sub.txt')
# f = open(entities_file_name, "r",encoding='utf-8-sig')
# ENTITIES_LIST = list(set(f.read().split('\n')))

# DCTA_MYSQL_USER = os.getenv('DCTA_MYSQL_USER')
# DCTA_MYSQL_PWD = os.getenv('DCTA_MYSQL_PWD')
# DCTA_MYSQL_HOST = os.getenv('DCTA_MYSQL_HOST')
# DCTA_MYSQL_PORT  = os.getenv('DCTA_MYSQL_PORT')
# DCTA_MYSQL_DB  = os.getenv('DCTA_MYSQL_DB')
# DCTA_MYSQL_TABLE  = os.getenv('DCTA_MYSQL_TABLE')

# mysql_string = 'mysql+pymysql://'+ DCTA_MYSQL_USER + ':'+ DCTA_MYSQL_PWD + '@' + DCTA_MYSQL_HOST \
#             + ":" + str(DCTA_MYSQL_PORT) + '/' + DCTA_MYSQL_DB

# data
chatlog_file_name  = os.path.join(os.getcwd(),'chats_log.csv')
chat_full_name  = os.path.join(os.getcwd(),'chats_df.csv')

#----------------------------------------------read sql to df----------------------------------------------------------------------------#
# @st.cache
def read_csv_to_df():

#----------------------- read data and prepare data -----------------------------------#
    # engine = create_engine(mysql_string)
    df = pd.read_csv(chat_full_name)

    return (df)

df = read_csv_to_df()

select_col = ['message_id','text', 'sender_name','csp_item', 'qa_item', 'non_answer','user_time']
non_answer_col = ['message_id','user_time','sender_name', 'text', 'non_answer']
df= df[select_col]
df['qa_item'] = df['qa_item'].fillna('CSP')
df['sender_name'] = df['sender_name'].fillna(' ')


inclusion_order = [('入选标准第' + str(i) +  '条') for i in range (1,18)]
exclusion_order = [('排除标准第' + str(i) +  '条') for i in range (1,26)]


df_inclusion = df.loc[df['csp_item'].isin(inclusion_order)]
df_inclusion.drop_duplicates()

df_exclusion = df.loc[df['csp_item'].isin(exclusion_order)]
df_exclusion.drop_duplicates()

df_inclusion['csp_item_short'] = [item[4:] for item in df_inclusion['csp_item']]
df_exclusion['csp_item_short'] = [item[4:] for item in df_exclusion['csp_item']]

df_qa = df[df['qa_item'] == 'Q&A']
df_qa['csp_item_short'] = [item[4:] for item in df_qa['csp_item']]

df_non_answer = df[df['non_answer'].notnull()][non_answer_col]
df_non_answer['user_time'] = [time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp)) for timestamp in df_non_answer.user_time.to_list()]

#----------------------------Streamlit plot-------------------------------------------------#

g1, g2, g3 = st.columns((2.2,3,1.2))

#--------------------inclusion ----------------------------------
fig = px.histogram(df_inclusion, x = 'csp_item_short', template = 'seaborn',color = "sender_name")

# fig.update_traces(marker_color='#264653')

fig.update_layout(title_text="Inclusion",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

g1.plotly_chart(fig, use_container_width=True) 

#------------------exclusion-------------------------
fig = px.histogram(df_exclusion, x = 'csp_item_short', template = 'seaborn',color = "sender_name")

# fig.update_traces(marker_color='#264653')

fig.update_layout(title_text="Excluion",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

g2.plotly_chart(fig, use_container_width=True) 

#------------------qa-------------------------
fig = px.histogram(df_qa, x = 'csp_item_short', template = 'seaborn',color = "sender_name")

# fig.update_traces(marker_color='#264653')

fig.update_layout(title_text="Q&A Log",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

g3.plotly_chart(fig, use_container_width=True) 
#-------------------------------preparetion ------------------------------------------------#


fig = go.Figure(data=go.Table(
    columnwidth = [2,1,1,1],
    header = dict(values=df_non_answer.columns.to_list(), 
            line_color='darkslategray',
            fill_color='lightskyblue',
            font=dict(color='black', size=11),
            align=['left','center'],), 
    cells = dict(values=[df_non_answer.message_id, df_non_answer.user_time, df_non_answer.sender_name, df_non_answer.text, df_non_answer.non_answer],
            line_color='darkslategray',
            fill_color='lightcyan',
            font=dict(color='black', size=11),
            align=['left', 'center'],
    )))
    
fig.update_layout(margin=dict(l=5, r=5, b=5, t=5))
        # paper_bgcolor = background_color)
st.write(fig)


#---------------------------Question distribution -----------------------------------
#     with col1:
#         st.subheader('Inclusion')
       
#         fig = px.bar(df_inclusion, x = 'csp_item' ,color = "qa_item", category_orders=dict(csp_item=inclusion_order),     \
#                        template = 'seaborn', color_continuous_scale=px.colors.diverging.Temps)

#         st.plotly_chart(fig,  use_container_width=True)

#         # Question_distribution = pd.DataFrame(df_final_single_message_id['text'].value_counts()).head(30)
#         # Question_distribution.reset_index(inplace=True)
#         # Question_distribution.columns = ['Question', 'Number']
        
#         # fig = go.Figure(data=go.Table(
#         #     columnwidth = [7,1],
#         #     header = dict(values=Question_distribution.columns.to_list(), 
#         #             line_color='darkslategray',
#         #             fill_color='lightskyblue',
#         #             font=dict(color='black', size=11),
#         #             align=['left','center'],), 
#         #     cells = dict(values=[Question_distribution.Question, Question_distribution.Number],
#         #             line_color='darkslategray',
#         #             fill_color='lightcyan',
#         #             font=dict(color='black', size=11),
#         #             align=['left', 'center'],
#         #     )))
            
#         # fig.update_layout(margin=dict(l=5, r=5, b=5, t=5),
#         #         paper_bgcolor = background_color)
#         # st.write(fig)
            
# #--------------------------- for Q&A log -------------------------------------------------@
# #     with col2:

# #         st.subheader('Q&A Log Inquiry')
    
# #         entity_question_df = pd.DataFrame(df_final[df_final['clean_text'].isin(question_button_list)]['clean_text'].value_counts()).head(30)
# #         entity_question_df.reset_index(inplace=True)
# #         entity_question_df.columns = ['Question', 'Number']
    
# #         fig = go.Figure(data=go.Table(
# #             columnwidth = [7,1],
# #             header = dict(values=entity_question_df.columns, 
# #                     line_color='darkslategray',
# #                     fill_color='lightskyblue',
# #                     font=dict(color='black', size=11),  
# #                     align=['left','center'],), 
# #             cells = dict(values=[entity_question_df.Question, entity_question_df.Number],
# #                     line_color='darkslategray',
# #                     fill_color='lightcyan',
# #                     font=dict(color='black', size=11),
# #                     align=['left', 'center'],
# #             )))
            
# #         fig.update_layout(margin=dict(l=5, r=5, b=5, t=5),
# #                 paper_bgcolor = background_color)
# #         st.write(fig)
# #     #---------------------------entity distribution -------------------------------------------------------------------#

# #     st.subheader('Entity Distribution')

# #     entity_chat_list = [x for x in df_final['text'] if 'inform' not in x ]
# #     button_list  = [x.split('{}')[0].split('\"')[3] for x in df_final['text'] if 'inform' in x ]
# #     entity_button_list = [ item for item in button_list if item in ENTITIES_LIST]
# #     # df_final['entity_button'] = entity_button_list
# #     question_button_list = [ item for item in button_list if item not in ENTITIES_LIST]

# #     entity_chat_list = list(set(entity_chat_list))
# #     button_list = list(set(button_list))
# #     entity_button_list = list(set(entity_button_list))
# #     question_button_list = list(set(question_button_list))

# # #--------------------------------------plotting -----------------------------------------------------------------------#

# #     entity_chat_df = pd.DataFrame(df_final_single_message_id[df_final_single_message_id['text'].isin(entity_chat_list)])
    
# #     fig = px.histogram(entity_chat_df, x="text").update_xaxes(categoryorder='total descending')

# #     st.plotly_chart(fig,  use_container_width=True)

# #     # ---------------------------intent  distribution -----------------------------------
# #     col3, col4 = st.columns(2)
# #     with col3:
# #         st.subheader('Intent Confidence Average')
# #         target_list = [ 'inform_protocol', 'affirm', 'out_of_scpe', 'deny', 'thanks', 'bot_challenge', 'goodbye', 'nlu_fallback']
# #         final_list = [col for col in target_list if col in df_final.columns]
# #         intent_distribution = pd.DataFrame(df_final[final_list].mean().sort_values(ascending=False))
# #         fig = px.bar(intent_distribution,  height=800, width=800)
# #         st.plotly_chart(fig, use_container_width=True)

# #         # ----------------------------extractor  distribution ----------------------------------- 
# #         st.subheader('Extractor Distribution')
# #         extractor_distribution = pd.DataFrame(df_final['sub_extractor'].value_counts())
# #         fig = px.bar(extractor_distribution,  height=800, width=800)
# #         st.plotly_chart(fig, use_container_width=True)

# #     # ----------------------------No anwwer  distribution ----------------------------------- 

# #     with col4:
# #         st.subheader('No Answer Question')
# #         no_answer_question = pd.DataFrame(df_final[df_final['action'] == 'no answer question']['text'])
        
# #         no_answer_question.reset_index(inplace=True)
# #         no_answer_question.columns = ['Message_id', 'Question']
            
# #         fig = go.Figure(data=go.Table(
# #             columnwidth = [1,2],
# #             header = dict(values=no_answer_question.columns.to_list(), 
# #                     line_color='darkslategray',
# #                     fill_color='lightskyblue',
# #                     font=dict(color='black', size=11),
# #                     align=['left','center'],), 
# #             cells = dict(values=[no_answer_question.Message_id, no_answer_question.Question],
# #                     line_color='darkslategray',
# #                     fill_color='lightcyan',
# #                     font=dict(color='black', size=11),
# #                     align=['left', 'center'],
# #             )))
            
# #         fig.update_layout(margin=dict(l=5, r=5, b=5, t=5),
# #                 paper_bgcolor = background_color)
# #         st.write(fig)

# #     #----------------------------------------- shwo site id and sender name ------------------------------------------------------------#

# #     # entity_chat_df = pd.DataFrame(df_final[df_final['text'].isin(entity_chat_list)])
    
# #     fig = px.histogram(df_final, x="site_id")

# #     st.plotly_chart(fig)


from email import header
import streamlit as st
import pandas as pd
import numpy as np
import os, json, csv
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
# from sqlalchemy import create_engine

SUB_COL= ['sub_entity', 'sub_confidence_entity', 'sub_value', 'sub_extractor', 'sub_processors']

entities_file_name  = os.path.join(os.getcwd(),'sub.txt')
f = open(entities_file_name, "r",encoding='utf-8-sig')
ENTITIES_LIST = list(set(f.read().split('\n')))

# DCTA_MYSQL_USER = os.getenv('DCTA_MYSQL_USER')
# DCTA_MYSQL_PWD = os.getenv('DCTA_MYSQL_PWD')
# DCTA_MYSQL_HOST = os.getenv('DCTA_MYSQL_HOST')
# DCTA_MYSQL_PORT  = os.getenv('DCTA_MYSQL_PORT')
# DCTA_MYSQL_DB  = os.getenv('DCTA_MYSQL_DB')
# DCTA_MYSQL_TABLE  = os.getenv('DCTA_MYSQL_TABLE')

# mysql_string = 'mysql+pymysql://'+ DCTA_MYSQL_USER + ':'+ DCTA_MYSQL_PWD + '@' + DCTA_MYSQL_HOST \
#             + ":" + str(DCTA_MYSQL_PORT) + '/' + DCTA_MYSQL_DB


chatlog_file_name  = os.path.join(os.getcwd(),'chats_log.csv')
chat_full_name  = os.path.join(os.getcwd(),'converted_log.csv')

st.set_page_config(
     page_title="Ex-stream-ly Cool App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

header = st.container()
dataset = st.container()
features = st.container()
log_display = st.container()

background_color = '#F5F5F5'

hide_manu_style = """
    <style>
    #mainManu {invisibility: hidden;}
    footer {invisibility: hidden;}
    </style>
"""
st.markdown(hide_manu_style, unsafe_allow_html=True)

#----------------------------------------------read sql to df----------------------------------------------------------------------------#
@st.cache
def read_csv_to_df():

#----------------------- read data and prepare data -----------------------------------#
    # engine = create_engine(mysql_string)
    df = pd.read_csv(chat_full_name)

    return (df)
#------------------------------Streamlit -----------------------------------------------#

df_final = read_csv_to_df()
df_final_single_message_id = df_final.drop_duplicates(subset='message_id')
with header:
    st.title("DL04 DCTA Analsysis")

with dataset:

    st.write("Total Number of conversation: ", len(df_final))
    # st.write(df1.head(20))

#-------------------------------preparetion ------------------------------------------------#
    entity_chat_list = [x for x in df_final['text'] if 'inform' not in x ]
    button_list  = [x.split('{}')[0].split('\"')[3] for x in df_final['text'] if 'inform' in x ]
    entity_button_list = [ item for item in button_list if item in ENTITIES_LIST]
    # df_final['entity_button'] = entity_button_list
    question_button_list = [ item for item in button_list if item not in ENTITIES_LIST]

    entity_chat_list = list(set(entity_chat_list))
    button_list = list(set(button_list))
    entity_button_list = list(set(entity_button_list))
    question_button_list = list(set(question_button_list))

    col1, col2 = st.columns(2)

#---------------------------Question distribution -----------------------------------
    with col1:
        st.subheader('All Question Distribution')
        Question_distribution = pd.DataFrame(df_final_single_message_id['text'].value_counts()).head(30)
        Question_distribution.reset_index(inplace=True)
        Question_distribution.columns = ['Question', 'Number']
        
        fig = go.Figure(data=go.Table(
            columnwidth = [7,1],
            header = dict(values=Question_distribution.columns.to_list(), 
                    line_color='darkslategray',
                    fill_color='lightskyblue',
                    font=dict(color='black', size=11),
                    align=['left','center'],), 
            cells = dict(values=[Question_distribution.Question, Question_distribution.Number],
                    line_color='darkslategray',
                    fill_color='lightcyan',
                    font=dict(color='black', size=11),
                    align=['left', 'center'],
            )))
            
        fig.update_layout(margin=dict(l=5, r=5, b=5, t=5),
                paper_bgcolor = background_color)
        st.write(fig)
            
#--------------------------- for Q&A log -------------------------------------------------@
    with col2:

        st.subheader('Q&A Log Inquiry')
    
        entity_question_df = pd.DataFrame(df_final[df_final['clean_text'].isin(question_button_list)]['clean_text'].value_counts()).head(30)
        entity_question_df.reset_index(inplace=True)
        entity_question_df.columns = ['Question', 'Number']
    
        fig = go.Figure(data=go.Table(
            columnwidth = [7,1],
            header = dict(values=entity_question_df.columns, 
                    line_color='darkslategray',
                    fill_color='lightskyblue',
                    font=dict(color='black', size=11),  
                    align=['left','center'],), 
            cells = dict(values=[entity_question_df.Question, entity_question_df.Number],
                    line_color='darkslategray',
                    fill_color='lightcyan',
                    font=dict(color='black', size=11),
                    align=['left', 'center'],
            )))
            
        fig.update_layout(margin=dict(l=5, r=5, b=5, t=5),
                paper_bgcolor = background_color)
        st.write(fig)
    #---------------------------entity distribution -------------------------------------------------------------------#

    st.subheader('Entity Distribution')

    entity_chat_list = [x for x in df_final['text'] if 'inform' not in x ]
    button_list  = [x.split('{}')[0].split('\"')[3] for x in df_final['text'] if 'inform' in x ]
    entity_button_list = [ item for item in button_list if item in ENTITIES_LIST]
    # df_final['entity_button'] = entity_button_list
    question_button_list = [ item for item in button_list if item not in ENTITIES_LIST]

    entity_chat_list = list(set(entity_chat_list))
    button_list = list(set(button_list))
    entity_button_list = list(set(entity_button_list))
    question_button_list = list(set(question_button_list))

#--------------------------------------plotting -----------------------------------------------------------------------#

    entity_chat_df = pd.DataFrame(df_final_single_message_id[df_final_single_message_id['text'].isin(entity_chat_list)])
    
    fig = px.histogram(entity_chat_df, x="text").update_xaxes(categoryorder='total descending')

    st.plotly_chart(fig,  use_container_width=True)

    # ---------------------------intent  distribution -----------------------------------
    col3, col4 = st.columns(2)
    with col3:
        st.subheader('Intent Confidence Average')
        target_list = [ 'inform_protocol', 'affirm', 'out_of_scpe', 'deny', 'thanks', 'bot_challenge', 'goodbye', 'nlu_fallback']
        final_list = [col for col in target_list if col in df_final.columns]
        intent_distribution = pd.DataFrame(df_final[final_list].mean().sort_values(ascending=False))
        fig = px.bar(intent_distribution,  height=800, width=800)
        st.plotly_chart(fig, use_container_width=True)

        # ----------------------------extractor  distribution ----------------------------------- 
        st.subheader('Extractor Distribution')
        extractor_distribution = pd.DataFrame(df_final['sub_extractor'].value_counts())
        fig = px.bar(extractor_distribution,  height=800, width=800)
        st.plotly_chart(fig, use_container_width=True)

    # ----------------------------No anwwer  distribution ----------------------------------- 

    with col4:
        st.subheader('No Answer Question')
        no_answer_question = pd.DataFrame(df_final[df_final['action'] == 'no answer question']['text'])
        
        no_answer_question.reset_index(inplace=True)
        no_answer_question.columns = ['Message_id', 'Question']
            
        fig = go.Figure(data=go.Table(
            columnwidth = [1,2],
            header = dict(values=no_answer_question.columns.to_list(), 
                    line_color='darkslategray',
                    fill_color='lightskyblue',
                    font=dict(color='black', size=11),
                    align=['left','center'],), 
            cells = dict(values=[no_answer_question.Message_id, no_answer_question.Question],
                    line_color='darkslategray',
                    fill_color='lightcyan',
                    font=dict(color='black', size=11),
                    align=['left', 'center'],
            )))
            
        fig.update_layout(margin=dict(l=5, r=5, b=5, t=5),
                paper_bgcolor = background_color)
        st.write(fig)

    #----------------------------------------- shwo site id and sender name ------------------------------------------------------------#

    # entity_chat_df = pd.DataFrame(df_final[df_final['text'].isin(entity_chat_list)])
    
    fig = px.histogram(df_final, x="site_id")

    st.plotly_chart(fig)

     #----------------------------------------- shwo chat log ------------------------------------------------------------#

    st.subheader('Chat Log File')
    file = open(chatlog_file_name,encoding="utf-8")
    csvreader = csv.reader(file)
    data_lines = list(csvreader)

    for line in data_lines[:100]:
        if line != []:
            st.write(line[0])

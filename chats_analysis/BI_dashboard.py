from email import header
import streamlit as st
import pandas as pd
import numpy as np
import requests
import os, json, csv, sys, subprocess,re
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime,timedelta
from streamlit_timeline import timeline
import time
from st_aggrid import AgGrid, GridUpdateMode, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder

from bokeh.plotting import figure, output_file, show, save
from bokeh.models import ColumnDataSource, FactorRange,LabelSet
from bokeh.transform import factor_cmap
from bokeh.palettes import Spectral5, Spectral6

# from sqlalchemy import create_engine
log_file_name  = os.path.join(os.getcwd(),'DCTA_logo.png')
st.set_page_config(page_title='DCTA BI dashboard',  layout='wide', page_icon=':chatbot:')

t1, t2 = st.columns((0.07,1)) 

t1.image(log_file_name, width = 80)
t2.title("Digital Clinical Trial Assistant  - Conversational Report")

t2.markdown(" **| email:** AsiaScience.DeskSupport@astrazeneca.com")

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

#-------------------------------------------------define functions ------------------------------------------------------
def run_and_display_stdout(*cmd_with_agrs):
    result = subprocess.Popen(cmd_with_agrs, stdout=subprocess.PIPE)
  
    for line in iter(lambda: result.stdout.readline(), b""):
        st.text(line.decode("utf-8"))

def bokeh_plot (x, counts, marker, color):

# index_cmap = factor_cmap('section_item_csp_item', palette=Spectral5, factors=section_order, end=1)
                
        counts_label = []

        for item in counts:

                if item == 0:
                        item_label = ' '
                else:
                        item_label = str(item)

                counts_label.append(item_label)
        source = ColumnDataSource(data=dict(x=x, counts=counts, counts_label=counts_label))

        p = figure(x_range=FactorRange(*x), plot_height=250, background_fill_color="#fafafa",
                toolbar_location=None, title= marker)
        p.vbar(x='x', top='counts', width=0.6, source=source, fill_color=color, line_color=None )

        p.y_range.start = 0
        p.xaxis.axis_label_text_font_size = '6px'
        p.x_range.range_padding = 0.05
        p.xgrid.grid_line_color = None
        #     p.xaxis.axis_label = "CSP Inqury by SManufacturer grouped by # Cylinders"
        p.xaxis.major_label_orientation = 1.2
        p.xgrid.grid_line_color = None
        p.ygrid.grid_line_color = None  
        p.yaxis.visible = False
        p.xaxis.axis_line_color = color
        p.outline_line_color = None

        labels = LabelSet(x='x', y='counts', text='counts_label', level='glyph',
                  x_offset=-5, y_offset=-10, source=source, render_mode='canvas',text_color='midnightblue',text_font_size = {'value': '10px'})

        p.add_layout(labels)

        st.bokeh_chart(p, use_container_width=True)
        return


# if st.button("Run"):
#     run_and_display_stdout("ls", "-Al", "/")

# fetch the site_id
try:
        site_list_get = st.experimental_get_query_params()
        site_list_get = {k: v[0] if isinstance(v, list) else v for k, v in site_list_get.items()} # fetch the first item in each query string as we don't have multiple values for each query string key in this example
        site_list_get = site_list_get['siteid'].split(',')
# # st.write('fetched site_id:', site_list_get)
except :        
        site_list_get = ['999']
        st.write('collect site_id error, use default admin')

        
#  refresh
if site_list_get == ['999']:
        if st.button('Refesh'):
                st.write(current_time)
                #      run_and_display_stdout("bash", "BI_dashboard.sh")
                subprocess.run(["bash", "BI_dashboard.sh"])


chatlog_file_name  = os.path.join(os.getcwd(),'chats_log.csv')
chat_full_name  = os.path.join(os.getcwd(),'chats_df.csv')


#----------------------------------------------read sql to df----------------------------------------------------------------------------#
@st.cache
def read_csv_to_df(csv_file_name,sep):

    df = pd.read_csv(csv_file_name,sep=sep)

    if 'user_time' in df.columns:
        df['user_time'] = pd.to_datetime(df['user_time'])

    return (df)

@st.cache
def convert_df(df):
     # IMPORTANT: Cache the conversion to prevent computation on every rerun
     return df.to_csv().encode('utf_8_sig')
df = read_csv_to_df(chat_full_name,',').copy()

log_csv = read_csv_to_df(chatlog_file_name,'&&')
log_csv = convert_df(log_csv)


#-----------------------------function start_date_json-------- ----------------------------------------------------------------#

def start_date_json (time_dict):
    string = time_dict['year'] +'-' + time_dict['month'] +'-' + time_dict['day']  +' ' + time_dict['hour']      \
        +':' + time_dict['minute'] +':' + time_dict['second'] 

    return (datetime.strptime(string, "%Y-%m-%d %H:%M:%S"))


# --------------------------------- data preperation --------------------------------------------------------------------------#

select_col_target = ['message_id','text','site_id','site_name', 'sender_name','csp_item',               \
                'section_item', 'qa_item', 'non_answer','user_time', 'feedback']
select_col = [item for item in df.columns if item in select_col_target]
if 'non_answer' in select_col:  
        non_answer_col = ['message_id','user_time','sender_name', 'text', 'non_answer']
else:
        non_answer_col = []

df= df[select_col]
df = df.drop_duplicates()
df['count'] = 1


df['sender_name'] = df['sender_name'].fillna(' ')
df['site_name'] = df['site_name'].fillna('测试中心')
df['site_id'] = [str(int(float((item)))) for item in df['site_id'].fillna('0')]


df.section_item.fillna('', inplace=True)
df.csp_item.fillna('', inplace=True)

df.section_item = [item for item in [item.split('%@') for item in df.section_item]]
df.csp_item = [item.split('%@') for item in df.csp_item]

df = df.explode(['section_item','csp_item'])

if 'qa_item' in select_col:
        df['qa_item'] = df['qa_item'].fillna('CSP')


# -------------------------header selectbox for report -------------------------------------------#

with st.spinner('Updating Report...'):
                
        #Metrics setting and rendering
        if site_list_get == ['999']:
                list_options = df['site_name'].unique()
        else:
                list_options = list(df[df['site_id'].isin(site_list_get)]['site_name'].unique())
        
        site_list_selected = st.multiselect('Sites Selection', list_options, default = list_options,
                help = 'Filter report to show selected sites')

        # st.write('selected_site:', site_list_selected)

        df_selected = df[df['site_name'].isin(site_list_selected)]

        start_time = pd.Timestamp(df_selected['user_time'].min()) - timedelta(hours=1)
        end_time = pd.Timestamp(df_selected['user_time'].max()) + timedelta(hours=1)

        inclusion_items = [('入选标准第' + str(i) +  '条') for i in range (1,18)]
        exclusion_items = [('排除标准第' + str(i) +  '条') for i in range (1,26)]

        inclusion_order = [('第' + str(i) +  '条') for i in range (1,18)]
        exclusion_order = [('第' + str(i) +  '条') for i in range (1,26)]

        range_list = pd.date_range(start_time,end_time,freq='H')
        start_date, end_date = st.select_slider(
                        'Select a range of date',
                        options=range_list,
                        value=(range_list[0], range_list[-1]))

  
        df_selected = df_selected[(df_selected.user_time >= start_date) & (df_selected.user_time <= end_date)]

        df_inclusion = df_selected[df_selected['csp_item'].isin(inclusion_items)]
        df_inclusion.drop_duplicates()

        df_exclusion = df_selected[df_selected['csp_item'].isin(exclusion_items)]
        df_exclusion.drop_duplicates()


        df_inclusion['csp_item_short'] = [item[4:] for item in df_inclusion['csp_item']]
        df_exclusion['csp_item_short'] = [item[4:] for item in df_exclusion['csp_item']]

        inclusion_order = [item for item in inclusion_order if item in df_inclusion['csp_item_short'].unique()]
        exclusion_order = [item for item in exclusion_order if item in df_exclusion['csp_item_short'].unique()]


        if 'qa_item' in df_selected.columns:

                df_qa = df_selected[df_selected['qa_item'] == 'Q&A']
                df_qa['csp_item_short'] = [item[4:] for item in df_qa['csp_item']]
        else:
                df_qa = []

        if 'non_answer' in df_selected.columns:
                df_non_answer = df_selected[df_selected['non_answer'].notnull()][non_answer_col]
                # df_non_answer['user_time'] = [time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(timestamp)) for timestamp in df_non_answer.user_time.to_list()]
        else:
                df_non_answer = []
        
        with open('style.css') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

        m1, m2, m3, m4, m5,m6 = st.columns((1,1,1,1,1,1))
        
        m1.metric(label ='Total Conversations',value = df_selected.message_id.nunique())
        m2.metric(label ='Number of PIs',value = df_selected['sender_name'].nunique())
        m3.metric(label ='Inclusion Inquiry',value = len(df_inclusion))
        m4.metric(label ='Exclusion Inquiry',value = len(df_exclusion))
        m5.metric(label ='Q&A Log',value = len(df_qa))
        m6.metric(label ='Non Answers #',value = len(df_non_answer))


with st.spinner('Sites Selected!'):
        time.sleep(1)    
#----------------------------Streamlit plot-------------------------------------------------#


#--------------------inclusion ----------------------------------

        
section_order =  ['知情同意','年龄','受试者类型和疾病特征','生殖方面' ]

# reorder section item
df_inclusion['csp_item'] = pd.Categorical(df_inclusion['csp_item'], inclusion_items )
df_inclusion = df_inclusion.sort_values('csp_item')
df_inclusion.reset_index(drop=True,inplace=True)

df_exclusion['csp_item'] = pd.Categorical(df_exclusion['csp_item'], exclusion_items )
df_exclusion = df_exclusion.sort_values('csp_item')
df_exclusion.reset_index(drop=True,inplace=True)

# get x and factor for plotting 
df_group_inclusion = df_inclusion.groupby('csp_item').count()
df_group_exclusion = df_exclusion.groupby('csp_item').count()
count_inclusion = df_group_inclusion['count'].to_list()
count_exclusion = df_group_exclusion['count'].to_list()
x_inclusion = []
x_exclusion = []
color_inclusion= []
color_exclusion = []

for item in df_group_inclusion.index.to_list():
       
    number = int(re.compile(r'\d+').findall(item)[0])

    if number in range(1,4):
        section = '\n知情同意'
    elif number == 4:
        section = '\n年龄'
    elif number in range(5,15):
        section = '\n受试者类型和疾病特征'
    elif number in range(15, 18):
        section = '\n生殖方面'
    x_inclusion.append((section, item[4:]))
    color_inclusion.append(section)
    

for item in df_group_exclusion.index.to_list():
       
    number = int(re.compile(r'\d+').findall(item)[0])

    if number in range(1,16):
        section = '\n医学疾病'
    elif number in range(16,19):
        section = '既往治疗\n合并治疗'
    elif number in range(19,23):
        section = '既往/合并用药\n临床研究经验'
    elif number in range(23, 27):
        section = '\n其他排除标准'
    x_exclusion.append((section, item[4:]))
    color_exclusion.append(section)

    
c1, c2 = st.columns((2,3))
with c1:
        bokeh_plot(x_inclusion,count_inclusion,'Inclusion','lightsteelblue')

with c2:
        bokeh_plot(x_exclusion,count_exclusion,'Exclusion','peachpuff')

# fig = px.histogram(df_inclusion, x = 'csp_item_short',  
#                   category_orders = dict(csp_item_short=inclusion_order),
#                   template = 'seaborn',
# #                   color = "sender_name")

# # fig.update_traces(marker_color='#264653')

# fig.update_layout(title_text="Inclusion",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

# g1.plotly_chart(fig, use_container_width=True) 


#------------------exclusion-------------------------
# fig = px.histogram(df_exclusion, x = 'csp_item_short', 
#                    category_orders = dict(csp_item_short=exclusion_order),
#                    template = 'seaborn',
#                    color = "sender_name")

# # fig.update_traces(marker_color='#264653')

# fig.update_layout(title_text="Exclusion",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

# g2.plotly_chart(fig, use_container_width=True) 

#------------------qa-------------------------
# if len(df_qa) > 0:
#         fig = px.histogram(df_qa, x = 'csp_item_short', template = 'seaborn',color = "sender_name")

#         # fig.update_traces(marker_color='#264653')

#         fig.update_layout(title_text="Q&A Log",title_x=0,margin= dict(l=0,r=10,b=10,t=30), yaxis_title=None, xaxis_title=None)

#         g3.plotly_chart(fig, use_container_width=True) 
#-------------------------------preparetion ------------------------------------------------#
gd = GridOptionsBuilder.from_dataframe(df_non_answer)
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=False, grouptable = True)

with st.expander("Non Answered Questions", expanded=False):
        if len(df_non_answer):
                st.markdown("**Total Now Answer :" + str(len(df_non_answer))+"**")
                sel_mode = st.radio("Selection Type", options = ['single', 'multiple'])
                gd.configure_selection(selection_mode = sel_mode, use_checkbox=True)
                gridoptions = gd.build()
                grid_table = AgGrid(df_non_answer, gridOptions=gridoptions, 
                                update_mode = GridUpdateMode.SELECTION_CHANGED,
                                height = 500, 
                                allow_upsafe_jscode=True,
                                theme = "fresh")

                st.write('Details')
                sel_row = grid_table["selected_rows"]
                st.write(sel_row)
        else:
                st.markdown("**Total Now Answer :" + '0' +"**")

        # fig = go.Figure(data=go.Table(
        # columnwidth = [2,1,1,8,1],
        # header = dict(values=df_non_answer.columns.to_list(), 
        #         line_color='darkslategray',
        #         fill_color='lightskyblue',
        #         font=dict(color='black', size=11),
        #         align=['left','center'],), 
        # cells = dict(values=[df_non_answer.message_id, df_non_answer.user_time, df_non_answer.sender_name, df_non_answer.text, df_non_answer.non_answer],
        #         line_color='darkslategray',
        #         fill_color='lightcyan',
        #         font=dict(color='black', size=11),
        #         align=['left'],
        # )))
        
        # fig.update_layout(width=1200, height=800, margin=dict(l=5, r=5, b=5, t=5))
        #         # paper_bgcolor = background_color)
        # st.write(fig)



#-------------------------------preparetion ------------------------------------------------#


with st.expander("Conversation History", expanded=False):
        # load data
        charts_result_name = os.path.abspath('chats_result.json')
        with open(charts_result_name, "r",encoding='utf-8') as f:
                time_data = f.read()

        new_json = json.loads(time_data)

        new_json['events'] = [item for item in new_json['events']  if (item['text']['headline'].split('<br>')[0] in df_selected['site_name'].unique())   \
                        and (start_date_json(item['start_date']) >= start_date )
                        and (start_date_json(item['start_date']) <= end_date) 
                        ]
        st.write('Total History Inquired: ', len(new_json['events']))
        # render timeline
        timeline(new_json, height=800)

#-------------------------------preparetion ------------------------------------------------#
gd = GridOptionsBuilder.from_dataframe(df)
gd.configure_pagination(enabled=True)
gd.configure_default_column(editable=False, grouptable = True)

with st.expander("Full Dataset View", expanded=False):
        st.markdown("**Total Conversations :" + str(df_selected.message_id.nunique()) + "\t Full Extraction :" + str(len(df_selected)) + "**")
        sel_mode_full = st.radio("Selection Type", options = ['single', 'multiple'],key='full')
        gd.configure_selection(selection_mode = sel_mode_full, use_checkbox=True)
        gridoptions = gd.build()
        grid_table = AgGrid(df_selected, gridOptions=gridoptions, 
                        update_mode = GridUpdateMode.SELECTION_CHANGED,
                        height = 500, 
                        allow_upsafe_jscode=True,
                        theme = "fresh")

        st.write('Details')
        sel_row = grid_table["selected_rows"]
        st.write(sel_row)

st.download_button(
label="Log File Download",
data=log_csv,
file_name='DCTA_conversational.csv',
mime='text/csv',
)

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


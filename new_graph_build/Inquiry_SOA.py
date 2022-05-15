from email import header
import streamlit as st
import pandas as pd
import pdfplumber
import numpy as np
import os, json
import plotly.figure_factory as ff
import plotly.express as px

header = st.container()
dataset = st.container()
features = st.container()
log_display = st.container()

#---------------------------read SOA to DF-----------------------------------------------------------------------


SOA_file_name  = os.path.abspath('SOA.pdf')

# df.to_csv(full_chats_csv_name,encoding='utf-8-sig')

pdf = pdfplumber.open('SOA.pdf')

new_columns = ['访视活动','筛选','治疗干预期1','治疗干预期2','治疗干预期3','治疗干预期4','治疗干预期5','治疗干预期6','治疗干预后期','随访期1','随访期2','详细信息参见以下章节']

## first df 
p0 = pdf.pages[0]
table = p0.extract_table()
df = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df.columns = new_columns
df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6', '治疗干预后期', '随访期1', '随访期2']
df.loc[12][df_col] = df.loc[12]['治疗干预期1']

# page[1]
p0 = pdf.pages[1]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = new_columns
df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6', '治疗干预后期', '随访期1']
for line in [6,8,9,10]:
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
for line in [11]:
    df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
for line in [12]:
    df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6','治疗干预后期']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
for line in [13]:
    df_col = ['治疗干预期1','治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6','治疗干预后期','随访期1']
    df1.loc[line][df_col] = df1.loc[line,'筛选']
df1 = df1.drop([0,1,2])
df = pd.concat([df,df1],ignore_index=True)

#page[2]
p0 = pdf.pages[2]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = list(range(0,14))
df1.loc[4,11] = df1.loc[4,10]
df1 = df1.drop(columns=[7,10])
df1.columns = new_columns
for line in [3]:
    df_col = ['治疗干预期1','治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6','治疗干预后期','随访期1']
    df1.loc[line][df_col] = df1.loc[line]['筛选']
for line in [9,11,12]:
    df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6','治疗干预后期','随访期1']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
for line in [13]:
    df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5',
       '治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
df1 = df1.drop([0,1,2])
df = pd.concat([df,df1],ignore_index=True)


#page[3]
p0 = pdf.pages[3]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = new_columns
df1.loc[4]['访视活动'] = df1.loc[4]['访视活动'] + df1.loc[5]['访视活动']
df1.loc[6]['访视活动'] = df1.loc[6]['访视活动'] + df1.loc[7]['访视活动']
for line in [9]:
    df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
df1 = df1.drop([0,1,2,5,7])
df = pd.concat([df,df1],ignore_index=True)


#page[4]
p0 = pdf.pages[4]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = new_columns

for line in [9]:
    df_col = ['治疗干预期2', '治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期1']
df1 = df1.drop([0,1,2])
df = pd.concat([df,df1],ignore_index=True)


#page[5]
p0 = pdf.pages[5]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = new_columns

for line in [6,7,8,9,11]:
    df_col = ['治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期2']
df1 = df1.drop([0,1,2])
df = pd.concat([df,df1],ignore_index=True)

#page[6]
p0 = pdf.pages[6]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = new_columns

for line in [3]:
    df_col = ['治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期2']
    
for line in [8]:
    df_col = ['治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6','治疗干预后期','随访期1','随访期2']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期2']
df1 = df1.drop([0,1,2])
df = pd.concat([df,df1],ignore_index=True)

# last df
p0 = pdf.pages[7]
table = p0.extract_table()
df1 = pd.DataFrame(table[1:], columns=table[0]).fillna("Section")
df1.columns = new_columns

for line in [3,4]:
    df_col = ['治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6']
    df1.loc[line][df_col] = df1.loc[line,'治疗干预期2']
    

for line in [6]:
    df_col = ['治疗干预期1','治疗干预期2','治疗干预期3', '治疗干预期4', '治疗干预期5','治疗干预期6','治疗干预后期','随访期1']
    df1.loc[line][df_col] = df1.loc[line,'筛选']
    
df1 = df1.drop([0,1,2])
df = pd.concat([df,df1],ignore_index=True)



#-------------------set section and 访视活动, df multi-index---------------------------------------------------
df['Section'] = 'Section'
section_working  = ''
for row, col in df.iterrows():
    if (len(set( col[1:])) == 1) and (list(set(col[1:]))[0] == 'Section'):
        section_working = col['访视活动']
        col['Section'] = section_working


    else: 
        col['Section'] = section_working


df.set_index('Section', inplace=True)

# ------------data clean up, convert to None if not esist
pattern = ['', 'NA']
for row, col in df.iteritems():
    df[row] = [None if x in pattern else x for x in df[row]]

df.to_csv("SOA_1.csv",encoding='utf-8-sig')

with header:
    st.title("DL04 SOA Inquiry Test")
    st.subheader('for discussion on SOA approach')

#------------------------------Streamlit ------------------------------------------------#
col1, col2, col3 = st.columns(3)

with col1:
    section_list = list(set(list(df.index)))
    section_list.sort(key=list(df.index).index)
    section = st.selectbox(
     'Please select main setion',
     [_ for _ in section_list])

st.write('You selected:', section)

with col3:
    visit_section = st.selectbox(
     'Please select visit activity',
     [_ for _ in list(list(df.columns[1:]))])

    st.write('You selected:', visit_section)

# with col3:
#     st.header("An owl")
#     st.image("https://static.streamlit.io/examples/owl.jpg")



st.table(df.loc[section][['访视活动', visit_section,'详细信息参见以下章节']].dropna()[1:])

st.table(df)


# option = st.selectbox(
#      'How would you like to be contacted?',
#      [_ for _ in df.columns[1:]])

# st.write('You selected:', option)

# st.table(df[['area', option]].dropna())

# st.table(df)
     #-----------------------Prepare and output Data for log_show ------------------------------------

   
# with st.sidebar:
#     st.title("Conversation logs")

#     list1 = []
#     chats_data = ''
#     msg = ''
#     num = 0
#     # print('-'* 60)
#     for j in df.data:
#         a = json.loads(j)
#         if msg != '' and a['event'] == 'user':
#             # print('-'* 120)
#             chats_data += '\n'+ ('-'* 120)
            
#         if a['event'] == 'user':
#             # print('user_intent:', a['parse_data']['intent']['name'], a['parse_data']['intent']['confidence'])
#             chats_data += '\n'+ 'user_intent:' + str(a['parse_data']['intent']['name']) + str(a['parse_data']['intent']['confidence'])
#             num = num + 1
            
#         if a['event'] == 'bot':
#             # print('BOT: ', a['text'])
#             chats_data +=  '\n'+'BOT: ' + str(a['text'])
            
#         if a['event'] == 'action':
#             # print(' '* 80, '|  action:', a['name'])
#             chats_data += '\n'+ 'action:' + a['name']
            
#         if a['event'] == 'slot':
#             # print(' ' * 80, '|  slot:',a['name'], a['value'])
#             chats_data +=  '\n'+'slot:' +  str(a['name']) + str(a['value'])
#         try:
#     #         print('message_id:',a['parse_data']['message_id'])
#             chats_data +=  '\n'+'message_id:' + a['parse_data']['message_id']
                
#             # print('USER:', a['parse_data']['text'])
#             chats_data +=  '\n'+'USER:'+ a['parse_data']['text']
            
#             if msg == '':
#                 msg = a['parse_data']['message_id']
#             # else:
#                 # a['parse_data']['message_id']
#             list1.append(msg)

#         except:
#             list1.append(a)
#             pass

#     with open('chats_225_1.csv','a',encoding='utf-8-sig') as file:
#         file.write(chats_data)
        
#     print('total number',num)

#    #---------------------------Show log data --------------------------------------------

#     list_working = []
#     list_final = []
#     for item in list1:
#         if type(item) != str:
#             list_working.append(item)
#         else:

#             list_final.append(list_working)
#             list_working = []
            
#     sel_col, display_col = st.columns(2)

#     range_value = sel_col.slider('Please select range of total conversation', 0, 153, (2, 4))

#     st.write('range :', range_value)

#     for item in range(range_value[0], range_value[1]):

#         st.write(list1[item])
  

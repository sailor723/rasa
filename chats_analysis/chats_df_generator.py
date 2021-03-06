#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pymysql, json, os
from sqlalchemy  import create_engine, Column, Integer, String
# import pandas_profiling

DCTA_MYSQL_USER = os.getenv('DCTA_MYSQL_USER')
DCTA_MYSQL_PWD = os.getenv('DCTA_MYSQL_PWD')
DCTA_MYSQL_HOST = os.getenv('DCTA_MYSQL_HOST')
DCTA_MYSQL_PORT  = os.getenv('DCTA_MYSQL_PORT')
DCTA_MYSQL_DB  = os.getenv('DCTA_MYSQL_DB')
DCTA_MYSQL_TABLE  = os.getenv('DCTA_MYSQL_TABLE')

mysql_string = 'mysql+pymysql://'+ DCTA_MYSQL_USER + ':'+ DCTA_MYSQL_PWD + '@' + DCTA_MYSQL_HOST \
            + ":" + str(DCTA_MYSQL_PORT) + '/' + DCTA_MYSQL_DB

# from sqlalchemy import create_engine
# engine = create_engine('mysql+pymysql://weiping:@localhost:3306/test_db')
# df = pd.read_sql('tracker1',engine)


#-------------------------------------read mysql ------------------------------------------------------------------------#
# engine = create_engine('mysql+pymysql://root:Ecc!123456@localhost:3306/test_db')

engine = create_engine(mysql_string)
df = pd.read_sql('tracker',engine)

# full_chats_csv_name = os.path.abspath('new_all.csv')
chat_full_name  = os.path.join(os.getcwd(),'converted_log.csv')

# df.to_csv(full_chats_csv_name,encoding='utf-8-sig')
# df = pd.read_csv(full_chats_csv_name,encoding='utf-8-sig')

#----------------------------------special convert from csv -----------------------------------------#

value_list = df.value
df.shape
v_list = []
for row, col in df.iterrows():

    tracker = df.loc[row]['value']
    try:
        v_list.extend(json.loads(tracker)['events'])
    except:
        print('warming, error for json load, tracker is:', tracker)
        continue

# print(len(v_list))

list1 = [v_list.index(item) for item in v_list if item['event'] == 'slot']
SLOT_COL =list(set([v_list[index]['name'] for index in list1]))
SUB_COL= ['sub_entity', 'sub_confidence_entity', 'sub_value', 'sub_extractor', 'sub_processors','action']
#--------------------------------- start convert ----------------------------------------------------#
initial = True

df2 = pd.DataFrame(columns = SUB_COL)

for a in v_list:
    # if v_list.index(a) == 1000:
    #     break
    
    print(f"Total records are {len(v_list)},now procedding {v_list.index(a) + 1}")
    if a['event'] == 'user':

        text_in_memory = a['text']
        message_id_in_memory = a['message_id']

        if 'intent_ranking' in a['parse_data']:
#             print('intent_ranking', a['parse_data']['intent_ranking'])

# ------------------- df1 for itent ranking --------------------------------------------------#

            df1_ori = pd.DataFrame(a['parse_data']['intent_ranking'])[['name','confidence']]
            df1 = pd.DataFrame(a['parse_data']['intent_ranking'])[['name','confidence']].T
            df1.columns = df1.loc['name']
            df1 = df1.drop(['name'],axis=0)
            df1.insert(0,'text', a['text'])
            text_ori =  a['text']
            df1.insert(0,'message_id', a['message_id'])
            df1.reset_index(inplace=True)
            # print('df1_columns:', df1.columns)
            df1 = df1.loc[:,~df1.columns.duplicated()]
            df1[SLOT_COL] = ""


#------------------------- extract sub and main entity ----------------------------------------------------------#

            df2_read = pd.DataFrame(a['parse_data']['entities'])

            if df2_read.empty:
                df2_read = df2
            else:
                df2_read = df2_read.drop(['start', 'end'], axis = 1)
                if len(df2_read) == 2:
                    df2_read = df2_read.drop([1])
                df2_read = df2_read.add_prefix('sub_')

            #     df2.insert(0, 'message_id', a['message_id'])
            df2_final = pd.concat([df2, df2_read], sort=False, ignore_index=True).fillna(0)
            df2_final.insert(0,'message_id', a['message_id'])
            df2_final
#----------------------------merge df1 and df2 ----------------------------------------------------------------#

            df_working = pd.merge(df1,df2_final,how="left",on="message_id")
            df_working = df_working.set_index('message_id')
            df_working.columns = [j + f'_{i}' if df_working.columns.duplicated()[i] else j for i,j in enumerate(df_working.columns)]
            if initial == True:
                df_final = df_working
                initial = False
            else:
#                 if len(df_working) > 1:
#                     print('df_working:', df_working)
                df_final = df_final.append(df_working)
#----------------------------extract slot     ----------------------------------------------------------------#
    if a['event'] == 'slot' and a['name'] != 'index_list':
  
        if a['value'] != None and a['value'] != []:
            if type(a['value']) == list and a['value'] == a['value']:
                a['value'] = a['value'][0]
        else:
            a['value'] = ""
        try:
            df_final.loc[message_id_in_memory, a['name']] = a['value']
        except:
            print('error a_name with a_value')
            print('df_final_loc:', df_final.loc[message_id_in_memory, a['name']])
            print('a_value:', a['value'])
            continue
       
        
#----------------------------no answer question----------------------------------------------------------------#
    if a['event'] == 'bot' and '????????????????????????????????????????????????????????????????????????CRA' in a['text']:

        df_final.loc[message_id_in_memory,'action'] = 'no answer question'
        # print('a_location:', v_list.index(a))
    if a['event'] == 'action' and a['name'] == 'action_default_fallback':
        # print('a_location:', v_list.index(a))
        
        df_final.loc[message_id_in_memory, 'action'] = 'new action_default_fallback'
 
#         df_final['action'] =  a['name']
#         print('message_id by action : ', message_id_in_memory)
#         print('user_text by action', text_in_memory)
#         print('df_finaL_text', df_final.loc[:-1]['text'])

value_list = []

for row, col in df_final.iterrows():
    if 'inform_protocol'in col.text:
        value_list.append(col['text'].split('{}')[0].split('\"')[3])
    else:
        value_list.append(col['text'])
df_final['clean_text'] = value_list

df_final

df_final.to_csv(chat_full_name)

print('total conversation:', df_final.shape[0])


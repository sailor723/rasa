#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pymysql, json
import pandas_profiling
import os

SUB_COL= ['sub_entity', 'sub_confidence_entity', 'sub_value', 'sub_extractor', 'sub_processors', 'action']

from sqlalchemy import create_engine
engine = create_engine('mysql+pymysql://weiping:@localhost:3306/test_db')
df = pd.read_sql('tracker1',engine)


#-------------------------------------read mysql ------------------------------------------------------------------------#
# def con_sql(sql):
# 	db = pymysql.connect(host='127.0.0.1', port=3306, user='weiping', passwd='', db='test_db', charset='utf8')
# 	cursor = db.cursor()
# 	cursor.execute(sql)
# 	result = cursor.fetchall()
# 	df = pd.DataFrame(list(result),columns=['id','sender_id','type_name','timestamp','intent_name','action_name','data'])
# 	db.close()
# 	return df

# df = con_sql('select * from tracker1')

full_chats_csv_name = os.path.abspath('new_all.csv')
chat_full_name  = os.path.join(os.getcwd(),'converted_log.csv')

# df.to_csv(full_chats_csv_name,encoding='utf-8-sig')
df = pd.read_csv(full_chats_csv_name,encoding='utf-8-sig')

#----------------------------------special convert from csv -----------------------------------------#
v_list = []
for row, col in df.iterrows():

    tracker = df.loc[row]['value']
    v_list.extend(json.loads(tracker)['events'])
print(len(v_list))

#--------------------------------- start convert ----------------------------------------------------#

initial = True

df2 = pd.DataFrame(columns = SUB_COL)

for a in v_list:
    
    print(f"Total records are {len(v_list)},now procedding {v_list.index(a)}")
    if a['event'] == 'user':

        text_in_memory = a['text']
        message_id_in_memory = a['message_id']
        
        # print("process text:           ", a['text'])
        # print('message_id_in_memory', message_id_in_memory)
        
        # print("_" * 80)
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
# #----------------------------merge df1 and df2 ----------------------------------------------------------------#

            df_working = pd.merge(df1,df2_final,how="left",on="message_id")
            df_working = df_working.set_index('message_id')
            df_working.columns = [j + f'_{i}' if df_working.columns.duplicated()[i] else j for i,j in enumerate(df_working.columns)]
            if initial == True:
                df_final = df_working
                initial = False
            else:
                # if len(df_working) > 1:
                #     print('df_working:', df_working)
                df_final = df_final.append(df_working)
    if a['event'] == 'action' and a['name'] == 'action_default_fallback':
        
        df_final.loc[message_id_in_memory]['action'] = 'new action_default_fallback'
 
#         df_final['action'] =  a['name']
        # print('message_id by action : ', message_id_in_memory)
        # print('user_text by action', text_in_memory)
#         print('df_finaL_text', df_final.loc[:-1]['text'])

value_list = []

for row, col in df_final.iterrows():
    if 'inform_protocol'in col.text:
        value_list.append(col['text'].split('{}')[0].split('\"')[3])
    else:
        value_list.append(col['text'])
df_final['clean_text'] = value_list

df_final.to_csv(chat_full_name)

print('total conversation:', df_final.shape[0])


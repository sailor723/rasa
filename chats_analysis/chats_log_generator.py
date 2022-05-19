#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os, json
from sqlalchemy  import create_engine, Column, Integer, String

DCTA_MYSQL_USER = os.getenv('DCTA_MYSQL_USER')
DCTA_MYSQL_PWD = os.getenv('DCTA_MYSQL_PWD')
DCTA_MYSQL_HOST = os.getenv('DCTA_MYSQL_HOST')
DCTA_MYSQL_PORT  = os.getenv('DCTA_MYSQL_PORT')
DCTA_MYSQL_DB  = os.getenv('DCTA_MYSQL_DB')
DCTA_MYSQL_TABLE  = os.getenv('DCTA_MYSQL_TABLE')

mysql_string = 'mysql+pymysql://'+ DCTA_MYSQL_USER + ':'+ DCTA_MYSQL_PWD + '@' + DCTA_MYSQL_HOST \
            + ":" + str(DCTA_MYSQL_PORT) + '/' + DCTA_MYSQL_DB
# engine = create_engine('mysql+pymysql://root:Ecc!123456@localhost:3306/test_db')
engine = create_engine(mysql_string)
df = pd.read_sql('tracker',engine)
# df = pd.read_csv('new_all.csv')
#-----------------------------read csv file from redis-------------------------------------------------------------------#
# redis_output_name = os.path.abspath('redis_output.csv')
redis_log_name = os.path.abspath('chats_log.csv')
entity_csp_name = os.path.abspath('entity_csp.csv')
# df.to_csv(redis_output_name,encoding='utf-8-sig')
#---------------------------------

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

print(len(v_list))

#-----------------------------dict to json-------------------------------------------------------------------#
# new_col = [eval(item) if item != None else item for item  in df.parse_data]
# df.parse_data = new_col
# new_col = [eval(item) if item != None else item for item  in df.data]
# df.data = new_col
# new_col = [eval(item) if item != None else item for item  in df.metadata]
# df.metadata = new_col

#-----------------------------function chunkstring-------- ----------------------------------------------------------------#
def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

#-----------------------------interprate data for log file, extract entities and csp---------------------------------------#
list1 = []
chats_data = ''
msg = ''
num = 0
print('-'* 120)
entity_list = []
csp_list = []
for a in v_list:

    if msg != '' and a['event'] == 'user':
        print('-'* 120)
        chats_data += '\n'+ ('-'* 120)
        
    if a['event'] == 'user':
        print('user_intent:', a['parse_data']['intent']['name'], a['parse_data']['intent']['confidence'])
        chats_data += '\n'+ 'user_intent:' + str(a['parse_data']['intent']['name']) + str(a['parse_data']['intent']['confidence'])
        num = num + 1
        
    if a['event'] == 'bot':
        print('BOT: ','\n'.join(list(chunkstring(a['text'],40))))
    
        chats_data +=  '\n'+'BOT: ' +'\n'.join(list(chunkstring(a['text'],40)))
        if len(entity_list) == (len(csp_list) + 1):
            csp_list.append(a['text'].strip())
        
       
#     if a['event'] == 'action':
#         print(' '* 80, '|  action:', a['name'])
#         chats_data += '\n'+ 'action:' + a['name']
        
    if a['event'] == 'slot':
        print(' ' * 80, '|  slot:',a['name'], a['value'])
        if a['name'] == 'sub' and a['value'] != None:

            entity_list.append(a['value'][0])
    try:
#         print('message_id:',a['parse_data']['message_id'])
        chats_data +=  '\n'+'message_id:' + a['parse_data']['message_id']
            
        print('USER:', '\n'.join(list(chunkstring(a['parse_data']['text'],40))))
        chats_data +=  '\n'+'USER:'+ '\n'.join(list(chunkstring(a['parse_data']['text'],40)))
        
        if msg == '':
            msg = a['parse_data']['message_id']
        else:
            a['parse_data']['message_id']

    except:
        list1.append(a)
        pass

with open(redis_log_name,'w',encoding='utf-8-sig') as file:
    file.write(chats_data)

df_entity_csp = pd.DataFrame(zip(entity_list, csp_list), columns = ['entity', 'csp'])
df_entity_csp.to_csv(entity_csp_name, encoding='utf-8-sig')
    
print('total number',num)
        

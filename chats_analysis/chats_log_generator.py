#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import os, json
from datetime import datetime
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

print("length of tracker ", len(v_list))


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

#-----------------------------function start_date_json-------- ----------------------------------------------------------------#

def start_date_json (time_stamp):
    time_key = ["year", "month", "day", "hour", "minute","second"]
    time_value = [dt_object.strftime("%Y"), dt_object.strftime("%m"), dt_object.strftime("%d"),dt_object.strftime("%H"),dt_object.strftime("%M"),dt_object.strftime("%S")]
    dict(zip(time_key, time_value))
    dict1 = dict(zip(time_key, time_value))
    return (dict1)

if len(v_list) > 0:
#-----------------------------interprate data for log file, extract entities and csp---------------------------------------#
# generate log file
    chats_data_combined = ''
    list1 = []
    chats_data = ''
    chats_data_json = ''
    msg = ''
    num = 0
    print('-'* 120)
    user_message = ''
    site_name = ''
    sender_name = ''
    json_list = []

    for a in v_list:

        if msg != '' and a['event'] == 'user':

            print('site_name', site_name)
            print('sender_name', sender_name)
            print('user_message', user_message)
            if sender_name:
                user_message =  site_name + '<br>' + sender_name + '<br><br><b>' + user_message +'</b>'
                json_list.append({'start_date': time_json,'text': {'headline': user_message, 'text': chats_data_json}})

            print('-'* 120)

            chats_data_combined += chats_data
            
            chats_data =  ('-'* 120 )
            chats_data_json = ''
    #         print('timestamp:', a['timestamp'])
    #         chats_data += '\n'+ 'timestamp:' + str(v_list[0]['timestamp'])
        if a['event'] == 'user':
            
            chats_data += '\n'+ 'timestamp:' + str(a['timestamp'])
            
            dt_object = datetime.fromtimestamp(a['timestamp'])
            time_json = start_date_json(a['timestamp'])
                                        
            print('user_intent:', a['parse_data']['intent']['name'], a['parse_data']['intent']['confidence'])
            chats_data += '\n'+ 'user_intent:' + str(a['parse_data']['intent']['name']) + str(a['parse_data']['intent']['confidence'])
            num = num + 1
            
        if a['event'] == 'bot':
                                        
            print('BOT: ', a['text'])
            chats_data +=  '\n'+'BOT: ' + str(a['text'])

    #         chats_data_json +=  '<br>'+'BOT: ' + ''.join(['<p>' + item + '</p>' for item in cut_text(a['text'],40)])
            chats_data_json +=  '<br><br>'+'BOT: ' + a['text']
            
            
        if a['event'] == 'action':
                                                                                
            print(' '* 80, '|  action:', a['name'])
            chats_data += '\n'+ 'action:' + a['name']
        
            
        if a['event'] == 'slot':
                                                
            print(' ' * 80, '|  slot:',a['name'], a['value'])
            chats_data +=  '\n'+'slot:' +  str(a['name']) + str(a['value'])
            if a['name'] == 'site_name':
                site_name = a['value']
            if a['name'] == 'sender_name':
                sender_name = a['value']

        try:
    #         print('message_id:',a['parse_data']['message_id'])
            chats_data +=  '\n'+'message_id:' + a['parse_data']['message_id']
                
            print('USER:', a['parse_data']['text'])
            user_message = a['parse_data']['text']
            chats_data +=  '\n'+'USER:'+ a['parse_data']['text']
    #         chats_data_json +=  '<br>'+'USER:'+ a['parse_data']['text'] + '<br>'
                                                                                                        
    #         chats_data_json += '<br>'+'USER: ' + ''.join(['<p>' + item + '</p>' for item in cut_text(a['parse_data']['text'],40)]) + '<br>'   
            chats_data_json += '<br>'+'USER: ' + a['parse_data']['text']
                                                                                                        
            if msg == '':
                msg = a['parse_data']['message_id']
            else:
                a['parse_data']['message_id']

        except:
            list1.append(a)
            pass
    if sender_name:
        user_message =  site_name + '<br>' + sender_name + '<br><br><b>' + user_message +'</b>'
        json_list.append({'start_date': time_json,'text': {'headline': user_message, 'text': chats_data_json}})
        print('-'* 120)

    chats_data_combined += chats_data
        
    # write log file
    with open('chats_log.csv','w',encoding='utf-8-sig') as file:
        file.write(chats_data_combined)

    # write json file
    json_file = {'text': {'headline': 'Welcome to DCTA Dialog',
            'text': 'DCTA conversational log'}, 

    'events': json_list}
    # write to json
    with open('chats_result.json','w',encoding='utf-8') as fp:
        json.dump(json_file, fp,ensure_ascii=False)

# print('total number',num)
        

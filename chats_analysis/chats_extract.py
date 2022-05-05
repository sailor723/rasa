#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import pymysql, json
def con_sql(sql):
	db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='Passwor@d1', db='dl04', charset='utf8')
	cursor = db.cursor()
	cursor.execute(sql)
	result = cursor.fetchall()
	df = pd.DataFrame(list(result),columns=['id','sender_id','type_name','timestamp','intent_name','action_name','data'])
	db.close()
	return df
df = con_sql('select * from events')


chat_data=''
for j in df.data:
    i = json.loads(j)

    if i['event'] == 'user':
        print ( i['event'])
        chat_data+='\n' + 'user: ' + str(i['text']) + '......' +  str(i['parse_data']['intent']['name'])+','
        print('User: {}'.format(i['text']))
        if len(i['parse_data']['entities']) > 0:
            chat_data+='User ' + str(i['parse_data']['entities'][0]['entity'])+','+str(i['parse_data']['entities'][0]['value'])+','
            print('extra data:', str(i['parse_data']['entities'][0]['entity']), '=',
                    str(i['parse_data']['entities'][0]['value']))
        else:
            chat_data+=",,"
    elif i['event'] == 'bot':
        print('Bot: {}'.format(i['text']))
        try:
            
            chat_data+='\n' + 'Bot: ' + str(i['text']) + '......' + str(i['metadata']['utter_action'])+'\n'
        except KeyError:
            chat_data+='Bot: ' + str(i['text'])+'\n'
            pass
else:
    with open('chats_simple_401.csv','a',encoding='utf-8-sig') as file:
        file.write(chat_data)

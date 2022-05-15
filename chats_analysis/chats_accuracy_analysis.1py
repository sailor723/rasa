import pandas as pd
import numpy as np
import json, os
import pandas_profiling
from neo4j import GraphDatabase
import pandas as pd
import json, os, argparse

class Neo4jconnection:

    def __init__(self, uri, user, password):
        
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None

        try:
            self._driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
        except Exception as e:
            print("Failed to create the driver", e)

    def close(self):

        if self._driver is not None:
            self._driver.close()

    def query(self, query, parameters=None, db=None):

        assert self._driver is not None, "Driver not initialized"
        session = None
        response = None

        try:
            session = self._driver.session(database = db) if db is not None else self._driver.session()
            response = list(session.run(query,parameters))
        except Exception as e:
            print("Query failed", e)
        finally:
            if session is not None:
                session.close()
        return response

conn = Neo4jconnection(uri="bolt://localhost", user='neo4j', password="test")
full_chats_csv_name = os.path.abspath('chats_full_401.csv')

df = pd.read_csv(full_chats_csv_name)

#------------------------------------ constructure node_all ------------------------------------------------#
node_all = []
node_working = []
list1 = []
chats_data = ''
msg = ''
num = 0
print('-'* 120)
for j in df.data:
    a = json.loads(j)
    if msg != '' and a['event'] == 'user':
        print('-'* 120)
        chats_data += '\n'+ ('-'* 120)
        
    if a['event'] == 'user':
        print('user_intent:', a['parse_data']['intent']['name'], a['parse_data']['intent']['confidence'])
        chats_data += '\n'+ 'user_intent:' + str(a['parse_data']['intent']['name']) + str(a['parse_data']['intent']['confidence'])
        num = num + 1
        node_working.append(str(a['parse_data']['intent']['name']))
        
    if a['event'] == 'bot':
        print('BOT: ', a['text'])
        chats_data +=  '\n'+'BOT: ' + str(a['text'])
        node_working.append(a['text'])
        
    if a['event'] == 'action':
        print(' '* 80, '|  action:', a['name'])
        chats_data += '\n'+ 'action:' + a['name']
        
    if a['event'] == 'slot':
        print(' ' * 80, '|  slot:',a['name'], a['value'])
        chats_data +=  '\n'+'slot:' +  str(a['name']) + str(a['value'])
        if a['value'] != None and a['name'] == 'sub':
            node_working.append(a['value'])
    try:
#         print('message_id:',a['parse_data']['message_id'])
        chats_data +=  '\n'+'message_id:' + a['parse_data']['message_id']
            
        print('USER:', a['parse_data']['text'])
        chats_data +=  '\n'+'USER:'+ a['parse_data']['text']
        node_all.append(node_working)
        node_working = []
        
        if msg == '':
            msg = a['parse_data']['message_id']
        else:
            a['parse_data']['message_id']

    except:
        list1.append(a)
        pass

# with open('chats_225_log.csv','a',encoding='utf-8-sig') as file:
#     file.write(chats_data)
    
# print('total number',num)





silent_node = 0
normal_node = 0 
correct_node = 0
error_node = 0
error_node
for node in node_all:
    print(len(node))

for node in node_all:
    if len(node) < 3:
        silent_node = silent_node + 1
    elif len(node) == 3:
        normal_node = normal_node + 1

        if node[1].split('\n')[0] == ' ':
            target_node = node[1].split('\n')[1].strip()
        else:

            target_node = node[1].split('\n')[0].strip()
        target_node

        print('entity_node:', node[0][0])
        print('target_node:', target_node)


        params = {'entity': node[0][0], 'target': target_node}

        query = """
        match(n{name:$entity}) -[] -(p{name:$target})
        return n,p
        """
        result = conn.query(query, parameters=params)

        if result:
            print('yes')
            correct_node = correct_node + 1
        else:
            error_node = error_node + 1
            print('No')

silent_node
normal_node
correct_node
error_node

silent_ratio = (silent_node) / ( silent_node + normal_node)
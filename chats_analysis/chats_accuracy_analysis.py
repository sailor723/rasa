import pandas as pd
import numpy as np
import json, os
from neo4j import GraphDatabase

#---------------------------  Neo4j Connection -----------------------------------------------#
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

# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")
conn = Neo4jconnection(uri="bolt://127.0.0.1", user='neo4j', password="test")


#---------------------------  Neo4j Connection -----------------------------------------------#

full_chats_csv_name = os.path.abspath('entity_csp.csv')
df = pd.read_csv(full_chats_csv_name)

correct_answer = 0
error_answer = 0
error_list =[]
for row, col in df.iterrows():

    entity_node = col.entity

    params = {'entity_node': entity_node}
    query = """
    match(entity_node {name:$entity_node}) <-[r] -(csp_node ) 
    return  r,csp_node
    """
    result = conn.query(query, parameters=params)
    try: 
        if result[0].data()['csp_node']['name_item']:

            if result[0].data()['csp_node']['name_item'].strip() == col.csp.split('\n')[1].strip():
                correct_answer = correct_answer + 1
            else:
                error_answer = error_answer + 1
                error_list.append([row, col.entity, col.csp])
                print('false')
    except:
        # print('this is QA')
        # print('row', row)
        # print('entity_node', entity_node)
        # print('result:', result[0].data()['csp_node']['name'].strip())
        # print('df:', col.csp.split('\n')[0].strip())
        if result[0].data()['csp_node']['name'].strip() in col.csp:
            correct_answer = correct_answer + 1

        else:
            error_answer = error_answer + 1
            print('Qa false')
            error_list.append([row, col.entity, col.csp])

df_error = pd.DataFrame(error_list, columns = ['number', 'entity', 'csp'])
df_error.to_csv('error_inquiry.csv', index=False, mode='w')

print('total number:', len(df))
print('correct_answer: ', correct_answer)
print('error_answer:', error_answer)
print('error list:', error_list)


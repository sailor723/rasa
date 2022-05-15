
import datetime as dt
from neo4j import GraphDatabase
from typing import Any, Text, Dict, List
import pandas as pd
import random, os
import json, webbrowser, arrow, dateparser
# from rasa_sdk.events import SlotSet


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


entity_csp_name = os.path.abspath('entity_csp.csv')
df = pd.read_csv(entity_csp_name)

for row, col in df.iterrows():
    entity = col.entity.upper()

    if col.csp.split('\n')[0] == ' ':
        
        csp = col.csp.split('\n')[1]
    else:
        csp = col.csp.split('\n')[0]

    print('entity:', entity)
    print('csp:', csp)
        
    params = {'entity': entity, 'csp': csp}
    
    query = """
        match(n{name:$entity}) -[r] - (m) return m.name
            """
    result = conn.query(query, parameters=params)
    
    for item in result:
  
        if csp.strip() == item.data()['m.name']:
            print('FOUND!!!!')
            break
        else:
            print('Not Found')
    # print(result[0].data()['m.description'])
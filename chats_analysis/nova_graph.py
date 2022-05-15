from neo4j import GraphDatabase
import pandas as pd
import json, os

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
 
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")

result = conn.query("MATCH(n) RETURN COUNT(n) AS count")

print(result[0]['count'])

# ----------------- MAIN CODE --------------------------------------------------

            
query = ''

params = {'node_head': 'NSCLC', 'node_tail':'入组5条'}

query = """
MATCH p=(n:NSCLC)-[*]->(m:入组5条) 
RETURN p
"""

    
result = conn.query(query, parameters=params)

msg = ''
for item in result[0].data()['p']:

    if type(item) == str:
        msg = msg + item


    elif type(item) == dict:
        msg = msg + item['name']
  

print (msg)
            

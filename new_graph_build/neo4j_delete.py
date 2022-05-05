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
 
parser = argparse.ArgumentParser(description='Neo4j information')
parser.add_argument('--url', dest='url', type=str, help='url of neo4j')
parser.add_argument('--user', dest='user', type=str, help='username of Neo4j')
parser.add_argument('--password', dest='password', type=str, help='password of Neo4j')
args = parser.parse_args()
url = "bolt:" + args.url
user = args.user
password = args.password
print(url)
print(user)
print(password)
 
conn = Neo4jconnection(uri=url, user=user, password=password)
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")

result = conn.query("MATCH(n) DETACH DELETE(n)")

# print(result[0]['count'])




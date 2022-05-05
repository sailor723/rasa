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
# conn = Neo4jconnection(uri="bolt://127.0.0.1", user='neo4j', password="test")

result = conn.query("MATCH(n) RETURN COUNT(n) AS count")

print(result[0]['count'])

# ----------------- MAIN CODE --------------------------------------------------

# question_file_name  = os.path.abspath('DL04_annotation_20220321 cyr combined.xlsx')
question_file_name  = os.path.abspath('DL04_annotation_combined.xlsx')

df = pd.read_excel(question_file_name, sheet_name='Group',header=0)

node1 = []
node2 = []
node_all = []
for row, col in df.iterrows():
    if col['version'] == 1:
        node1.append(col['user'])
    else:
        node2.append(col['user'])
    

node_all = [node1, node2]
    
#------------------------Create KG ----------------------------------------#

params = {'group': node1}
query = """
MATCH(n{name:'DL04'})
SET n.version_1 = $group
RETURN n
"""
result = conn.query(query, parameters=params)


params = {'group': node2}
query = """
MATCH(n{name:'DL04'})
SET n.version_2 = $group
RETURN n
"""
result = conn.query(query, parameters=params)

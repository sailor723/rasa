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

 
# conn = Neo4jconnection(uri=url, user=user, password=password)
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")
conn = Neo4jconnection(uri="bolt://127.0.0.1", user='neo4j', password="test")

result = conn.query("MATCH(n) RETURN COUNT(n) AS count")

print(result[0]['count'])

# ----------------- MAIN CODE --------------------------------------------------

question_file_name  = os.path.abspath('DL04_annotation_20220321 cyr combined.xlsx')
# question_file_name  = os.path.abspath('DL04_annotation_combined.xlsx')

df_inclusion = pd.read_excel(question_file_name, sheet_name='Inclusion',header=0)
df_exclusion = pd.read_excel(question_file_name, sheet_name='Exclusion',header=0)
df_dl04 = pd.read_excel(question_file_name, sheet_name='DL04',header=0)
df_inclusion = df_inclusion.astype(str)
df_exclusion = df_exclusion.astype(str)
df_dl04 = df_dl04.astype(str)

node_all = []

#------------------------Data Preparation for DL04----------------------------------------#

for row, index in df_dl04.iterrows():

    sub_node_list = [item.split('、')[1] for item in df_dl04.loc[row]['Entity'].splitlines()]
    node_working = []
    
    for item in sub_node_list:

        node_working.append(df_dl04.columns[0])
        node_working.append(df_dl04.loc[row]['DL04'])
        node_working.append(df_dl04.loc[row]['CSP'])
        node_working.append(df_dl04.loc[row]['Detail'])
        node_working.append(df_dl04.loc[row]['page'])
        node_working.append(item.strip('，').strip(','))
        node_all.append(node_working)
        node_working = []
#------------------------Data Preparation for Inclusion----------------------------------------#

for row, index in df_inclusion.iterrows():

    sub_node_list = [item.split('、')[1] for item in df_inclusion.loc[row]['Entity'].splitlines()]
    node_working = []
    
    for item in sub_node_list:

        node_working.append(df_inclusion.columns[0])
        node_working.append(df_inclusion.loc[row]['入组标准'])
        node_working.append(df_inclusion.loc[row]['CSP'])
        node_working.append(df_inclusion.loc[row]['Detail'])
        node_working.append(df_inclusion.loc[row]['page'])
        node_working.append(item.strip('，').strip(','))
        node_all.append(node_working)
        node_working = []

#------------------------Data Preparation for Inclusion----------------------------------------#

for row, index in df_exclusion.iterrows():

    sub_node_list = [item.split('、')[1] for item in df_exclusion.loc[row]['Entity'].splitlines()]
    node_working = []
    
    for item in sub_node_list:

        node_working.append(df_exclusion.columns[0])
        node_working.append(df_exclusion.loc[row]['排除标准'])
        node_working.append(df_exclusion.loc[row]['CSP'])
        node_working.append(df_exclusion.loc[row]['Detail'])
        node_working.append(df_exclusion.loc[row]['page'])
        node_working.append(item.strip('，').strip(','))
        node_all.append(node_working)
        node_working = []

#------------------------Create KG ----------------------------------------#
for node in node_all:
    query = ''

    params = {'name': node[0] + node[1], 'label': node[0], 'name_item': node[0] + node[1], 'description': node[2],  
            'detail': node[3], 'page': node[4], 'target_node': node[5]}

    if node[0] == '入组标准':
        query = """
        MERGE(q: Inclusion {name:'入组标准'})
        MERGE(o:Inclusion {name:$name}) 
        MERGE(p:Facts {name:$target_node}) 
        SET o.description = $description
        SET o.detail = $detail
        SET o.page = $page
        SET o.label = $label
        SET o.name_item = $name_item
        MERGE (q) - [:Include] - (o) 
        MERGE (o) -[r:Include ] ->(p) 
        RETURN o,r,p
        """
    if node[0] == '排除标准':
        query = """
        MERGE(q: Exclusion {name:'排除标准'})
        MERGE(o:Exclusion {name:$name}) 
        MERGE(p:Facts {name:$target_node}) 
        SET o.description = $description
        SET o.detail = $detail
        SET o.page = $page
        SET o.label = $label
        SET o.name_item = $name_item
        MERGE (q) - [:Include] - (o) 
        MERGE (o) -[r:Include ] ->(p) 
        RETURN o,r,p
        """
    elif node[0] == 'DL04':
        query = """
        MERGE(q: DL04 {name:'DL04'})
        MERGE(o:DL04 {name:$name}) 
        MERGE(p:Facts {name:$target_node}) 
        SET o.description = $description
        SET o.detail = $detail
        SET o.label = $label
        SET o.page = $page
        SET o.name_item = $name_item
        MERGE (q) - [:Include] - (o) 
        MERGE (o) -[r:Include ] ->(p) 
        RETURN o,r,p
        """

    result = conn.query(query, parameters=params)
    print(node)

#------------------------Hoursekeeping KG----------------------------------------#
query = """
MERGE(o:DL04 {name:'DL04'})
MERGE(p:Inclusion {name:'入组标准'})
MERGE (o) -[r:Include {name: 'has'} ] ->(p) 
RETURN o,p,r
"""
result = conn.query(query, parameters=params)

query = """
MERGE(o:DL04 {name:'DL04'})
MERGE(p:Exclusion {name:'排除标准'})
MERGE (o) -[r:Include {name: 'has'} ] ->(p) 
RETURN o,p,r
"""
result = conn.query(query, parameters=params)

query = """
MERGE(o:Facts {name:'器官和骨髓'})
REMOVE o:Facts
SET o: Inclusion
RETURN o
"""
result = conn.query(query, parameters=params)

query = """
MERGE(o:Facts {name:'治疗洗脱期'})
REMOVE o:Facts
SET o:Inclusion
RETURN o
"""
result = conn.query(query, parameters=params)

#------------------------Write entities txt ifle----------------------------------------#

with open("sub.txt","w",encoding='utf-8-sig') as datafile:  
    datafile.writelines("\n".join([node[5] for node in node_all]))


query = """
MERGE(o:DL04 {name:'DL04'})
RETURN o.version_1, o.version_2
"""
result = conn.query(query)
v1 = result[0]['o.version_1']
v2 = result[0]['o.version_2']

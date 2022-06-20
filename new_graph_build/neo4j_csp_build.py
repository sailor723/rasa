from neo4j import GraphDatabase
import pandas as pd
import os

DCTA_NEO4J_USER = os.getenv('DCTA_NEO4J_USER')
DCTA_NEO4J_PWD = os.getenv('DCTA_NEO4J_PWD')
DCTA_NEO4J_HOST = "bolt://" + os.getenv('DCTA_NEO4J_HOST')

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
 
conn = Neo4jconnection(uri=DCTA_NEO4J_HOST, user=DCTA_NEO4J_USER, password=DCTA_NEO4J_PWD)
# conn = Neo4jconnection(uri="bolt://127.0.0.1", user='neo4j', password="test")

result = conn.query("MATCH(n) RETURN COUNT(n) AS count")

print(result[0]['count'])

# ----------------- MAIN CODE --------------------------------------------------

# question_file_name  = os.path.abspath('DL04_annotation_20220321 cyr combined.xlsx')
question_file_name  = os.path.abspath('DL04_annotation_20220321 cyr combined.xlsx')

df_inclusion = pd.read_excel(question_file_name, sheet_name='Inclusion',header=0)
df_inclusion_V2 = pd.read_excel(question_file_name, sheet_name='Inclusion_V2',header=0)
df_exclusion = pd.read_excel(question_file_name, sheet_name='Exclusion',header=0)
df_exclusion_V2 = pd.read_excel(question_file_name, sheet_name='Exclusion_V2',header=0)
df_dl04 = pd.read_excel(question_file_name, sheet_name='DL04',header=0)
df_inclusion = df_inclusion.astype(str)
df_exclusion = df_exclusion.astype(str)
df_inclusion_V2 = df_inclusion_V2.astype(str)
df_exclusion_V2 = df_exclusion_V2.astype(str)
df_dl04 = df_dl04.astype(str)
df_inclusion['CSP_V2'] = df_inclusion_V2['CSP'] + "\t/DL04 V2"
df_exclusion['CSP_V2'] = df_exclusion_V2['CSP'] + "\t/DL04 V2"


#-------------------------function to prepare for Graph Build ------------------------------------------------------#

def node_generate_for_KG (df_to_generate):

    for row, index in df_to_generate.iterrows():
        
        sub_node_list = [item.split('、')[1].strip() for item in df_to_generate.loc[row]['Entity'].splitlines()]

        node_working = []
        
        for item in sub_node_list:

            node_working.append(df_to_generate.columns[0])
            node_working.append(df_to_generate.loc[row][df_to_generate.columns[0]])
            node_working.append(df_to_generate.loc[row]['CSP'])
            node_working.append(df_to_generate.loc[row]['Detail'])
            node_working.append(df_to_generate.loc[row]['page'])
            node_working.append(item.strip('，').strip(','))
            if '入选标准' in list(df_to_generate.columns) or '排除标准' in list(df_to_generate.columns):
                df_to_generate.loc[row]['CSP_V2']
                node_working.append(df_to_generate.loc[row]['CSP_V2'])
            else:
                print(df_to_generate['DL04'])
            node_all.append(node_working)
            node_working = []
        
    return(node_all)
    
#------------------------Data Preparation --------------------------------------------------------#

node_all = []

node_generate_for_KG(df_dl04)
    
node_generate_for_KG (df_inclusion)

node_generate_for_KG (df_exclusion)
    
#------------------------Create KG ----------------------------------------#

for node in node_all:
    query = ''

    if len(node) == 7:
        params = {'name': node[0] + node[1], 'label': node[0], 'name_item': node[0] + node[1], 'description': node[2],  
                'detail': node[3], 'page': node[4], 'target_node': node[5], 'version': node[6]}
    else:
        params = {'name': node[0] + node[1], 'label': node[0], 'name_item': node[0] + node[1], 'description': node[2],  
                'detail': node[3], 'page': node[4], 'target_node': node[5]}

    if node[0] == '入选标准':
        query = """
        MERGE(q: Inclusion {name:'入选标准'})
        MERGE(o:Inclusion {name:$name}) 
        MERGE(p:Facts {name:$target_node}) 
        SET o.description = $description
        SET o.description_v2 = $version
        SET o.detail = $detail
        SET o.page = $page
        SET o.label = $label
        SET o.name_item = $name_item
        set p.description = 'entity'
        MERGE (q) - [:Include] - (o) 
        MERGE (o) -[r:Include ] ->(p) 
        set r.type = 'has_entity'
        RETURN o,r,p
        """
    if node[0] == '排除标准':
        query = """
        MERGE(q: Exclusion {name:'排除标准'})
        MERGE(o:Exclusion {name:$name}) 
        MERGE(p:Facts {name:$target_node}) 
        SET o.description = $description
        SET o.description_v2 = $version
        SET o.detail = $detail
        SET o.page = $page
        SET o.label = $label
        SET o.name_item = $name_item
        set p.description = 'entity'
        MERGE (q) - [:Include] - (o) 
        MERGE (o) -[r:Include ] ->(p) 
        set r.type = 'has_entity'
        RETURN o,r,p
        """
    elif node[0] == 'DL04':
        query = """
        MERGE(q: DL04_MAIN {name:'DL04'})
        MERGE(o:DL04 {name: $name}) 
        MERGE(p:Facts {name:$target_node}) 
        SET o.description = $description
        SET o.detail = $detail
        SET o.version = "1,2"
        SET o.label = $label
        SET o.page = $page
        SET o.name_item = $name_item
        set p.description = 'entity'
        MERGE (q) - [:Include] - (o) 
        MERGE (o) -[r:Include ] ->(p) 
        RETURN o,r,p
        """

    result = conn.query(query, parameters=params)
    print(node)

#------------------------Hoursekeeping KG----------------------------------------#


query = """
match(n{name:'DL04'}) -[r] -(m{name:'DL04'}) 
delete r
return n,r,m
"""
result = conn.query(query, parameters=params)

query = """
MERGE(o:DL04 {name:'DL04'})
MERGE(p:Inclusion {name:'入选标准'})
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

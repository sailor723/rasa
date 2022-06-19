from neo4j import GraphDatabase
import pandas as pd
import os, re


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
# conn = Neo4jconnection(uri="bolt://localhost", user='neo4j', password="test")
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")

result = conn.query("MATCH(n) RETURN COUNT(n) AS count")

print(result[0]['count'])

# ----------------- MAIN CODE --------------------------------------------------

question_file_name  = os.path.abspath('DL04_QA_ner.xlsx')

df = pd.read_excel(question_file_name, sheet_name='QA_NER',header=0)

# df = df_all[['主题词.1', '问题拆解', '拆解后问题回答']].dropna()
#------------------------Data Preparation ----------------------------------------------------#
list_item = df['回答'].tolist()
for item in list_item:
    if item != item:
        print('item before:', item)
        list_item[list_item.index(item)] = list_item[list_item.index(item)-1]
        print('item after:', item)
df['回答'] = list_item


#------------------------Data Preparation for Q&A Log----------------------------------------#
df['主题词.1'] = [ item.replace('入组', '入选').replace('\t', '') for item in df['主题词.1'] ]
node_all = []
node_working = []

for row, index in df.iterrows():

    split_list = re.split('(\d+)', index['主题词.1'])
    print(split_list)
    if len(split_list) == 3:
        node_working.append(split_list[0] + '第' + split_list[1] + '条')       
        node_working.append(index['标题'].upper().strip())
        node_working.append(index['问题'].upper().strip())
        node_working.append(index['回答'].strip())    

        node_all.append(node_working)
        node_working = []

#------------------------Create KG ----------------------------------------#
for node in node_all:
    query = ''
    params = {'head_node': node[0].strip(), 'index': node[1], 'question_node': node[2], 'answer_node': node[3] }

    if '排除标准' in node[0]:
        query = """
        MERGE(q: Exclusion {name:$head_node})
        MERGE(t: Exclusion {name:$index})
        MERGE(o:Exclusion {name:$answer_node}) 
        MERGE(p:Exclusion {name:$question_node}) 
        SET o.description = 'answer'
        SET p.description = 'question'
        SET t.description = 'question_index'
        MERGE (q) - [s:has_answer] -> (o) 
        MERGE (o) -[r:to_question ] ->(p) 
        MERGE (p) -[w:to_index ] ->(t) 
        set s.type = 'has_anwser'
        set r.type = 'to_question'
        set w.type = 'to_index'
        RETURN o,r,p,t,w
        """
    elif '入选标准' in node[0]:
        query = """
        MERGE(q: Inclusion {name:$head_node})
        MERGE(t: Inclusion {name:$index})
        MERGE(o:Inclusion {name:$answer_node}) 
        MERGE(p:Inclusion {name:$question_node})  
        SET o.description = 'answer'
        SET p.description = 'question'
        SET t.description = 'question_index'
        MERGE (q) - [s:has_answer] -> (o) 
        MERGE (o) -[r:to_question ] ->(p) 
        MERGE (p) -[w:to_index ] ->(t) 
        set s.type = 'has_anwser'
        set r.type = 'to_question'
        set w.type = 'to_index'
        RETURN o,r,p,w
        """
    result = conn.query(query, parameters=params)
    print(node)

#------------------------Hoursekeeping KG----------------------------------------#
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


#------------------------Write entities txt ifle----------------------------------------#

# with open("sub.txt","w",encoding='utf-8-sig') as datafile:  
#     datafile.writelines("\n".join([node[4] for node in node_all]))

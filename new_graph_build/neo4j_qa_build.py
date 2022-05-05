from neo4j import GraphDatabase
import pandas as pd
import json, os, re, argparse

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
# conn = Neo4jconnection(uri="bolt://localhost", user='neo4j', password="test")
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")

result = conn.query("MATCH(n) RETURN COUNT(n) AS count")

print(result[0]['count'])

# ----------------- MAIN CODE --------------------------------------------------

question_file_name  = os.path.abspath('DL04_annotation_20220321 cyr combined.xlsx')

df = pd.read_excel(question_file_name, sheet_name='QA_log',header=0)

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
node_all = []
node_working = []

for row, index in df.iterrows():

    print(type(index['主题词.1']))
    split_list = re.split('(\d+)', index['主题词.1'])
    print(split_list)
    if len(split_list) == 3:
        node_working.append(split_list[0] + '第' + split_list[1] + '条')
        node_working.append(index['问题'].upper())
        node_working.append(index['回答'])    

        node_all.append(node_working)
        node_working = []

#------------------------Create KG ----------------------------------------#
for node in node_all:
    query = ''

    params = {'head_node': node[0].strip(), 'question_node': node[1], 'answer_node': node[2] }

    if '排除标准' in node[0]:
        query = """
        MERGE(q: Exclusion {name:$head_node})
        MERGE(o:Exclusion {name:$answer_node}) 
        MERGE(p:Exclusion {name:$question_node}) 
        SET o.label = 'answer'
        SET p.label = 'question'
        MERGE (q) - [s:has_answer] - (o) 
        MERGE (o) -[r:to_question ] ->(p) 
        set s.type = 'has_anwser'
        set r.type = 'to_question'
        RETURN o,r,p
        """
    elif '入组标准' in node[0]:
        query = """
        MERGE(q: Inclusion {name:$head_node})
        MERGE(o:Inclusion {name:$answer_node}) 
        MERGE(p:Inclusion {name:$question_node}) 
        SET o.label = 'answer'
        SET p.label = 'question'
        MERGE (q) - [s:has_answer] - (o) 
        MERGE (o) -[r:to_question ] ->(p) 
        set s.type = 'has_anwser'
        set r.type = 'to_question'
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


#------------------------Write entities txt ifle----------------------------------------#

# with open("sub.txt","w",encoding='utf-8-sig') as datafile:  
#     datafile.writelines("\n".join([node[4] for node in node_all]))

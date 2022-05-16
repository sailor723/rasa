from neo4j import GraphDatabase
import pandas as pd
import json, os, argparse
from pathlib import Path
from PyPDF2 import PdfFileReader, PdfFileWriter
import pdfplumber



NEO4J_USER = os.getenv('DCTA_NEO4J_USER')
NEO4J_PWD = os.getenv('DCTA_NEO4J_PWD')
NEO4J_URL = "bolt://" + os.getenv('DCTA_NEO4J_URL')

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

conn = Neo4jconnection(uri=NEO4J_URL, user=NEO4J_USER, password=NEO4J_PWD)
 
# conn = Neo4jconnection(uri="bolt://localhost", user='neo4j', password="test")
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")
# ----------------- MAIN CODE --------------------------------------------------

CSP_file_name  = os.path.abspath('d967sc00001.pdf')

pdf_path = (CSP_file_name)

pdf_path = (pdf_path)

input_pdf = PdfFileReader(str(pdf_path))

pdf_writer = PdfFileWriter()
for n in range(66, 67):
    page = input_pdf.getPage(n)
    pdf_writer.addPage(page)
pdf_writer.getNumPages()

with Path("Table9.pdf").open(mode="wb") as output_file:
    pdf_writer.write(output_file)

#—————————————————————————————————————————— read tabel8 and convert into CSV——————————————————————————————————————#
pdf = pdfplumber.open('Table9.pdf')

## first df 
p0 = pdf.pages[0]
table = p0.extract_table()
df = pd.DataFrame(table[1:], columns=table[0])

[''.join(item.split('\n')) for item in df['治疗']]

df['治疗'] = [''.join(item.split('\n')) for item in df['治疗']]
df['最短清洗期'] = [''.join(item.split('\n')) for item in df['最短清洗期']]

node_all = []
node = []

node_all.append(['受试者类型和疾病特征',"Include",'治疗洗脱期'])
node_head = '治疗洗脱期'
for index, row in df.iterrows():
    if row['最短清洗期'] == None:
        node_head = row['治疗']
        node_all.append([node_head,'Include',node_head])
    else:
        node_rel = row['治疗']
        node_cont = (row['最短清洗期'])
        node_all.append([node_head,node_rel,node_cont])

node_all
#——————————————————————————————————————————build into graph DB ——————————————————————————————————————#


######################## build DL04 centrol node #########################################
for node in node_all:

    query = ''
    params = {'node_head': node[0], 'node_target': node[1], 'node_description':node[2]}

    if node[0] == '受试者类型和疾病特征':
        query = """
        MERGE(p:Inclusion {name:$node_head}) 
        MERGE(q:Inclusion {name:$node_description}) 
        SET q.description = $node_head
        CREATE(p) -[r:Include ] ->(q)
        RETURN p,q,r
        """
    else:
        query = """
        MERGE(p:Inclusion {name:$node_head}) 
        MERGE(q:Inclusion {name:$node_target}) 
        SET q.description = $node_description
        MERGE (p) -[r:Include ] ->(q) 
        RETURN p,q,r
        """
    result = conn.query(query, parameters=params)
    print(node)



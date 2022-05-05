from neo4j import GraphDatabase
import pandas as pd
import json, os, argparse
from pathlib import Path
from PyPDF2 import PdfFileReader, PdfFileWriter
import pdfplumber

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

# ----------------- MAIN CODE --------------------------------------------------

CSP_file_name  = os.path.abspath('d967sc00001.pdf')

pdf_path = (CSP_file_name)
input_pdf = PdfFileReader(str(pdf_path))

pdf_writer = PdfFileWriter()
for n in range(65, 67):
    page = input_pdf.getPage(n)
    pdf_writer.addPage(page)
pdf_writer.getNumPages()

with Path("Table8.pdf").open(mode="wb") as output_file:
    pdf_writer.write(output_file)

#—————————————————————————————————————————— read tabel8 and convert into CSV——————————————————————————————————————#
pdf = pdfplumber.open('Table8.pdf')

## first df 
p0 = pdf.pages[0]
table = p0.extract_table()
df = pd.DataFrame(table[0:], columns=table[0])
df.columns = ['name','description']

node_all = []
node = []
node_head_name = '器官和骨髓'
for index, row in df.iterrows():
    if row['description'] == None:
        node_head = row['name']
        node_all.append([node_head_name,'Include',node_head])
    else:
        node_rel = row['name']
        node_cont = (row['description'])
        node_all.append([node_head,node_rel,node_cont])

node_all
#——————————————————————————————————————————build into graph DB ——————————————————————————————————————#


######################## build DL04 centrol node #########################################
for node in node_all:
    query = ''
    params = {'node_head': node[0].upper(), 'node_target': node[1].upper(), 'node_description':node[2]}

    if node[0] == '器官和骨髓':

        query = """
        MERGE(p:Inclusion {name:$node_head}) 
        MERGE(q:Inclusion {name:$node_description}) 
        MERGE(p) -[r:Include ] ->(q)
        RETURN p,q,r
        """
    else:
        query = """
        MERGE(p:Inclusion {name:$node_head}) 
        MERGE(q:Inclusion {name:$node_target}) 
        SET q.description = $node_target + ':' + $node_description
        MERGE (p) -[r:Include ] ->(q) 
        RETURN p,q,r
        """

    result = conn.query(query, parameters=params)
    print(node)



from neo4j import GraphDatabase
import os


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
# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")

result = conn.query("MATCH(n) DETACH DELETE(n)")




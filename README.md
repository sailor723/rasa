# DCTA for backend
DCTA project as backend

Folder and features include:

data: training data for nlu, stories, rules

domain: rasa control domain file

actions: actions to search neo4j for feedback to PI inquiry

new_graph_build: to build up Neo4j based on annoation file

chats_analysis: BI dashboard for chats analysis

endpoints: trackerstore and webhook define file

config: NLU and rule policy file

# DCTA Rasa Setup Guide

1.	Spacy setup
    Spacy is a NLU package, which is base for the project. 
    Install spaCy · spaCy Usage Documentation
    1.1, install spacy and download language model
    Install spacy 
    pip install -U pip setuptools wheel
    pip install -U spacy
    1.2 spacy English model md 
    python -m spacy download en_core_web_sm
    1.3 Spacy Chinse model model trf and md”
    python -m spacy download zh_core_web_trf
    python -m spacy download zh_core_web_md
    spacy info to check

2.	Rasa setup, please make sure to have python 3.8 and pip
    2.1 setup venv 
    python3 -m venv ./venv
    source ./venv/bin/activate
    2.2 rasa install
    pip3 install -U --user pip && pip3 install rasa
    rasa --version to check
    Installation (rasa.com)

3.	DB Prerequires  
    DCTA need Neo4j, Redis, Mysql install and configured.

4.	Python library
    We need Streamlit, Stremlist timeline, plotly, boken
    First steps — Bokeh 2.4.3 Documentation
    Installation - Streamlit Docs
    Getting started with plotly in Python

    requirements.txt:
    streamlit >=1.3.0
    streamlit-timeline==0.0.2
    potly==5.8.2
    boken==2.4.1
    pip install requirements.txt

5.	DCTA project setup
    DCTA was derived by env, below is example of env setting:
    DCTA_NEO4J_USER=neo4j
    DCTA_NEO4J_HOST=localhost
    DCTA_REDIS_PWD=
    DCTA_MYSQL_DB=test_db
    PWD=/home/weiping/dev/DCTA/rasa/new_graph_build
    DCTA_NEO4J_PWD=test
    DCTA_MYSQL_PORT=3306
    DCTA_REDIS_PORT=6379
    DCTA_MYSQL_PWD=Ecc!123456
    DCTA_MYSQL_USER=root
    DCTA_MYSQL_HOST=127.0.0.1
    DCTA_REDIS_HOST=127.0.0.1
    OLDPWD=/home/weiping/dev/DCTA/rasa
    This is example in endpoints.yml for trackerstore

    Rasa port number: 
    Rasa core: 5005
    Rasa action server: 5055
    But these can be customized

6.  DCTA rasa code in Bitbucket
    Browse Digital Clinical Trial Assistant / rasa - Bitbucket-Production (astrazeneca.com)
    After clone, please checkout to az-ecc:
    Git checkout -b az-ecc origin az-ecc
    Then please:
    6.1 rebuild Neo4j by:
    DCTA/rasa/new_graph_build/bash neo4j_all.sh
    6.2 train model by:
    DCTA/rasa: rasa train

7. Start up api and actions:
    DCTA/rasa/bash api.sh
    DCTA/rasa/bash actions.sh

8. Open web browser to check everything ready



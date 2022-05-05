from socket import MSG_EOR
from typing import Text, List, Any, Dict
from matplotlib.pyplot import subplot

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, AllSlotsReset, Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from sqlalchemy import create_engine


import datetime as dt
from neo4j import GraphDatabase
from typing import Any, Text, Dict, List
import pandas as pd
import random, os
import json, webbrowser, arrow, dateparser
# from rasa_sdk.events import SlotSet

city_db = {
    "brussels": "Europe/Brussels",
    "zagreb": "Europe/Zagred",
    "london": "Europe/London",
    "lisbon": "Europe/Amsterdam",
    "seattle": "US/Pacific",
    "Beijing": "China/Beijing"
}

ALLOWED_MAIN_TYPES = ["入选标准", "排除标准","全部"]

#--------------------------- Initial Entities List -------------------------------------------#
engine = create_engine('mysql+pymysql://weiping:@localhost:3306/test_db')
df_user= pd.read_sql('t_remind',engine)
df_user = df_user.drop([0])

#--------------------------- Initial Entities List -------------------------------------------#
entities_file_name  = os.path.join(os.getcwd(),'new_graph_build/sub.txt')
f = open(entities_file_name, "r",encoding='utf-8-sig')
ENTITIES_LIST = list(set(f.read().split('\n')))

#---------------------------  Neo4j Connection -----------------------------------------------#
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

# conn = Neo4jconnection(uri="bolt://81.70.254.56", user='neo4j', password="neo4j56")
conn = Neo4jconnection(uri="bolt://127.0.0.1", user='neo4j', password="test")

#---------------------------  action_initial——protocol  -----------------------------------------------#
# this is to generate selection box -------------------------------------------------------------------#
class ActionInitialProtocol(Action):

    def name(self) -> Text:
        return "action_initial_protocol"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        print('I am action_initial_protocol')
        main = tracker.get_slot('main')
        sub = tracker.get_slot('sub')
        question_list = tracker.get_slot('question_list')
        print('main:', main)
        print('sub:', sub)
        print('question_list::', question_list)


#----------------------------process question_list-----------------------------------------------#

        if question_list:
                
            dict1 = {}
            dict2 = {}
            button_list = []

            for item in question_list:
                            
                dict1["sub"] = item
                dict1 = json.dumps(dict1,ensure_ascii=False)
                dict2["payload"] = "/inform_protocol"  + str(dict1) 
                dict2["title"] = item
                button_list.append(dict2)
                dict1 = {}
                dict2 = {}

            print(button_list)

            dispatcher.utter_message(text='此项下还有以下问题，请参照选择。您也可以输入其他问题。谢谢', buttons= button_list)

            return []
#--------------------------- GENERATE RANDOM 13 entities ----------------------------------------#

        initial_entities = ['RESTART'] + [ENTITIES_LIST[i] for i in random.sample([_ for _ in range(len(ENTITIES_LIST))],13)]

# -------------------------- dispatch 14 entities for selction -----------------------------------#
 
        dict1 = {}
        dict2 = {}
        button_list = []

        for item in initial_entities:
            
            dict1["sub"] = item                                  # pointer sub to entity
            dict1 = json.dumps(dict1,ensure_ascii=False)
            dict2["payload"] = "/inform_protocol"  + str(dict1)  # define intent as /inform_protocol, add sub entities 
            dict2["title"] = item                                # add sub entity as title 
            button_list.append(dict2)                            # build button_list with dict2
            dict1 = {}
            dict2 = {}

     
        dispatcher.utter_message(text='小易推荐如下选项，请参照选择。谢谢', buttons= button_list)         # return to rasa with button_list
        return []

        # return {"sub": sub}


class ActionLogin(Action):
    
    def name(self) -> Text:
        return "action_Login"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('tracker_sende_id:', tracker.current_state()['sender_id'])

        trackcer_sender_id = tracker.current_state()['sender_id']

        try:
            sender_id = [_ for _ in trackcer_sender_id.split('+')][1] 

            site_id = [_ for _ in trackcer_sender_id.split('+')][4]

            version = '1.0'
        except:
            sender_id = ''
            site_id =''
            version = ''

        msg = '\n' + '我是阿斯利康的临床试验智能助手小易，很高兴为您服务.'

        if sender_id == '':
            text = msg
        else:
            text = '你好' + sender_id + ',' + site_id+ '方案版本是' + version +  msg 

        dispatcher.utter_message(text= text)

        return [SlotSet("sender_id", sender_id),SlotSet("site_id", site_id),]        

class ActionCheckProtocol(Action):
    
    def name(self) -> Text:
        return "action_check_protocol"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        print('tracker_sende_id:', tracker.current_state()['sender_id'])

        sender_id = 'Andy' + '老师'
        
        site_info = df_user[df_user.user_id == 'Andy']['site_id'].to_string().split('   ')[1].strip()

        sub = None
        print('I am in check_protocol----------------------------------------------------------------------')
        if tracker.get_slot('sub'):
            sub = list(set(tracker.get_slot('sub')))                           # get sub entity, no need main
            print('sub:', sub)
        question_list = tracker.get_slot('question_list')       #get question_list
        print('question_list:', question_list)

#--------------------------- GENERATE RANDOM 13 entities ----------------------------------------#

        initial_entities = ['RESTART'] +  [ENTITIES_LIST[i] for i in random.sample([_ for _ in range(len(ENTITIES_LIST))],13)]

# -------------------------- Generate button list for 14 entities -------------------------------------------------------#
 
        dict1 = {}
        dict2 = {}
        button_list = []

        for item in initial_entities:
            
            dict1["sub"] = item                                  # pointer sub to entity
            dict1 = json.dumps(dict1,ensure_ascii=False)
            dict2["payload"] = "/inform_protocol"  + str(dict1)  # define intent as /inform_protocol, add sub entities 
            dict2["title"] = item                                # add sub entity as title CSP原文
            button_list.append(dict2)                            # build button_list with dict2
            dict1 = {}
            dict2 = {}

        msg2 = '***小易推荐如下选项，请参照选择。谢谢***'
        # dispatcher.utter_message(text='小易推荐如下选项，请参照选择。谢谢', buttons= button_list)  

# -------------------------- age intent process  --------------------------------#

        intent = tracker.get_intent_of_latest_message()

        print('intent:',intent)

        if intent == 'age':
            sub = '年龄'
        print('* sub is :', sub)
        if sub == None:
                msg = '请提供您要查询的具体内容，谢谢'
                dispatcher.utter_message(text=msg)
                question_list = None
                return [SlotSet("sub",None), SlotSet("question_list", question_list)]


#-------------------construct sub into sub_list, as there maybe 2+ sub entities---#

        if sub[0] == 'RESTART':
            return [Restarted()]

        else:
            if type(sub) == str:
                sub_list = []
                sub_list.append(sub)
            else:
                sub_list = sub

            sub_list = [item.upper() for item in sub_list]               # upper sub 
    
            print('after check sub:', sub_list)

            # latest_message = tracker.latest_message['text']
            # ent = tracker.latest_message['entities']

            print('ready to check Neo4j again------------------------------------------')

#----------------------------check question_list ---------------------------------------------------------#

            try:

                if question_list and sub_list[0] in question_list:              # check question_list, also sub[0] in question_list
                                                                               # means to check anwser from question
        
                    print('had question_list, processing')
                    params = {'node_sub': sub_list}
                    
                    query = """
                    match  (question_node) <-[to_questions] - (answer_node) 
                    where question_node.name in $node_sub
                    return answer_node.name 
                    
                    """
                    result = conn.query(query, parameters=params)

                    msg = result[0].data()['answer_node.name']

                    for item in sub_list:
                        question_list.pop(question_list.index(item))

                    if question_list:
                        dict1 = {}
                        dict2 = {}
                        button_list = []

                        msg2 = '***此项下还有以下问题，请参照选择。您也可以输入其他问题。谢谢***'

                        print('question_list in action:', question_list)

                        for item in question_list:
                                        
                            dict1["sub"] = item
                            dict1 = json.dumps(dict1,ensure_ascii=False)
                            dict2["payload"] = "/inform_protocol"  + str(dict1) 
                            dict2["title"] = item
                            button_list.append(dict2)
                            dict1 = {}
                            dict2 = {}
                    
                    dispatcher.utter_message(text= ( msg + ' \n' + msg2 ), buttons= button_list)
                    print('before question return--------------------------------------------------------------------')
                    return [SlotSet("sub",None), SlotSet("question_list", question_list)]
                    # return [SlotSet("sub",None)]                             # keep question_list
            except:
                print('error for check neo4j for question list')


# -------------------------- then, system will perform query --------------------------------#
            try:

                params = {'node_sub': sub_list}
                
                query = """
                match (question_node) <-[to_questions*0..1] - (answer_node) <- [has_answer*0..1] -(csp_node) -[r*] ->(entity_node) -[*0..3] ->(entity_value)
                where csp_node.label in ['入组标准', '排除标准','DL04'] and ( entity_node.name in $node_sub )
                return csp_node, collect( distinct question_node) as q_nodes, collect( distinct  entity_value) as entity_values
                ORDER BY csp_node.name_item DESC
                """
                result = conn.query(query, parameters=params)

                print('result:', result)
    # -------------------------- then, form dispatchd massage ---------------------------------#

                if len(result) == 0:
                    msg = '对不起，小易没有找到。我还需要学习'
                else:

                    csp_description = result[0].data()['csp_node']['description']
                    page_num = '试验方案第' + result[0].data()['csp_node']['page'] + '页'
                    name_item = result[0].data()['csp_node']['name_item']

                    msg_csp = ' \n' + name_item + ' \n' + csp_description       

                    try:
                        msg_entity_value = ''
                        for e_value in [ item for item in result[0].data()['entity_values'] if 'description' in item.keys()]:
                            msg_entity_value = msg_entity_value + ' \n' +  e_value['name'] + ':' +  e_value['description'] 
 
                    except:
                        msg_entity_value = ''

                    question_list = [ item['name'] for item in result[0].data()['q_nodes'] if 'label' in item.keys() and item['label'] == 'question']
                        
                    if question_list:          

                        # question_list.sort()
 
                        dict1 = {}
                        dict2 = {}
                        button_list = []

                        print('question_list in action:', question_list)

                        for item in question_list:
                                        
                            dict1["sub"] = item
                            dict1 = json.dumps(dict1,ensure_ascii=False)
                            dict2["payload"] = "/inform_protocol"  + str(dict1) 
                            dict2["title"] = item
                            button_list.append(dict2)
                            dict1 = {}
                            dict2 = {}
                            msg2 = '***此项下还有以下问题，请参照选择。您也可以输入其他问题。谢谢***'

                    dispatcher.utter_message(text=( page_num + msg_csp + msg_entity_value + ' \n' +  msg2), buttons= button_list)
                    # dispatcher.utter_message(text=( page_num + msg_csp + msg_entity_value + ' \n' +  msg2))
    
                    return [SlotSet("sub",None), 
                            SlotSet("question_list", question_list)]
                            # SlotSet("csp_description", csp_description),
                        # SlotSet("page_num", page_num)]
            except:
                print('error for check neo4j entities')
            # return [SlotSet("sub",None)]
            # return [AllSlotsReset()]
            # return []

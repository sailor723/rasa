from ast import Continue
from socket import MSG_EOR
from token import ISTERMINAL
from typing import Text, List, Any, Dict
from matplotlib.pyplot import subplot

from rasa_sdk import Tracker, FormValidationAction, Action
from rasa_sdk.events import EventType, SlotSet, AllSlotsReset, Restarted
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from regex import subn

from sqlalchemy import create_engine


import datetime as dt
from neo4j import GraphDatabase
from typing import Any, Text, Dict, List
import pandas as pd
import random, os
import json, webbrowser, arrow, dateparser, requests
# from rasa_sdk.events import SlotSet

city_db = {
    "brussels": "Europe/Brussels",
    "zagreb": "Europe/Zagred",
    "london": "Europe/London",
    "lisbon": "Europe/Amsterdam",
    "seattle": "US/Pacific",
    "Beijing": "China/Beijing"
}


DCTA_NEO4J_USER = os.getenv('DCTA_NEO4J_USER')
DCTA_NEO4J_PWD = os.getenv('DCTA_NEO4J_PWD')
DCTA_NEO4J_HOST = "bolt://" + str(os.getenv('DCTA_NEO4J_HOST'))

print('DCTA_NEO4J_HOST:', DCTA_NEO4J_HOST)

ALLOWED_MAIN_TYPES = ["入选标准", "排除标准","全部"]

TARGET_NODE_LIST = ["入选标准", "排除标准","DL04"]
#--------------------------- Initial Entities List -------------------------------------------#
entities_file_name  = os.path.join(os.getcwd(),'new_graph_build/sub.txt')
f = open(entities_file_name, "r",encoding='utf-8-sig')
ENTITIES_LIST = list(set(f.read().split('\n')))

def string_convert(string_input):                               # string convert to unicode 
    string_output = ''

    for i in string_input:
        codes = ord(i)                                          # 将字符转为ASCII或UNICODE编码
        if codes <= 126:                                        # 若是半角字符
            string_output = string_output + chr(codes+65248)    # 则转为全角
        else:
            string_output = string_output + i                   # 若是全角，则不转换

    return(string_output)

def fill_name_des(name_len, des_len, list_value):                # transfer name and description as table display
    
    msg = ""

    for dict_item in list_value:
                      
        new_string = string_convert(dict_item['name'])
        names = [new_string[i:i+name_len] for i in range(0, len(new_string), name_len)]
        names = [ item.ljust(name_len, chr(12288)) for item in names]

        new_string = string_convert(dict_item['description'])
        des = [new_string[i:i+des_len] for i in range(0, len(new_string), des_len)]
        des = [ item.ljust(des_len, chr(12288) ) for item in des]

        if len(names) > len(des):
            des.extend([' '* des_len] *(len(names) - len(des)))
        else:
            names.extend([' '* name_len] *(len(des) - len(names)))

        msg = msg + ''.join(list(map(lambda x: x[0]+' : '+x[1] + '\n', zip(names, des))))
    

    return (msg)

def check_for_all (entity_list, csp_nodes):
    
    for item in csp_nodes:

        selected_csp = []
        item['description'].replace(" ","")

        if False in [y in item['description'].replace(" ","") for y in entity_list]:
            continue 
        else:
            selected_csp.append(csp_nodes.pop(csp_nodes.index(item)))

    return(selected_csp, csp_nodes)

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
conn = Neo4jconnection(uri=DCTA_NEO4J_HOST, user=DCTA_NEO4J_USER, password=DCTA_NEO4J_PWD)


#--------------------------- check for table 9 -----------------------------------------------------------
def list_for_table9(entity_list):

    if len(entity_list) > 1:
    
        query = """
        match(n{name:'治疗洗脱期'}) -[] -> (m) return m.name
        """
        result = conn.query(query)
        table9_list = [item.data()['m.name'] for item in result]
        if '治疗洗脱期' in entity_list:

            l1 = [ item for item in entity_list if item in table9_list]
 
            if l1 != []:
                entity_list.pop(entity_list.index('治疗洗脱期'))


    return(entity_list)

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
        index_list = tracker.get_slot('index_list')
        print('main:', main)
        print('sub:', sub)
        print('index_list::', index_list)


#--------------------------- GENERATE RANDOM 15 entities ----------------------------------------#

        initial_entities = [ENTITIES_LIST[i] for i in random.sample([_ for _ in range(len(ENTITIES_LIST))],15)]

# -------------------------- dispatch 15 entities for selction -----------------------------------#
 
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
        return [SlotSet("sender_id", None)]

class ActionLogin(Action):
    
    def name(self) -> Text:
        return "action_Login"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('tracker_sende_id:', tracker.current_state()['sender_id'])

        trackcer_sender_id = tracker.current_state()['sender_id']

        try:
            sender_id = [_ for _ in trackcer_sender_id.split('+')][0]
            sender_name = [_ for _ in trackcer_sender_id.split('+')][1]
            site_id = [_ for _ in trackcer_sender_id.split('+')][4]
            version = [_ for _ in trackcer_sender_id.split('+')][5].split('-')[0]
            token = [_ for _ in trackcer_sender_id.split('+')][6]
        except:
            # sender_id = ''
            # site_id =''
            # version = ''
            sender_id = '123465'
            sender_name = 'zhaoyisheng'
            site_id ='北京肿瘤医院'
            version = '2.0'
            token = None

        msg = '我是阿斯利康的临床试验智能助手小易，很高兴为您服务。'

#--------------------------- GENERATE RANDOM 15 entities ----------------------------------------#

        initial_entities =  [ENTITIES_LIST[i] for i in random.sample([_ for _ in range(len(ENTITIES_LIST))],15)]

# -------------------------- Generate button list for 15 entities -------------------------------------------------------#
 
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

        msg2 = '<b>小易推荐如下选项，请参照选择。谢谢</b>'

        if sender_id == '':
            text = msg + '\n' + msg2
        else:
            text = '您好' + sender_name + '，' + site_id + '的方案版本是' + version + '。' +  msg  + '\n' + msg2

        dispatcher.utter_message(text= text, buttons= button_list )

        return [SlotSet("sender_id", sender_id),
                SlotSet("sender_name", sender_name), 
                SlotSet("site_id", site_id), 
                SlotSet("version", version),
                SlotSet("token", token),
                ]        

class ActionCheckProtocol(Action):
    
    def name(self) -> Text:
        return "action_check_protocol"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        print('I am in check_protocol------------------')

#--------------------------- extract slot ----------------------------------------#

        print('tracker_sende_id:', tracker.current_state()['sender_id'])

        sender_id = tracker.get_slot('sender_id')

        if sender_id == None:
            sender_id = ''

        print('sender_id', sender_id)

        sender_name = tracker.get_slot('sender_name')

        item_number = tracker.get_slot('item_number')

        main = tracker.get_slot('main')

        site_id = tracker.get_slot('site_id')

        version = tracker.get_slot('version')

        token = tracker.get_slot('token')

        message = tracker.latest_message['text']
      
        text_CRA = '我不太理解，我会转给给负责咱们中心的CRA'

        text_CRA_no_found = '我在方案中没有找到，我会把问题转给负责咱们中心的CRA'

        sub_list = tracker.get_slot('sub_list')

        # sub = None
        
        # if tracker.get_slot('sub'):
        #     sub = list(set(tracker.get_slot('sub')))                           # get sub entity, no need main
        #     print('sub:', sub)
        index_list = tracker.get_slot('index_list')       #get index_list
        print('index_list:', index_list)

#--------------------------- GENERATE RANDOM 15 entities ---------------------------------------------------------------#

        initial_entities =  [ENTITIES_LIST[i] for i in random.sample([_ for _ in range(len(ENTITIES_LIST))],15)]

# -------------------------- Generate button list for 5 entities -------------------------------------------------------#
 
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

        msg2 = '<b>小易推荐如下选项，请参照选择。谢谢</b>'

# -------------------------- age intent process  --------------------------------#

        intent = tracker.get_intent_of_latest_message()

        print('intent:',intent)

        if intent == 'age':
            sub_list = ['年龄']
        print('* sub_list is :', sub_list)
        print('item_number:', item_number)

        if (not sub_list) and (item_number == None):

                msg = '请提供您要查询的具体内容，谢谢'
                dispatcher.utter_message(text=msg)
                index_list = None
                return [SlotSet("sub",None), SlotSet("sub_list",None), SlotSet("item_number",None), SlotSet("index_list", index_list),
                        SlotSet("sender_id", sender_id),
                        SlotSet("sender_name", sender_name), 
                        SlotSet("site_id", site_id), 
                        SlotSet("version", version),
                        SlotSet("token", token)
                        ]

#-------------------construct sub into sub_list, as there maybe 2+ sub entities---#
      
        if sub_list and len(sub_list) > 0:
            if sub_list[0] == 'RESTART':
                return [Restarted()]
            else:
                # if type(sub) == str:
                #     sub_list = []
                #     sub_list.append(sub)
                # else:
                #     sub_list = sub

                sub_list = [item.upper() for item in sub_list]               # upper sub 
        
                sub_list = list_for_table9(sub_list)

                print('after check and with table9, sub_list:', sub_list)

                print('ready to check Neo4j ----------------')

#----------------------------check index_list ---------------------------------------------------------#

                if index_list and sub_list[0] in index_list:              # check index_list, also sub[0] in index_list

                    try:                                 
                        print('had index_list, processing')
                        params = {'node_sub': sub_list}
                        query = """
                        match  (index_node) <-[to_index] - (question_node) <-[to_questions] - (answer_node) 
                        where ToUpper(index_node.name) in $node_sub
                        return question_node, answer_node 
                        """
                        result = conn.query(query, parameters=params)
                        msg = ''
                        for item in result:
                            if ('入选标准' not in item.data()['answer_node']['name'][:4]) and ('排除标准' not in item.data()['answer_node']['name'][:4]):
                                msg_QA =  '<b>DL04问题: </b>'+ item.data()['question_node']['name']  + '\n<b>DL04回答: </b>' + item.data()['answer_node']['name'] +'\n'
                                msg = msg_QA + msg

                        # for item in sub_list:
                        #     index_list.pop(index_list.index(item))

                        if index_list:
                            dict1 = {}
                            dict2 = {}
                            button_list = []

                            msg2 = '<b>此项下还有以下Q＆A Log中问题，请参照选择。您也可以输入其他问题。谢谢</b>'

                            print('index_list in action:', index_list)

                        for item in index_list:
                                        
                            dict1["sub"] = item
                            dict1 = json.dumps(dict1,ensure_ascii=False)
                            dict2["payload"] = "/inform_protocol"  + str(dict1) 
                            dict2["title"] = item
                            button_list.append(dict2)
                            dict1 = {}
                            dict2 = {}
                    
                        dispatcher.utter_message(text= ( msg + '\n' + msg2 ), buttons= button_list)          
    
                        return [SlotSet("sub",None), SlotSet("sub_list",None), SlotSet("item_number",None), SlotSet("index_list", index_list),
                                SlotSet("sender_id", sender_id),
                                SlotSet("sender_name", sender_name), 
                                SlotSet("site_id", site_id), 
                                SlotSet("version", version),
                                SlotSet("token", token)]
                        # return [SlotSet("sub",None)]                             # keep question_list
                    except:
                        print('error for check neo4j for index_list')
  
                node_item_list = []
# -------------------------- then, system will perform query --------------------------------#
        else:

            sub_list = []
            if item_number and main:
                print('---------------main:', main)
                node_item_number = main + '第' + item_number + '条'
                node_item_list = [node_item_number]
                print('node_item_number:', [node_item_number])
            else:
                node_item_list = []
             
        try:
 
            print('sub_list:', sub_list)
            print('node_item_list:', node_item_list)
            params = {'node_sub': sub_list, 'node_item': node_item_list}

            print('params:', params)
 
            query = """
            match (index_node) <-[to_index*0..1] - (question_node) <-[to_questions*0..1] - (answer_node) <- [has_answer*0..1] -(csp_node) -[r*] ->(entity_node) -[*0..3] ->(entity_value)
            where csp_node.label in ["入选标准", "排除标准","DL04"]  and  (( ToUpper(entity_node.name) in $node_sub )or (csp_node.name_item in $node_item))
            return collect(distinct index_node) as index_nodes, csp_node, collect( distinct  entity_value) as entity_values
            ORDER BY csp_node
            """
            result = conn.query(query, parameters=params)
            print('result:', result)
    # -------------------------- then, form dispatchd massage ---------------------------------#

            if len(result) == 0:
                # msg = '对不起，小易没有找到。我还需要学习'

                text_CRA = '我不太理解，我会转给负责咱们中心的CRA'

                payload = {
                    "userId": sender_id,
                    "question": message
                }
                print('payload:', payload)

                #请求头
                # header = {
                #     "content-type": "application/json",
                #     "token": token
                # }
                # print('payload:', payload)
                # print('header:', header)

                # url = 'http://127.0.0.1:8090/unansweredQuestion/addUnansweredQuestion'
                # res = requests.post(url,json=payload,headers=header)

                # print('res.text:',res.text)

                final_message = sender_name + '老师，您的问题"' + message +'"' + text_CRA_no_found
                dispatcher.utter_message(text=final_message)
                return [SlotSet("sub",None), SlotSet("sub_list",None), SlotSet("item_number",None),
                    SlotSet("index_list", index_list)]
                
            else:
                final_message = ''
                msg_csp = ''
                msg_entity_value_list = []
                s_node = []
                p_node = []

                for item in result:     

                    if item.data()['csp_node']['label'] != 'DL04':
                        if version == "1.0":
                            csp_description = item.data()['csp_node']['description']
                        else:
                            csp_description = item.data()['csp_node']['description_v2']
                        page_num = '试验方案第' + item.data()['csp_node']['page'] + '页'
                        name_item = item.data()['csp_node']['name_item']
    
                    else:
                        csp_description = item.data()['csp_node']['description']
                        name_item = item.data()['csp_node']['name_item']
                        page_num = '试验方案第' +item.data()['csp_node']['page'] + '页'

                    msg_csp = page_num + ' \n' + name_item + ' \n' + csp_description 

                    msg_entity_value = '\n'.join([(item['name'] + ' : \n' + item['description']) for item in item.data()['entity_values'] if 'description' in item.keys()])

                    final_message = final_message + msg_csp + msg_entity_value + '\n'
                        # for entity_value in item.data()['entity_values']:               # process entity value

                        #     try:
                        #         msg_entity_value1 = fill_name_des(5, 14, entity_value[:2]) 
                        #         msg_entity_value2 = fill_name_des(12, 8, entity_value[2:])
                                
                        #     except:
                        #         msg_entity_value1 = ''
                        #         msg_entity_value2 = '\n'
    
                            # msg_entity_value = msg_entity_value + msg_entity_value1 + msg_entity_value2[:-1]

                        # question_list = [ item['name'] for item in item.data()['q_nodes'] if 'label' in item.keys() and item['label'] == 'question']
 
                    index_list = [ item['name'] for item in item.data()['index_nodes'] if 'label' in item.keys() and item['label'] == 'question_index']
                            
                    if index_list:          

                        button_list = []

                        dict1 = {}
                        dict2 = {}

                        print('index_list in action:', index_list)

                        for item in index_list:
                                        
                            dict1["sub"] = item
                            dict1 = json.dumps(dict1,ensure_ascii=False)
                            dict2["payload"] = "/inform_protocol"  + str(dict1) 
                            dict2["title"] = item
                            button_list.append(dict2)
                            dict1 = {}
                            dict2 = {}
                            msg2 = '<b>此项下还有以下Q＆A Log中问题，请参照选择。您也可以输入其他问题。谢谢</b>'

                final_message = final_message + msg2

                print('final_message:', final_message)
    
                dispatcher.utter_message(text=final_message, buttons= button_list)
                # dispatcher.utter_message(text=( page_num + msg_csp + msg_entity_value + ' \n' +  msg2))

                return [SlotSet("sub",None), SlotSet("sub_list",None), SlotSet("item_number",None),
                        SlotSet("index_list", index_list),
                        SlotSet("sender_id", sender_id),
                        SlotSet("sender_name", sender_name), 
                        SlotSet("site_id", site_id), 
                        SlotSet("version", version),
                        SlotSet("token", token)]
        
        except:
            print('error for check neo4j entities')
            
            text_CRA = '我不太理解，我会转给负责咱们中心的CRA'

            payload = {
                "userId": sender_id,
                "question": message
            }
            print('payload:', payload)


            final_message = sender_name + '老师，您的问题"' + message +'"' + text_CRA_no_found
            dispatcher.utter_message(text=final_message)
            return [SlotSet("sub",None), SlotSet("sub_list",None), SlotSet("item_number",None)]
            # return [SlotSet("sub",None)]
            # return [AllSlotsReset()]
            # return []
class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return 'action_default_fallback'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = tracker.latest_message['text']
        print('message:', message)

        dispatcher.utter_message(text=("this is from fallback" +  message))

        # Revert user message which led to fallback.
        return []

class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return 'action_write_text'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = tracker.latest_message['text']
        sender_id = tracker.get_slot('sender_id')
        sender_name = tracker.get_slot('sender_name')
        site_id = tracker.get_slot('site_id')
        version = tracker.get_slot('version')
        token = tracker.get_slot('token')
        # token = 'eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE2ODI2ODU2MjYsInVzZXIiOnsiaWQiOjEyMzQ2NSwic3RhdHVzIjoxLCJjcmVhdGVkVGltZSI6bnVsbCwiY3JlYXRlZEJ5IjpudWxsLCJ1cGRhdGVkVGltZSI6bnVsbCwidXBkYXRlZEJ5IjpudWxsLCJzZXgiOmZhbHNlLCJ1c2VyTmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJFMTBBREMzOTQ5QkE1OUFCQkU1NkUwNTdGMjBGODgzRSIsIm5hbWUiOiJBZG1pbiAiLCJidWlsdEluIjp0cnVlLCJ0eXBlIjoxLCJhY3RpdmUiOnRydWUsInNpdGVWT0xpc3QiOltdLCJlbWFpbCI6bnVsbH0sInN1YiI6ImFkbWluIn0.-QHy3YbbelIWzWx8yvTqaaHbBjAIPWQK_O11Txg6msLEU_GX-Ld4VlGLOZGhdsJJCP1mYKFdhzZEits7sv20Sw'
        print('message:', message)
        text_CRA = '我不太理解，我会转给负责咱们中心的CRA'

        payload = {
            "userId": sender_id,
            "question": message
        }
        print('payload:', payload)

        #请求头
        header = {
            "content-type": "application/json",
            "token": token
        }
        print('payload:', payload)
        print('header:', header)

        try:
            url = 'http://127.0.0.1:8090/unansweredQuestion/addUnansweredQuestion'
            res = requests.post(url,json=payload,headers=header)

            print('res.text:',res.text)
        except:
            Continue

        dispatcher.utter_message(text=(sender_name +'老师，您的问题"' + message +'""' + text_CRA))

        # Revert user message which led to fallback.
        return [ SlotSet("sender_id", sender_id),
            SlotSet("sender_name", sender_name), 
            SlotSet("site_id", site_id), 
            SlotSet("version", version),
            SlotSet("token", token)
            
                ]
class ActionDefaultFallback(Action):
    """Executes the fallback action and goes back to the previous state
    of the dialogue"""

    def name(self) -> Text:
        return 'action_new_scope'

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        message = tracker.latest_message['text']
        sender_id = tracker.get_slot('sender_id')
        sender_name = tracker.get_slot('sender_name')
        site_id = tracker.get_slot('site_id')
        version = tracker.get_slot('version')
        token = tracker.get_slot('token')
        # token = 'eyJhbGciOiJIUzUxMiJ9.eyJleHAiOjE2ODI2ODU2MjYsInVzZXIiOnsiaWQiOjEyMzQ2NSwic3RhdHVzIjoxLCJjcmVhdGVkVGltZSI6bnVsbCwiY3JlYXRlZEJ5IjpudWxsLCJ1cGRhdGVkVGltZSI6bnVsbCwidXBkYXRlZEJ5IjpudWxsLCJzZXgiOmZhbHNlLCJ1c2VyTmFtZSI6ImFkbWluIiwicGFzc3dvcmQiOiJFMTBBREMzOTQ5QkE1OUFCQkU1NkUwNTdGMjBGODgzRSIsIm5hbWUiOiJBZG1pbiAiLCJidWlsdEluIjp0cnVlLCJ0eXBlIjoxLCJhY3RpdmUiOnRydWUsInNpdGVWT0xpc3QiOltdLCJlbWFpbCI6bnVsbH0sInN1YiI6ImFkbWluIn0.-QHy3YbbelIWzWx8yvTqaaHbBjAIPWQK_O11Txg6msLEU_GX-Ld4VlGLOZGhdsJJCP1mYKFdhzZEits7sv20Sw'
        print('message:', message)
        text_CRA = '现在小易还不能回答，我会转给负责咱们中心的CRA'

        payload = {
            "userId": sender_id,
            "question": message
        }
        print('payload:', payload)

        #请求头
        header = {
            "content-type": "application/json",
            "token": token
        }
        print('payload:', payload)
        print('header:', header)

        try:
            url = 'http://127.0.0.1:8090/unansweredQuestion/addUnansweredQuestion'
            res = requests.post(url,json=payload,headers=header)

            print('res.text:',res.text)
        except:
            Continue


        dispatcher.utter_message(text=(sender_name +'老师，您的问题"' + message +'""' + text_CRA))

        # Revert user message which led to fallback.
        return [ SlotSet("sender_id", sender_id),
            SlotSet("sender_name", sender_name), 
            SlotSet("site_id", site_id), 
            SlotSet("version", version),
            SlotSet("token", token)
                ]


class ValidateSimplePizzaForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_simple_protocol_form"

    def validate_main(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate main value."""
        print("in validate main")

        main = tracker.get_slot('main')

        sub = tracker.get_slot('sub')

        item_number = tracker.get_slot('item_number')

        if item_number:
            sub = ' '

        if slot_value.lower() not in ALLOWED_MAIN_TYPES:
            dispatcher.utter_message(text=f"We only accept" + ",".join(ALLOWED_MAIN_TYPES))
            return {"main": None}
        
        # dispatcher.utter_message(text=f"OK! You want to check {slot_value} in CSP.")
        return {"main": slot_value,"sub": sub}

    def validate_sub(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate sub value."""
        print("in validate sub")

        main = tracker.get_slot('main')
        
        sub = tracker.get_slot('sub')

        sub_list = []

        entities = tracker.latest_message['entities']

        for entities_value in tracker.latest_message['entities']:
            if entities_value.get('entity') == 'sub':
                print(entities_value.get('value'))
                sub_list.append(entities_value.get('value'))

        print('entities:', entities)

        print("main---------：",main)
        
        print("sub_list ---------：",sub_list)

        print("sub_ ---------：",sub)
        
        if main:

            if sub:

                # dispatcher.utter_message(text=f"OK! You want to check {sub_list} in CSP.")

                return {"sub": sub, "sub_list": sub_list}
                
            else:
                 
                return {"sub": None, "sub_list": None}
        else:
            if sub:
                return {"main": '入选标准', "sub_list": sub_list}
            else:
                return{"main": None}
            
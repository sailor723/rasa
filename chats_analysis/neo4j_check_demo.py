
import pandas as pd
import os
import pdfplumber
pd.set_option('max_colwidth',200)

# ----------------- MAIN CODE --------------------------------------------------

# question_file_name  = os.path.abspath('DL04_annotation_20220321 cyr combined.xlsx')
question_file_name  = os.path.abspath('/home/weiping/dev/DCTA/rasa/new_graph_build/DL04_annotation_20220321 cyr combined.xlsx')

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


chat_full_name  = os.path.join(os.getcwd(),'converted_log.csv')


df = pd.read_csv(chat_full_name,encoding='utf-8-sig')

#----------------------------- table 8 --------------------------------------------------------------
table8_name  = os.path.abspath('../new_graph_build/Table8.pdf')
pdf = pdfplumber.open(table8_name)

p0 = pdf.pages[0]
table = p0.extract_table()
df_table8 = pd.DataFrame(table[0:], columns=table[0])
df_table8.columns = ['name','description']

#----------------------------- table 9 --------------------------------------------------------------
table9_name  = os.path.abspath('../new_graph_build/Table9.pdf')
pdf = pdfplumber.open(table9_name)

p0 = pdf.pages[0]
table = p0.extract_table()
df_table9 = pd.DataFrame(table[0:], columns=table[0])
df_table9.columns = ['name','description']


## first df 
p0 = pdf.pages[0]
table = p0.extract_table()
df = pd.DataFrame(table[0:], columns=table[0])
df.columns = ['name','description']
#---------------------construcate entity and csp list from result --------------------------------------
entity_list = []
csp_list = []
for row, col in df.iterrows():
    if 'inform' not in col['text'] and '标准' in col['bot_category']:
 
        if col['bot_category'].strip() in ['入选标准第11条','入选标准第14条']:
            entity_list.append(col['sub_value'])

            csp_list.append(col['bot_text'])
        else:

            entity_list.append(col['sub_value'])
            csp_list.append(col['bot_category'])


#--------------------------check with orginal file -------------------------------------------------------
check_result = []

for item in list(zip(entity_list, csp_list)):

    if '入选标准第' in item[1]:
        if item[0] in df_inclusion[df_inclusion['入选标准'] == item[1].split('标准')[1].strip()]['Entity'].to_string():
            check_result.append(1)
        else:
            check_result.append(0)
            print(item)
    if '排除标准第' in item[1]:
        if item[0] in df_exclusion[df_exclusion['排除标准'] == item[1].split('标准')[1].strip()]['Entity'].to_string():
            check_result.append(1)
        else:
            check_result.append(0)
            print(item)
    else:
        b = "".join(df_table8[df_table8['name'] == item[0]]['description'].to_list())
        if b in item[1]:
            print('YES')
        else:
            print('NO')
    
        c = "".join(df_table9[df_table9['name'] == item[0]]['description'].to_list())
        if b in item[1]:
            print('YES')
        else:
            print('NO')

b = "".join(df_table8[df_table8['name'] == item[0]]['description'].to_list())


list_exclusion = [item for item in list2 if '排除标准第' in item]

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
        set p.type = 'entity'
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
        set p.type = 'entity'
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

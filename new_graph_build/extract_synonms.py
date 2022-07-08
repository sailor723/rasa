import os
# from spacy import displacy
import pandas as pd

nlu_file  = os.path.abspath('../data/nlu.yml')
sub_text  = os.path.abspath('sub.txt')

question_file_name  = os.path.abspath('DL04_annotation.xlsx')

df_inclusion = pd.read_excel(question_file_name, sheet_name='Inclusion',header=0)

#----------------------------process nlu -------------------------------------------------------------#
f = open(nlu_file,"r")   #设置文件对象
line = f.readline()
line = line[:-1]
synonym = False
i = 0
e_list = []
entity_dict = {}
e_key = []
e_value = []
e_value_working = []
new_synonym = False
while line:             #直到读取完文件
    line = f.readline()  #读取一行文件，包括换行符
    i += 1
    try:
        if line[0] == '-' and 'synonym' in line:
            synonym = True
            e_list.append(line)
           
            e_key.append(line.split(':')[1].split('\n')[0].strip())
            new_synonym = True
   
            print(e_key, '-----------------------------')

        elif line[0] == '-' and 'synonym' not in line:
            synonym = False
 
        if synonym:
            if ('examples' not in line) and ('synonym' not in line):
                if new_synonym:
                    e_value.append(e_value_working)
                    e_value_working = []
                new_synonym = False
                e_value_working.append(line.split('-')[1].split('\n')[0].strip())
                e_list.append(line)

        line = line[:-1] 
    except:
        continue
e_value_working.append(line.split('-')[1].split('\n')[0].strip())

dict_sym = dict(zip(e_key, e_value[1:]))
# print(e_list)
f.close()

# --------------------------------------process csp------------------------------------------------------------#
df_inclusion.info

sub_node_list = [item.split('、')[1].strip() for item in df_inclusion.loc[1]['Entity'].splitlines()]


entity_list = [','.join([s.split('\n')[0] for s in item]) for item in [ group_item.split('、')[1:] for group_item in df_inclusion['Entity']]]

df_inclusion['Entity'] = entity_list

df_inclusion['text'] = df_inclusion[['分类', 'Entity']].groupby('分类')['Entity'].transform(lambda x: ','.join(x))

x = df_inclusion[['分类','text']].drop_duplicates()

dict_entity = dict(zip(x['分类'],x['text']))


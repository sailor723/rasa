import spacy,os
from spacy.language import Language
from spacy import displacy
import pandas as pd
#-----------------------extract from synonms--------------------------#
nlu_file  = os.path.abspath('../data/nlu.yml')
f = open(nlu_file,"r")   #设置文件对象
line = f.readline()
line = line[:-1]
synonym = False
i = 0
e_list = []
while line:             #直到读取完文件
    line = f.readline()  #读取一行文件，包括换行符
    i += 1
    try:
        if (line[0] == '-') and ('synonym' in line  )       \
            and  ('排除标准' not in line) and ('入选标准' not in line) \
            and  ('项目编号' not in line) and ('方案短标题' not in line)   :
            synonym = True
        elif line[0] == '-' and 'synonym' not in line:
            synonym = False
 
        if synonym:
            if ('examples' not in line) and ('synonym' not in line):             \
                    e_list.append(line)
        line = line[:-1] 
    except:
        continue
f.close()
e_list =[ item.strip().split(' ')[1] for item in e_list]
#------------------Prepare nlp model---------------------------------------#
df = pd.read_csv("sub.txt",header = None)
df.columns = ['Entity']
E_list = [ item for item in df.Entity.to_list() if item not in ['项目名称', '标题', '项目编号', '编号', '方案短标题', '目标人群','版本']]
e_list.extend(E_list)

nlp = spacy.load("zh_core_web_md")
nlp.tokenizer.pkuseg_update_user_dict(e_list)
ruler = nlp.add_pipe("entity_ruler")
patterns = []

for entity in e_list:
    patterns.append({"label":"Entity", "pattern": entity})
ruler.add_patterns(patterns)

@Language.component("remove_cardinal")
def remove_grp(doc):
    original_ents = list(doc.ents)
    for ent in doc.ents:
        if ent.label_ == 'CARDINAL':
            original_ents.remove(ent)
    doc.ents = original_ents
    return(doc)
nlp.add_pipe("remove_cardinal")
nlp.analyze_pipes()
#------------------read excel---------------------------------------#

question_file_name  = os.path.abspath('DL04_annotation_combined.xlsx')

df = pd.read_excel(question_file_name, sheet_name='QA_log',header=0)

l1 = df['回答'].tolist()
l2 = df['问题'].tolist()

combine_list = []
for i in range(len(l1)):
    combine_list.append(str(l1[i]) + str(l2[i]))

entity_list = []
for item in combine_list:
    print('item:', item)
    doc = nlp(item)
    entity_list.append(",".join(list(set([t.text for t in doc.ents]))))

df.insert(8, '标题', entity_list)

# for ent in doc.ents:
#     print(ent.text, ent.label_)
 
# print('/'.join([t.text for t in doc]))


df.to_excel("updated.xlsx", sheet_name='QA_log_new')


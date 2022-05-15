import spacy,os
from spacy import displacy
import pandas as pd

nlu_file  = os.path.abspath('../data/nlu.yml')
sub_text  = os.path.abspath('sub.txt')

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
        if line[0] == '-' and 'synonym' in line:
            synonym = True
        elif line[0] == '-' and 'synonym' not in line:
            synonym = False
 
        if synonym:
            if ('examples' not in line) and ('synonym' not in line):
                e_list.append(line)
            if 'kras' in line:
                print('i_______', i)
                print(line)
                print(len(e_list))
        line = line[:-1] 
    except:
        continue
f.close()


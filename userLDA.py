import sys
sys.path.append("..")

#Load the dataset from the CSV and save it to 'data_text'
#Import相關資源
import matplotlib.pyplot as plt
import numpy as np
import jieba.analyse
import jieba
import codecs

# see logging events
import logging
logging.disable(50)

import os
from gensim import corpora, models, similarities
import gensim

import re
jieba.case_sensitive = True 
# 可控制對於詞彙中的英文部分是否為case sensitive, 預設False
from tqdm import tqdm, trange

userdict_path='..\\dcard_linebot\\LSI\\userDict.txt'
stopword_path='..\\dcard_linebot\\LSI\\stopword.txt'
# stopword_path='../dcard_linebot/LSI/stopword.txt'
#模型存放路徑
save_path='./LDA/'

#### Load data
import pandas as pd

from pytrends.request import TrendReq
from pprint import pprint

### build a user information and personal LDA    
def load_data(userID):
    data = pd.read_csv('./data/'+str(userID)+'.csv',encoding='utf-8')

    # We only need the Headlines text column from the data
    data_text = data[:][['title','href','context']]
    data_text['index'] = data_text.index

    documents = data_text
    # print(documents)
    return documents

def createFolder(directory):
    try:
        if not os.path.exists("./LDA/"+directory):
            os.makedirs("./LDA/"+directory)
    except OSError:
        print('Error: Creating directory. '+ directory)
        
#Jieba斷詞及去除停用字
def preprocess(context):
    result = []
    # if(context == 'NULL'): return result
    
    remove_msg = re.sub('[(%。，》／：…？/」▲※▼▲★●【｜】◎:&\'-.『』！!-〈〉‘’\n（）「；～＆ㄜ〰🔴🙂🤮🈶🤓🤧👏😯👆🌚😥😃🥴🌝😜😝😨🖐👌😁👼👻－👵👿📖🔆😮🌟🏭👎👈😳😇😣😁😖😩😫😙😞🤗🙂🤨🔔🤩😦🤮😇💡🙋🧐😁💜🤕😰👨🎉🎉👋💻🚀📢🐣🚩👀🔹🔸🔺🙇😟😬🐶🤯🤬🤪😍👧💁👊😱🔥🙂😣🤤🤫😥📌📍🐳😟😨😠👏😾🤫👉👇😑😆😂😄😱👿👌🙇🤵😟🧐～🙏👍💪🙄🙃😒👂😭😡🤦😢😅😀😭🌸😊🤔😊😏😔😐💥🐦💦😵😓😡💸🥺🤷🤦🤣🥳💩💢🤢👩🏻👩😧🔪😤💰😎😚🤭💝💞💓🥰💗💘🤝🍀🔻🎈🔎🙂👆🎓👣🗣🤳🙋🌀👥🙇)(a-zA-Z))]',"",context)
#     remove_msg = re.sub('[(餐廳 服務 廚師 主廚 菜色 食材 採用 店家 攤子 客人 環境 滋味 品項 座位 裝潢 料理 烹調 團隊 窗戶)]',"",remove_msg)
    seg_list = jieba.cut(remove_msg)
    final_msg = " ".join(seg_list)
    msg_drop = final_msg.strip().replace("  ", " ")
    msg_drop = msg_drop.strip().replace("    ", " ")
    msg_drop = msg_drop.strip().replace("  ", " ")
    final_msg= msg_drop.strip().replace("  ", " ")
    context = final_msg
    
        
    #去除停用字
    #載入停用詞字典
    f = open(stopword_path,encoding = 'utf-8-sig')
    stoplist = f.readlines()
    f.close()

    for i in range(len(stoplist)):
        stoplist[i] = re.sub('\n',"",stoplist[i])
        
    #開始消除停用字
    content = context.split(' ')
    del_context=[]
    for word in range(len(content)):
        for j in range(len(stoplist)):
            if content[word] == stoplist[j]:
                del_context.append(stoplist[j])

    #print("去除單詞:")
    #print(del_context)

    for k in range(len(del_context)):
        try:
            content.remove(del_context[k])
        except:
            print("",end="")
            #print(del_context[k]+":已刪除")

    #去除相同單詞
    temp = list(set(content))
    #恢復原本排列
    content= sorted(temp,key=content.index)
        
    #刪除一個字獨立成一詞的
    del_single_word=[]
    for l in range(len(content)):
        if len(content[l])<2:
            del_single_word.append(content[l])

    for n in range(len(del_single_word)):
        try:
            content.remove(del_single_word[n])
        except:
            print("",end="")

    #去除相同單詞
    temp = list(set(content))
    #恢復原本排列
    content = sorted(temp,key=content.index)
    # print("save")
    return content

def build_dictionary(userID,processed_docs):
    dictionary = gensim.corpora.Dictionary(processed_docs)
#     for word,index in dictionary.token2id.items(): 
#         print(word +" id:"+ str(index))
    dictionary.save(save_path + '/'+str(userID)+"/word.dict")
    return dictionary

def build_corpus(userID,processed_docs,dictionary):
    bow_corpus = [dictionary.doc2bow(document) for document in processed_docs if document != []]
    bow_corpus
    corpora.MmCorpus.serialize(save_path+'/'+str(userID)+"/bow_corpus.mm", bow_corpus)
    return bow_corpus

def build_personal_LDA(userID):
    createFolder(str(userID))
    documents = load_data(userID)
    processed_docs = documents['context'].map(preprocess)
    print(processed_docs[:10])
    dictionary = build_dictionary(userID,processed_docs)
    bow_corpus = build_corpus(userID,processed_docs,dictionary)
    
    lda_model = gensim.models.LdaMulticore(bow_corpus, num_topics=8, id2word=dictionary, passes=2)

    lda_model.save(save_path+'/'+str(userID)+'/bow_lda_model.lda')
    # For each topic, we will explore the words occuring in that topic and its relative weight
    for idx, topic in lda_model.print_topics(-1):
        print("Topic: {} \nWord: {}".format(idx, topic))
        print("\n")

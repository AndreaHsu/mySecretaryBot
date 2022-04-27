import sys
sys.path.append("..")
import os
import gensim
from gensim import corpora, models, similarities
import jieba.analyse
import jieba
jieba.case_sensitive = True 
import re
import csv
userdict_path='..\\dcard_linebot\\LSI\\userDict.txt'
stopword_path='..\\dcard_linebot\\LSI\\stopword.txt'

from userLDA import preprocess

def SearchBookmarkLDA(msgg,userID):

    lda_model = models.LdaModel.load("LDA/"+userID + '/bow_lda_model.lda')

    if (os.path.exists("LDA/"+userID + "/word.dict")):
        dictionary = corpora.Dictionary.load("LDA/"+userID + "/word.dict")
        bow_corpus = corpora.MmCorpus("LDA/"+userID + "/bow_corpus.mm") # 將數據流的語料變為內容流的語料
        print("Used files generated from first tutorial")
    else:
        print("Please run first tutorial to generate data set")

    temp = preprocess(msgg)
    print(temp)
    if(temp == []):
        temp = [msgg]
    print(temp)
    bow_vector = dictionary.doc2bow(temp)
    vec_lda = lda_model[bow_vector]
    
    print('判斷文章:\n'+msgg+"\n")
    print(lda_model[bow_corpus])
    # 建立索引
    index = similarities.MatrixSimilarity(lda_model[bow_corpus]) 
    print(index)
    # 計算相似度（前五名）
    # sims = index[vec_lda_tfidf]
    sims = index[vec_lda]
    print("********************************\n")

    sims = sorted(enumerate(sims), key=lambda item: -item[1])
    for i in range(len(sims[:8])):
        print(sims[:8][i])
        print(sims[:8][0][0])
    print(sims[:8])
    print(sims[:8][1][1])
    
    context_ID=[]
    for i in range(8):
        context_ID.append(int(sims[:8][i][0]))

    title_list = []
    url_list = []
    num = 0
    # 開啟 CSV 檔案
    print("open")
    with open("./data/"+userID+".csv", newline='',encoding = 'utf-8-sig') as csvFile:
        # 轉成一個 dictionary, 讀取 CSV 檔內容，將每一列轉成字典
        rows_dict = csv.DictReader(csvFile)
        rows = list(rows_dict)
        
        num = len(rows)
      # 迴圈輸出 指定欄位
        
        for i in context_ID:
            if(rows[i]['title'] != 'title'): 
                title_list.append(rows[i]['title'])
            if(rows[i]['href'] != 'href'): 
                url_list.append(rows[i]['href'])
            
    response = ""
    response = '小秘書提供以下書籤文章，給您參考:'+"\n" + '===============' + "\n"
    for i in range(len(title_list)):
        if i != len(title_list)-1:
            response = response + str(i+1) + '.' + title_list[i] + '\n' + url_list[i] + '\n' + '===============' + '\n'
        else:
            response = response + str(i+1) + '.' + title_list[i] + "\n" + url_list[i]

    return response,title_list,url_list
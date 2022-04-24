import re
import os
from gensim import corpora,similarities
import csv
from gensim.matutils import cossim
from userLDA import preprocess

def trustCos(msgg,Path):
    if (os.path.exists(Path + "word.dict")):
        dictionary = corpora.Dictionary.load(Path + "word.dict")
        bow_corpus = corpora.MmCorpus(Path+"bow_corpus.mm") # 將數據流的語料變為內容流的語料
        print("Used files generated from first tutorial")
    else:
        print("Please run first tutorial to generate data set")
        
    bow_vector = dictionary.doc2bow(preprocess(msgg))
    
    
    print('判斷文章:\n'+msgg+"\n")

    title_list = []
    url_list = []
    num = 0
    # 開啟 CSV 檔案
    with open("./data/fact.csv", newline='',encoding = 'utf-8-sig') as csvFile:
        # 轉成一個 dictionary, 讀取 CSV 檔內容，將每一列轉成字典
        rows_dict = csv.DictReader(csvFile)
        rows = list(rows_dict)
        
        num = len(rows)
      # 迴圈輸出 指定欄位
        for i in range(num):
            title_list.append(rows[i]['title'])
            url_list.append(rows[i]['href'])
    
    #cos餘弦相似度
    
    top = 0.0
    ID = 0
    for i in range(num):
        bow_vector1 = dictionary.doc2bow(preprocess(title_list[i]))
        score = cossim(bow_vector, bow_vector1)
        if(score > top):
            ID = i
            top = score
#         print(title_list[i],cossim(bow_vector, bow_vector1))
        
    print(title_list[ID],url_list[ID],top)
    
    response = ""
    if(top >= 0.09):
        response = '根據系統比對，這篇文章極度可疑，以下為政府相關澄清資訊文章，給您參考:'+"\n" + '===============' + "\n"
        response = response  + title_list[ID] + '\n' + url_list[ID] + '\n' + '===============' + '\n'
    final_score = int(top*100)

    return response ,final_score,title_list[ID],url_list[ID]
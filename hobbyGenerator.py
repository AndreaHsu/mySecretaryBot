import os
import sys
sys.path.append("..")
import gensim
from gensim import corpora, models, similarities
from dataBase import db,cursor

import re
from userLDA import preprocess

def calculate_hobby(unseen_document,Path):
    lda_model = models.LdaModel.load( Path + 'bow_lda_model.lda')
    if (os.path.exists(Path + "word.dict")):
        dictionary = corpora.Dictionary.load(Path + "word.dict")
        bow_corpus = corpora.MmCorpus(Path+"bow_corpus.mm") # 將數據流的語料變為內容流的語料
        print("Used files generated from first tutorial")
    else:
        print("Please run first tutorial to generate data set")

    bow_vector = dictionary.doc2bow(preprocess(unseen_document))
    vec_lda = lda_model[bow_vector]

    like = ""
    point = 0
    
    for index, score in sorted(vec_lda, key=lambda tup: -1*tup[1]):
        print("Score: {}\t Topic: {}".format(score, lda_model.print_topic(index, 5)))
        if(like == ""):
            if(score > 0.8):
                like = "極度有興趣"#"稍無興趣"#"極度有興趣"
            elif(score > 0.4):
                like = "有興趣"#"稍無興趣"#"有興趣"
            elif(score > 0.3):
                like = "普通可閱讀"#"稍無興趣"#"普通可閱讀"
            elif(score > 0.2):
                like = "稍無興趣"
            else:
                like = "沒興趣"
                
            point = score
            
    return like,point

def personal_like(userID,text):
    #產生個人喜好
    like = ""

    sql = "SELECT id FROM users WHERE userLineID = \'" + userID + "\';"
    # print (sql)
    try:
        # Execute the SQL command
        cursor.execute(sql)
        # 取得所有資料
        result = cursor.fetchone()
        print(result)
    except:
        print("Error: Unable to fetch the data")
            
    ID = result[0]
    Path = "./LDA/"+str(ID)+"/"
    print(text)
    like,point = calculate_hobby(text,Path)
    
    return like,point

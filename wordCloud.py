import jieba
from jieba.analyse import extract_tags
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pyimgur
import re

from key import CLIENT_ID

def wordcloud(title,text,imgID):
    fontPath = r'C:\Users\user\Downloads\NotoSansCJKtc-hinted\NotoSansCJKtc-Regular.otf'
    stopword_path ='.\..\\dcard_linebot\\LSI\\stopword.txt'
    #去除停用字
    #載入停用詞字典
    f = open(stopword_path,encoding = 'utf-8-sig')
    stoplist = f.readlines()
    f.close()

    for i in range(len(stoplist)):
        stoplist[i] = re.sub('\n',"",stoplist[i])

    # stopwords = {}.fromkeys(stoplist)

    content = "" + title + text

    # 設定使用 big5 斷詞
    # jieba.set_dictionary('CGF_dictionary.txt')
    wordlist = jieba.cut(text)
    words = " ".join(wordlist)

    my_wordcloud = WordCloud(font_path =fontPath, stopwords=stoplist,background_color='white',max_words=200).generate(words)

    # plt.imshow(my_wordcloud)
    # plt.axis("off")
    # picture = plt.show()

    my_wordcloud.to_file('.\\img\\'+str(imgID)+'.jpg')
    return save_img(imgID)
    
def save_img(imgID):
    PATH = "./img/"+str(imgID) +".jpg"

    im = pyimgur.Imgur(CLIENT_ID)
    uploaded_image = im.upload_image(PATH, title=str(imgID))
    print(uploaded_image.title)
    print(uploaded_image.link)
    print(uploaded_image.size)
    print(uploaded_image.type)
    
    return uploaded_image.link
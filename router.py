# import flask dependencies  
from flask import Flask,request
import requests
import json
import csv
from linebot import ( 
    LineBotApi, WebhookHandler
)   
from linebot.exceptions import ( 
    InvalidSignatureError
)
from linebot.models import ( 
    MessageEvent, TextMessage, TextSendMessage,QuickReply,ImageSendMessage,
    QuickReplyButton,MessageAction,CameraAction,CameraRollAction,
    LocationAction,FlexSendMessage,LocationMessage,TemplateSendMessage,
    CarouselTemplate,CarouselColumn,PostbackTemplateAction,MessageTemplateAction,
    URITemplateAction,ButtonsTemplate,PostbackAction,URIAction,ConfirmTemplate,
    BubbleContainer,ImageComponent,StickerSendMessage,LocationSendMessage,
    ImageCarouselTemplate,ImageCarouselColumn,PostbackEvent,
)
from initialUser import setup_crawer
from textHandler import handleText,user_describe
from dataBase import db,cursor
from userLDA import build_personal_LDA
from crawler import crawl_only_text,crawl
from textRank import ExtractableAutomaticSummary
from otherHandler import handleImage,handleVideo,handleAudio,handleLocation,handleSticker
from key import linebotApi,webhookHandler

# initialize the flask app  
app = Flask(__name__)  
line_bot_api = linebotApi
handler = webhookHandler

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # print(body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# handle user profile
@app.route('/currency_exchange', methods=['POST'])
def handle_currency_exchange():
    # body = request.get_data(as_text=True)
    # print(request.headers)
    # print(request.form)
    # print(body)
    
    like = ""
    hobby = []
    point = {"hobby":0,
             "believe":0,
             "summary":0,
             "hot":0,
             "recommend":0}
    userID = ""
    data = request.form
    print(data)
    for key, value in data.items():
        if(key.find('point') != -1):
            point[value] = 1
        elif(key.find('like') != -1):
            if value != '':
                like += value + "，"
                hobby.append(value)
            
    userID = data["userID"]
            
    print(like)
    print(point)
    print(userID)
    
    sql = "INSERT INTO users (userLineID, hobby, believe, summary, hot,recommend) VALUES (\'" + userID + "\',\'" + like + "\'," + str(point['believe']) + ',' + str(point['summary']) + ',' + str(point['hot']) + ',' + str(point['recommend']) + ');'
    print (sql)
    try:
       # Execute the SQL command
        cursor.execute(sql)
        db.commit()
#         db.close()
        cursor.execute('SELECT last_insert_id()')
        ID = cursor.fetchone()
        print(ID)
        ID = ID[0]
        print(ID)
        print("finish")
    except:
        print ("Error: unable to fetch data")
    
    for item in hobby:
        setup_crawer(item,ID)
    # ID = 18
    build_personal_LDA(ID)
    return 'Personal setting finished!'

@app.route('/get_img', methods=['POST','GET'])
def handle_get_img():
    body = request.get_data(as_text=True)
    print(body)
    
    return get_img(2)

@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data[0:1] == "A":
        url = event.postback.data[2:]
        print(url)
        
        text = crawl_only_text(url)
        #產生摘要
        demo = ExtractableAutomaticSummary(text)
        demo.calculate()
        summary = demo.get_abstract(4)
        print(summary)
        
        text_message = []
        try:
            contents = json.load(open('summary_flex.json','r',encoding='utf-8'))
            print(contents["body"]["contents"][0]["contents"][1]["text"])

            for i in range(4):
                print(summary[i])
                contents["body"]["contents"][i]["contents"][1]["text"] = summary[i]
                
            text_message.append(FlexSendMessage(alt_text='summary',contents=contents))
        except:
            print("OH NO!!")
            
        line_bot_api.reply_message(
            event.reply_token,
            text_message)

    elif event.postback.data[0:1] == "B":
        result = event.postback.data[2:].split('&')
        url = result[1]
        print(url)
        ID = result[0]
        print(ID)
        userID = event.source.user_id
        print(userID)
        #檢查是否已經加入
        sql = "SELECT * FROM bookmarks WHERE article_url = \'" + url + "\' AND userLINEID = \'"+ userID +"\';"
        print(sql)
        try:
            cursor.execute(sql)
            # 取得所有資料
            result = cursor.fetchone()
            print(result)
        except:
            print ("Error: unable to fetch data")
        
        if(result == None):
            #寫入資料庫
            sql = "INSERT INTO bookmarks (userLINEID,article_url) VALUES (%s,%s)"
            print (sql)
            try:
                # Execute the SQL command
                cursor.execute(sql,(userID,url))
                db.commit()

                print("bookmark insert finish")
            except:
                print ("Error: unable to fetch data")
            
            title,text,keywords,image = crawl(url)
            
            mseg_drop = text.strip().replace("\n", " ")
            msg_drop = mseg_drop.strip().replace("  ", " ")
            msg_drop = msg_drop.strip().replace("    ", " ")
            msg_drop = msg_drop.strip().replace("  ", " ")
            text= msg_drop.strip().replace("  ", " ")
            
            keywords_list = ""
            for keyword in keywords:
                keywords_list += keyword
                keywords_list += ','
            print(text)
            print(keywords_list)
            with open ('./data/'+str(ID)+'.csv', 'a+', newline='',encoding = 'utf-8-sig') as csvFile:
                print("oxo")
                # build csvwriter
                writer = csv.writer(csvFile)
                writer.writerow([title,url,text,keywords_list])
                
            print('=======================finish insert=======================')
            
            #看看是否加入書籤的文章已達重新訓練LDA的門檻
            sql = "SELECT * FROM bookmarks WHERE userLineID=\'" +userID+"\';"
            print (sql)
            try:
                # Execute the SQL command
                cursor.execute(sql)
                result = cursor.fetchall()
                if (len(result) >= 2):
                    build_personal_LDA(int(ID))
                    print("rebuild LDA")
#                     # train 完後 delete
#                     sql = "DELETE FROM bookmarks WHERE userLineID=\'" +userID+"\''"
#                     print (sql)
                print("bookmark select finish")
            except:
                print ("Error: unable to fetch bookmarks data")
            
        else:
            line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='此文章已經在書籤內囉~'))
            
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='加入書籤完成囉~'))
    
@handler.add(MessageEvent)#, message=TextMessage)
def handle_message(event):
    print(event.source)

    if(event.type == 'message'):
        message = event.message
        if(message.type == 'text'):
            reply = handleText(message, event.reply_token, event.source)
        elif(message.type == 'image'):
            reply = handleImage(message,event.reply_token,event.source)
        elif(message.type == 'video'):
            reply = handleVideo(message,event.reply_token,event.source)
        elif(message.type == 'audio'):
            reply = handleAudio(message,event.reply_token,event.source)
        elif(message.type == 'location'):
            reply = handleLocation(message,event.reply_token,event.source)
        elif(message.type == 'sticker'):
            reply = handleSticker(message,event.reply_token,event.source)
    
    line_bot_api.reply_message(
        event.reply_token,
        reply)
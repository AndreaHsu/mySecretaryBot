import re
import json
from linebot import ( 
    LineBotApi, WebhookHandler
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
from dataBase import db,cursor
from crawler import urlfind,crawl,crawl_only_text
from wordCloud import wordcloud
from hobbyGenerator import calculate_hobby
from internetVolume import internet_volume
from opendata import trustCos
from searchBookmark import SearchBookmarkLDA
from dcard_linebot.CFG.crawer_Dcard import crawing_all_related_articles_multi

# user request message
user_describe = dict()

def handleText(message, replyToken, source):
    if(message.text == '個人設定'):
        #quickreply
        text_message = TextSendMessage(text='請選擇',
                                quick_reply=QuickReply(items=[
                                    QuickReplyButton(action=MessageAction(label="首次設定", text="設定--首次")),
                                    QuickReplyButton(action=MessageAction(label="修改設定", text="設定--修改"))
                                ]))
    elif(re.match("設定--",message.text)):
        if(message.text == '設定--首次'):
            text_message=TextSendMessage(text='https://liff.line.me/1656310997-pPydj0KQ')
        elif(message.text == '設定--修改'):
            text_message = TextSendMessage(text='OK')
    elif(message.text == 'Finish setting'):
         text_message=TextSendMessage(text='完成個人設定')
            
    elif(re.search("http",message.text) != None):
        url = urlfind(message.text)[0]
        # print(url)
        title =""
        text = ""
        keywords = []
        image =""
        wordcloud_link =""
        # check if we can crawl the url
        try:
            title,text,keywords,image = crawl(url)
            # print(text)
            if(text == ""):
                text_message = TextSendMessage(text='小秘書目前無法爬取該文章$',emojis = [{
                    "index": 12,
                    "productId": "5ac1bfd5040ab15980c9b435",
                    "emojiId": "024"
                }])
                return text_message
        except:
            text_message = TextSendMessage(text='小秘書目前無法爬取該文章$',emojis = [{
                    "index": 12,
                    "productId": "5ac1bfd5040ab15980c9b435",
                    "emojiId": "024"
                }])
            return text_message

        # 先看資料庫裡有沒有該文章
        sql = "SELECT * FROM articles WHERE url = \'" + url + "\';"
        print (sql)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # 取得所有資料
            result = cursor.fetchone()
            print(result)
            
            ID = result[0]
            wordcloud_link = wordcloud_link +result[8]
                
            print(ID,title,keywords,wordcloud_link,image)
            print("article select finish")
        except:
            print ("Error: unable to fetch data")
            
        if(result == None):
            print(title,"======",text,"======",keywords,"======",image)
            
            keywords_list = ""
            
            for keyword in keywords:
                keywords_list += keyword
                keywords_list += ','
            
            #寫入資料庫
            sql = "INSERT INTO articles (title,url,keywords,top_img) VALUES (%s,%s,%s,%s)"
            # print (sql)
            try:
                # Execute the SQL command
                cursor.execute(sql,(title,url,keywords_list,image))
                db.commit()
                
                cursor.execute('SELECT last_insert_id()')

                imgID = cursor.fetchone()
                imgID = imgID[0]
                print(imgID)
                
                print("article insert finish")
            except:
                print ("Error: unable to fetch data")
            
            wordcloud_link = wordcloud(title,text,imgID)

            sql = "UPDATE articles SET wordcloud_link=\'"+ wordcloud_link +" \'WHERE id =\'"+ str(imgID) +"\';"
            # print (sql)
            try:
                # Execute the SQL command
                cursor.execute(sql)
                db.commit()
                print("article update wordcloud_link finish")
            except:
                print ("Error: unable to fetch data")
        
        #產生個人喜好
        like = ""
        userID = source.user_id

        sql = "SELECT * FROM users WHERE userLineID = \'" + userID + "\';"
        # print (sql)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # 取得所有資料
            result = cursor.fetchone()
            print(result)
            if(result == None):
                text_message = TextSendMessage(text='請先填寫基本資料!\n讓小秘書先行了解你$',emojis = [{
                        "index": 19,
                        "productId": "5ac1bfd5040ab15980c9b435",
                        "emojiId": "003"
                    }])
                return text_message
        except:
            print("Error: unable to fetch data")
        
        ID = result[0]
        choice = {}
        choice["hobby"] = result[2]
        choice["believe"] = result[3]
        choice["hot"] = result[5]

        Path = "./LDA/"+str(ID)+"/"
        # print(text)
        like,point = calculate_hobby(text,Path)
        
        #產生聲量
        volume,score = internet_volume(keywords[0:3])
        print(volume,score)
        
        #產生信賴度
        """response,fact_score,fact_title,fact_url = trustCos(text,"./LDA/fact/")
        print(response,fact_score,fact_title,fact_url)
        commend = ""
#         fact_score = "???"
#         commend = "目前無可疑"
        if(response == ''):
            fact_score = "???"
            commend = "目前無可疑"
        else:
            commend = "十分可疑"
        """
        fact_score = "average"
        commend = "目前無可疑"
        
        #回傳訊息
        text_message = []
        
        try:
            contents = json.load(open('flex.json','r',encoding='utf-8'))
            # print(contents["contents"][0]["header"]["contents"][2])
            item = contents["contents"][0]["header"]["contents"][2]["contents"][0]["width"]
            # print(item)
            #更改個人喜好
            star = point/0.8*100
            if(star > 1): star = 100
            contents["contents"][0]["header"]["contents"][1]["text"] = str(int(star))+"%"
            contents["contents"][0]["body"]["contents"][0]["contents"][0]["text"] = like
            contents["contents"][0]["header"]["contents"][2]["contents"][0]["width"] = str(int(star))+"%"
            #更改可信賴度
            contents["contents"][1]["header"]["contents"][1]["text"] = str(fact_score)+"%"
            contents["contents"][1]["body"]["contents"][0]["contents"][0]["text"] = commend
            if(fact_score == 'average'):
                contents["contents"][1]["header"]["contents"][2]["contents"][0]["width"] = str(80)+"%"
            else:
                contents["contents"][1]["header"]["contents"][2]["contents"][0]["width"] = str(fact_score)+"%"
            #更改聲量
            contents["contents"][2]["header"]["contents"][1]["text"] = str(score)+"%"
            contents["contents"][2]["body"]["contents"][0]["contents"][0]["text"] = volume
            contents["contents"][2]["header"]["contents"][2]["contents"][0]["width"] = str(score)+"%"
            
            print("success flex message change")
            text_message.append(FlexSendMessage(alt_text='flex',contents=contents))
        except:
            print("Error: flex message change")
        
        # if(response!= ""):
            # text_message.append(TextSendMessage(text = response))
        
        text_message.append(TextSendMessage(text ="以下是此文章的文字雲，幫助您一目瞭然!"))
        text_message.append(ImageSendMessage( 
                original_content_url= wordcloud_link,
                preview_image_url= wordcloud_link))
            
        if(len(title) > 40):
            title = title[0:39]
#             print(title)
        text_message.append(TemplateSendMessage(
                        alt_text='Buttons template',
                        template=ButtonsTemplate(
#                             thumbnail_image_url=wordcloud_link,
#                             thumbnail_image_url=image,
                            title=title,
                            text='Please select',
                            actions=[
                                PostbackTemplateAction(
                                    label='查看摘要',
                                    display_text='查看摘要',
                                    data='A&'+url
                                ),
                                URIAction(
                                    label='查看正文',
                                    uri=url
                                ),
                                PostbackTemplateAction(
                                    label='加入書籤',
                                    display_text='加入書籤',
                                    data='B&'+str(ID)+'&'+url
                                ),
                            ]
                        )
                    ))
        
    elif(message.text == '推薦文章'):
        userID = source.user_id
        sql = "SELECT hobby FROM users WHERE userLineID = \'" + userID + "\';"
        # print (sql)
        try:
           # Execute the SQL command
            cursor.execute(sql)
            # 取得所有資料
            result = cursor.fetchone()
            if(result == None):
                text_message = TextSendMessage(text='請先填寫基本資料!\n讓小秘書先行了解你$',emojis = [{
                        "index": 19,
                        "productId": "5ac1bfd5040ab15980c9b435",
                        "emojiId": "003"
                    }])
                return text_message

            hobby = result[0].split("，")
            print(hobby)
            print("hobby select finish")
        except:
            print ("Error: unable to fetch data")
        
        text_message = []
        length = len(hobby)-1
        title_list =[]
        total_href =[]
        
        for i in range(length):
            titles,articles_id,href = crawing_all_related_articles_multi(hobby[i],1)
            print("finish")
            title_list.append(titles)
            total_href.append(href)
        print(title_list)
        print(total_href)
        print("craw finish")

        text_message.append(TextSendMessage(text='為你推薦以下文章!!'))
        text_message.append(TemplateSendMessage(
             alt_text='Dcard articles',
             template=CarouselTemplate(columns=[
                 CarouselColumn(
                         thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                         title=title_list[0][0],
                         text='文章1',
                         actions=[
                             URIAction(
                                 label='馬上查看',
                                 uri=total_href[0][0]
                             )
                         ]
                     ),
                 CarouselColumn(
                         thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                         title=title_list[0][1],
                         text='文章2',
                         actions=[
                             URIAction(
                                 label='馬上查看',
                                 uri=total_href[0][1]
                             )
                         ]
                     ),
                 CarouselColumn(
                         thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                         title=title_list[0][2],
                         text='文章3',
                         actions=[
                             URIAction(
                                 label='馬上查看',
                                 uri=total_href[0][2]
                             )
                         ]
                     ),
                 CarouselColumn(
                         thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                         title=title_list[0][3],#[1][0],
                         text='文章4',
                         actions=[
                             URIAction(
                                 label='馬上查看',
                                 uri=total_href[0][3]#[1][0]
                             )
                         ]
                     ),
                 CarouselColumn(
                         thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                         title=title_list[0][4],#[1][1],
                         text='文章5',
                         actions=[
                             URIAction(
                                 label='馬上查看',
                                 uri=total_href[0][4]#[1][1]
                             )
                         ]
                     ),
                 CarouselColumn(
                         thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                         title=title_list[0][5],#[1][2],
                         text='文章6',
                         actions=[
                             URIAction(
                                 label='馬上查看',
                                 uri=total_href[0][5]#[1][2]
                             )
                         ]
                     )
             ]))) 
    
    elif(message.text == '收錄文章'):
        userID = source.user_id
        # check the person has registered
        sql = "SELECT * FROM users WHERE userLineID = \'" + userID + "\';"
        # print (sql)
        try:
            # Execute the SQL command
            cursor.execute(sql)
            # 取得所有資料
            result = cursor.fetchone()
            print(result)
            if(result == None):
                text_message = TextSendMessage(text='請先填寫基本資料!\n讓小秘書先行了解你$',emojis = [{
                        "index": 19,
                        "productId": "5ac1bfd5040ab15980c9b435",
                        "emojiId": "003"
                    }])
                return text_message
        except:
            print("Error: unable to fetch data")
        # start asking bookmark
        try:
            sql = "UPDATE users SET server = 1 Where userLineID = \'"+ userID+ "\';"
            print(sql)
            cursor.execute(sql)
            db.commit()
        except:
            print("wrong")

        user_describe[userID] = ""
        text_message = TextSendMessage(text='請描述你想找的收錄文章~句子或是詞語都可以喔~')
    else:
        userID = source.user_id
        cursor.execute('SELECT server FROM users WHERE userLineID = %(uid)s' , {'uid': userID})
        result = cursor.fetchone()
        print(type(result[0]))
        num = result[0]
        if(num == 1):
            if(message.text == '沒有'):
                cursor.execute('UPDATE users SET server = 0 Where userLineID = %(uid)s' , {'uid': userID})
                db.commit()
                print(user_describe[userID])
                text_message = []
                text_message.append(TextSendMessage(text='好的!正在搜尋書籤~'))
                
                sql = "SELECT id FROM users WHERE userLineID = \'" + userID + "\';"
                print (sql)
                try:
                    # Execute the SQL command
                    cursor.execute(sql)
                    # 取得所有資料
                    result = cursor.fetchone()
                    print(result)
                except:
                    print("fail to fetch id")
            
                ID = result[0]
                response,bookmark_title,bookmark_url = SearchBookmarkLDA(user_describe[userID],str(ID))
                print(response)
#                 text_message.append(TextSendMessage(response))
                text_message.append(TemplateSendMessage(
                     alt_text='bookmark articles',
                     template=CarouselTemplate(columns=[
                         CarouselColumn(
                                 thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                                 title=bookmark_title[0],
                                 text='書籤1',
                                 actions=[
                                     URIAction(
                                         label='馬上查看',
                                         uri=bookmark_url[0]
                                     )
                                 ]
                             ),
                         CarouselColumn(
                                 thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                                 title=bookmark_title[1],
                                 text='書籤2',
                                 actions=[
                                     URIAction(
                                         label='馬上查看',
                                         uri=bookmark_url[1]
                                     )
                                 ]
                             ),
                         CarouselColumn(
                                 thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                                 title=bookmark_title[2],
                                 text='書籤3',
                                 actions=[
                                     URIAction(
                                         label='馬上查看',
                                         uri=bookmark_url[2]
                                     )
                                 ]
                             ),
                         CarouselColumn(
                                 thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                                 title=bookmark_title[3],
                                 text='書籤4',
                                 actions=[
                                     URIAction(
                                         label='馬上查看',
                                         uri=bookmark_url[3]
                                     )
                                 ]
                             ),
                         CarouselColumn(
                                 thumbnail_image_url='https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png',
                                 title=bookmark_title[4],
                                 text='書籤5',
                                 actions=[
                                     URIAction(
                                         label='馬上查看',
                                         uri=bookmark_url[4]
                                     )
                                 ]
                             )
                     ]))) 
                user_describe[userID] = ""
                
            else:
                print(message.text)
                user_describe[userID] += message.text
                print(user_describe[userID])
                text_message = TextSendMessage(text='好的!還有甚麼要補充描述的嗎?沒有的話請輸入"沒有"喔~')
        else:
            text_message = []
            text_message.append(TextSendMessage(text='感謝您的訊息~'))
            text_message.append(TextSendMessage(text='小秘書還在學習如何處理相關訊息!'))
            text_message.append(TextSendMessage(text='不妨點選選單中的功能與小秘書互動喔$',emojis = [{
                    "index": 17,
                    "productId": "5ac1bfd5040ab15980c9b435",
                    "emojiId": "001"
                }]))
            
    return text_message
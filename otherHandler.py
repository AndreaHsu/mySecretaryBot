from linebot.models import ( 
    MessageEvent, TextMessage,TextSendMessage,StickerSendMessage
)
def handleExceptText():
    text_message = []
    text_message.append(TextSendMessage(text='感謝您的訊息~'))
    text_message.append(TextSendMessage(text='小秘書還在學習如何處理相關訊息!'))
    text_message.append(TextSendMessage(text='不妨點選選單中的功能與小秘書互動喔$',emojis = [{
            "index": 17,
            "productId": "5ac1bfd5040ab15980c9b435",
            "emojiId": "001"
        }]))
    return text_message 

def handleImage(message, replyToken, source):
    return handleExceptText()

def handleVideo(message, replyToken, source):
    return handleExceptText()

def handleAudio(message, replyToken, source):
    return handleExceptText()

def handleLocation(message, replyToken, source):
    return handleExceptText()

def handleSticker(message, replyToken, source):
    #sticker reply
    sticker_message = StickerSendMessage(
                                        package_id='1',
                                        sticker_id='1'
                                    )
    return sticker_message

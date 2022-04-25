from pytrends.request import TrendReq

def internet_volume(keywords):
    #get top keywords on the Net
    pytrend = TrendReq(hl='en-US', tz=360)
    df = pytrend.trending_searches(pn='taiwan')
    top = df.head()

    keywords.append(top.values[0][0])
    keywords.append(top.values[1][0])
    
    pytrend.build_payload(
         kw_list=keywords,
         cat=0,
         timeframe='now 4-H',
         geo='TW',
         gprop='')
    data = pytrend.interest_over_time()

    total = dict()
    article_volume = 0
    top_volume = 0
    i=0
    for key in keywords:
        total.update({key: 0})
        for item in data[key]:
            total[key] += item
        if i < 3:
            article_volume += total[key]
        else :
            top_volume += total[key]
        i+=1

    print(total)
    volume = ""
    score = 0
    
    if(article_volume >= top_volume):
        score = 100
    else:
        score = int(article_volume/top_volume*100)
    
    if(score >= 90):
        volume = "網路熱搜"
    elif(score >= 70):
        volume = "熱度不錯"
    elif(score >= 50):
        volume = "普通文章"
    elif(score >= 30):
        volume = "稍無熱潮"
    else:
        volume = "最近冷門"
        
    return volume,score
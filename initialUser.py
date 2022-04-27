import sys
sys.path.append("..")
from dcard_linebot.CFG.crawer_Dcard import crawing_all_related_articles_multi,carwling_an_article_context,save_csvfile

def setup_crawer(topic,userId):
    save_Path = "./data/"
    save_Name = str(userId)
    title_list,articles_id,total_href = crawing_all_related_articles_multi(topic,1)
    context_list,hastag_list = carwling_an_article_context(title_list,articles_id)
    print("ok")
    save_csvfile(save_Path,save_Name,title_list,total_href,context_list,hastag_list)
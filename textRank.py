import networkx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import re
import jieba
jieba.case_sensitive = True 
import csv

class ExtractableAutomaticSummary:
    def __init__(self,article):
        """
        抽取式自动摘要
        :param article: 文章内容，列表，列表元素为字符串，包含了文章内容，形如['完整文章']
        :param num_sentences: 生成摘要的句子数
        """
        self.article = article
        self.stopwords = None
        self.word_embeddings = {}
        self.sentences_vectors = []
        self.ranked_sentences = None
        self.similarity_matrix = None
        
    def __get_sentences(self,sentences):
        """
        断句函数
        :param sentences:字符串，完整文章，在本例中，即为article[0]
        :return:列表，每个元素是一个字符串，字符串为一个句子
        """
        sentences = re.sub('([（），。！？\?])([^”’])', r"\1\n\2", sentences)  # 单字符断句符
        sentences = re.sub('(\.{6})([^”’])', r"\1\n\2", sentences)  # 英文省略号
        sentences = re.sub('(\…{2})([^”’])', r"\1\n\2", sentences)  # 中文省略号
        sentences = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', sentences)
        sentences = sentences.replace(' ', '\n')
        # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
        sentences =sentences.rstrip()  # 段尾如果有多余的\n就去掉它
        # 很多规则中会考虑分号;，但是这里忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
        return sentences.split("\n")

    def __get_stopwords(self):
        # 加载停用词，下载地址见最上注释
        self.stopwords = [line.strip() for line in open('./../dcard_linebot/LSI/stopword.txt',encoding='utf-8').readlines()]

    def __remove_stopwords_from_sentence(self,sentence):
        sentence = [i for i in sentence if i not in self.stopwords]
        return sentence

    def __get_word_embeddings(self):
    	# 获取词向量，不要第一行，第一行是该词向量表的统计信息
        with open('./../dcard_linebot/wiki.zh.vector', encoding='utf-8') as f:
            lines = f.readlines()
            for _, line in enumerate(lines):
                if _ != 0:
                    values = line.split()
                    word = values[0]
                    coefs = np.asarray(values[1:], dtype='float32')
                    self.word_embeddings[word] = coefs

    def __get_sentence_vectors(self,cutted_clean_sentences):
        # 获取句向量，将句子中的每个词向量相加，再取均值，所得即为句向量
        for i in cutted_clean_sentences:
            if len(i) != 0:
                v = sum(
                    [self.word_embeddings.get(w.strip(), np.zeros((400,))) for w in i]
                ) / (len(i) + 1e-2)
            else:
                v = np.zeros((400,))
                # 因为预训练的词向量维度是300
            self.sentences_vectors.append(v)

    def __get_simlarity_matrix(self):
        # 计算相似度矩阵，基于余弦相似度
        self.similarity_matrix = np.zeros((len(self.sentences_vectors), len(self.sentences_vectors)))
        for i in range(len(self.sentences_vectors)):
            for j in range(len(self.sentences_vectors)):
                if i != j:
                    self.similarity_matrix[i][j] = cosine_similarity(
                        self.sentences_vectors[i].reshape(1, -1), self.sentences_vectors[j].reshape(1, -1)
                    )
                    # 这里reshape不可少，不信你查sklearn手册

    def calculate(self):
        self.__get_word_embeddings()
        # 获取词向量
        self.__get_stopwords()
        # 获取停用词
        sentences = self.__get_sentences(self.article)
        cutted_sentences = [jieba.cut(s) for s in sentences]
        # 对每个句子分词
        cutted_clean_sentences = [self.__remove_stopwords_from_sentence(sentence) for sentence in cutted_sentences]
        # 句子分词后去停用词
        # 先分词，再去停用词，直接去停用词会把每个字分开，比如变成‘直 接 去 停 用 词 会 把 每 个 字 分 开’
        self.__get_sentence_vectors(cutted_clean_sentences)
        # 获取句向量
        self.__get_simlarity_matrix()
        # 获取相似度矩阵
        nx_graph = networkx.from_numpy_array(self.similarity_matrix)
        print(nx_graph)
        try:
            scores = networkx.pagerank(nx_graph,max_iter=800)
        except:
            scores = networkx.pagerank_numpy(nx_graph)
        # 将相似度矩阵转为图结构
        self.ranked_sentences = sorted(
            ((scores[i], s) for i, s in enumerate(sentences)), reverse=True
        )
        # 排序

    def get_abstract(self,num_abstract_sentences):
        summary = []
        for i in range(num_abstract_sentences):
#             print(self.ranked_sentences[i][0])
#             print(self.ranked_sentences[i][1])
            summary.append(self.ranked_sentences[i][1])
            
        return summary

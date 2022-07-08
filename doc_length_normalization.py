# -*- coding : utf-8-*-
import re
import os
from pybloom_live import ScalableBloomFilter
import pandas as pd
import math

MAX_SIZE = 10000000
term_pattern = re.compile(r'\s*([\u4e00-\u9fa5]+)\s+')  # 匹配中文词项
global count
data = pd.read_csv('inverted_index_table.csv', sep=',', header=0, usecols=[1, 2], encoding='utf-8')
term = list(data['词项'])
doc_frequency = list(data['doc_frequency'])
load_dic = dict(zip(term, doc_frequency))


def build_stopwords_bloom():
    """
    构建stop_words的bloom过滤器
    :return: stopwords_bloom
    """
    stop_file = open('cn_stopwords.txt', 'r', encoding='utf-8')  # 打开停用词表文件
    lines = stop_file.readlines()
    stopwords_bloom = ScalableBloomFilter(initial_capacity=MAX_SIZE)
    for line in lines:
        lline = line.rstrip()
        stopwords_bloom.add(lline)
    return stopwords_bloom


def length_normalization():
    """
    进行文件的长度归一化操作
    :return: 长度归一化后的词项：权重文件
    """
    count = 1
    for root, ds, fs in os.walk(base):
        for f in fs:
            '''
             对每个文件操作
            '''
            # 创建当前文件的单词字典
            words_dic = dict()
            fullname = os.path.join(root, f)
            docID = count
            print("start normalize doc" + str(docID))
            cur_f = open(fullname, 'r', encoding='gbk', errors='ignore')
            content = cur_f.read()
            all_words = re.findall(term_pattern, content)  # 找到该文件中所有的中文匹配项 存放在all_words

            for word in all_words:
                if word in stop_words_bloom:
                    all_words.remove(word)
                else:
                    # 如果该单词之前已经出现过
                    if words_dic.__contains__(word):
                        words_dic[word] += 1
                    # 如果该单词在之前没有出现过
                    else:
                        words_dic[word] = 1
            # 计算tf取对数+1
            for word in words_dic:
                words_dic[word] = 1 + math.log10(words_dic[word])

            L2 = 0
            # 计算文档长度的2范数
            for word in words_dic:
                L2 += math.pow(words_dic[word], 2)
            L2 = math.sqrt(L2)

            # 计算归一化长度
            for word in words_dic:
                words_dic[word] /= L2
            cur_f.close()

            # 写入文档
            t = list(words_dic.keys())
            l = list(words_dic.values())
            df = pd.DataFrame(zip(t, l), columns=['词项', '归一化长度'])
            path = './length_normalized_docs_txt/normalized_doc' + str(docID) + '.txt'
            df.to_csv(path, encoding='utf-8-sig')
            print("finished normalize doc" + str(docID))
            count += 1
            # with open('ddddchain.txt', 'w', encoding='utf-8') as fp:




if __name__ == "__main__":
    stop_words_bloom = build_stopwords_bloom()
    base = "./data/"
    length_normalization()

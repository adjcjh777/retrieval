# -*- coding : utf-8-*-
import re
import os
from pybloom_live import ScalableBloomFilter
import pandas as pd
import math

MAX_SIZE = 10000000
term_pattern = re.compile(r'\s*([\u4e00-\u9fa5]+)\s+')  # 匹配中文词项
global count


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


def travers_data(base):
    """
    遍历整个文件夹并返回未进行停用词去除的词项字典
    :param base:
    :return: terms_dic
    """
    terms_dic = dict()
    '''
        保存所有的词项的集合 
        term_dic的key是词项 value是一个字典
        value的key是df value是docID的列表
    '''
    fullname_list = []
    count = 1
    for root, ds, fs in os.walk(base):
        for f in fs:
            '''
             对每个文件操作
            '''
            fullname = os.path.join(root, f)
            fullname_list.append(fullname)
            docID = count
            print("start doc" + str(docID))
            cur_f = open(fullname, 'r', encoding='gbk', errors='ignore')
            content = cur_f.read()
            all_words = re.findall(term_pattern, content)  # 找到该文件中所有的中文匹配项 存放在all_words

            # 对于在当前文件中出现的所有单词
            for word in all_words:
                # 如果该单词之前已经出现过
                if terms_dic.__contains__(word):
                    if docID not in terms_dic[word].keys():
                        terms_dic[word][docID] = 1  # 在该文档中第一次出现tf赋初始值为1
                    else:
                        terms_dic[word][docID] += 1  # tf+1
                # 如果该单词在之前没有出现过
                else:
                    terms_dic[word] = {}
                    terms_dic[word][docID] = 1

            cur_f.close()
            print("finished doc" + str(docID))
            count += 1

    return terms_dic


def del_stopwords_in_the_end(origin_dic: dict, stopwords_bloom):
    """
    在写入csv之前进行停用词的删除
    :return:
    """
    key_list = list(origin_dic.keys())
    for key in key_list:
        if key in stopwords_bloom:
            del origin_dic[key]
    return origin_dic


def dic_to_csv(dic_data: dict, doc_frequency):
    """
    将字典写入csv文件
    :param dic_data: 处理完的字典数据
    :param doc_frequency: 统计后的df列表
    :return:
    """
    k = list(dic_data.keys())
    df = doc_frequency
    v = list(dic_data.values())
    df = pd.DataFrame(list(zip(k, df, v)), columns=['词项', 'doc_frequency', 'docID-tf'])
    df.to_csv('inverted_index_table_add_tf_idf.csv', encoding='utf-8-sig')


def calculate_tf_idf(sorted_dic, doc_frequency):
    """
    计算所有词项在出现文档中的的tf_idf
    :return:
    """
    cnt = 0
    for i in sorted_dic:
        for j in sorted_dic[i]:
            tf_idf = (1 + math.log(sorted_dic[i][j], 10)) * math.log(N / doc_frequency[cnt], 10)
            sorted_dic[i][j] = tf_idf
        cnt += 1
    return sorted_dic


if __name__ == "__main__":
    stop_words_bloom = build_stopwords_bloom()
    base = "./data/"
    all_term_dic = travers_data(base)
    result_dic = del_stopwords_in_the_end(all_term_dic, stop_words_bloom)
    # 先将字典根据词项排序
    sorted_dic = dict((k, result_dic[k]) for k in sorted(result_dic.keys()))

    # 统计doc_frequency
    doc_frequency = []
    for term in sorted_dic.keys():
        doc_frequency.append(len(sorted_dic[term]))
    N = 532
    sorted_dic_with_tf_idf = calculate_tf_idf(sorted_dic, doc_frequency)

    print('正在写入数据')
    dic_to_csv(sorted_dic_with_tf_idf, doc_frequency)
    print('数据写入完成')

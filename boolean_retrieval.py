import pandas as pd
import time
import math
import os

"""
读取csv
"""
print("loading inverted index")

data = pd.read_csv('inverted_index_table.csv', sep=',', header=0, usecols=[1, 3], encoding='utf-8')
term = list(data['词项'])
docID_tf = list(data['docID-tf'])
key_list_of_docID_tf = []  # 存放docID_tf中每一项字典的key构成的列表
# 将从csv读取的字符串形式的字典转换成字典
for i in range(len(docID_tf)):
    docID_tf[i] = eval(docID_tf[i])
    key_list_of_docID_tf.append(list(docID_tf[i].keys()))
# 处理完后docID——tf是字典构成的列表
normalized_doc_list = []
dic1 = dict(zip(term, key_list_of_docID_tf))  # 是一个key为词项 value为出现该词项的文件序号的列表
files = os.listdir('./data/')

def load_doc():
    """
    在程序准备阶段读取532个长度归一化后的文件到内存
    :return: normalized_doc_list
    """
    print("loading docs")
    base = './length_normalized_doc_with_stopwords/'
    cnt = 1
    while cnt <= 532:
        fullname = base + 'normalized_doc' + str(cnt) + '.csv'
        docID = cnt
        # print("loading doc" + str(docID))
        df_1 = pd.read_csv(fullname)
        key = []
        value = []
        for item in df_1["词项"]:  # “词项”用作键
            key.append(item)
        for j in df_1["归一化长度"]:  # “归一化长度”用作值
            value.append(j)
        dic = dict(zip(key, value))
        normalized_doc_list.append(dic)
        cnt += 1


def relevance_sort(index_of_terms, input_term_dic: dict, doc_set):
    """
    文档相似度排序
    :param index_of_terms:查询词项在倒排索引表中的索引
    :param input_term_dic:输入的词项构成的字典 values为归一化后的长度 1 + log10(tf)
    :param doc_set: 按照要求求得的词项的集合
    :return:
    """
    cos = {}  # 记录文档doc和输入相似度的字典
    doc_term = {}
    for doc in doc_set:
        doc_term[doc] = []
        cos[doc] = 0.0
        # 对每篇文档求其和输入文档的相似度cos(doc,input)
        for i in index_of_terms:
            # 从所有词项的列表中根据索引找到i词项在当前文档中的tf_idf （已读入docID_tf)
            tmp = 0
            if term[i] in normalized_doc_list[doc - 1]:
                tmp = normalized_doc_list[doc - 1][term[i]]
                doc_term[doc].append(tmp)
            cos[doc] += tmp * input_term_dic[term[i]]

    if len(cos) > 1:
        # 结果序列长度大于一时输出排序后的结果
        cos_tuple = sorted(cos.items(), key=lambda x: x[1], reverse=True)
        cos_dic_list = []
        for cos_pair in cos_tuple:  # 将元组转化为字典
            cos_pair_dic = {}
            cos_pair_list = list(cos_pair)
            cos_pair_dic[cos_pair_list[0]] = cos_pair_list[1]
            cos_dic_list.append(cos_pair_dic)
        final_res = []

        end_time = time.perf_counter()

        print("共找到" + str(len(cos_dic_list)) + "篇文档")
        t = 1
        print("查询结果如下：")
        for item in cos_dic_list:
            for j in set(item):
                final_res.append(files[j - 1])
                print("No. %d" % t, end=' ')
                t += 1
                print("doc_No.{}".format(j), end=" ")
                print(files[j - 1])
        return final_res,end_time  # 返回排序后的文件列表
    else:
        end_time = time.perf_counter()
        # 结果序列长度小于等于1直接输出
        if len(cos) == 0:
            print("查询结果为空！")

        else:
            final_res = []
            for i in list(cos.keys()):
                final_res.append(files[i - 1])
            print("共找到" + str(len(final_res)) + "篇文档")
            print("查询结果如下：")
            t = 1
            print("No. %d" % t, end=' ')
            t += 1
            print(final_res[0])
            return final_res,end_time


def and_retrieval():
    """
     求所有词项docID的交集
     :return:
     """
    print("请输入以and连接的查询项：", end='')
    s = input().replace(' ', '')  # 去除用户输入可能多输的空格
    start_time = time.perf_counter()  # 用户输入结束，计时开始
    input_term_list = list(s.split("and"))  # 以AND分割词项存入列表
    if len(input_term_list) == 1:
        print("参数不足，请重新输入")
        return
    # 将输入当成文档 构造长度归一化的输入文档
    input_term_dic = {}
    for word in input_term_list:
        input_term_dic[word] = 1
    L2 = math.sqrt(len(input_term_list))
    for word in input_term_dic:
        input_term_dic[word] /= L2

    # 找到词项的索引 从0开始
    index_of_terms = []

    try:
        for t in input_term_list:
            index_of_terms.append(term.index(t))

    except ValueError:
        print("查询失败！ 查询词不存在！")
        return

    docID_set = set()
    for item in key_list_of_docID_tf[index_of_terms[0]]:
        docID_set.add(item)
    docID_set.update(key_list_of_docID_tf[index_of_terms[0]])

    # 用intersection方法求交集
    for j in range(len(index_of_terms)):
        s2 = set()
        s2.update(key_list_of_docID_tf[index_of_terms[j]])
        docID_set = docID_set.intersection(s2)

    # #用&符号求交集
    # sig_time_start = time.perf_counter()
    # for j in range(len(index_of_terms)):
    #     s2 = set()
    #     s2.update(key_list_of_docID_tf[index_of_terms[j]])
    #     docID_set = docID_set & s2
    # sig_time_end = time.perf_counter()
    # print('&时间:%s毫秒' % ((sig_time_end - sig_time_start) * 1000))

    # 把求得的目标文档列表和输入查询构成的文档传入排序函数 输出排序后的结果
    sorted_res,end_time = relevance_sort(index_of_terms, input_term_dic, docID_set)
    write_query(sorted_res, input_term_list)

    print('查询时间:%s毫秒' % ((end_time - start_time) * 1000))


def or_retrieval():
    """
    多词or查询
    :return:
    """
    print("请输入以or连接的查询项：", end='')
    s = input().replace(' ', '')  # 去除用户输入可能多输的空格
    start_time = time.perf_counter()  # 用户输入结束，计时开始
    input_term_list = list(s.split("or"))  # 以AND分割词项存入列表
    if len(input_term_list) == 1:
        print("参数不足，请重新输入")
        return
    # 将输入当成文档 构造长度归一化的输入文档
    input_term_dic = {}
    for word in input_term_list:
        input_term_dic[word] = 1
    L2 = math.sqrt(len(input_term_list))
    for word in input_term_dic:
        input_term_dic[word] /= L2

    # 找到词项的索引 从0开始
    index_of_terms = []

    try:
        for t in input_term_list:
            index_of_terms.append(term.index(t))

    except ValueError:
        print("查询失败! 查询词不存在！")
        return

    docID_set = set()

    for j in index_of_terms:
        docID_set.update(key_list_of_docID_tf[j])

    docID_list = list(docID_set)
    docID_list.sort()
    # 把求得的目标文档列表和输入查询构成的文档传入排序函数 输出排序后的结果
    final_res,end_time=relevance_sort(index_of_terms, input_term_dic, docID_list)

    print('查询时间:%s毫秒' % ((end_time - start_time) * 1000))


def not_retrieval():
    """
    not查询 可以只有一项 not a1 不需要排序，则不需要长度归一化
    :return:
    """
    print("请输入以not开头 not连接的查询项（形式如：not a1 not a2)：", end='')
    s = input().replace(' ', '')  # 去除用户输入可能多输的空格
    start_time = time.perf_counter()  # 用户输入结束，计时开始
    input_term_list = list(s.split("not"))  # 以AND分割词项存入列表
    del input_term_list[0]
    res = set(range(1, 532))  # 初始化集合为全集 然后逐个求差集得到结果
    r = set()
    # 对出现的词项逐个求差集
    for i in input_term_list:
        try:
            tmp = set(dic1[i])
            r = res.difference(tmp)
        except KeyError:  # 如果词项i不在语料库中 在出现keyerror时抛出异常 将tmp置为全集
            tmp = set(range(1, 532))
            r = res.difference(tmp)

    final_res = list(r)
    final_res.sort()
    end_time = time.perf_counter()

    print("共找到" + str(len(final_res)) + "篇文档")
    print("查询结果如下：")

    if len(final_res) == 0:
        print("查询结果为空！")
    else:
        t = 1
        for i in final_res:
            print("No. %d" % t, end=' ')
            t += 1
            print("doc_No.{}".format(i), end=" ")
            print(files[i - 1])

    print('查询时间:%s毫秒' % ((end_time - start_time) * 1000))


def mix_retrieval():
    """
    and or not 混合检索 不需要排序
    :return:
    """
    print("请按如下格式输入(括号请按全角形式输入)：(A1 and A2...AN) and (B1 or B2...BM) and not (C1 or C2...CK)")
    s = input().replace(' ', '')  # 去除用户输入可能多输的空格
    start_time = time.perf_counter()  # 用户输入结束，计时开始
    try:
        lst = list(s.split("）"))  # 将输入以）分割为三部分每一部分形式为 （a1 and a2   （b1 or b2  （c1 or c2
        # 处理第一个括号
        part1 = lst[0][1:]  # 从a1的第一个字符开始
        lstpart1 = list(part1.split("and"))  # 提取第一部分的所有词项
        r = dic1[lstpart1[0]]  # 先初始化r集合为第一部分中的第一个词项出现的所有文档的列表
        if len(lstpart1) > 1:  # 如果第一部分的词项数大于一个
            for i in range(1, len(lstpart1)):
                r = list(set(r).intersection(dic1[lstpart1[i]]))  # 对包含剩下词项的文件序号列表求交集

        # 处理第二个括号
        part2 = lst[1][4:]  # 从b1的第一个字符开始 不读前面的and
        lstpart2 = list(part2.split('or'))  # 第二个括号内的词项
        r1 = dic1[lstpart2[0]]
        if len(lstpart2) > 1:  # 如果第二部分长度大于一个词项
            for i in range(1, len(lstpart2)):
                r1 = list(set(r1).union(dic1[lstpart2[i]]))  # 对包含剩下词项的文件序号列表求并集
        r = list(set(r).intersection(r1))  # 第一第二个括号对应的文档序号列表求交集

        # 处理第三个括号
        part3 = lst[2][7:]  # 从c1的第一个字符开始 不读前面的and not
        lstpart3 = list(part3.split('or'))  # 第三个括号内的词项
        r2 = dic1[lstpart3[0]]  # 先求第三项的并集
        if len(lstpart3) > 1:
            for i in range(1, len(lstpart3)):
                r2 = list(set(r2).union(dic1[lstpart3[i]]))  # 对包含剩下词项的文件名列表求并集
        r = list(set(r).difference(r2))  # 第一第二个括号和第三个括号对应的文档列表求差集

        end_time = time.perf_counter()  # 找到所有文档，计时结束

        print("共找到" + str(len(r)) + "篇文档")
        t = 1
        for i in r:
            print("No. %d" % t, end=' ')
            t += 1
            print("doc_No.{}".format(i), end=" ")
            print(files[i - 1])
        # 相关度排序

        print('查询时间:%s毫秒' % ((end_time - start_time) * 1000))

    except:
        print("查询失败! 查询词不存在！")


def write_query(sorted_res, input_term_list):
    """
    将最终排序后的结果写到指定文件夹中 文件名为 词项+空格+词项...txt
    :param sorted_res: 排序后的查询结果文档
    :param input_term_list: 输入的词项表
    :return:
    """
    path = './query/'  # 写入到query文件夹
    filename = input_term_list[0]
    for i in range(1, len(input_term_list)):
        filename += ' ' + input_term_list[i]
    filename += '.txt'
    fp = open(path + filename, 'w+')
    for item in sorted_res:
        str1 = item + '\n'
        fp.write(str1)
    fp.close()


def mode_choose():
    """
    选择需要查询的模式
    :return: None
    """
    print("请输入对应的数字选择所需的检索")
    print("[1]AND查询")
    print("[2]OR查询")
    print("[3]NOT查询")
    print("[4]多词的AND、OR、NOT查询")
    print("输入其他数字退出系统")


if __name__ == "__main__":
    load_doc()  # 载入语料库和准备过程
    while 1:
        mode_choose()
        n = input()
        if n == '1':
            and_retrieval()
            print("按下任意键继续。", end="")
            t = input()
        elif n == '2':
            or_retrieval()
            print("按下任意键继续。", end="")
            t = input()
        elif n == '3':
            not_retrieval()
            print("按下任意键继续。", end="")
            t = input()
        elif n == '4':
            mix_retrieval()
            print("按下任意键继续。", end="")
            t = input()
        else:
            break
    # """
    # 创建GUI
    # """
    # root = tkinter.Tk()
    # width = 500
    # height = 500
    # screenwidth = root.winfo_screenwidth()
    # screenheight = root.winfo_screenheight()
    # root.title('布尔检索')
    # size_geo = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
    # root.geometry(size_geo)  # 对应的格式为宽乘以高加上水平偏移量加上垂直偏移量
    # label = tkinter.Label(root, text="Boolean Retrieval", font=("Times New Roman", 30), fg="black")
    # label.pack()  # 调用pack方法将label标签显示在主界面，后面也会用到就不一一解释了
    # # tkinter.Label(root, text="输入查询式（注意空格）：").grid(row=5)
    # search_button = tkinter.Button(root, text="开始查找", command=and_retrieval)
    # search_button.pack(side='right')
    # root.resizable(None,None)
    #
    # tk_entry = tkinter.Entry(root)
    #
    # root.mainloop()

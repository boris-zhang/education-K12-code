#!/usr/local/var/pyenv/versions/anaconda3-5.3.1/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
File Name           : question_semantic_similarity.py
Description         : 计算词集合的语义相似度。
                        1. 读取题目增量训练模型，题目数据
                        2. 计算题目词集之间的相似度
                        3. 将相似度高于阈值的结果写入题目相似度表
Created at          : 2019/12/3
Lastly updated at   : 2019/12/26
---------------------------------------------------------------------------
"""
__author__ = 'zhang zhiyong'


import warnings
warnings.filterwarnings("ignore")

import datetime
import argparse
from gensim.models import word2vec

import sys
sys.path.append("../pub/lib/")
import mysql_conn as msc
import general_logging as gl
import text_mining_lib as tml

LOGFILEPATH = './log/question_semantic_similarity_%s.log' % datetime.datetime.now().strftime('%Y-%m-%d')


def load_wordVectors(model_filepath):
    loginfo = 'loding question word2ven model...'
    gl.write_log(logpath, 'info', loginfo)

    model = word2vec.Word2Vec.load(model_filepath)
    vocab = list(model.wv.vocab.keys())  # 所有的单词
    return model, vocab


def fetch_dest_segwords(tablename, field_value):
    mysql = msc.MyPymysqlPool("dbMysql")
    sql = ''.join(['SELECT question_seqno, question_stem, question_stem_segment_clear FROM ', \
                   tablename, " where is_segmented=1 and in_tablename='", field_value, "'", ])
    rst = mysql.getAll(sql)
    mysql.dispose()

    loginfo = ' %d matched questions have been fetched.' % len(rst)
    gl.write_log(logpath, 'info', loginfo)
    return rst


def fetch_base_segwords(tablename, field_value):
    mysql = msc.MyPymysqlPool("dbMysql")
    sql = ''.join(['SELECT question_seqno, question_stem, question_stem_segment_clear FROM ', \
                   tablename, " where is_segmented=1 and grade_name like '三年级%'", \
                              " and in_tablename='", field_value, "'", ])
    rst = mysql.getAll(sql)
    mysql.dispose()

    loginfo = ' %d base questions have been fetched.' % len(rst)
    gl.write_log(logpath, 'info', loginfo)
    return rst


def calculate_similarity(model, word1_list, word2_list):
    similarity = -1
    try:
        similarity = model.n_similarity(word1_list, word2_list)
    except KeyError:
        loginfo = ' The words similarity is not available!'
        gl.write_log(logpath, 'error', loginfo)

    return similarity

def insert_question_similarity(model, vocab, dest_records, base_records, threshold, tablename):
    mysql = msc.MyPymysqlPool("dbMysql")

    # 计算rst中两两记录之间的相似度，将大于阈值的存入question_similarity_table
    i = 0
    j = 0
    for dest_record in dest_records:
        # mysql.begin()  # 开启事务
        seqno1 = dest_record[0]
        stem1 = dest_record[1]
        segwords1 = dest_record[2]
        segwords1_list = segwords1.split()
        max_similarity = -1
        max_seqno = -1
        for base_record in base_records:
            seqno2 = int(base_record[0])
            stem2 = base_record[1]
            segwords2 = base_record[2]
            segwords2_list = segwords2.split()

            if len(segwords1_list)>0 and len(segwords2_list)>0:
                similarity = calculate_similarity(model, segwords1_list, segwords2_list)
                if similarity > max_similarity:
                    max_similarity = similarity
                    max_seqno = seqno2
                if (similarity >= threshold):
                    sql = ''.join(['insert into ', tablename,
                                   "(question_seqno1,question_seqno2,question_stem1,question_stem2," \
                                   "question_stem_segment1,question_stem_segment2,similarity,load_time)" \
                                   " values(", str(seqno1), ",", str(seqno2), ",'", str(stem1), "','", str(stem2),
                                   "','", str(segwords1), "','", str(segwords2), "',", str(similarity), \
                                   ", CURRENT_TIMESTAMP());"])
                    mysql.insert(sql)
                    i += 1
        j += 1
        print('seqno1, max_seqno, max_similarity: ', seqno1, max_seqno, max_similarity)
        mysql.end()  # 结束提交
    mysql.dispose()
    loginfo = '%d similar rows have been inserted into %s!' % (i, tablename)
    gl.write_log(logpath, 'info', loginfo)


def comand_line_set():
    args = argparse.ArgumentParser(description='Word2vec words retrieval information', epilog='Information end')
    args.add_argument("-l", type=str, dest="logpath", help="the log path", default=LOGFILEPATH)
    args.add_argument("-m", type=str, dest="word2Vec_question_filepath", help="the path of word2vec model",
                      default='./model/word2Vec_question_rebuild.model')
    args.add_argument("-t", type=str, dest="question_segmentation_table", help="the segmentation question table name",
                      default='core.question_similarity_prepare')
    args.add_argument("-f", type=str, dest="dest_field", help="the searched in_table field value",
                      default='question_baseinfo_testerror')
    args.add_argument("-a", type=str, dest="base_field", help="the base in_table field value",
                      default='question_baseinfo_crawler')
    args.add_argument("-d", type=str, dest="question_similarity_table", help="the question similarity table",
                      default='core.question_similarity_rebuild')
    args.add_argument("-i", type=int, dest="threshold", help="the similarity threshold",
                      default=0.85)
    args = args.parse_args()
    args_dict = args.__dict__
    return args_dict


if __name__=='__main__':
    global logpath

    args_dict = comand_line_set()
    logpath = args_dict.get("logpath")
    word2Vec_question_filepath = args_dict.get("word2Vec_question_filepath")
    question_segmentation_tablename = args_dict.get("question_segmentation_table")
    dest_field = args_dict.get("dest_field")
    base_field = args_dict.get("base_field")
    question_similarity_tablename = args_dict.get("question_similarity_table")
    threshold = args_dict.get("threshold")

    gl.write_log(logpath, 'info', '\n\n')
    loginfo = 'starting to calculate question semantic similarity ...'
    gl.write_log(logpath, 'info', loginfo)

    dest_rst = fetch_dest_segwords(question_segmentation_tablename, dest_field)
    dest_records = list(list(x.values()) for x in dest_rst)
    base_rst = fetch_base_segwords(question_segmentation_tablename, base_field)
    base_records = list(list(x.values()) for x in base_rst)

    model, vocab = load_wordVectors(word2Vec_question_filepath)
    insert_question_similarity(model, vocab, dest_records, base_records, threshold, question_similarity_tablename)

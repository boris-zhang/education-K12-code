#!/usr/local/var/pyenv/versions/anaconda3-5.3.1/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
File Name          : question_stem_segmentation.py
Description        : 对题干分词，支持多关键词精确检索和语义拓展查询。
                    1. 从题目相似度准备表中读入题干
                    2. 使用Jieba进行分词，使用了comp用户字典，停用词字典
                    3. 将分词结果写入分词题目信息表（题目流水号, 题干，题干分词）
Created at         : 2019/12/2
Lastly updated at  : 2019/12/26
---------------------------------------------------------------------------
"""
__author__ = 'zhang zhiyong'

import datetime
import argparse
import re

import sys
sys.path.append("../pub/lib/")
import mysql_conn as msc
import text_mining_lib as tml
import general_logging as gl


# only accept Chinese and English characters
GOOD_WORDS = 'en&cn'
# CUT_WORDS = '[’!"#$%&\'()*+,-./:;<=>?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
CUT_WORDS = '[a-zA-Z0-9’!"#$&\',．＿①②③④⑤()()（）./:：;；?@，。?★、…【】《》？“”‘’！[\\]^_`{|}~]+'
LOGFILEPATH = 'question_stem_segmentation_%s.log' % datetime.datetime.now().strftime('%Y-%m-%d')


def write_segmented_words(tablename, seqno, stemwords, segwords):
    mysql = msc.MyPymysqlPool("dbMysql")
    sql = ''.join(['update ', tablename, " set is_segmented=1, question_stem_segment='", \
                   segwords.strip(' '), "' where question_seqno=", str(seqno)])
    try:
        mysql.update(sql)
    except Exception:
        print('update error: ', sql)
    mysql.dispose()


def segment_questions(records, tablename):
    i = 0
    for record in records:
        seqno = record["question_seqno"]
        stemwords = record["question_stem"]
        segmented_words = tml.words_segment(stemwords, stopwords, GOOD_WORDS, HMM=True) # 实际检测有HMM效果更好
        segwords = re.sub(CUT_WORDS, '', str(segmented_words))
        segwords = tml.iterate_replacements(segwords, '\\', '')
        segwords = tml.iterate_replacements(segwords, '  ', ' ')   # 将segwords中多个空格迭代替换为1个空格
        write_segmented_words(tablename, seqno, stemwords, segwords)
        if i % 500 == 0:
            loginfo = ' progress status: %d ' % i
            gl.write_log(logpath, 'info', loginfo)
        i += 1
    loginfo = ' Total %d keyword\'s segmented words have been writen.' % i
    gl.write_log(logpath, 'info', loginfo)


def get_records(tablename):
    mysql = msc.MyPymysqlPool("dbMysql")
    sql = ''.join(['SELECT question_seqno, upper(question_stem) as question_stem FROM ', \
                   tablename, " where is_segmented=0", ])
    rst = mysql.getAll(sql)
    mysql.dispose()

    loginfo = ' %d rows are fetched.' % len(rst)
    gl.write_log(logpath, 'info', loginfo)
    return rst


def comand_line_set():
    args = argparse.ArgumentParser(description='word segmentation for keywords in question table', epilog='')
    # optional parameter
    args.add_argument("-l", type=str, dest="logpath", help="the log path",
                      default='./log/' + LOGFILEPATH)
    args.add_argument("-q", type=str, dest="question_segmentation_table", help="the segmentation question table",
                      default='core.question_similarity_prepare')
    args.add_argument("-p", type=str, dest="comp_dictpath", help="the path of comp dictionary file",
                      default='../pub/dict/dict_comp_math.txt')
    args.add_argument("-s", type=str, dest="stopword_path", help="the path of stop words file",
                      default='../pub/dict/comp_stop_words_less.txt')

    args = args.parse_args()
    args_dict = args.__dict__
    return args_dict


if __name__ == '__main__':
    global logpath

    args_dict = comand_line_set()
    logpath = args_dict.get("logpath")
    question_tablename = args_dict.get("question_segmentation_table")
    comp_dictpath = args_dict.get("comp_dictpath")
    stopword_path = args_dict.get("stopword_path")

    gl.write_log(logpath, 'info', '\n\n')
    loginfo = 'question segmentation starting...'
    gl.write_log(logpath, 'info', loginfo)

    # preload dicts to save running time
    tml.load_dicts(comp_dictpath, logpath)
    stopwords = tml.get_stopwords(stopword_path, logpath)

    records = get_records(question_tablename)
    segment_questions(records, question_tablename)

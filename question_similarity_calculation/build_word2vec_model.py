#!/usr/local/var/pyenv/versions/anaconda3-5.3.1/bin/python
# -*- coding: utf-8 -*-
"""
---------------------------------------------------------------------------
File Name           : build_word2vec_model.py
Description         : 计算词集合的语义相似度。
                        1. 读取词集合，增量训练已有的word2vec模型
                        2. 利用训练后的模型计算不同词集之间的相似度
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
import multiprocessing

import sys
sys.path.append("../pub/lib/")
import mysql_conn as msc
import general_logging as gl
import text_mining_lib as tml

LOGFILEPATH = './log/build_word2vec_model_%s.log' % datetime.datetime.now().strftime('%Y-%m-%d')


def build_model(model_filepath, sentences, embedding_size=128, in_window=5, in_min_count=5):
    w2vModel = word2vec.Word2Vec(sentences, sg=1, size=embedding_size, window=in_window,
                                 min_count=in_min_count, workers=multiprocessing.cpu_count())
    w2vModel.save(model_filepath)
    loginfo = ' model %s has been built initially!' % model_filepath
    gl.write_log(logpath, 'info', loginfo)


def incrementally_build_model(original_modelpath, new_model_filepath, sentences):
    model = word2vec.Word2Vec.load(original_modelpath)
    model.build_vocab(sentences, update=True)
    print(model.corpus_count, model.iter)
    model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)
    model.save(new_model_filepath)

    loginfo = ' word2vec model %s has been built incrementally based on %s!' % (new_model_filepath, original_modelpath)
    gl.write_log(logpath, 'info', loginfo)



def write_segmented_clearwords(tablename, model_filepath):
    mysql = msc.MyPymysqlPool("dbMysql")

    sql = ''.join(['SELECT question_seqno, question_stem_segment FROM ', \
                   tablename, " where is_segmented=1 and grade_name like '三年级%'", ])
    rst = mysql.getAll(sql)

    model = word2vec.Word2Vec.load(model_filepath)
    vocab = list(model.wv.vocab.keys())
    for record in rst:
        seqno = record["question_seqno"]
        segwords = record["question_stem_segment"]
        segwords_list = segwords.strip(' ').split(' ')
        segwords_clear_list = tml.clear_word_from_vocab(segwords_list, vocab)  # 清除不在model中的单词
        segwords_clear = ' '.join(segwords_clear_list)  # 转换为字符串
        sql = ''.join(['update ', tablename, " set question_stem_segment_clear_rebuild='", \
                       str(segwords_clear), "' where question_seqno=", str(seqno), ";"])
        print(sql)
        try:
            mysql.update(sql)
            mysql.end()
        except Exception:
            print('update error: ', sql)
    mysql.dispose()


def fetch_segwords(tablename):
    mysql = msc.MyPymysqlPool("dbMysql")
    sql = ''.join(['SELECT question_stem_segment FROM ', tablename, " where is_segmented=1", ])
    rst = mysql.getAll(sql)
    mysql.dispose()

    loginfo = ' %d rows have been fetched.' % len(rst)
    gl.write_log(logpath, 'info', loginfo)
    return rst


def comand_line_set():
    args = argparse.ArgumentParser(description='Word2vec words retrieval information', epilog='Information end')
    args.add_argument("-i", type=str, dest="initial", help="build initially, 1 or 0!", default=0, choices={0,1})
    args.add_argument("-l", type=str, dest="logpath", help="the log path", default=LOGFILEPATH)
    args.add_argument("-d", type=str, dest="segmentation_filepath", help="the path of question segmentation file", \
                      default='../data/segment_wiki_chs_question.txt')
    args.add_argument("-o", type=str, dest="word2Vec_general_filepath", help="the path of original word2vec model", \
                      default='../pub/model/word2Vec_general_question.model')
    args.add_argument("-m", type=str, dest="word2Vec_question_filepath", help="the path of question word2vec model", \
                      default='./model/word2Vec_question_rebuild.model')
    args.add_argument("-t", type=str, dest="tablename", help="the segmentation question table name", \
                      default='core.question_similarity_prepare')

    args = args.parse_args()
    args_dict = args.__dict__
    return args_dict


if __name__=='__main__':
    global logpath

    args_dict = comand_line_set()
    initial = int(args_dict.get("initial"))
    logpath = args_dict.get("logpath")
    word2Vec_question_filepath = args_dict.get("word2Vec_question_filepath")
    tablename = args_dict.get("tablename")

    gl.write_log(logpath, 'info', '\n\n')
    loginfo = 'building word2vec model...'
    gl.write_log(logpath, 'info', loginfo)

    # 初始化目标模型为基于分词文本文件训练模型
    if initial == 1:
        segmentation_filepath = args_dict.get("segmentation_filepath")
        sentences = word2vec.PathLineSentences(segmentation_filepath, max_sentence_length=4000000)
        print('build_model...')
        build_model(word2Vec_question_filepath, sentences)
        print('build_model finished.')
        word2Vec_base_filepath = word2Vec_question_filepath
    else:
        word2Vec_base_filepath = args_dict.get("word2Vec_general_filepath")

    rst = fetch_segwords(tablename)
    records = list(list(x.values()) for x in rst)
    # print(len(sentences))
    incrementally_build_model(word2Vec_base_filepath, word2Vec_question_filepath, records)

    # 清理分词中不在模型中的内容，以便后续比较
    write_segmented_clearwords(tablename, word2Vec_question_filepath)

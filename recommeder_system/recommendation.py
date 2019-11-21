#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 10/1/2019 7:08 PM
# @Author  : Gaopeng.Bai
# @File    : recommendation.py
# @User    : baigaopeng
# @Software: PyCharm
# Reference:**********************************************

import tensorflow as tf
import os
from six.moves import cPickle


class recommendation():
    def __init__(self, save_dir="../data_resources/save_data", model="MANN", k=3):
        self.MANN_weight_path = os.path.join(save_dir, model)
        save_id2vocab_dir = save_dir + '/' + 'id2word'
        self.id2vocab_file = os.path.join(save_id2vocab_dir, "vocab.pkl")
        self.save_dir = save_dir
        self.model = model
        self.k = k

    def MANN_predict(self, x, x_label):
        """
        predict model that specify in Constructor.
        :param x: input x
        :param x_label: input y-1 target
        :return: a list of prediction, default 100
        """
        with tf.compat.v1.Session() as sess:
            meta = [fn for fn in os.listdir(self.save_dir + '/' + self.model) if fn.endswith('meta')]
            saver = tf.compat.v1.train.import_meta_graph(self.save_dir + '/' + self.model + '/' + meta[0])
            saver.restore(sess, tf.compat.v1.train.latest_checkpoint(self.save_dir + '/' + self.model))
            graph = tf.compat.v1.get_default_graph()
            # # input of model
            input_x = graph.get_operation_by_name('x_squences').outputs[0]
            input_x_label = graph.get_operation_by_name('x_label').outputs[0]
            # # prediction
            prediction = graph.get_operation_by_name('output').outputs[0]
            # # for retraining
            train_y = graph.get_operation_by_name('y').outputs[0]
            # train_op = graph.get_operation_by_name('train_op').outputs[0]
            # predict
            sp_predict = sess.run(prediction, feed_dict={input_x: x, input_x_label: x_label})[0][0]
            _, predict_number = tf.compat.v1.nn.top_k(sp_predict, k=100)
            a = sess.run(predict_number)
            return self.convert_id_string(a[:self.k])

    def convert_id_string(self, value):
        """
        seek the specific song id in dict.
        :param value: index in dict
        :return:  Song track id.
        """
        # the dict to convert id to specific string.
        list = []
        with open(self.id2vocab_file, 'rb') as f:
            vocab = cPickle.load(f)
        word2id = dict(zip(vocab.keys(), vocab.values()))
        for i in value:
            list.append("spotify:track:"+word2id.get(i))
        return list

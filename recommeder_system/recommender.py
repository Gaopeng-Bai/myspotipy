#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 10/1/2019 7:08 PM
# @Author  : Gaopeng.Bai
# @File    : recommender.py
# @User    : baigaopeng
# @Software: PyCharm
# Reference:**********************************************

import tensorflow as tf
import os


class recommender:
    def __init__(self, save_dir="../data_resources/save_data", model="MANN"):
        self.MANN_weight_path = os.path.join(save_dir, model)

    def MANN_predict(self, x):
        with tf.Session() as sess:
            meta = [fn for fn in os.listdir(self.MANN_weight_path) if fn.endswith('meta')]
            saver = tf.train.import_meta_graph(self.MANN_weight_path + meta[0])
            saver.restore(sess, tf.train.latest_checkpoint(self.MANN_weight_path))
            prediction = tf.get_collection('pred_network')[0]
            graph = tf.get_default_graph()

            input_x = graph.get_operation_by_name('x_squences').outputs[0]

            sp_predict = sess.run(prediction, feed_dict={input_x: x})

            return sp_predict

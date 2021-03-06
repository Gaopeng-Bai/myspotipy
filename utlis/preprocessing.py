#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 9/28/2019 4:15 PM
# @Author  : Gaopeng.Bai
# @File    : preprocessing.py
# @User    : baigaopeng
# @Software: PyCharm
# Reference:https://github.com/Gaopeng-Bai/myspotipy.git

import os
from itertools import repeat

import numpy as np
from typing import Optional, Any, List, Dict, Union

from six.moves import cPickle


def one_hot_encode(x, dim):
    res = np.zeros(np.shape(x) + (dim,), dtype=np.float32)
    it = np.nditer(x, flags=['multi_index'])
    while not it.finished:
        res[it.multi_index][it[0]] = 1
        it.iternext()
    return res


def one_hot_decode(x):
    return np.argmax(x, axis=-1)


class data_processing:
    id2word: Dict[Union[int, Any], Any]
    word2id: Dict[Any, Union[int, Any]]
    current_playlist: List[Any]
    vocab: Optional[Any]
    vocabulary_size: int

    def __init__(self, save_dir='../data_resources/save_data', seq_length=50, batch_size=32, tasks_size=10):
        self.vocab2id_file = os.path.join(save_dir, "vocab2id", "vocab.pkl")
        self.id2vocab_file = os.path.join(save_dir, "id2word", "vocab.pkl")

        self.batch_size = batch_size
        self.tasks_size = tasks_size
        self.seq_length = seq_length
        self.init_container()

    def init_container(self):
        """
        Initialize the playlist when user open new playlist. Clear container stored old playlist.
        @return: no defined.
        """
        self.current_playlist = []

    def playlist_processing(self, playlist):
        """
        The playlist is preprocessed, the song is converted to a specified ID,
        and if the id does not exist, the dictionary is updated.
        @param playlist: the song list of current playlist
        @return: List of playlist ids.
        """
        with open(self.vocab2id_file, 'rb') as f:
            vocab = cPickle.load(f)
        vocabulary_size = len(vocab)
        self.stable_size = 14130
        word2id = dict(zip(vocab.keys(), vocab.values()))

        for i in playlist:
            self.current_playlist.append(i[14:])
            # check dictionary to update
            # if not in dictionary, store index idCount+1
            if word2id.get(i[14:]) is None:
                # vocabulary_size += 1
                # word2id[i[14:]] = vocabulary_size
                word2id[i[14:]] = 0

        # put char into dictionary random sort
        word2id = dict(zip(word2id.keys(), word2id.values()))
        self.id2word = dict(zip(word2id.values(), word2id.keys()))
        # store new dictionary into local files.
        # with open(self.vocab2id_file, 'wb') as f:
        #     cPickle.dump(word2id, f)
        # with open(self.id2vocab_file, 'wb') as f:
        #     cPickle.dump(self.id2word, f)

        return list(map(word2id.get, self.current_playlist))

    def fetch_batch(self, playlist):
        """
        Reshape a batch by using current sequence of playlist.
        The elements of playlist much be lager than (self.task_size+2)
        @param playlist: current sequence of playlist.
        @return: x, x_label, y for model.
        """
        y_output = []
        y_out = []
        x_out = []
        x_array = np.arange(self.seq_length, dtype=float).reshape(1, self.seq_length)
        data = self.playlist_processing(playlist)
        playlist = self.standardization(data)

        # manage a batch table for next step
        for i in range(len(playlist) - 2):
            x = []
            y = playlist[i + 1]
            temp_list = playlist[:i + 1]

            if len(temp_list) >= self.seq_length:
                x.append(temp_list[:self.seq_length])
                x_array = np.insert(x_array, len(x_array), np.array(x[0]), axis=0)
            else:
                x.append(temp_list)
                while len(x[0]) < self.seq_length:
                    x[0].append(-1)
                x_array = np.insert(x_array, len(x_array), np.array(x[0]), axis=0)

            y_output.append(one_hot_encode(int(y * self.stable_size), self.stable_size))
        # fetch mini-batch from batch table.
        x, y = x_array[1:, :], np.array(y_output)
        while len(x) < self.batch_size:
            # duplicate list
            x = [a for item in x for a in repeat(item, 2)]
            y = [b for item in y for b in repeat(item, 2)]

        self.x_container = np.array(x)
        self.y_container = np.array(y)
        # choice tasks size item.
        x_out = self.x_container[0:self.batch_size, :]
        y_out = self.y_container[0:self.batch_size, :]

        x_labels = np.concatenate(
            [np.zeros(shape=[self.batch_size, 1]), np.array(y_out)[:, :-1]], axis=1
        )

        return np.array(x_out), x_labels, np.array(y_out)

    def standardization(self, playlist):
        """
        convert each value to 0-1 number. normalization algorithm: Linear transformation.
         y=(x-min)/(max-min).
        @param playlist: input a playlist.
        @return: normalized value list.
        """
        new_list = []
        for i in playlist:
            new_list.append(i / self.stable_size)
        return new_list

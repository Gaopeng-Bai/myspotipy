#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:**********************************************
# @Time    : 7/28/2019 3:40 PM
# @Author  : Gaopeng.Bai
# @File    : Gui_main.py
# @User    : baigaopeng
# @Software: PyCharm
# Reference:https://github.com/Gaopeng-Bai/myspotipy.git

import sys
import threading

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from GUI.spotify_gui import Ui_Spotify as ui
from spotipy.spotify_api import spotify_api, ms_to_time
from utlis.preprocessing import data_processing
from recommeder_system.recommendation import recommendation


class Gui_main(ui):
    playing: bool
    volume_before_mute: int

    def __init__(self, mainwindow):
        self.volume_mute = False
        self.mainwindow = mainwindow
        self.current_playlist = ''
        self.song_index = 0
        self.songs_num = 0
        self.current_song_lists = []
        self.my_spotify = spotify_api()
        self.preprocessing = data_processing()
        self.recommender_ = recommendation()

    def gui_init(self):
        self.playlists_init()
        self.playlist_contain_init()
        self.recommendation_contain_init()
        self.play_playlist_button()
        self.devices_button_init()

        self.bottom_volume_control()
        self.bottom_volume_button()
        self.bottom_button()

        self.Test.clicked.connect(self.test_function)
        self.refresher.clicked.connect(self.recommendation_system)

    def bottom_button(self):
        """
        initialize bottom button.
        :return:
        """
        self.nextsong.clicked.connect(self.play_next_song)
        self.previous_song.clicked.connect(self.play_prev_song)
        self.playsong.clicked.connect(self.play_button)
        self.thumbdown.clicked.connect(self.positive_recommender)
        self.thumbup.clicked.connect(self.negative_recommender)

    def positive_recommender(self):
        self.my_spotify.current_playing_info()
        if self.current_song_lists:
            if self.my_spotify.current_playing_information['song_uri'] is not None:
                self.current_song_lists.append(self.my_spotify.current_playing_information['song_uri'])
                QMessageBox.about(None, 'Positive feedback', 'Please press refresh button')
            else:
                QMessageBox.about(None, 'No playing info', 'Please play a song and press this button again')
        else:
            QMessageBox.about(None, 'No playlist', 'Please choose a playlist first')

    def negative_recommender(self):
        self.my_spotify.current_playing_info()
        if self.current_song_lists:
            if self.my_spotify.current_playing_information['song_uri'] is not None:
                # current song never appear again.
                QMessageBox.about(None, 'Negative feedback', 'This song never appear again')
            else:
                QMessageBox.about(None, 'No playing info', 'Please play a song and press this button again')
        else:
            QMessageBox.about(None, 'No playlist', 'Please choose a playlist first')

    def play_button(self):
        """
        Play current song operation
        :return:
        """
        if hasattr(self, 'avaiable'):
            self.playing = not self.playing
            if self.playing:
                self.playsong.setStyleSheet("border-image: url(:/icon/pause.ico);")
                self.remote_play_playlist()
            else:
                self.my_spotify.stop_play()
                # kill thread of progress bar
                self.playsong.setStyleSheet("border-image: url(:/icon/play.ico);")
        else:
            QMessageBox.about(None, 'No valid devices', 'Please open your devices')

    def play_button_set(self):
        self.playsong.setStyleSheet("border-image: url(:/icon/pause.ico);")
        self.playing = True

    def play_prev_song(self):
        if self.song_index < 0:
            self.song_index = self.songs_num - 1
        else:
            self.song_index -= 1
        self.remote_play_playlist()

    def play_next_song(self):
        if self.song_index > self.songs_num - 1:
            self.song_index = 0
        else:
            self.song_index += 1
        self.remote_play_playlist()

    def bottom_volume_button(self):
        self.volume.setToolTip('Press mute')

        self.volume.clicked.connect(self.volume_button_clicked)

    def volume_button_clicked(self):
        if hasattr(self, 'avaiable'):
            self.volume_mute = not self.volume_mute

            if self.volume_mute:
                self.volume_before_mute = self.volumevalue.value()
                self.volume.setToolTip('Cancel mute')
                self.volume.setStyleSheet("border-image: url(:/icon/volumeoff.ico);")
                self.volumevalue.setValue(0)
                self.my_spotify.volume_change(0)
            else:
                self.volumevalue.setValue(self.volume_before_mute)
                self.my_spotify.volume_change(self.volume_before_mute)
                self.volume.setToolTip('Press mute')
                self.volume.setStyleSheet("border-image: url(:/icon/volumeon.ico);")
        else:
            QMessageBox.warning(None, 'No valid devices', 'Please open your devices')

    def bottom_volume_control(self):
        self.volumevalue.setMinimum(0)
        self.volumevalue.setMaximum(100)
        self.volumevalue.setSingleStep(1)  # %song duration time
        self.volumevalue.setValue(100)

        self.volume_pertg.setText('100')
        self.volumevalue.valueChanged.connect(self.volume_value_event)

    def volume_value_event(self):
        if hasattr(self, 'avaiable'):
            self.my_spotify.volume_change(self.volumevalue.value())
            self.volume_pertg.setText(str(self.volumevalue.value()))
        else:

            QMessageBox.warning(None, 'No valid devices', 'Please open your devices')

    def gui_bottom_init(self):
        try:
            self.my_spotify.current_playing_info()
            self.Songname.setText(self.my_spotify.current_playing_information['song_name'])
            self.songauther.setText(self.my_spotify.current_playing_information['artists'])
            self.fulltimeofsong.setText(
                ms_to_time(self.my_spotify.current_playing_information['duration_ms']))
            self.progressinsong.setText(
                ms_to_time(self.my_spotify.current_playing_information['progress_ms']))
            # image fill ?

            self.progress_bar_with_timer()
            self.play_button_set()
        except TypeError:
            QMessageBox.warning(None, 'Bottom init error', 'No playing on the device')

    def progress_bar_with_timer(self):
        progress = int(self.my_spotify.current_playing_information['progress_ms'])
        self.duration = int(self.my_spotify.current_playing_information['duration_ms'])

        step = int((self.duration / 1000) / 100)
        current_position = (progress / self.duration) * 100
        self.progressofsong.setMinimum(0)
        self.progressofsong.setMaximum(100)
        self.progressofsong.setSingleStep(step)  # %song duration time
        self.progressofsong.setValue(current_position)

        self.progressofsong.sliderMoved.connect(self.jump_timer)

        timer_thread = threading.Thread(name='timer_set', target=self.sync_timer_progress_bar)
        timer_thread.start()

    def jump_timer(self):
        position = self.progressofsong.value()
        self.my_spotify.seek_to_position(int(position/100*self.duration))

    def sync_timer_progress_bar(self):
        while 1:
            self.my_spotify.current_playing_info()
            progress_ms = self.my_spotify.current_playing_information['progress_ms']
            if progress_ms == 0:
                self.gui_bottom_init()
            self.progressinsong.setText(ms_to_time(progress_ms))
            self.progressofsong.setValue(int((progress_ms / self.duration) * 100))

    def play_playlist_button(self):
        self.playplaylist.setToolTip('Play current playlist')
        self.playplaylist.clicked.connect(self.remote_play_playlist)

    def remote_play_playlist(self):
        if self.current_playlist:
            uri = self.my_spotify.playlists['uri'][self.my_spotify.playlists['name'].index(self.current_playlist)]

            if hasattr(self, 'avaiable'):
                self.my_spotify.play_playlist(uri, self.song_index)
                self.gui_bottom_init()
            else:
                QMessageBox.warning(None, 'No valid devices', 'Please open your devices')
        else:
            QMessageBox.warning(None, 'Null playlist', 'Please pick a playlist first')

    def playlists_init(self):
        self.playlists.addItems(self.my_spotify.playlists['name'])
        self.playlists.itemClicked.connect(self.playlist_clicked)

    def playlist_contain_init(self):
        # init the contents of playlist display
        self.playlists_details.setColumnCount(3)
        self.playlists_details.verticalHeader().setVisible(False)
        self.playlists_details.setStyleSheet("QHeaderView::section{Background-color:rgb(0,1,1)}")
        self.playlists_details.setHorizontalHeaderLabels(['Title', 'Artist', 'Time'])
        self.playlists_details.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.playlists_details.resizeColumnsToContents()
        self.playlists_details.resizeRowsToContents()
        self.playlists_details.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.playlists_details.setSelectionBehavior(QAbstractItemView.SelectRows)

    def recommendation_contain_init(self):
        # init the contents of playlist display
        self.Recommender.setColumnCount(3)
        self.Recommender.verticalHeader().setVisible(False)
        self.Recommender.setStyleSheet("QHeaderView::section{Background-color:rgb(0,1,1)}")
        self.Recommender.setHorizontalHeaderLabels(['Title', 'Artist', 'Time'])
        self.Recommender.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.Recommender.resizeColumnsToContents()
        self.Recommender.resizeRowsToContents()
        self.Recommender.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.Recommender.setSelectionBehavior(QAbstractItemView.SelectRows)

    def playlist_clicked(self, item):
        self.my_spotify.get_playlists_detials(item.text())

        self.current_playlist = item.text()
        self.nameofplaylist.setText(self.my_spotify.container['name'])
        self.Nameofauther.setText(self.my_spotify.container['owner'])
        self.numberofsongs.setText(str(self.my_spotify.container['total']))
        self.logoplaylist.setStyleSheet("border-image: url(:/" + item.text() + ".jpg);")
        self.fill_playlist_details()

    def fill_playlist_details(self):
        self.playlists_details.clearContents()
        self.songs_num = len(self.my_spotify.container['song_name'])
        self.playlists_details.setRowCount(self.songs_num)
        for i, item in enumerate(self.my_spotify.container['song_name']):
            title = QTableWidgetItem(item)
            name = QTableWidgetItem(self.my_spotify.container['artist'][i])
            time = QTableWidgetItem(self.my_spotify.container['time'][i])
            self.current_song_lists.append(self.my_spotify.container['song_uri'][i])
            title.setForeground(QBrush(QColor(255, 255, 255)))
            name.setForeground(QBrush(QColor(255, 255, 255)))
            time.setForeground(QBrush(QColor(255, 255, 255)))
            self.playlists_details.setItem(i, 0, title)
            self.playlists_details.setItem(i, 1, name)
            self.playlists_details.setItem(i, 2, time)

        self.playlists_details.itemDoubleClicked.connect(self.play)

    # devices button
    def devices_button_init(self):
        self.devices.setToolTip('Click to get your devices')
        self.devices.setPopupMode(QToolButton.MenuButtonPopup)
        self.devices.setIcon(QIcon('resource/devices.ico'))
        self.devices.setAutoRaise(True)
        self.devices.clicked.connect(self.devices_button_menu)

    def devices_button_menu(self):
        self.my_spotify.show_available_device()

        menu = QMenu(self.mainwindow)
        for avaiable in self.my_spotify.devices['devices_name']:
            self.avaiable = QAction(QIcon('icon/' + avaiable + '.ico'), avaiable, self.mainwindow)
            menu.addAction(self.avaiable)
        self.devices.setMenu(menu)
        if hasattr(self, 'avaiable'):
            # set default devices as computer
            if 'Computer' in self.my_spotify.devices['devices_name']:
                self.my_spotify.choice_device('Computer')
                self.gui_bottom_init()

            self.avaiable.triggered.connect(self.device_choice_click)
            self.devices.setToolTip('Choice device, Computer as default')
        else:
            self.devices.setToolTip('No valid devices')

    def device_choice_click(self):
        self.my_spotify.choice_device(self.avaiable.text())
        # current playlist initializer

        self.gui_bottom_init()

    def recommendation_system(self):
        """
        preprocessing the current list of songs for recommender system. put all content of recommended list into
        frontend. connect each song to play button to play the recommended song.
        :return: None
        """
        self.preprocessing.init_container()
        x, x_label, y = self.preprocessing.fetch_batch(self.current_song_lists)
        recommendation_list = self.recommender_.MANN_predict(x, x_label)
        self.my_spotify.finding_song_by_track(recommendation_list)
        # fill the gui for recommendation list
        self.Recommender.clearContents()
        count = len(self.my_spotify.recommender_songs["song_name"])
        self.Recommender.setRowCount(count)
        for i, item in enumerate(self.my_spotify.recommender_songs["song_name"]):
            title = QTableWidgetItem(item)
            name = QTableWidgetItem(self.my_spotify.recommender_songs["artist_name"][i])
            time = QTableWidgetItem(self.my_spotify.recommender_songs["song_name"][i])
            title.setForeground(QBrush(QColor(255, 255, 255)))
            name.setForeground(QBrush(QColor(255, 255, 255)))
            time.setForeground(QBrush(QColor(255, 255, 255)))
            self.Recommender.setItem(i, 0, title)
            self.Recommender.setItem(i, 1, name)
            self.Recommender.setItem(i, 2, time)
        self.Recommender.itemDoubleClicked.connect(self.play_single)

    def play_single(self, item):
        self.my_spotify.play_song(item.text)

    def play(self, item):
        """
        Remote play songs follow the current item
        @param item:
        @return:
        """
        self.song_index = int(item.row())
        self.remote_play_playlist()

    def test_function(self):
        self.my_spotify.finding_song_by_track("spotify:track:2vCtiBvJJZfz773yTfAxPP")
        print("current has %d threads" % (threading.activeCount() - 1))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    Gui = Gui_main(MainWindow)
    Gui.setupUi(MainWindow)
    Gui.gui_init()
    MainWindow.show()
    sys.exit(app.exec_())

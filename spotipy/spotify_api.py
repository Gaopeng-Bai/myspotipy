#!/usr/bin/python3
# -*-coding:utf-8 -*-

# Reference:https://spotipy.readthedocs.io/en/latest/
# @Time    : 7/28/2019 3:40 PM
# @Author  : Gaopeng.Bai
# @File    : spotify_api.py
# @User    : baigaopeng
# @Software: PyCharm
# Reference:**********************************************

import sys, os, json, time
from typing import Dict, List, Any, Optional, Union

import spotipy
import spotipy.util as util
import requests
from spotipy.oauth2 import SpotifyClientCredentials


def ms_to_time(millis):
    seconds = int((millis / 1000) % 60)
    minutes = int((millis / (1000 * 60)) % 60)
    if len(str(seconds)) < 2:
        seconds = "0" + str(seconds)
    else:
        seconds = str(seconds)
    return str(minutes) + ":" + seconds


def download_image(image_url, name):
    path = 'resource\\%s.jpg' % (name)
    if not os.path.exists(path):
        try:
            response = requests.get(image_url)
            # 获取的文本实际上是图片的二进制文本
            img = response.content
            # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
            # 保存路径

            with open(path, 'wb') as f:
                f.write(img)
        except Exception as ex:
            print("------download image error----")


class spotify_api:
    final_devices_id: object
    devices: Dict[str, List[Any]]
    current_playing_information: Dict[str, Union[str, Any]]
    token: Optional[Any]
    username: object
    container: Dict[str, List[Any]]

    def __init__(self):

        self.playlists = {'name': [], 'uri': []}

        self.authorize()
        self.get_playlists()

    def container_init(self):
        self.container = {'song_name': [], 'song_uri': [], 'song_image': [], 'artist': [], 'time': []}

    def authorize(self):
        if len(sys.argv) > 1:
            self.username = sys.argv[1]
        else:
            print("Usage: %s username" % (sys.argv[0],))
            sys.exit()

        scope = 'playlist-read-private,' \
                'playlist-read-collaborative,' \
                'app-remote-control,' \
                'streaming,' \
                'user-read-playback-state,' \
                'user-read-currently-playing,' \
                'user-modify-playback-state'
        self.token = util.prompt_for_user_token(self.username, scope)
        if self.token:
            self.sp = spotipy.Spotify(auth=self.token)
            self.sp.trace = True  # turn on tracing
            self.sp.trace_out = True  # turn on trace out

        else:
            print("Can't get token for", self.username)
            return 0
        self.show_available_device()

    def get_playlists_detials(self, playlist_name):
        """
        put relevant information into local container from user database.
        @param playlist_name: playlist url in spotify.
        @return: not defined.
        """
        self.container_init()
        playlists = self.sp.user_playlists(self.username)
        for list in playlists['items']:
            if list['name'] == playlist_name:
                self.container['name'] = list['name']
                self.container['image'] = list['images'][0]['url']
                download_image(self.container['image'], self.container['name'])
                self.container['total'] = list['tracks']['total']
                self.container['owner'] = list['owner']['display_name']
                self.container['uri'] = list['uri']

                results = self.sp.user_playlist(self.username, list['id'], fields="tracks,next")
                tracks = results['tracks']
                self.add_tracks(tracks)
                while tracks['next']:
                    tracks = self.sp.next(tracks)
                    self.add_tracks(tracks)

    def add_tracks(self, results):
        for i, item in enumerate(results['items']):
            track = item['track']
            self.container['song_name'].append(track['name'])
            self.container['artist'].append(track['artists'][0]['name'])
            self.container['time'].append(ms_to_time(track['duration_ms']))
            self.container['song_uri'].append(track['uri'])
            for image in track['album']['images']:
                if image['height'] < 300:
                    self.container['song_image'].append(image['url'])

    def get_playlists(self):
        """
        get all playlists from spotify user database.
        @return:
        """
        self.sp = spotipy.Spotify(auth=self.token)
        self.sp.trace = False
        playlists = self.sp.user_playlists(self.username)
        for playlist in playlists['items']:
            self.playlists['name'].append(playlist['name'])
            self.playlists['uri'].append(playlist['uri'])

        self.playlists['name'].pop(0)
        self.playlists['uri'].pop(0)

    def audio_analysis_for_track(self, uri):
        start = time.time()
        analysis = self.sp.audio_analysis(uri)
        features = self.sp.audio_features(uri)

        return analysis, features

    def check_devices(self):
        """
        get all available devices.
        @return: the list of devices id.
        """
        return self.sp.devices()

    def show_available_device(self):
        """
        store all available devices info into local parameters.
        @return:
        """
        self.devices = {'devices_name': [], 'devices_id': []}
        mydevice = self.check_devices()
        for ids in mydevice['devices']:
            self.devices['devices_name'].append(ids['type'])
            self.devices['devices_id'].append(ids['id'])

    def choice_device(self, name):
        try:
            self.final_devices_id = self.devices['devices_id'][self.devices['devices_name'].index(name)]
        except ValueError:
            print('No valid devices')

    def volume_change(self, value):
        """
        remote control volume by specify the value.
        @param value: the volume value (0-100)
        @return: not defined.
        """
        self.sp.volume(value, device_id=self.final_devices_id)

    # device: Smartphone, Computer
    def play_song(self, specific_uri):
        self.sp.start_playback(device_id=self.final_devices_id, uris=[specific_uri])
        print('playing')

    def play_playlist(self, playlist_uri, position):
        self.sp.start_playback(device_id=self.final_devices_id, context_uri=playlist_uri, offset={"position": position})

    def stop_play(self):
        self.sp.pause_playback(device_id=self.final_devices_id)

    def finding_song_by_track(self, track_id):
        """
        Run again each time you recommend a song to clear the recommended container.
        :param track_id: Details of the track ID of the song to be searched
        :return: a dic of self.recommender_songs contain the content of recommendation
        """
        temp = self.sp.track(track_id)
        self.recommender_songs = {"song_name": [], "artist_name": [], "duration_time": []}
        for i in temp:
            self.recommender_songs["song_name"].append(i["name"])
            self.recommender_songs["artist_name"].append(i["artists"][0]["name"])
            self.recommender_songs["duration_time"].append(ms_to_time(i["duration_ms"]))

    def current_playing_info(self):
        """
        get current playing song information and store into local parameters.
        @return:
        """
        self.current_playing_information = {}
        sum_artist = ''

        info = self.sp.current_playback()

        self.current_playing_information['song_name'] = info['item']['name']

        for art in info['item']['artists']:
            sum_artist = sum_artist + "&" + art['name']
        self.current_playing_information['artists'] = sum_artist[1:]
        self.current_playing_information['song_uri'] = info['item']['uri']
        self.current_playing_information['duration_ms'] = info['item']['duration_ms']

        for img in info['item']['album']['images']:
            if img['height'] < 300:
                self.current_playing_information['image'] = img['url']

        self.current_playing_information['remaining_ms'] = info['item']['duration_ms'] - info['progress_ms']
        self.current_playing_information['progress_ms'] = info['progress_ms']
        self.current_playing_information['shuffle_state'] = info['shuffle_state']
        self.current_playing_information['repeat_state'] = info['repeat_state']
        self.current_playing_information['is_playing'] = info['is_playing']

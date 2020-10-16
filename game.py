import constants
import random
import urllib.request
import re
from player import Player
import pafy
import vlc
import time
import json
from contextlib import closing
from Levenshtein import distance as levenshtein_distance


class Game:
    def __init__(self):
        self.player = Player()
        self.media_player = None

    def play_game(self):
        self.player.initialize_favourite_singers()
        while True:
            singer = random.choice(self.player.favourite_singers)
            id_of_song_being_played = self.play_song(singer)
            song_name = Game.get_song_name_from_youtube(id_of_song_being_played)
            song_name = Game.normalize_song_name(song_name, singer)
            start_time = time.time()
            player_guess = input("Guess the name of the song being played\n")
            seconds_took_to_guess = int(time.time() - start_time)
            if Game.is_player_guess_right(player_guess.lower(), song_name.lower()):
                print("You've guessed right, well done!")
                self.player.score += Game.calculate_given_points(seconds_took_to_guess, True)
            else:
                print("Wrong guess!")
                self.player.score += Game.calculate_given_points(seconds_took_to_guess, False)
            self.media_player.stop()
            print(f"Your score is: {self.player.score}")

    @staticmethod
    def calculate_given_points(seconds_took_to_answer, is_player_guess_right):
        given_points = constants.MIN_GIVEN_POINTS
        if is_player_guess_right:
            if seconds_took_to_answer >= constants.MAX_TIME_PER_SONG:
                given_points = constants.MIN_GIVEN_POINTS
            else:
                given_points = ((-5 / 6) * seconds_took_to_answer) + 100

        return given_points

    @staticmethod
    def is_player_guess_right(player_guess, song_name):
        return levenshtein_distance(player_guess, song_name) <= 1

    def play_song(self, singer_name):
        youtube_song_search_url = Game.build_youtube_song_search_url(singer_name)
        with closing(urllib.request.urlopen(youtube_song_search_url)) as youtube_song_search_url_obj:
            youtube_song_search_result_ids = re.findall(r"watch\?v=(\S{11})",
                                                        youtube_song_search_url_obj.read().decode())
        id_of_song_being_played = random.choice(youtube_song_search_result_ids)
        youtube_song_url = "https://www.youtube.com/watch?v=" + id_of_song_being_played
        video_object = pafy.new(youtube_song_url)
        best_audio_object = video_object.getbestaudio()
        play_url = best_audio_object.url
        self.media_player = vlc.MediaPlayer(play_url)
        self.media_player.play()
        return id_of_song_being_played

    @staticmethod
    def build_youtube_song_search_url(singer_name):
        youtube_song_search_url = "https://www.youtube.com/results?search_query="
        words_in_singer_name = singer_name.split()
        if len(words_in_singer_name) > 1:
            youtube_song_search_url += "+".join(words_in_singer_name)
        else:
            youtube_song_search_url += singer_name
        return youtube_song_search_url

    @staticmethod
    def get_song_name_from_youtube(song_id):
        params = {"format": "json", "url": f"https://www.youtube.com/watch?v={song_id}"}
        url = "https://www.youtube.com/oembed"
        query_string = urllib.parse.urlencode(params)
        url = f"{url}?{query_string}"
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            return data['title']

    @staticmethod
    def normalize_song_name(song_name, singer):
        song_name = ''.join(char for char in song_name if char.isdigit() or char.isalpha() or char.isspace()
                            or char == '\'')
        song_name = song_name.replace(singer, '')
        return song_name





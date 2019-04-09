#!/usr/local/bin python3

import os
import sys
from argparse import ArgumentParser
import numpy as np
import json
from tqdm import tqdm
from station import station_generator
from match_score import term_match_score
from speech_sound import consonants, vowels
from preprocess import preprocess
from pykakasi import kakasi

kakasi_h2a = kakasi()
kakasi_h2a.setMode('H', 'a')
conv_h2a = kakasi_h2a.getConverter()
kakasi_j2h = kakasi()
kakasi_j2h.setMode('J', 'H')
conv_j2h = kakasi_j2h.getConverter()

def initial2initials(initial, initials):
    # 歌詞のイニシャルから検索対象の単語のイニシャルを指定 (母音が共通のもの)
    return [i for i in initials if vowels(conv_h2a.do(initial)) == vowels(conv_h2a.do(i))]

def initial2stations(stations):
    # イニシャルに該当する単語の検索
    _initial2stations = dict()
    for station in stations:
        if station.reading[0] in _initial2stations:
            _initial2stations[station.reading[0]].append(station)
        else:
            _initial2stations[station.reading[0]] = [station]
    return _initial2stations

parser = ArgumentParser()
parser.add_argument('--lyrics_filename', type=str)
parser.add_argument('parody_filename', type=str)
parser.add_argument('--hparams_filepath', type=str, default='../data/hparams/hparams_v1.json')
parser.add_argument('--lyrics', type=str, default='')
parser.add_argument('--verbose', action='store_true')
args = parser.parse_args()

class StationPath:
    # 単語列のパス
    def __init__(self, stations, remaining_lyrics, match_score, pcrs, remaining_stations):
        self.stations = stations
        self.remaining_lyrics = remaining_lyrics
        self.match_score = match_score
        self.pcrs = pcrs
        self.remaining_stations = remaining_stations


def search_station_path(lyrics, remaining_stations, hparams):
    # beam search による最適パスの探索
    # 最大で memory_step 前までのノードを考慮して次のノードを探索できる
    lyrics = preprocess(lyrics, macron='double_vowel_to_macron')
    station_paths = [
        StationPath(
            stations=[],
            remaining_lyrics=lyrics,
            match_score=0.,
            pcrs=[1.],
            remaining_stations=remaining_stations
        )
    ]
    remaining_lyrics_length = len(lyrics.split())
    while remaining_lyrics_length > 0 and remaining_stations:
        phrase_consumption_rate = 0.
        _station_paths = [p for path in station_paths for p in extend_path(path, hparams)]
        remaining_lyrics2path = dict()
        # beam_size 件のパスを保持する
        # 残りの歌詞が同じ場合は，よりスコアの高いほうを保持する
        for path in _station_paths:
            if path.remaining_lyrics in remaining_lyrics2path:
                if remaining_lyrics2path[path.remaining_lyrics].match_score < path.match_score:
                    remaining_lyrics2path[path.remaining_lyrics] = path
            else:
                remaining_lyrics2path[path.remaining_lyrics] = path
        # beam_size ** (memory_steps - 1) 件以上のパスは保持しない
        memory_count = hparams['beam_size'] ** (hparams['memory_steps'] - 1)
        station_paths = sorted(remaining_lyrics2path.values(), key=lambda x: x.match_score, reverse=True)[:memory_count]
        remaining_lyrics_length = max([len(path.remaining_lyrics.split()) for path in station_paths])
    if args.verbose:
        print()
    return sorted(station_paths, key=lambda x: x.match_score, reverse=True)[0]

def extend_path(path, hparams):
    # パスの次のノードを検索
    if path.remaining_lyrics == '':
        return [path]
    if path.remaining_lyrics[0] in '*':
        path.remaining_lyrics = ''
        return [path]
    lyrics_initial = conv_j2h.do(path.remaining_lyrics[0])[0]
    init2sta = initial2stations(path.remaining_stations)
    candidate_stations = [station for i in initial2initials(lyrics_initial, init2sta.keys()) for station in init2sta[i]] or path.remaining_stations
    path_fields = []
    for station in candidate_stations:
        score, remaining_lyrics, pcr = term_match_score(station.reading, path.remaining_lyrics, path.pcrs[-1], hparams)
        pcrs = path.pcrs + [pcr]
        path_fields.append((score, station, remaining_lyrics, pcrs))
    path_fields = sorted(path_fields, key=lambda x: x[0], reverse=True)[:hparams['beam_size']]
    paths = []
    for score, station, remaining_lyrics, pcrs in path_fields:
        remaining_stations = path.remaining_stations[:]
        if not hparams['repeated']:
            # 単語の重複を禁じる場合，使用した単語をパスの使用可能単語リストから消去
            remaining_stations.remove(station)
        pcrs = pcrs
        paths.append(
            StationPath(
                stations=path.stations + [station],
                remaining_lyrics=remaining_lyrics,
                match_score=path.match_score + score,
                pcrs=pcrs,
                remaining_stations=remaining_stations
            )
        )
    return paths

def main():
    with open(args.hparams_filepath, 'r') as hparams_file:
        hparams = json.load(hparams_file)
    if args.lyrics:
        # 歌詞を直接入力する場合
        lyrics = args.lyrics
    else:
        # 歌詞を .txt ファイルから受け取る場合
        lyrics_filepath = os.path.join('../data/lyrics/', args.lyrics_filename)
        with open(lyrics_filepath, 'r') as lyrics_file:
            lyrics = lyrics_file.read()
    if hparams['no_deprecated']:
        stations = [station for station in station_generator(hparams) if not station.deprecated]
    else:
        stations = [station for station in station_generator(hparams)]
    if not os.path.exists('../result/parody/'):
        # parody 用のディレクトリが存在していない場合は作成しておく
        os.makedirs('../result/parody/', exist_ok=True)
    parody_filepath = os.path.join('../result/parody/', args.parody_filename)
    if os.path.exists(parody_filepath):
        # 出力ファイルが事前に存在する場合は，追記しないように元のファイルを消去する
        os.remove(parody_filepath)
    for line in tqdm(lyrics.split('\n'), desc='processing lines'):
        # 入力ファイルの各行を替え歌に変換していく
        best_path = search_station_path(line, stations, hparams)
        for station in best_path.stations:
            if not hparams['repeated']:
                # 単語の重複を禁じる場合，使用した単語をパスの使用可能単語リストから消去
                stations.remove(station)
            if args.verbose:
                # 画面に替え歌の歌詞を表示
                print('%s\t%s\t%s\t%s' % (station.name, station.reading, station.company, station.railway))
            if parody_filepath:
                # ファイルに書き込み
                with open(parody_filepath, 'a') as parody_file:
                    parody_file.write('%s\t%s\t%s\t%s\n' % (station.name, station.reading, station.company, station.railway))

if __name__ == '__main__':
    main()

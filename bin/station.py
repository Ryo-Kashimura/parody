#!/usr/local/bin python3

import os
import re
import csv

class Station:

    def __init__(self, row):
        self.raw_name = row[0]
        # アスタリスクの消去 (例: さぬき* -> さぬき)
        _name = re.sub(r'\*', '', row[0])
        # かっこの中身(都道府県名など)をかっこごと消去
        m = re.search(r'(?P<station_name>.*)((\(.+\))|(\[.+\]))', _name)
        if m:
            # '星の駅　/　星' などの駅名を '/' の左側の名前に統一する
            _name = m.group('station_name')
            m = re.search(r'(?P<station_name>.*) \/ .*', _name)
            if m:
                _name = m.group('station_name')
        self.name = _name
        # アスタリスクの消去
        _reading = re.sub(r'\*', '', row[1])
        # 'ほしのえき　/　ほし' などの読みを '/' の左側の読みに統一する
        m = re.search(r'(?P<reading>.*) \/ .*', _reading)
        if m:
            _reading = m.group('reading')
        self.reading = _reading
        self.prefecture = row[4]
        self.company = row[5]
        self.railway = row[6]
        self.deprecated = row[-2] == 'D'

    def __str__(self):
        strings = [
            'raw_name  : ' + self.raw_name,
            'name      : ' + self.name,
            'reading   : ' + self.reading,
            'prefecture: ' + self.prefecture,
            'company   : ' + self.company,
            'railway   : ' + self.railway,
            'deprecated: ' + str(self.deprecated)
        ]
        return '\n'.join(strings)

def raw_data_generator(data_filepath):
    with open(data_filepath, 'r', encoding='shift-jis') as raw_data_file:
        reader = csv.reader(raw_data_file, delimiter='\t')
        header = next(reader)
        for row in reader:
            yield row

def station_generator(hparams):
    station_dictionary_dir = hparams['station_dictionary_dir']
    station_filepaths = [
        os.path.join(station_dictionary_dir, filename) for filename in os.listdir(station_dictionary_dir)
        if re.match(r'station_dictionary_\d{8}\.tsv', filename)
    ]
    if not station_filepaths:
        print('ERROR: No station dictionary file was found.')
    gen = raw_data_generator(station_filepaths[0])
    for row in gen:
        yield Station(row)

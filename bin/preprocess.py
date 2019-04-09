#!/usr/local/bin python3

import re
from pykakasi import kakasi
from speech_sound import vowels

kakasi_h2a = kakasi()
kakasi_h2a.setMode('H', 'a')
conv_h2a = kakasi_h2a.getConverter()

def delete_brackets(text):
    # かっこを中身ごと消去
    brackets = ['()', '[]', '{}', '<>', '「」', '（）', '〔〕', '［］', '『』', '【】', '〈〉', '｛｝', '《》']
    regex = '(' + '|'.join(['\\%s.*\\%s' % tuple(b) for b in brackets]) + ')'
    return re.sub(regex, '', text)

def double_consonant2vowel(text):
    # 促音便を前の字の母音に変換
    text = list(text)
    # 母音をひらがなに変換する辞書
    v2h = {v: h for v, h in [('a', 'あ'), ('i', 'い'), ('u', 'う'), ('e', 'え'), ('o', 'お')]}
    for i, c in enumerate(text):
        if c in 'っ' and i > 0:
            v = vowels(conv_h2a.do(text[i - 1]))[0]
            try:
                text[i] = v2h[v]
            except KeyError:
                pass
    return ''.join(text)

def macron2vowel(text):
    # 長音符を前の字の母音に変換
    text = list(text)
    # 母音をひらがなに変換する辞書
    v2h = {v: h for v, h in [('a', 'あ'), ('i', 'い'), ('u', 'う'), ('e', 'え'), ('o', 'お')]}
    for i, c in enumerate(text):
        if c in 'ー' and i > 0:
            v = vowels(conv_h2a.do(text[i - 1]))[0]
            try:
                text[i] = v2h[v]
            except KeyError:
                pass
    return ''.join(text)

def double_vowel2macron(text):
    # 連続する母音(同母音, 'ou')を長音符に変換
    text = list(text)
    # 母音をひらがなに変換する辞書
    v2h = {v: h for v, h in [('a', 'あ'), ('i', 'い'), ('u', 'う'), ('e', 'え'), ('o', 'お')]}
    for i, c in enumerate(text):
        if c == 'う' and i > 0:
            # 'ou' の処理
            vs = vowels(conv_h2a.do(text[i - 1]))
            if (text[i - 1] == ' ') or (not vs):
                continue
            v = vs[0]
            try:
                if v2h[v] in 'うお':
                    text[i] = 'ー'
            except KeyError:
                pass
        elif c in 'あいえお' and i > 0:
            # 同母音の処理
            vs = vowels(conv_h2a.do(text[i - 1]))
            if (text[i - 1] == ' ') or (not vs):
                continue
            v = vs[0]
            try:
                if v2h[v] == c:
                    text[i] = 'ー'
            except KeyError:
                pass
    return ''.join(text)

def syllabic_nasal2vowel(text):
    # 撥音便を前の字の母音に変換
    text = list(text)
    # 母音をひらがなに変換する辞書
    v2h = {v: h for v, h in [('a', 'あ'), ('i', 'い'), ('u', 'う'), ('e', 'え'), ('o', 'お')]}
    for i, c in enumerate(text):
        if c in 'ん' and i > 0:
            vs = vowels(conv_h2a.do(text[i - 1]))
            if (text[i - 1] == ' ') or (not vs):
                continue
            v = vs[0]
            try:
                text[i] = v2h[v]
            except KeyError:
                pass
    return ''.join(text)

def replace_unromanizable_hiragana(text):
    # kakasi でローマ字に正しく変換できないひらがなを変換可能なひらがなに変換
    unromanizable2hiragana = {
        'くぁ': 'か', 'くぃ': 'き', 'くぅ': 'く', 'くぇ': 'け', 'くぉ': 'こ', 'てゃ': 'ちゃ', 'てゅ': 'ちゅ', 'てょ': 'ちょ', 'でゅ': 'ぢゅ', 'ふゅ': 'ひゅ', 'うぁ': 'わ', 'うぃ': 'い', 'うぇ': 'え', 'うぉ': 'お'
    }
    for key, value in unromanizable2hiragana.items():
        text = re.sub(r'%s' % key, value, text)
    return text

def preprocess(text, macron='macron_to_vowel'):
    # 前処理のまとめ
    text = delete_brackets(text)
    text = replace_unromanizable_hiragana(text)
    text = double_consonant2vowel(text)
    text = syllabic_nasal2vowel(text)
    text = re.sub('を', 'お', text)
    if macron == 'macron_to_vowel':
        text = macron2vowel(text)
    elif macron == 'double_vowel_to_macron':
        text = double_vowel2macron(text)
    # 最後に 'ん' が残った場合は消す (例: 'スクリーン' -> ['す', 'く', 'りー', 'ん'] -> ['す', 'く', 'りー'])
    text = re.sub(r'ん', '', text)
    return text

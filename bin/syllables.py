#!/usr/local/bin python3

import re
from pykakasi import kakasi

kakasi = kakasi()
kakasi.setMode('H', 'a')
conv = kakasi.getConverter()

def syllables(term):
    # 音節に区切る
    # まずは子音で分割
    regex = r'([^%s])' % 'あいうえおんぁぃぅぇぉゃゅょゎっー'
    term = re.sub(regex, '/\\1', term)
    # 次に長音符->母音、小文字の間を区切る
    regex = r'(ー)([%s])' % 'あいうえおんぁぃぅぇぉゃゅょゎっ'
    term = re.sub(regex, '\\1/\\2', term)
    # 撥音便, 長音符->母音, 撥音便の間を区切る
    regex = r'([んー])([あいうえおん])'
    term = re.sub(regex, '\\1/\\2', term)
    if term[0] == '/':
        term = term[1:]
    _syllables = term.split('/')
    # 次に連続する母音の間で分割
    regex = r"([aiueo])([aiueo])"
    syllables = []
    for syllable in _syllables:
        pos = 0
        while len(syllable) > 0 and pos < len(syllable) - 1:
            if re.search(regex, conv.do(syllable[pos:pos + 2])):
                syllables.append(syllable[:pos + 1])
                syllable = syllable[pos + 1:]
                pos = 0
            else:
                pos += 1
        if syllable:
            syllables.append(syllable)
    return syllables

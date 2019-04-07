#!/usr/local/bin python3

import numpy as np
import re
import json
from pykakasi import kakasi
from syllables import syllables
from speech_sound import consonants, vowels
from preprocess import preprocess

kakasi = kakasi()
kakasi.setMode('H', 'a')
conv = kakasi.getConverter()

def lyrics_syllable_genrator(lyrics):
    # 歌詞をフレーズ(文節)に区切る
    lyrics_phrases = lyrics.split()
    for i, p in enumerate(lyrics_phrases):
        # 長音符を母音に戻す
        syls = [preprocess(syl, macron='macron_to_vowel') for syl in syllables(p)]
        for j, syl in enumerate(syls):
            # 残りの音節
            remaining_syllables = preprocess(''.join(syls[j + 1:]), macron='double_vowel_to_macron')
            # 残りのフレーズ
            if remaining_syllables:
                remaining_phrases = [remaining_syllables] + lyrics_phrases[i + 1:]
            else:
                remaining_phrases = lyrics_phrases[i + 1:]
            # フレーズの消化率
            pcr = (j + 1) / len(syls)
            assert(0. <= pcr and pcr <= 1.)
            # フレーズ内の音節の位置
            pos = j
            yield syl, pcr, remaining_phrases, pos

def term_match_score(term, lyrics, phrase_comsumption_rate, hparams):
    # 単語の歌詞に対するスコア
    # まずは単語を長音符化
    term = preprocess(term, macron='double_vowel_to_macron')
    lyrics_syl_gen = lyrics_syllable_genrator(lyrics)
    # 長音符を母音に戻す
    term_syls = [preprocess(syl, macron='macron_to_vowel') for syl in syllables(term)]
    remaining_phrases = lyrics.split()
    old_pcr = phrase_comsumption_rate
    new_pcr = 1. - old_pcr
    # 音節ごとのスコアとレートのペア
    score_rates = []
    for i, syl in enumerate(term_syls):
        try:
            _syl, new_pcr, remaining_phrases, _pos = next(lyrics_syl_gen)
            score_rates.append(syllable_match_score(syl, _syl, i, _pos, hparams))
        except StopIteration:
            return -1e+6, ' '.join(remaining_phrases), new_pcr
    remaining_lyrics = ' '.join(remaining_phrases)
    # 単語に対するスコアを計算
    term_score = 0.
    min_score, syl_rate = 1e+6, 1.
    if score_rates:
        # syl_rate の降順にソート
        score_rates = sorted(score_rates, key=lambda x: x[1], reverse=True)
        for _score, _rate in score_rates:
            if _rate > 1.:
                syl_rate *= _rate
            else:
                syl_rate = _rate
            if _score < min_score:
                min_score = _score
        term_score += np.sum([s for s, r in score_rates]) * syl_rate
    else:
        min_score = 0.
    term_score = np.min([term_score, term_score * min_score])
    # フレーズ消化率によるレートの計算
    theta = hparams['theta_pcr']
    pcr_rate = (float(np.max([old_pcr, new_pcr]) == 1.) * (1. - theta) + theta) * (float(old_pcr * new_pcr == 1.) * (1. - theta) + theta)
    length_rate = len(term_syls)
    # スコアの最終的な評価
    score = term_score * pcr_rate * length_rate
    return score, remaining_lyrics, new_pcr

def syllable_match_score(syl_a, syl_b, term_syl_pos, lyrics_syl_pos, hparams):
    # 音節と音節の類似度
    roman_a, roman_b = conv.do(syl_a), conv.do(syl_b)
    c = consonant_match_score(consonants(roman_a), consonants(roman_b)) * (1. + float(term_syl_pos == 0) * float(lyrics_syl_pos == 0))
    v = vowel_match_score(vowels(roman_a), vowels(roman_b))
    coefs = hparams['syl_score_coefs']
    rates = hparams['syl_rates']
    if c >= 1. and v:
        syl_score = coefs[0] * (1. + c) * v
        syl_rate = rates[0]
    elif c < 1. and v:
        syl_score = coefs[1] * (1. + c) * v
        syl_rate = rates[1]
    elif 0. < c and c < 1. and (not v):
        syl_score = coefs[2] * c
        syl_rate = rates[2]
    else:
        syl_score = coefs[3]
        syl_rate = rates[3]
    return syl_score, syl_rate

def consonant_match_score(consonants_a, consonants_b):
    # 子音の類似度
    if ''.join(consonants_a) == ''.join(consonants_b):
        return 1.
    else:
        with open('../data/sim/consonants2sim.json') as consonants2sim_file:
            consonants2sim = json.load(consonants2sim_file)
        try:
            sim = consonants2sim[''.join(consonants_a)][''.join(consonants_b)]
        except KeyError:
            sim = 0.
        return sim

def vowel_match_score(vowels_a, vowels_b):
    # 母音の類似度
    if not (vowels_a or vowels_b):
        return np.exp(1.) - 1.
    else:
        return np.exp(
            np.sum([float(v_a == v_b) for v_a, v_b in zip(vowels_a, vowels_b)]) * np.min([len(vowels_a), len(vowels_b)]) / np.max([len(vowels_a), len(vowels_b)])
        ) - 1.

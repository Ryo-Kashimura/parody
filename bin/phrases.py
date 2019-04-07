#!/usr/local/bin python3

import re
import MeCab
import jaconv
from preprocess import preprocess

class Phrase:

    def __init__(self, terms, reading):
        self.terms = terms
        self.writing = ''.join(terms)
        if reading != '*':
            self.reading = reading
        else:
            self.reading = ''

def phrases(text):
    text = preprocess(text)
    tagger = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    phrases, phrase_term_tags = [], []
    for line in tagger.parse(text).split('\n'):
        tab_split = line.split('\t')
        if len(tab_split) == 2:
            term, tags = tab_split
            tags = tags.split(',')
        else:
            continue
        if tags[0] == '記号':
            continue
        if phrase_term_tags:
            previous_term, previous_tags = phrase_term_tags[-1]
            previous_is_not_noun = previous_tags[0] != '名詞'
            current_is_independent = (tags[0] == '名詞') or (tags[1] == '自立')
            if previous_is_not_noun and current_is_independent:
                phrases.append(
                    Phrase(
                        terms=''.join([term for term, tags in phrase_term_tags]),
                        reading=jaconv.kata2hira(''.join([tags[-2] for term, tags in phrase_term_tags]))
                    )
                )
                phrase_term_tags = [(term, tags)]
            else:
                phrase_term_tags.append((term, tags))
        else:
            phrase_term_tags.append((term, tags))
    if phrase_term_tags:
        phrases.append(
            Phrase(
                terms=''.join([term for term, tags in phrase_term_tags]),
                reading=jaconv.kata2hira(''.join([tags[-2] for term, tags in phrase_term_tags]))
            )
        )
    return phrases

def phrase_generator(text):
    for phrase in phrases(text):
        yield phrase

import codecs
import numpy as np
import random

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import ConditionalFreqDist
from nltk.util import ngrams
from scipy import stats

from utils import get_none_tuple, get_none_list
from realizer import Realizer

import csv
import pandas as pd


article = []
df = pd.DataFrame()
class NgramModel:
    
    def __init__(self, txt, sentences, lang='english'):
        self.text = txt # self._load_file(filepath)
        self.lang = lang
        self.sentences = sentences
    
    def _load_file(self, filepath):
        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            return f.read().replace('\n', ' ')
    
    def _select_nextword(self, ngram, cfdist=None):
        """ Select a word from a range of possibilities, given a frame of
        (n-1) words previously generated.
        """
        xk = np.arange(cfdist[ngram].B())
        pk = []
        candidates = []
        for next_word in cfdist[ngram]:
            candidates.append(next_word)
            pk.append(cfdist[ngram].freq(next_word))
        
        custm = stats.rv_discrete(values=(xk, pk))
        return candidates[custm.rvs()]
    
    def gen_text(self, n, nb_sents=None, nb_words=None):
        """ Enable text generation.
        """
        if n < 1:
            raise ValueError("n must be higher or equal than 1.")
        if nb_sents is None and nb_words is None:
            raise ValueError("nb_sents or nb_words must be set.")
        
        tok_sents = [get_none_list(n-1)+word_tokenize(sentence, language=self.lang) for sentence in self.sentences]
        words = []
        for tok_sent in tok_sents:
            words += tok_sent
        words += [None] # None is set as the end of a sentence
        
        # Compute conditional frequency distribution for each n-gram
        ngrams_ = ngrams(words, n)
        ngrams_cfd = ConditionalFreqDist((ngram[:-1], ngram[-1]) for ngram in ngrams_)
        
        frame = get_none_tuple(n-1)
        gen_tokens = []
        nb_sents_gen = 0
        while True:
            new_word = self._select_nextword(frame, ngrams_cfd)
            
            if new_word is None:
                nb_sents_gen += 1
                if nb_sents is not None and nb_sents_gen == nb_sents:
                    break
                frame = get_none_tuple(n-1)
                continue
            
            frame += (new_word,)
            frame = frame[1:]
            gen_tokens.append(new_word)
        
        realizer = Realizer(lang=self.lang)
        return realizer.realize(gen_tokens)

if __name__ == '__main__':
    count = 0
    with open('./data/input_texts.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            if count >= 5000:
                break
            sentences = sent_tokenize(row[1], 'english')
            if len(row[1]) == 0 or row[1] == "text" or len(sentences) < 20:
                print('Skipped')
                continue
            ngramModel = NgramModel(row[1], sentences, lang='english')
            text = ngramModel.gen_text(5, nb_sents=random.randrange(50,100))
            df = pd.concat([df, pd.DataFrame([{ "article": text, "labels": 0 }])], ignore_index=True)
            count += 1
    df.to_csv('./generated_ngrams/ngram_data_result.csv', index=False)
    print(count)
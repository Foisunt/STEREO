#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import multiprocessing
import gensim
import codecs

import logging  # Setting up the loggings to monitor gensim
logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)

from argParseDummy import args


# In[ ]:


class Sentences(object):
    def __init__(self, filename):
        self.filename = filename

    def __iter__(self):
        for line in codecs.open(self.filename, 'r', 'utf-8'):
            yield line.split()


def trainW2V(args, source_path, save_path, min_count):
    sentences = Sentences(source_path)
    cores = multiprocessing.cpu_count()
    model = gensim.models.Word2Vec(size=args.emb_dim, window=5,min_count = min_count, workers=cores-1, sg=1, iter=5)
    model.build_vocab(sentences, progress_per=1000000)
    model.train(sentences, total_examples=model.corpus_count, epochs=5, report_delay=5)
    model.save(save_path)


# In[ ]:


if __name__ == "__main__":
    args()
    print('Pre-training word embeddings ...')
    trainW2V(args)
    print('finished training Word2Vec on preprocessed data')


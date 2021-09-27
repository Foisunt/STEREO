#!/usr/bin/env python
#  -*- coding: utf-8  -*-

import logging

import gensim
import numpy as np
from sklearn.cluster import KMeans
from pathlib import Path


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class W2VEmbReader:

    def __init__(self, emb_path, emb_dim=None):
        pathStr = str(emb_path)
        logger.info('Loading embeddings from: ' + pathStr)
        self.embeddings = {}
        emb_matrix = []

        # loading pretrained vectors
        model = gensim.models.Word2Vec.load(pathStr)
        self.emb_dim = emb_dim

        for word in model.wv.vocab:
            self.embeddings[word] = list(model.wv[word])
            emb_matrix.append(list(model.wv[word]))

        if emb_dim is not None:
            assert self.emb_dim == len(self.embeddings['study'])

        self.vector_size = len(self.embeddings)
        self.emb_matrix = np.asarray(emb_matrix)

        logger.info('  #vectors: %i, #dimensions: %i' % (self.vector_size, self.emb_dim))

    def get_emb_given_word(self, word):

        try:
            return self.embeddings[word]
        except KeyError:
            return None

    def get_emb_matrix_given_vocab(self, vocab, emb_matrix):

        counter = 0.
        for word, index in vocab.items():
            try:
                emb_matrix[index] = self.embeddings[word]
                counter += 1
            except KeyError:
                pass

        logger.info(
            '%i/%i word vectors initialized (hit rate: %.2f%%)' % (counter, len(vocab), 100 * counter / len(vocab)))
        # L2 normalization
        norm_emb_matrix = emb_matrix / np.linalg.norm(emb_matrix, axis=-1, keepdims=True)

        return norm_emb_matrix

    def get_aspect_matrix(self, n_clusters):
        """
            We need it for initialization: KMeans-clustered word embeddings
        """

        km = KMeans(n_clusters=n_clusters)
        km.fit(self.emb_matrix)
        clusters = km.cluster_centers_

        # L2 normalization
        norm_aspect_matrix = clusters / np.linalg.norm(clusters, axis=-1, keepdims=True)
        return norm_aspect_matrix.astype(np.float32)

    def get_emb_dim(self):
        return self.emb_dim

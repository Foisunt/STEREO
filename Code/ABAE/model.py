#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import logging

import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
#tf.sysconfig.get_build_info()

from custom_layers import Attention, Average, WeightedSum, WeightedAspectEmb, MaxMargin, OrthRegularizer
from w2v_emb_reader import W2VEmbReader as EmbReader

# In[2]:


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)


# In[3]:


#vocab is a dictionary with word:index
def create_model(args, vocab, emb_path, k):
    
    maxlen = args.maxlen    
    vocab_size = len(vocab)

    # Inputs
    sentence_input = keras.layers.Input(shape=(maxlen,), dtype='int32', name='sentence_input')
    neg_input = keras.layers.Input(shape=(args.neg_size, maxlen), dtype='int32', name='neg_input')

    # Construct word embedding layer
    word_emb = keras.layers.Embedding(vocab_size, args.emb_dim, mask_zero=True, name='word_emb')

    # Compute sentence representation
    e_w = word_emb(sentence_input)
    y_s = Average()(e_w)
    att_weights = Attention(name='att_weights')([e_w, y_s])
    z_s = WeightedSum()([e_w, att_weights])

    # Compute representations of negative instances
    e_neg = word_emb(neg_input)
    z_n = Average()(e_neg)

    # Reconstruction
    p_t = keras.layers.Dense(k)(z_s)
    p_t = keras.layers.Activation('softmax', name='p_t')(p_t)
    r_s = WeightedAspectEmb(k, args.emb_dim,W_regularizer=OrthRegularizer(args, k), name='aspect_emb')(p_t) 

    # Loss
    loss = MaxMargin(name='max_margin')([z_s, z_n, r_s])
    model = keras.Model(inputs=[sentence_input, neg_input], outputs=loss)

    # Word embedding and aspect embedding initialization
    if emb_path:
        emb_reader = EmbReader(emb_path, emb_dim=args.emb_dim)
        logger.info('Initializing word embedding matrix')
        K.set_value(
            model.get_layer('word_emb').embeddings,
            emb_reader.get_emb_matrix_given_vocab(vocab, K.get_value(model.get_layer('word_emb').embeddings)))
        logger.info('Initializing aspect embedding matrix as centroid of kmean clusters')
        K.set_value(
            model.get_layer('aspect_emb').W,
            emb_reader.get_aspect_matrix(k))

    return model


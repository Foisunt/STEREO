#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import logging
from time import time
from tqdm import tqdm

import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
from tensorflow.keras.preprocessing import sequence

import codecs

import utils as U

from optimizers import get_optimizer
from model import create_model


# In[2]:


def sentence_batch_generator(data, batch_size):
    n_batch = len(data) // batch_size
    batch_count = 0
    np.random.shuffle(data)

    while True:
        if batch_count >= n_batch:
            np.random.shuffle(data)
            batch_count = 0

        batch = data[batch_count * batch_size: (batch_count + 1) * batch_size]
        batch_count += 1
        yield batch

def negative_batch_generator(data, batch_size, neg_size):
    data_len = data.shape[0]
    dim = data.shape[1]

    while True:
        indices = np.random.choice(data_len, batch_size * neg_size)
        samples = data[indices].reshape(batch_size, neg_size, dim)
        yield samples

def packed_batch_generator(genA, genB, batch_size):
    while True:
        yield ([next(genA), next(genB)], np.ones((batch_size, 1)))


# In[3]:


def train(args, vocab, train_x, emb_path, k=20, saveName = "modelDummyName"):
    #setting the logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    logger = logging.getLogger(__name__)
    
    #checking the path
    out_dir = args.out_dir_path  / (saveName+str(k))
    U.mkdir_p(out_dir)

    if args.seed>0:
        np.random.seed(args.seed)
    
    #pad data to model input length
    train_x = sequence.pad_sequences(train_x, maxlen=args.maxlen)
    print('Number of training examples: ', len(train_x))
    print('Length of vocab: ', len(vocab))
    
    #build model
    assert args.algorithm in {'rmsprop', 'sgd', 'adagrad', 'adadelta', 'adam', 'adamax'}
    optimizer = get_optimizer(args)
    logger.info('Building model')
    def max_margin_loss(y_true, y_pred):
        return K.mean(y_pred)
    t0 = time()
    model = create_model(args, vocab, emb_path, k)
    logger.info("Model built")
    
    #freeze the word embedding layer
    model.get_layer('word_emb').trainable = False
    model.compile(optimizer=optimizer, loss=max_margin_loss, metrics=[max_margin_loss])
    model.summary()
    
    #prepare batches
    logger.info('------------------------------------------------------------------------------------------------')
    vocab_inv = U.invert_vocab(vocab)
    sen_gen = sentence_batch_generator(train_x, args.batch_size)
    neg_gen = negative_batch_generator(train_x, args.batch_size, args.neg_size)
    gen = packed_batch_generator(sen_gen, neg_gen, args.batch_size)
    batches_per_epoch = len(train_x) // args.batch_size
    
    #train
    min_loss = float('inf')
    for ii in range(args.epochs):
        t0 = time()
        hist = model.fit(x=gen,initial_epoch=ii, epochs=ii+1, steps_per_epoch = batches_per_epoch)
        loss = hist.history["loss"][0]
        max_margin_loss = hist.history["max_margin_loss"][0]
        tr_time = time() - t0
        
        #new weights are better -> save
        if loss < min_loss:
            min_loss = loss
            word_emb = K.get_value(model.get_layer('word_emb').embeddings)
            aspect_emb = K.get_value(model.get_layer('aspect_emb').W)
            word_emb = word_emb / np.linalg.norm(word_emb, axis=-1, keepdims=True)
            aspect_emb = aspect_emb / np.linalg.norm(aspect_emb, axis=-1, keepdims=True)
            aspect_file = codecs.open(out_dir / 'aspect.log', 'w', 'utf-8')
            model.save_weights(out_dir / 'model_param')
            #print the representative words
            for ind in range(len(aspect_emb)):
                desc = aspect_emb[ind]
                sims = word_emb.dot(desc.T)
                ordered_words = np.argsort(sims)[::-1]
                desc_list = [vocab_inv[w] + ":" + str(sims[w]) for w in ordered_words[:25]]
                print('Aspect %d:' % ind)
                print(desc_list[0:3])
                aspect_file.write('Aspect %d:\n' % ind)
                aspect_file.write(' '.join(desc_list) + '\n\n')

    logger.info('Epoch %d, train: %is' % (ii, tr_time))
    logger.info('Total loss: %.4f, max_margin_loss: %.4f, ortho_reg: %.4f' % (loss, max_margin_loss, loss - max_margin_loss))
    return model


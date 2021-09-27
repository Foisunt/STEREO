#!/usr/bin/env python
# coding: utf-8

# In[1]:


import codecs
import operator
import re
import json

from os.path import isfile
from argParseDummy import args
from pathlib import Path
from tqdm import tqdm

# In[2]:


num_regex = re.compile(r'^[+-]?[0-9]+\.?[0-9]*$')

def is_number(token):
    return bool(num_regex.match(token))


# In[3]:


def create_vocab(source_path, save_path, args = args()):
    vocab_size=args.vocab_size
    maxlen=args.maxlen
    total_words, unique_words = 0, 0
    word_freqs = {}

    fin = codecs.open(source_path, 'r', 'utf-8')
    for line in tqdm(fin):
        words = line.split()
        if maxlen > 0 and len(words) > maxlen:
            continue

        for w in words:
            if not is_number(w):
                try:
                    word_freqs[w] += 1
                except KeyError:
                    unique_words += 1
                    word_freqs[w] = 1
                total_words += 1

    print('   %i total words, %i unique words' % (total_words, unique_words))
    Path("savedDataAndModels/wordFreqs.json").write_text(json.dumps(word_freqs))#for plotting stuff
    sorted_word_freqs = sorted(word_freqs.items(), key=operator.itemgetter(1), reverse=True)

    vocab = {'<pad>': 0, '<unk>': 1, '<num>': 2}
    index = len(vocab)

    for word, _ in sorted_word_freqs:
        vocab[word] = index
        index += 1
        if vocab_size > 0 and index > vocab_size + 2:
            break
    if vocab_size > 0:
        print('  keep the top %i words' % vocab_size)

    # Write (vocab, frequence) to a txt file
    vocab_file = codecs.open(save_path, mode='w', encoding='utf8')
    sorted_vocab = sorted(vocab.items(), key=operator.itemgetter(1))
    for word, index in sorted_vocab:
        if index < 3:
            vocab_file.write(word + '\t' + str(0) + '\n')
            continue
        vocab_file.write(word + '\t' + str(word_freqs[word]) + '\n')
    vocab_file.close()

    return vocab


# In[4]:

#reads a file with text, matches the occuring words with the dictionary vocab and returns a list of dict tokens
def read_trainingData(source, vocab, maxlen, numLines):
    num_hit, unk_hit, total = 0., 0., 0.
    maxlen_x = 0
    data_x = []

    fin = codecs.open(Path(source), 'r', 'utf-8')
    for i,line in enumerate(fin):
        if (i==numLines):
            break
        words = line.strip().split()
        if maxlen > 0 and len(words) > maxlen:
            continue
        if not len(words):
            continue

        indices = []
        for word in words:
            if is_number(word):
                indices.append(vocab['<num>'])
                num_hit += 1
            elif word in vocab:
                indices.append(vocab[word])
            else:
                indices.append(vocab['<unk>'])
                unk_hit += 1
            total += 1

        data_x.append(indices)
        if maxlen_x < len(indices):
            maxlen_x = len(indices)

    print('   <num> hit rate: %.2f%%, <unk> hit rate: %.2f%%' % (100 * num_hit / total, 100 * unk_hit / total))
    return data_x, maxlen_x


# In[5]:

def get_vocab(vocab_path):
    print(vocab_path)
    assert isfile(vocab_path)
    print("Loading vocab ...")
    vocabFile = open(Path(vocab_path), "r", encoding='utf8')
    vocab = vocabFile.read()
    vocab = eval(vocab) # because reading the .json gives a string like '{"<unk>":1, "<num>:2" .... }'
    vocabFile.close()
    print("Finished loading vocab ...")
    return vocab



#reads extracted data (containing stats)
# def get_extracted(args, vocab):
#     if not args.extractedProcessed_path.exists():
#         process_extracted(args)
#     trainExtr_x, maxlen_x = read_dataset(args.extractedProcessed_path, vocab, args.maxlen,-1)
#     return trainExtr_x, maxlen_x


# In[6]:


if __name__ == "__main__":
    args()
    vocab, train_x, maxlen = get_data()
    print(len(train_x))
    print(maxlen)

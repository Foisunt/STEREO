#!/usr/bin/env python
# coding: utf-8

# In[2]:


#!/usr/bin/env python
#  -*- coding: utf-8  -*-

import tensorflow.keras.optimizers as opt


# In[3]:


def get_optimizer(args):

    #clipvalue = 0 #tf 2.x seems to behave differently than 1.x with clipnorm and clipvalue.
    #clipnorm = 10
    #it is also bugged in tf 2.0 to 2.2 releases https://github.com/tensorflow/tensorflow/issues/33929

    if args.algorithm == 'rmsprop':
        optimizer = opt.RMSprop(lr=0.001, rho=0.9, epsilon=1e-06, clipnorm=clipnorm, clipvalue=clipvalue)
    elif args.algorithm == 'sgd':
        optimizer = opt.SGD(lr=0.01, momentum=0.0, decay=0.0, nesterov=False, clipnorm=clipnorm, clipvalue=clipvalue)
    elif args.algorithm == 'adagrad':
        optimizer = opt.Adagrad(lr=0.01, epsilon=1e-06, clipnorm=clipnorm, clipvalue=clipvalue)
    elif args.algorithm == 'adadelta':
        optimizer = opt.Adadelta(lr=1.0, rho=0.95, epsilon=1e-06, clipnorm=clipnorm, clipvalue=clipvalue)
    elif args.algorithm == 'adam':
        #optimizer = opt.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, clipnorm=clipnorm, clipvalue=clipvalue)
        optimizer = opt.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08)
    elif args.algorithm == 'adamax':
        optimizer = opt.Adamax(lr=0.002, beta_1=0.9, beta_2=0.999, epsilon=1e-08, clipnorm=clipnorm,
                               clipvalue=clipvalue)
    else:
        raise Exception("Can't find optimizer " + args.algorithm)

    return optimizer


#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np

#import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.backend as K
#tf.sysconfig.get_build_info()




#calculates ai for the attention mechanism, implements equations 2 and 3 from the paper
#gets [[ew], ys]
class Attention(keras.layers.Layer):
    def __init__(self,
                 W_regularizer=None,
                 b_regularizer=None,
                 W_constraint=None,
                 b_constraint=None,
                 bias=True, **kwargs):
        
        self.supports_masking = True
        self.init = keras.initializers.get('glorot_uniform')

        self.W_regularizer = keras.regularizers.get(W_regularizer)
        self.b_regularizer = keras.regularizers.get(b_regularizer)
        self.W_constraint = keras.constraints.get(W_constraint)
        self.b_constraint = keras.constraints.get(b_constraint)

        self.bias = bias
        super(Attention, self).__init__(**kwargs)
    
    def build(self, input_shape):
        assert type(input_shape) == list
        assert len(input_shape) == 2

        self.steps = input_shape[0][1]

        self.W = self.add_weight(shape = (input_shape[0][-1], input_shape[1][-1]),
                                 initializer=self.init,
                                 name='{}_W'.format(self.name),
                                 regularizer=self.W_regularizer,
                                 constraint=self.W_constraint)
        if self.bias:
            self.b = self.add_weight(shape = (1,),
                                     initializer='zero',
                                     name='{}_b'.format(self.name),
                                     regularizer=self.b_regularizer,
                                     constraint=self.b_constraint)
        self.built = True
        
    def compute_mask(self, input_tensor, mask=None):
        return None

    def call(self, input_tensor, mask=None):
        x = input_tensor[0]
        y = input_tensor[1]
        try:
            mask = mask[0]
        except Exception as e:
            print("mask none")
            print(e)
            print()
            raise e

        y = K.transpose(K.dot(self.W, K.transpose(y)))
        y = K.expand_dims(y, axis=-2)
        y = K.repeat_elements(y, self.steps, axis=1)
        eij = K.sum(x * y, axis=-1)

        if self.bias:
            b = K.repeat_elements(self.b, self.steps, axis=0)
            eij += b

        eij = K.tanh(eij)
        a = K.exp(eij)

        if mask is not None:
            a *= K.cast(mask, K.floatx())

        a /= K.cast(K.sum(a, axis=1, keepdims=True) + K.epsilon(), K.floatx())
        return a
    
    def get_output_shape_for(self, input_shape):
        return (input_shape[0][0], input_shape[0][1])

    def compute_output_shape(self, input_shape):
        return input_shape[0][0], input_shape[0][1]
    
    


# In[ ]:


#gets impu tensor [x,a] and returns x*a
class WeightedSum(keras.layers.Layer):
    def __init__(self, **kwargs):
        self.supports_masking = True
        super(WeightedSum, self).__init__(**kwargs)

    def call(self, input_tensor, mask=None):
        assert type(input_tensor) == list
        assert type(mask) == list

        x = input_tensor[0]
        a = input_tensor[1]

        a = K.expand_dims(a)
        weighted_input = x * a

        return K.sum(weighted_input, axis=1)

    def get_output_shape_for(self, input_shape):
        return (input_shape[0][0], input_shape[0][-1])

    def compute_mask(self, x, mask=None):
        return None

    def compute_output_shape(self, input_shape):
        return self.get_output_shape_for(input_shape)


# In[ ]:

class WeightedAspectEmb(keras.layers.Layer):
    def __init__(self, input_dim, output_dim,
                 init='uniform', input_length=None,
                 W_regularizer=None, **kwargs):
        super(WeightedAspectEmb, self).__init__(**kwargs)
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.init = keras.initializers.get(init)
        self.input_length = input_length
        self.W_regularizer = W_regularizer

    def build(self, input_shape):
        self.W = self.add_weight(shape = (self.input_dim, self.output_dim),
                                 initializer = self.init, 
                                 name='{}_W'.format(self.name),
                                 regularizer = self.W_regularizer)

    def call(self, x, mask=None):
        return K.dot(x, self.W)


# In[ ]:


class Average(keras.layers.Layer):
    def __init__(self, **kwargs):
        self.supports_masking = True
        super(Average, self).__init__(**kwargs)

    def call(self, x, mask=None):
        if mask is not None:
            mask = K.cast(mask, K.floatx())
            mask = K.expand_dims(mask)
            x = x * mask
        return K.sum(x, axis=-2) / K.sum(mask, axis=-2)

    def get_output_shape_for(self, input_shape):
        return input_shape[0:-2] + input_shape[-1:]

    def compute_mask(self, x, mask=None):
        return None

    def compute_output_shape(self, input_shape):
        return self.get_output_shape_for(input_shape)


# In[ ]:


class MaxMargin(keras.layers.Layer):
    def __init__(self, **kwargs):
        super(MaxMargin, self).__init__(**kwargs)

    def call(self, input_tensor, mask=None):
        z_s = input_tensor[0]
        z_n = input_tensor[1]
        r_s = input_tensor[2]

        z_s = K.l2_normalize(z_s, axis=-1)
        z_n = K.l2_normalize(z_n, axis=-1)
        r_s = K.l2_normalize(r_s, axis=-1)

        steps = z_n.shape[1]

        pos = K.sum(z_s * r_s, axis=-1, keepdims=True)
        pos = K.repeat_elements(pos, steps, axis=1)
        r_s = K.expand_dims(r_s, axis=-2)
        r_s = K.repeat_elements(r_s, steps, axis=1)
        neg = K.sum(z_n * r_s, axis=-1)

        loss = K.cast(K.sum(K.maximum(0., (1. - pos + neg)), axis=-1, keepdims=True), K.floatx())
        return loss

    def compute_mask(self, input_tensor, mask=None):
        return None

    def get_output_shape_for(self, input_shape):
        return (input_shape[0][0], 1)

    def compute_output_shape(self, input_shape):
        return input_shape[0][0], 1

    
# orthogonal regularization for aspect embedding matrix
class OrthRegularizer(keras.regularizers.Regularizer):
    def __init__(self, args, k):
        self.id_mat = K.eye(k)
        self.args = args
        
    def __call__(self, weight_matrix):
        w_n = weight_matrix / K.cast(K.epsilon() + K.sqrt(K.sum(K.square(weight_matrix), axis=-1, keepdims=True)), K.floatx())
        reg = K.sum(K.square(K.dot(w_n, K.transpose(w_n)) - self.id_mat ))
        return self.args.ortho_reg * reg

    def get_config(self):
        return {"id_mat":self.id_mat}
    
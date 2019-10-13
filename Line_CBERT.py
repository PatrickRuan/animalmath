#! -*- coding:utf-8 -*-

import json
import numpy as np
import pandas as pd
from random import choice
from keras_bert import load_trained_model_from_checkpoint, Tokenizer
import re, os
import codecs


maxlen = 100
config_path ='cbert1/chinese_L-12_H-768_A-12/bert_config.json'
checkpoint_path = 'cbert1/chinese_L-12_H-768_A-12/bert_model.ckpt'
dict_path = 'cbert1/chinese_L-12_H-768_A-12/vocab.txt'


token_dict = {}

with codecs.open(dict_path, 'r', 'utf8') as reader:
    for line in reader:
        token = line.strip()
        token_dict[token] = len(token_dict)


class OurTokenizer(Tokenizer):
    def _tokenize(self, text):
        R = []
        for c in text:
            if c in self._token_dict:
                R.append(c)
            elif self._is_space(c):
                R.append('[unused1]') # space类用未经训练的[unused1]表示
            else:
                R.append('[UNK]') # 剩余的字符是[UNK]
        return R

tokenizer = OurTokenizer(token_dict)



def seq_padding(X, padding=0):
    L = [len(x) for x in X]
    ML = max(L)
    return np.array([
        np.concatenate([x, [padding] * (ML - len(x))]) if len(x) < ML else x for x in X
    ])


class data_generator:
    def __init__(self, data, batch_size=32):
        self.data = data
        self.batch_size = batch_size
        self.steps = len(self.data) // self.batch_size
        if len(self.data) % self.batch_size != 0:
            self.steps += 1
    def __len__(self):
        return self.steps
    def __iter__(self):
        while True:
            #idxs = np.arange(len(self.data))
            idxs = range(len(self.data))
            idxs = list(range(len(self.data)))
            np.random.shuffle(idxs)
            X1, X2, Y = [], [], []
            for i in idxs:
                d = self.data[i]
                text = d[0][:maxlen]
                x1, x2 = tokenizer.encode(first=text)
                y = d[1]
                X1.append(x1)
                X2.append(x2)
                Y.append([y])
                if len(X1) == self.batch_size or i == idxs[-1]:
                    X1 = seq_padding(X1)
                    X2 = seq_padding(X2)
                    Y = seq_padding(Y)
                    yield [X1, X2], Y
                    [X1, X2, Y] = [], [], []


from keras.layers import *
from keras.models import Model
import keras.backend as K
from keras.optimizers import Adam


bert_model = load_trained_model_from_checkpoint(config_path, checkpoint_path, seq_len=None)

for l in bert_model.layers:
    l.trainable = True

x1_in = Input(shape=(None,))
x2_in = Input(shape=(None,))

x = bert_model([x1_in, x2_in])
x = Lambda(lambda x: x[:, 0])(x)
p = Dense(1, activation='sigmoid')(x)

model = Model([x1_in, x2_in], p)
model.compile(
    loss='binary_crossentropy',
    optimizer=Adam(1e-5), # 用足够小的学习率
    metrics=['accuracy']
)
h5_path = 'cbert1/05_02F2.h5'
model.load_weights(h5_path)
model._make_predict_function()
# amazing  https://github.com/keras-team/keras/issues/6462



f_neg = 'cbert1/neg.xls'
f_pos = "cbert1/pos.xls"
neg = pd.read_excel(f_neg, header=None)
pos = pd.read_excel(f_pos, header=None)




def sentence_inference(x):
  test = x
  maxlen =100
  d=[test,0]
  test=d[0][:maxlen]
  x1, x2 = tokenizer.encode(first=str(test))
  x1=[x1]
  x2=[x2]
  test =[x1, x2]
  model.predict(test)
  if model.predict(test) >=0.5:
    y = 1
  else: y=0
  #print(f'{x} \n {y}')
  return y, model.predict(test)




#!pip install line-bot-sdk

from flask import Flask, request, abort
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

#token
line_bot_api = LineBotApi('4UMZ57VIP0FSCa62WsYUUHwQ/KlZBNcyNTEzuOlyAfaIOMPjGSJKyAf4P6KDg8d1kHwImrxNg3fcXvIjxpioTu8OkQKbfI0lsiVcQ9BzkcLt0VkrRLfwgvSsS9wzAxnn48ZPjXHGXUYwUgWrPukIbgdB04t89/1O/w1cDnyilFU=')
#secret
handler = WebhookHandler('182080c576d83b01a786616b8abd1b33')

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    data = json.loads(body)
    y, s = sentence_inference(data['events'][0]['message']['text'])
    if y == 1:
        y = "正面評價"
    else: y = "負評"
    
    app.logger.info("Request body: " + body)
    try:
        line_bot_api.reply_message(data['events'][0]['replyToken'], TextSendMessage(text=y))
        print('2')

    except InvalidSignatureError:
        print('pre_3')
        abort(400)
        print('3')

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print('2_call')
    print(event)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    #app.run()
    app.run(host='0.0.0.0', port=8080, threaded=True)
    
    



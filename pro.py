import os
import time
import collections
import pandas as pd
import numpy as np
from collections import Counter
from google_images_download import google_images_download   #importing the library
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

class Drug(object):
    """__init__() functions as the class constructor"""
    def __init__(self, name=None, text=None, label=None):
        self.name = name
        self.text = text
        self.label = label  


def download_images(label, key_words):
  response = google_images_download.googleimagesdownload()   #class instantiation
  argument = {"keywords": key_words, "limit":5, "image_directory": "images", "prefix": label} 
  paths = response.download(argument)

#split line in dm2000, then get finename, textContents and labels
def split_fname_texts(line):
  obj = {}
  if '.jpg' in line:
    obj['name'] = line.split('.jpg', 1)[0] + '.jpg'
    obj['text'] = line.split('.jpg', 1)[1]
    obj['label'] = line.split('_', 1)[0]
  return obj

def construt(filepath):
  name_list, string_list = [], []
  with open(filepath, 'r') as rf:  
    for line in rf:
      if '.jpg' in line:
        splitted = line.split('.jpg', 1)
        name_list.append(splitted[0][:-1])
        string_list.append(splitted[1])

def split_keywords(line):
  obj = {}
  if '_' in line:
    split = line.split('_', 1)
    obj['label'] = split[0]
    obj['keywords'] = split[1] 
  return obj
   
def frequency_distribution(druglist):
  label_list = []
  for item in druglist:
    label_list.append(item.label)
  counter=collections.Counter(label_list)
  new_counter = collections.Counter(counter.values())
  return new_counter

def frequency(druglist, a, b):
  print('Drugs containing more than images between ' + str(a) + ' and ' + str(b))
  label_list = []
  for item in druglist:
    label_list.append(item.label)
  counter=collections.Counter(label_list)
  result = []
  count_list = []
  for item in counter:
    if counter[item] > a and counter[item] < b:
      result.append(item)
      count_list.append(counter[item])
  df = pd.DataFrame({'count':count_list})
  return result

def cal_top(df, n, test_str):
  #samples = df.sample(m)
  #for index, row in samples.iterrows():
    t_label = 'label'
    obj = test_str
    list_label, list_score, list_text,list_name = [], [], [], []
    for i, r in df.iterrows():
      list_label.append(r['label'])
      list_name.append(r['name'])
      list_text.append(r['text'])
      list_score.append((fuzz.partial_ratio(obj, r['text']) + fuzz.ratio(obj, r['text']))/2)
      #list_score.append(fuzz.partial_ratio(obj, r['text']))
    result_df = pd.DataFrame({'result_label': list_label, 'result_score': list_score, 'result_text': list_text, 'result_name': list_name})
    result_df = result_df.sort_values(by=['result_score'], ascending=False).head(n)
    result_df1 = result_df.groupby('result_label')['result_score'].sum().reset_index(name ='total_score')
    result_df1 = result_df1.sort_values(by=['total_score'], ascending=False)
    scores = result_df1['total_score'].tolist()
    norm = [round(float(i)/sum(scores), 2) for i in scores]
    result_df1['probability'] = norm
    '''
    print ('True label of test drug: ' + t_label + '\n')
    print ('Following are most similar texts from images:' + '\n')
    print (result_df)
    print ('Following are candidates from reference dataset:' + '\n')
    print (result_df1)
    '''
    return result_df, result_df1
def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=0) # only difference
'''
drug_list=[]#list of drugs to store fileName,Text and lablel information
with open('data/ocr.txt', 'r') as rf:
  for line in rf:
    split_r = split_fname_texts(line)
    drug_list.append(Drug(split_r['name'], split_r['text'], split_r['label']))
print len(drug_list)
df = pd.DataFrame([vars(f) for f in drug_list])
df.columns = ["label", "name", "text"]
#frequency(drug_list, 2)
final_list = frequency(drug_list, 4)#get the records with count more than 3
print len(final_list)
#print df['label']
df = df[df['label'].isin(final_list)]
print len(df)
cal_top(df, 15, 2)
'''




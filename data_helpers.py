import os
import numpy as np
import pandas as pd
import re
import itertools
from collections import Counter
import pyocr
import pyocr.builders
import PIL
from PIL import Image
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def clean_str(string):

    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

def process_raw(string):    
    string = string.replace('\n', ' ') #replace line break with space
    string = re.sub(' +',' ', string) #replace all extra white spaces
    #return string.strip().lower()
    return string

def ext_txt(imgf, language, record, tool):
    record['file'] = os.path.basename(imgf)
    txt = ' '
    try:
      txt = tool.image_to_string(Image.open(imgf), lang=language, builder=pyocr.builders.TextBuilder())
    except: 
      print("An exception occurred")    
    clean = process_raw(txt)
    return clean

def obj_ext_txt(imgf, img_obj, language, record, tool):
    record['file'] = os.path.basename(imgf)
    txt = ' '
    try:
      txt = tool.image_to_string(img_obj, lang=language, builder=pyocr.builders.TextBuilder())
    except:
      print("An exception occurred") 
    clean = process_raw(txt)
    return clean

def similarity(a, b):
    tokens_a = a.split()
    tokens_b = b.split()
    inter_len = len(list(set(tokens_a) & set(tokens_b)))
    ratio = inter_len/min(len(tokens_a), len(tokens_b))
    return ratio

def recog_crop(imagepath, language, record, tool):
    path, imagename = os.path.split(imagepath)
    #imagename = os.path.basename(imagepath)
    crop_file = os.path.join(path, 'res_' + os.path.splitext(imagename)[0] + '.txt')
    crop_list = []
    image_obj = Image.open(imagepath)
    with open(crop_file, 'r') as crops:
      for line in crops:
        crop = line.split(',')
        crop = list(map(int, crop))
        crop_list.append(crop)
    crop_list = sorted(crop_list, key=lambda x: x[3]-x[1])
    crop_list.reverse()
    res_text = ''
    #Following constrict the length of list
    #if len(crop_list) > 4:
    #  crop_list = crop_list[:5]
    for idx, val in enumerate(crop_list):
      #if (val[2]-val[0]) > 2*(val[3]-val[1]):
      cropped_image = image_obj.crop(val)
      res = obj_ext_txt(imagepath, cropped_image, language, record, tool)
      res_text += res + ' '
    return res_text

def compare_gt(result):
    df = pd.read_csv(result)
    fnames = df['file'].tolist()
    content = df['eng'].tolist()
    newfnames, gt, tessract, rec_tess, tess_score,rec_tess_score= [],[],[],[],[],[]
    index = 0
    s = ''
    for idx, val in enumerate(fnames):
      if '_cro_pped_' not in val:
        if s!='':
          rec_tess.append(s)
          s = ''
        newfnames.append(val)
        tessract.append(content[idx])
        with open('data/demo/' + os.path.basename(val)+'.txt', 'r') as gtf:
          gt.append(gtf.read())
      else:
        s += (str(content[idx])+' ')
    rec_tess.append(s)
    for idx, val in enumerate(gt):
      print (fuzz.partial_ratio(str(tessract[idx]), str(val)))
      print (fuzz.partial_ratio(str(rec_tess[idx]), str(val)))
    odf = pd.DataFrame()
    odf['file'] = newfnames
    odf['ground_truth'] = gt 
    odf['tess'] = tessract
    #odf['tess_score'] = tess_score
    odf['rec_tess'] = rec_tess
    #odf['rec_tess_score'] = rec_tess_score

    odf.to_csv('compare_gt.csv', encoding='utf_8_sig', index=False)
                      
def filter_images(result, filters):
		with open(filters) as todelist:
				content = todelist.readlines()
		content = [x.strip() for x in content]
		df = pd.read_csv(result)
		englist = df['eng']
		mylist = []
		for l in englist:
				ll = re.sub(' +',' ', l)
				mylist.append(ll)
		df['eng'] = mylist
		
		count = 0
		for index, row in df.iterrows():
#				if any(map(row['eng'].startswith, content)):
				if any(s in row['eng'] for s in content):
						count += 1
						print(row['file'])
						#os.remove(row['file'])		

#for s in content:
#						if row['eng'].startswith(s):
#								print(s)
#								count += 1
#								break
		print(len(content))
		print(df.count())		
		print(count)
		#dedf = df[df['eng'].str.startswith('> 2 ere th, three times daily or as directed by phy')]
		#print(dedf.count())

#filter_images('result.csv', 'todelete.txt')


#compare_gt('result.csv')

    

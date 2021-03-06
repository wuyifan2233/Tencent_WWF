# -*- coding: UTF-8 -*-
from math import e
import os
from numpy.lib.type_check import _imag_dispatcher
import pandas as pd
import shutil
import numpy as np
import cv2

from tqdm import tqdm
import pyfastcopy
import json,sklearn
from sklearn.model_selection import train_test_split



def main():
    
    dataset_name='top14-part5'
    check_txt=r"D:/WWF_Det\WWF_Det\Drop_txt/top14-p5-all.txt"
    stat_csv='D:/WWF_Det/WWF_Det/Pos_data_stat/top14-part5-dataset-stat.csv'

    #"D:\WWF\data-check-list\check_list\check-all.txt"

    image_base,label_base='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/allset/images/','D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/allset/labels/'
    
    x,y=os.listdir(image_base),os.listdir(label_base)
    img_id=[i.replace('.jpg','',1)for i in x]
    txt_id=[i.replace('.txt','',1)for i in y]

    err_id=np.unique(np.array([line.replace('\n','',1) for line in open(check_txt)])).tolist()
    for i in err_id:
         check_path=image_base+i+".jpg"
         assert os.path.exists(check_path),check_path+'not exists'
    droped_id=[i for i in txt_id if i in err_id]
    valuable_id=[i for i in txt_id if i not in err_id]
    kongpai_id=[i for i in img_id if i not in txt_id]
    fake_kongpai_id=[i for i in err_id if i not in droped_id]
    true_kongpai_id=[i for i in kongpai_id if not i in fake_kongpai_id]
    
    print("Allset Num: "+str(len(img_id)))
    print("Valuablset Num: "+str(len(valuable_id)))
    print("Defected Num: "+str(len(err_id)))
    print('Kongpai Num: '+str(len(kongpai_id)))
    print('Fake_kongpai Num: '+str(len(fake_kongpai_id)))
    print('True Kongpai Num: '+str(len(true_kongpai_id)))

    assert len(img_id)==len(valuable_id)+len(err_id)+len(true_kongpai_id), 'Number Mismatch!'
    assert len(kongpai_id)==len(fake_kongpai_id)+len(true_kongpai_id), 'Kongpai Num Mismatch!'
    for i in valuable_id:
        check_path=label_base+i+'.txt'
        assert os.path.exists(check_path),check_path+' not exists'
    
    print("Actual-droped Num: "+str(len(droped_id)))
    data={
        'Dataname':[dataset_name],
        'Allset_Num':[len(img_id)],
        'Valuable_Num':[len(valuable_id)],
        'Error_Num':[len(err_id)],
        'Actual_Kongpai_Num':[len(true_kongpai_id)],
        'UnKongpai_Num':[len(txt_id)],
        'Droped_unKongpai_Num':[len(droped_id)],
        'Kongpai_Num':[len(kongpai_id)],
        'Fake_Kongpai_Num':[len(fake_kongpai_id)]
    }
    df_store=pd.DataFrame(data)
    df_store.to_csv(stat_csv)
    x_dir='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/valuableset/images/'
    y_dir='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/valuableset/labels/'
    x_err='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/errset/'
    x_empty='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/emptyset/'
    if not os.path.exists(x_dir): os.makedirs(x_dir)
    if not os.path.exists(y_dir): os.makedirs(y_dir)
    if not os.path.exists(x_err): os.makedirs(x_err)
    if not os.path.exists(x_empty): os.makedirs(x_empty)
    for ID in tqdm(valuable_id):
        imgID=ID+'.jpg'
        txtID=ID+'.txt'
        shutil.copyfile(image_base+imgID,x_dir+imgID)
        shutil.copyfile(label_base+txtID,y_dir+txtID)

    for ID in tqdm(err_id):
        imgID=ID+'.jpg'
        shutil.copyfile(image_base+imgID,x_err+imgID)

    for ID in tqdm(true_kongpai_id):
        imgID=ID+'.jpg'
        shutil.copyfile(image_base+imgID,x_empty+imgID)
   
if __name__ == "__main__":
    
    main()
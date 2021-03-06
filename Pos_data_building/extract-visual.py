# -*- coding: UTF-8 -*-
import os
import pandas as pd
import shutil
import numpy as np
import cv2
from tqdm import tqdm
import pyfastcopy
import json

from xml.etree import ElementTree
from PIL import Image, ImageDraw, ImageFont
from collections import Counter

def cate_replacement(cate_name):
        ori_class=['laoshu','gaoyuanxuetu','chihu+shidiao','hongcuiya','paolu','huangyou']
        rename_class=['shu','gaoyuantu','chihu','hongzuishanya','pao','xiangyou']
        if cate_name in ori_class:
            for a,b in zip(ori_class,rename_class):
                if cate_name ==a:
                    cate_name=b
        return cate_name

def path_replacement(file_path,dataset_name):
    if dataset_name in ['top14-part2','top14-part1']:
        file_path=file_path.replace('/Raw_Data/','/Raw_Data/top14-p1-p2/',1)
        #file_path=file_path.replace('D:/top14-dataset-part1','D:/WWF_Det/WWF_Data/Raw_Data/top14-p1-p2')
    else:
        file_path=file_path.replace('-part','-p',1)
        file_path=file_path.replace('-raw/','/',1)
        file_path=file_path.replace('primary_supplement','sup9-p1')
    return file_path

def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    # 判断是否为opencv图片类型
    if (isinstance(img, np.ndarray)):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype('simsun.ttc', textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def extract_data(dataset_name,data_set='D:/WWF_Det/WWF_Data/Raw_Data/'):
    csv_file='D:/WWF_Det/WWF_Det/Raw_annoations/'+dataset_name+'.csv'
    df=pd.read_csv(csv_file)

    # cate_class=['baichunlu','chihu','zanghu','maoniu','ma','mashe','yang','yanyang','person','xuebao','malu','lanmaji','gaoyuanshanchun','gaoyuantu', \
    #     'lang','pao','shidiao','sheli','lv','chai','hanta','zongxiong','huangmomao',
    #     'anfuxueji','banchishanchun','banweizhenji','chihu+shidiao','danfuxueji','gaoyuanxuetu','gou','hongcuiya','hongsun','hongzuishanya','honweiqu','huangyou','huwujiu',
    #     'kuang','laoshu','maque','niaolei','paolu','shanque','shiji','shitu','shu','shutu','wuya','xiangyou','xique','xuege','xueji','xuezhi','you',
    #     'zongbeidong'
    #     ]
    cate_class=['baichunlu','chihu','zanghu','maoniu','ma','mashe','yang','yanyang','person','xuebao','malu','lanmaji','gaoyuanshanchun','gaoyuantu', \
        'lang','pao','shidiao','sheli','lv','chai','hanta','zongxiong','huangmomao',
        'anfuxueji','banchishanchun','banweizhenji','danfuxueji','gou','hongzuishanya','hongsun','honweiqu','xiangyou','huwujiu',
        'kuang','shu','maque','niaolei','shanque','shiji','shitu','shutu','wuya','xique','xuege','xueji','xuezhi','you',
        'zongbeidong'
        ]
    for index, row in tqdm(df.iterrows(), desc='Extracting data'):
        timu_data=json.loads(row['题目数据'])
        pic_id=row['题目ID']
        file_path=data_set+timu_data['Path']
        image_folder='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/allset/images/'
        text_folder='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/allset/labels/'
        if not os.path.exists(image_folder): 
            os.makedirs(image_folder, exist_ok = True)
        if not os.path.exists(text_folder): 
            os.makedirs(text_folder, exist_ok = True)
        file_path=path_replacement(file_path,dataset_name)

        assert os.path.exists(file_path),file_path

        index_pos=0 if dataset_name in ['top14-part2','top14-part1'] else 1
        cate=timu_data['Path'].split('/')[index_pos]
        image_name=str(pic_id)+'.jpg'
        label_dict=json.loads(row['标注答案'])
        shutil.copyfile(file_path,image_folder+image_name)
        if len(label_dict.keys()):
            bboxes=label_dict['objects']
            img = cv2.imread(file_path)
            if img is None:
                print(file_path)
                continue
            imgy,imgx=img.shape[:2]
            txt_path=text_folder+os.path.splitext(image_name)[0]+'.txt'
            
            with open(txt_path, 'w') as f:
                for bbox in bboxes:
                    x_list=[bbox['data'][i]['x'] for i in range(0,4)]
                    y_list=[bbox['data'][i]['y'] for i in range(0,4)]
                    topleft=[max(min(x_list),0),max(min(y_list),0)]
                    bottomright=[min(max(x_list),imgx-1),min(max(y_list),imgy-1)]
                    center_x=((topleft[0]+bottomright[0])/2)/imgx
                    center_y=((topleft[1]+bottomright[1])/2)/imgy
                    w=abs(bottomright[0]-topleft[0])/imgx
                    h=abs(bottomright[1]-topleft[1])/imgy
                    cate=cate_replacement(cate)
                    cate_id=cate_class.index(cate)
    
                    f.write(str(cate_id)+' '+str(center_x)+' '+str(center_y)+' '+str(w)+' '+str(h)+'\n')

def visual_data(dataset_name,data_set='D:/WWF_Det/WWF_Data/Raw_Data/'):
    csv_file='D:/WWF_Det/WWF_Det/Raw_annoations/'+dataset_name+'.csv'
    df=pd.read_csv(csv_file)
    
    txt_path='D:/WWF_Det/WWF_Det/Drop_txt/'+ dataset_name + '/extra.txt'
    position_list=['目标类别物体出现比例-全部出现','目标类别物体出现比例-部分出现','未知类别全部出现','未知类别部分出现']
    position_box_list=[]
    with open(txt_path, 'w') as f:
        for index, row in tqdm(df.iterrows(), desc='Visualizing bounding boxes'):
            timu_data=json.loads(row['题目数据'])
            pic_id=row['题目ID']
            file_path=data_set+timu_data['Path']
            
            visual_folder='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/allset/visualizations/'

            if not os.path.exists(visual_folder): 
                os.makedirs(visual_folder, exist_ok = True)
            file_path=path_replacement(file_path,dataset_name)

            assert os.path.exists(file_path),file_path
            index_pos=0 if dataset_name in ['top14-part2','top14-part1'] else 1
            cate=timu_data['Path'].split('/')[index_pos]
            image_name=str(pic_id)+'.jpg'
            label_dict=json.loads(row['标注答案'])
            if len(label_dict.keys()):
                bboxes=label_dict['objects']
                img = cv2.imread(file_path)
                if img is None:
                    print(file_path)
                    continue
                imgy,imgx=img.shape[:2]
                
                if len(bboxes):
                    for bbox in bboxes:
                        x_list=[bbox['data'][i]['x'] for i in range(0,4)]
                        y_list=[bbox['data'][i]['y'] for i in range(0,4)]
                        topleft=[int(max(min(x_list),0)),int(max(min(y_list),0))]
                        bottomright=[int(min(max(x_list),imgx-1)),int(min(max(y_list),imgy-1))]
                        cv2.rectangle(img, tuple(topleft), tuple(bottomright),(0,255,0), 2, 4)
                        center_x=int((topleft[0]+bottomright[0])/2)
                        center_y=int((topleft[1]+bottomright[1])/2)
                        if len(bbox['tags']):
                            if 'value'in bbox['tags'][0].keys():
                                value=bbox['tags'][0]['value']+[cate]
                                class_name=str(value)

                                img=cv2ImgAddText(img, class_name , int(topleft[0]),center_y,(0,255,255),20)
                                inter=list(set(value)&set(position_list))
                                if len(inter)==0:
                                    print(pic_id,'position missing')
                                    f.write(str(pic_id)+'\n')
                                else:
                                    position_box_list.append(inter[0])
                            else:
                                print(pic_id,'box attribute missing')
                                f.write(str(pic_id)+'\n')

                        else:
                            print(pic_id,'value missing')
                            f.write(str(pic_id)+'\n')

                elif not len(bboxes):
                    print(str(pic_id),'no box')
                    f.write(str(pic_id)+'\n')
                #ONLY plot the image if it is labeled.
                if not os.path.exists(visual_folder+image_name):
                    cv2.imwrite(visual_folder+image_name,img)
    df=pd.DataFrame(dict(Counter(position_box_list)), index=[0])
    df.to_excel('D:/WWF_Det\WWF_Det\Pos_data_stat/position/'+dataset_name+'.xlsx',encoding='utf_8_sig',index=False)


def unknown_check(dataset_name,data_set='D:/WWF_Det/WWF_Data/Raw_Data/'):
    csv_file='D:/WWF_Det/WWF_Det/Raw_annoations/'+dataset_name+'.csv'
    df=pd.read_csv(csv_file)
    
    txt_path='D:/WWF_Det/WWF_Det/Drop_txt/'+ dataset_name + '/extra-unknown.txt'
    position_list=['目标类别物体出现比例-全部出现','目标类别物体出现比例-部分出现','未知类别全部出现','未知类别部分出现']
    
    with open(txt_path, 'w') as f:
        for index, row in tqdm(df.iterrows(), desc='Checking unknown labels'):
            timu_data=json.loads(row['题目数据'])
            pic_id=row['题目ID']
            file_path=data_set+timu_data['Path']
            
            visual_folder='D:/WWF_Det/WWF_Data/Pos_Data/'+dataset_name+'/allset/visualizations/'

            if not os.path.exists(visual_folder): 
                os.makedirs(visual_folder, exist_ok = True)
            file_path=path_replacement(file_path,dataset_name)

            assert os.path.exists(file_path),file_path
            label_dict=json.loads(row['标注答案'])
            if len(label_dict.keys()):
                bboxes=label_dict['objects']
                
                if len(bboxes):
                    for bbox in bboxes:
                        if len(bbox['tags']):
                            if 'value'in bbox['tags'][0].keys():
                                value=bbox['tags'][0]['value']

                                inter=list(set(value)&set(position_list))
                                if len(inter):
                                    if inter[0] in ['未知类别全部出现','未知类别部分出现']:
                                        print(pic_id,'contain unknown object')
                                        f.write(str(pic_id)+'\n')
                           
def combine(dataset_list=['sup9-part1','top14-part1','top14-part2','top14-part3','top14-part4','top14-part5','top14-part6','xuebao-120-all'],extract=False,visual=False,unknown=True):
    for dataset in dataset_list:
        if extract:extract_data(dataset)
        if visual:visual_data(dataset)
        if unknown:unknown_check(dataset)  
if __name__ == "__main__":
    dataset_list=['sup9-part1','top14-part1','top14-part2','top14-part3',\
                'top14-part4','top14-part5','top14-part6','xuebao-120-all','top14-part7','top14-part8']
    combine(dataset_list=['rest-part1','rest-part2'],extract=True,visual=True)
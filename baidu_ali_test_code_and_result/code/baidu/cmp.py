# -*- coding: utf-8 -*-
"""
@File    :   cmp.py
@Version :   1.0
@Author  :   liuan
@Contact :   liuan0803@126.com
@License :   (C)Copyright liuan From UESTC
@Modify Time :   2020/4/2 14:58
@Desciption  :   None
"""

# import cv2
import os
# import numpy as np
import shutil
import json

def main():
    label_dir = 'D:\\liuan58\\ocrdata\\baidu-ali-test\\cmp\\label_org\\good\\good_txt'
    # test_dir = 'D:\\liuan58\\ocrdata\\baidu-ali-test\cmp\\res_baidu_good'
    test_dir = r'D:\liuan58\ocrdata\baidu-ali-test\cmp\res_ali_good'

    label_list = os.listdir(label_dir)
    baidu_list = os.listdir(label_dir)
    total_match = 0

    for label_name in label_list:
        try:
            print(label_name)
            txt_path = os.path.join(label_dir, label_name)
            # f = open(txt_path, "r", encoding="utf-8")
            f = open(txt_path, "r", encoding="gbk")#因为我的txt保存的编码方式是ANSI
            label_lines = f.readlines()
            f.close()

            baidu_label_path = os.path.join(test_dir, label_name)
            f = open(baidu_label_path, "r", encoding="utf-8")
            if f is None:
                print("************************************************************")
                print(txt_path)
                continue
            baidu_lines = f.readlines()
            f.close()
            #match
            if (len(label_lines) != len(baidu_lines)):
                print("************************************************************")
                print(txt_path)
                continue
            plus = 1
            for i, line in enumerate(label_lines):
                mark_label = label_lines[i].replace("-", "").replace("\ufeff","").replace(" ","").replace("\t", "").replace("\n", "")
                baidu_label = baidu_lines[i].replace("-", "").replace(" ", "").replace("\t", "").replace("\n", "")
                # mark_label
                if (mark_label != baidu_label):
                    print(txt_path)
                    print(label_lines[i])
                    print(baidu_lines[i])
                    plus = 0
                    # break
                    # return
                    # continue
            total_match += plus
        except:
            print("except")
    print('total_match:', total_match)
    print('finish.')


if __name__ == '__main__':
    main()
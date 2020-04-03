#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os
import base64
import time
import json
import codecs

# from urlparse import urlparse
# from com.aliyun.api.gateway.sdk import client
# from com.aliyun.api.gateway.sdk.http import request
# from com.aliyun.api.gateway.sdk.common import constant
import traceback
import urllib
import urllib2
import base64


def get_img_base64(img_file):
    with open(img_file, 'rb') as infile:
        s = infile.read()
        return base64.b64encode(s)


def predict(url, appcode, img_base64, kv_config, old_format):
    if not old_format:
        param = {}
        param['image'] = img_base64
        if kv_config is not None:
            param['configure'] = json.dumps(kv_config)
        body = json.dumps(param)
    else:
        param = {}
        pic = {}
        pic['dataType'] = 50
        pic['dataValue'] = img_base64
        param['image'] = pic

        if kv_config is not None:
            conf = {}
            conf['dataType'] = 50
            conf['dataValue'] = json.dumps(kv_config)
            param['configure'] = conf

        inputs = {"inputs": [param]}
        body = json.dumps(inputs)

    headers = {'Authorization': 'APPCODE %s' % appcode}
    request = urllib2.Request(url=url, headers=headers, data=body)
    try:
        response = urllib2.urlopen(request, timeout=10)
        return response.code, response.headers, response.read()
    except urllib2.HTTPError as e:
        return e.code, e.headers, e.read()

def img_rec(img_file):
    appcode = 'c0b3dc88a61b432d88e6fe99f0dc31d3'
    # appcode = '3pzMg8WEiB9Wti2TbRuwC1A3OOzNLp'
    url = 'https://dm-53.data.aliyun.com/rest/160601/ocr/ocr_vehicle.json'
    # 如果输入带有inputs, 设置为True，否则设为False
    is_old_format = False
    config = {'side': 'face'}
    # 如果没有configure字段，config设为None
    # config = None

    img_base64data = get_img_base64(img_file)
    stat, header, content = predict(url, appcode, img_base64data, config, is_old_format)
    if stat != 200:
        print
        'Http status code: ', stat
        print
        'Error msg in header: ', header['x-ca-error-message'] if 'x-ca-error-message' in header else ''
        print
        'Error msg in body: ', content
        exit()
    if is_old_format:
        result_str = json.loads(content)['outputs'][0]['outputValue']['dataValue']
        print(result_str.decode("unicode_escape").encode("utf-8"))
    else:
        result_str = content

    result = json.loads(result_str)
    return result

def write_result(file_path, result_json):
    f = codecs.open(file_path, "w", encoding='utf-8')
    f.write(result_json['plate_num'] + '\n')
    f.write(result_json['vehicle_type'] + '\n')
    f.write(result_json['owner'] + '\n')
    f.write(result_json['addr'] + '\n')
    f.write(result_json['use_character'] + '\n')
    f.write(result_json['model'] + '\n')
    f.write(result_json['vin'] + '\n')
    f.write(result_json['engine_num'] + '\n')
    f.write(result_json['register_date'] + '\n')
    f.write(result_json['issue_date'] + '\n')
    f.close()

def demo():
    # img_dir = r"D:\liuan58\ocrdata\baidu-ali-test\orgdata\testjpg"
    # out_dir = r"D:\liuan58\ocrdata\baidu-ali-test\orgdata\testjpg"
    img_dir = r"D:\liuan58\ocrdata\baidu-ali-test\orgdata\good\good_jpg"
    out_dir = r"D:\liuan58\\ocrdata\\baidu-ali-test\\ouput\\res_ali_good"
    img_list = os.listdir(img_dir)
    for img_name in img_list:
        img_path = os.path.join(img_dir, img_name)
        result_json = img_rec(img_path)
        if (result_json['success'] != True):
            continue
        #write
        out_path = os.path.join(out_dir, os.path.splitext(img_name)[0]+".txt")
        write_result(out_path, result_json)

if __name__ == '__main__':
    demo()
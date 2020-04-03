# coding:utf-8
import urllib, urllib2, base64
import os
import json
# import chardet
# import shutil
import time
import codecs


#调用信息
#18810630205
access_token = '24.4692007c18beb7050a397eb93d24ee95.2592000.1586153908.282335-14517538'
#18810466043
# access_token = '25.1edc2b5782fc1d1692f8cfbc4af572aa.315360000.1901090194.282335-19201134'
url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/vehicle_license?access_token=' + access_token
#获取文件列表
input_dir = r"D:\liuan58\ocrdata\baidu-ali-test\orgdata\good\good_jpg"
output_dir =r"D:\liuan58\ocrdata\baidu-ali-test\ouput\res_baidu_good"
image_list = os.listdir(input_dir)
count = 0

def write_result(result_content, path):
    result_jObj = json.loads(result_content)
    num = result_jObj["words_result_num"]
    if (num != None and num > 0):
        #open file
        fw = codecs.open(txt_path, "w", encoding="utf-8")
        #00
        str = result_jObj["words_result"][u"号牌号码"][u'words']
        print(str)
        fw.write(str+"\n")
        #01
        str = result_jObj["words_result"][u"车辆类型"][u'words']
        print(str)
        fw.write(str + "\n")
        # 02
        str = result_jObj["words_result"][u"所有人"][u'words']
        print(str)
        fw.write(str + "\n")
        # 03
        str = result_jObj["words_result"][u"住址"][u'words']
        print(str)
        fw.write(str + "\n")
        # 04
        str = result_jObj["words_result"][u"使用性质"][u'words']
        print(str)
        fw.write(str + "\n")
        # 05
        str = result_jObj["words_result"][u"品牌型号"][u'words']
        print(str)
        fw.write(str + "\n")
        # 06
        str = result_jObj["words_result"][u"车辆识别代号"][u'words']
        print(str)
        fw.write(str + "\n")
        # 07
        str = result_jObj["words_result"][u"发动机号码"][u'words']
        print(str)
        fw.write(str + "\n")
        # 08
        str = result_jObj["words_result"][u"注册日期"][u'words']
        print(str)
        fw.write(str + "\n")
        # 09
        str = result_jObj["words_result"][u"发证日期"][u'words']
        print(str)
        fw.write(str + "\n")
        #close file
        fw.close()


for image_filename in image_list:
    try:
        # 二进制方式打开图文件
        image_path = os.path.join(input_dir, image_filename)
        # image_path = "D:/del/1.jpg"
        f = open(image_path, 'rb')
        # 参数image：图像base64编码
        img = base64.b64encode(f.read())
        f.close()
        params = {"image": img}
        params = urllib.urlencode(params)
        request = urllib2.Request(url, params)
        request.add_header('Content-Type', 'application/x-www-form-urlencoded')
        response = urllib2.urlopen(request)
        content = response.read()
        txt_path = os.path.join(output_dir,os.path.split(image_path)[1].replace(".jpg", ".txt"))
        print(content)
        result_jObj = json.loads(content)
        num = result_jObj["words_result_num"]
        if (num != None and num>0):
            write_result(content, txt_path)
            time.sleep(1)
        else:
            time.sleep(1)
            continue

    except:
        # break
        continue
print('finish.')
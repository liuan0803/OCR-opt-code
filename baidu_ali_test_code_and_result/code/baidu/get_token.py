# coding:utf-8
import urllib.request, sys
import ssl

# client_id 为官网获取的AK， client_secret 为官网获取的SK
host = 'https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id=H75x4RHImpWxYyVPo3EkT10Q&client_secret=Rt1ykjf3bBxpGOYLrLSWdIMgGFZxTnpM'
request = urllib.request.Request(host)
request.add_header('Content-Type', 'application/json; charset=UTF-8')
response = urllib.request.urlopen(request)
content = response.read()
if (content):
    print(content)

print('mm')
import requests
import pandas as pd
import json,re

df = pd.read_excel('./tools/xzqh2020-03.xlsx')
# 注意要配置服务器端的key，而不是浏览器端的key
f = open('./key.js', 'r', encoding='utf-8')
keys = f.read()
keys = keys.strip()
key = re.findall(r"mapkey = '(.+)'", keys)[0]
f.close()
data = {}
for i in range(len(df)):
    p_code = df.iloc[i, 2]
    if data.get(str(p_code)):
        continue
    url = f'https://api.tianditu.gov.cn/v2/administrative?keyword={p_code}&childLevel=1&tk={key}'
    resp = requests.get(url)
    respdata = resp.json()
    print(p_code,'完成')
    if respdata['status']==200:
        for p in respdata['data']['district']:
            pc = p['gb']
            pname = p['name']
            pcenter = p['center']
            data[str(pc)] = {
                'c': pc,
                'n': pname, 
                't': pcenter,
                'd': []
            }
            for c in p['children']:
                cc = c['gb']
                cname = c['name']
                ccenter = c['center']
                data[pc]['d'].append({'c': cc, 'n': cname, 't': ccenter,'d': []})
    else:
        break

# 将数据转成json格式并保存
with open('./src/TdMapPicker/level.min.json', 'w', encoding='utf-8') as f:
    # 把data展平成tree的list
    newdata = []
    for key in data.keys():
        newdata.append(data[key])
    json.dump(newdata, f, ensure_ascii=False, indent=4)

import json
import requests
import re
import json

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
url = "https://c0.3.cn/stock?skuId=7748324&cat=670,671,2694&venderId=1000000326&area=1_72_4137_0&buyNum=1&choseSuitSkuIds=&extraParam={%22originid%22:%221%22}&ch=1&fqsp=0&pduid=1059759470&pdpin=&callback=jQuery5572362"
h = requests.get(url, headers=header).content.decode('gb2312', 'ignore')
i = re.sub('jQuery\d+', '', h).strip('[()]')
j = re.sub('":\w+,', '":"",', i)
print(json.loads(j)['stock']['weightValue'])

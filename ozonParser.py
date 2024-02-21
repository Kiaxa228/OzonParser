import requests
import json
import logging
from bs4 import BeautifulSoup
import regex

def main():
    with open('catalogOzon.har', 'r', encoding="utf8") as file_in:
        data = json.load(file_in)
    
    categoryLinks = []
    subcategoriesObjs = []

    with open('file_out.json', 'w',  encoding="utf8") as file_out:
        for entry in data["log"]["entries"]:
            try:
                obj = json.loads(entry["response"]["content"]["text"])
        
                if "url" in obj["data"]:
                    categoryLinks.append(obj["data"]["url"])
                    
                    for newObj in obj["data"]["columns"]:
                        for category in newObj["categories"]:
                            objSubcategory = {
                                "title": category["title"],
                                "url": category["url"],
                                "categories": [{"title": subcategory["title"], "url": subcategory["url"] } for subcategory in category["categories"]]
                            }

                            subcategoriesObjs.append(objSubcategory)
            except:
                pass
        
      
        ozonMap = {}

        for subCategory in subcategoriesObjs:

            subcategoryRes = getDataFromCatalog("https://www.ozon.ru" + subCategory['url'])

            with open('res.txt', 'w') as file_out:
                print(subcategoryRes, file=file_out)


def getDataFromCatalog(link: str):
    headers = {'User-Agent': 'PostmanRuntime/7.36.3', 'Cookie': '__Secure-ab-group=98; __Secure-access-token=4.0.B8TPTD6aSpadD0TF_QU1oA.98.AZSL8ggHsODoQGPQsUfXT0Zf9aeOHWAAAalK4daidyulG_wcoXeLuA7dUis8NGO5TA..20240218115556.p5ybnEzvLJHBKovRDV1CD_Ucbx0XsbrFBVVG6m78II8; __Secure-ext_xcid=575c9bac7e067458114c53790f241b07; __Secure-refresh-token=4.0.B8TPTD6aSpadD0TF_QU1oA.98.AZSL8ggHsODoQGPQsUfXT0Zf9aeOHWAAAalK4daidyulG_wcoXeLuA7dUis8NGO5TA..20240218115556.rNRps_M2HTXDNuj0Gjxn_ut_qJl4LqRmZusZW4jwtEE; __Secure-user-id=0; __cf_bm=C_09synrJ1__Ijv7np.3gUvpvCQbaGE7neBgL4Njqgk-1708250156-1.0-AVUbM3KGErqS7YQQiEEShLG/bK8Keqx+Xpu7wGPhIY3JPDGlGlhlFynj9ukKpRQsO30OTksS4tAEcL9pOx8ztcE=; abt_data=2ecc824f50b73ca9eb629fa120e4b2fd:2c45f3931534e69b946be022bd39755e7ec9155796efc6b4c109df4759343315def977760058ffb760ae6a42e6966d525ac63cb3c6c17073b7558d8bbc46810c3ce7eb3b497ce072de7d26f4504b76637c1259bdf974699f864991b80493b80677774bc0e4d9c66eedb38edd39b31ba65b7d9dcdc8c119e56141db4068228d6b9697e74021ea2d38777fb7530e18c9bbb48561e51d7189e40319e9596ca128bf841405bd52677d8770fef97f994528938b251a73f63521c5f2341a59c069f72356f8cf6efd023f028f99fd5f213e82bedee9d4f4346bcb2318dd5c7b09c1fbe45db45d69d34d93aff52b6376cac9a345592e8af6d2639a7088354ecd372a26fe; xcid=65964043c2a5a17bf0030c88671feb40'}
    res = []
    page = 2

    while not ('Простите, произошла ошибка' in (response := requests.get(link + f'?page={page}', headers=headers)).text or response.status_code != 200):
        res.extend(parseResponseForPrices(response))

        page += 1

        print(link + f'?page={page}')


def parseResponseForPrices(response):
    if response.status_code != 200:
        logging.warning('Не получилось список товаров в категории')
        return []
    else:
        soup = BeautifulSoup(response.text, 'lxml')
                
        data_state = soup.find(id=regex.compile(r'state-searchResultsV2-*')).get('data-state')  

        res = []

        for item in data_state['items']:
            if len(item['rightState'][0]['atom']['priceV2']['price']) == 2:
                res.append({
                    'title': item['mainState'][0]['atom']['textAtom']['text'],
                    'url': item['action']['link'],
                    'price': item['rightState'][0]['atom']['priceV2']['price'][0]['text'],
                    'oldPrice': item['rightState'][0]['atom']['priceV2']['price'][1]['text']
                })
            else:
                 res.append({
                    'title': item['mainState'][0]['atom']['textAtom']['text'],
                    'url': item['action']['link'],
                    'price': item['rightState'][0]['atom']['priceV2']['price'][0]['text']
                })
                 
        return res


if __name__ == '__main__':
    main()
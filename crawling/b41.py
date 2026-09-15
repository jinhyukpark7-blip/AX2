# from bs4 import BeautifulSoup
# # pip install beautifulsoup4
# import requests
# import pandas as pd


# requests.get("https://www.google.com")

# html = response.text

# soup = BeautifulSoup(html, "html.parser")

# logo = soup.select_one("naW5gc mL3MVc DYz2A").text
# subtitle = soup.select_one(".acUsEb.Qi40Vc.CoM3Df").text

# print(logo,subtitle)



import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import openpyxl

data = []

for i in range(1,5):
    # 1. 요청 결과를 response 변수에 저장
    response = requests.get("https://startcoding.pythonanywhere.com/basic/page={i}")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

# # 2. 클래스 선택자(.) 적용
# logo_elem = soup.select_one(".naW5gc.mL3MVc.DYz2A")
# subtitle_elem = soup.select_one(".acUsEb.Qi40Vc.CoM3Df")

# # 3. 요소 존재 여부 확인 후 텍스트 추출
# logo = logo_elem.text.strip() if logo_elem else "로고 요소를 찾을 수 없음"
# subtitle = (
#     subtitle_elem.text.strip() if subtitle_elem else "서브타이틀을 찾을 수 없음"
# )

# print(logo, subtitle)

items = soup.select(".product")
# print(f"가져온 상품 개수 : {len(items)}개 \n" + "-"*30) # 상품 개수 확인

for item in items:
    category = item.select_one(".product-category").text # 카테고리
    category_name = item.select_one(".product-name").text # 상품명
    category_link = item.select_one(".product-name > a")["href"] # 상품 상세 페이지 링크
    price = item.select_one(".product-price").text.spllit("원").replace(",","") # 가격
    data.append([category, category_name, category_link, price])
    print(category, category_name, category_link, price)

df = pd.DataFrame(data,columns=["카테고리","상품명","상세페이지링크","가격"])
df.to_excel("data.xlsx", index=False)

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
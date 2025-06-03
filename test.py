import requests
from bs4 import BeautifulSoup

url = "https://jeondong.sen.ms.kr/19970/subMenu.do"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, verify=False)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')

    a_tags = soup.find_all('a', attrs={"title": "클릭하면 내용을 보실 수 있습니다."})

    seen_tds = set()  # 중복 방지를 위한 집합

    if not a_tags:
        print("해당 속성을 가진 a 태그를 찾지 못했습니다.")
    else:
        for a_tag in a_tags:
            td_parent = a_tag.find_parent('td')
            if td_parent:
                # td 태그의 고유 문자열 표현(예: 내용)을 기준으로 중복 검사
                td_text = td_parent.get_text(strip=True)
                if td_text not in seen_tds:
                    print("----- td 태그 내용 -----")
                    print(td_text)
                    print('-' * 40)
                    seen_tds.add(td_text)

except requests.exceptions.RequestException as e:
    print("요청 중 오류 발생:", e)
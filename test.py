from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Chrome 드라이버 실행
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://jeondong.sen.ms.kr/19967/subMenu.do")

# 공지 span 로딩 대기
WebDriverWait(driver, 10).until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "span.flag_notice"))
)

results = []

# 공지 span을 기준으로 tr 추적
notices = driver.find_elements(By.CSS_SELECTOR, "span.flag_notice")
for notice in notices:
    # 해당 span이 속한 tr 찾기
    tr = notice.find_element(By.XPATH, "./ancestor::tr")
    subject_td = tr.find_element(By.CSS_SELECTOR, "td.subject")
    title = subject_td.text.strip()
    results.append(title)

driver.quit()

# 출력
print("📌 공지사항 제목 (공지글만):")
for i, title in enumerate(results, 1):
    print(f"{i}. {title}")

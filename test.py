from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_school_schedule():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get("https://jeondong.sen.ms.kr/19970/subMenu.do")
        time.sleep(2)

        schedule_table = driver.find_element(By.CLASS_NAME, "tbl_calendar")
        tds = schedule_table.find_elements(By.TAG_NAME, "td")

        schedule = []

        for td in tds:
            day = td.find_element(By.CLASS_NAME, "day").text.strip() if len(td.find_elements(By.CLASS_NAME, "day")) > 0 else None
            info = td.text.replace(day, "").strip() if day else td.text.strip()
            if day and info:
                schedule.append(f"[{day}일] {info}")

        driver.quit()

        if not schedule:
            return "🤖 학사일정 정보를 찾을 수 없어요."
        return "✅ 학사일정 크롤링 성공!\n" + "\n".join(schedule)

    except Exception as e:
        return f"❌ 오류 발생: {e}"

# 실행
print(get_school_schedule())

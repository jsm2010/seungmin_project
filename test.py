import re

def format_schedule(text):
    # 1) '기말고사' + 공백 + 숫자 + 줄바꿈 + 숫자가 있으면 모두 한 줄로 붙이기
    # 예: '기말고사\n3' 또는 '기말고사 3\n' 등 다 처리
    text = re.sub(r'(기말고사)\s*\n*\s*(\d+)', r'\1 \2', text)
    
    # 2) '기말고사 숫자일' 인 경우 숫자 뒤 '일' 제거
    text = re.sub(r'(기말고사\s*\d+)일', r'\1', text)

    # 3) 숫자+일 바로 뒤에 한글 붙으면 줄바꿈 (날짜 구분용)
    text = re.sub(r'(\d{1,2}일)(?=[가-힣])', r'\1\n', text)

    # 4) 날짜(숫자+일) 기준으로 분리해서 한 줄씩 정리
    parts = re.split(r'(\d{1,2}일)', text)
    result_lines = []
    for i in range(1, len(parts), 2):
        day = parts[i]
        desc = parts[i+1].strip() if i+1 < len(parts) else ''
        result_lines.append(f"{day}{desc}")

    return '\n'.join(result_lines)


sample_text = """6일현충일
9일성매매예방교육.성폭력예방교육.도박예방교육
25일(1)교과 3(2,3) 기말고사
3
26일(1)교과 3(2,3) 기말고사
3
27일(1)교과 3(2,3) 기말고사
3"""

print(format_schedule(sample_text))

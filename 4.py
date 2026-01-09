import schedule
import time
import pyautogui
from datetime import datetime

def send_ddo():
    """새벽 4시에 '또!'를 입력하고 엔터를 누르는 함수"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 또! 전송 중...")
    pyautogui.write("또!", interval=0.1)
    pyautogui.press('enter')
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 또! 전송 완료!")

# 매일 새벽 4시 정각에 실행
schedule.every().day.at("04:00").do(send_ddo)

print("새벽 4시 '또!' 알람이 시작되었습니다...")
print("종료하려면 Ctrl+C를 누르세요.")

# 무한 루프로 스케줄 실행
while True:
    schedule.run_pending()
    time.sleep(1)

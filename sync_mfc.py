import os
import requests

# 1. กำหนดค่าตัวแปร
MFC_VALUE = 0.0  # จะใส่โค้ด Web Scraping / API ดึงยอดเงิน MFC จริงที่นี่

# ตัวอย่าง: ดึงข้อมูลยอดเงินกองทุน MFC จาก API หรือ Scraping
# mfc_response = requests.get('MFC_API_ENDPOINT')
# MFC_VALUE = mfc_response.json()['total_value']

# 2. ยิงอัปเดตมูลค่าลง Firebase (mfc-port)
FIREBASE_URL = "https://mfc-port-default-rtdb.asia-southeast1.firebasedatabase.app/mfc_summary/current.json"

payload = {
    "value": MFC_VALUE
}

response = requests.put(FIREBASE_URL, json=payload)

if response.status_code == 200:
    print(f"Successfully updated MFC Total: ฿{MFC_VALUE}")
else:
    print(f"Failed to update Firebase: {response.status_code}, {response.text}")

import requests
from datetime import datetime, timedelta

FIREBASE_BASE_URL = "https://scb-e-class-default-rtdb.asia-southeast1.firebasedatabase.app"
FIREBASE_SECRET = "4H6vJBEPXMflq0kKYbxOy2DtNtmP7HAxo9v3mkjj"  # ⚠️ นำ Secret Key จาก Firebase มาใส่ตรงนี้
SUPABASE_URL = "https://iproktvvetsbxxmpptuj.supabase.co" # ⚠️ ใส่ URL Supabase จริงของคุณ
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlwcm9rdHZ2ZXRzYnh4bXBwdHVqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODcyOTU3NDEsImV4cCI6MjEwMjg3MTc0MX0.Kc0USo30u4gvZNJ1bsOdD9k6nwEBcY7lNMAQxWEFzqw"                          # ⚠️ ใส่ Anon Key Supabase จริงของคุณ

def create_daily_snapshot():
    try:
        # 1. กำหนดวันที่เป็น "เมื่อวาน" (เพราะรันตอน 06:00 น. เพื่อเก็บราคาปิด US/กองทุนไทย)
        target_date = datetime.now() - timedelta(days=1)
        snapshot_key = target_date.strftime('%Y%m%d') # เช่น '20260902'
        date_str = target_date.strftime('%Y-%m-%d')    # เช่น '2026-09-02'

        # 2. ดึงยอด MFC จาก Supabase
        mfc_res = requests.get(
            f"{SUPABASE_URL}/rest/v1/policies?portfolio_type=eq.mfc_fund",
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        ).json()
        
        mfc_total = sum(float(item.get('units', 0)) * float(item.get('navToday', item.get('nav', 0))) for item in mfc_res)

        # 3. ดึงยอด GPF จาก Firebase
        gpf_res = requests.get(f"{FIREBASE_BASE_URL}/gpf_ports/my-gpf-4750131.json").json()
        gpf_total = sum(float(f.get('units', 0)) * float(f.get('currentNav', 0)) for f in gpf_res.get('funds', []))

        # 4. ดึงยอด SCB จาก Firebase
        scb_res = requests.get(f"{FIREBASE_BASE_URL}/scb_summary/current.json").json()
        scb_total = float(scb_res.get('value', 0)) if scb_res else 0

        # 5. ดึงยอด DIME จาก Firebase (หน่วย USD) และแปลงเป็นเงินบาท (THB)
        dime_res = requests.get(f"{FIREBASE_BASE_URL}/dime_summary/current.json").json()
        dime_usd = float(dime_res.get('value', 0)) if dime_res else 0
        
        # ดึงอัตราแลกเปลี่ยนสด (USD -> THB)
        fx_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        if fx_res.status_code == 200:
            usd_to_thb = fx_res.json().get('rates', {}).get('THB', 34.0)
        else:
            usd_to_thb = 34.0 # ค่าสำรองฉุกเฉินกรณี API ล่ม
            
        dime_total = dime_usd * usd_to_thb

        # 6. คำนวณยอดรวมทั้งหมด
        total_wealth = mfc_total + gpf_total + scb_total + dime_total

        payload = {
            "date": date_str,
            "wealth": round(total_wealth, 2),
            "mfc": round(mfc_total, 2),
            "gpf": round(gpf_total, 2),
            "scb": round(scb_total, 2),
            "dime": round(dime_total, 2),
            "createdAt": datetime.now().isoformat()
        }

        # 7. ส่งบันทึกเข้า Firebase โดยแนบ Auth Secret เพื่อข้าม Security Rules
        save_url = f"{FIREBASE_BASE_URL}/wealth_history/{snapshot_key}.json?auth={FIREBASE_SECRET}"
        save_res = requests.put(save_url, json=payload)
        
        if save_res.status_code in [200, 201]:
            print(f"✅ บันทึก Snapshot ของวันที่ {date_str} สำเร็จ: ยอดรวม ฿{total_wealth:,.2f}")
        else:
            print(f"⚠️ บันทึกไม่สำเร็จ HTTP {save_res.status_code}: {save_res.text}")

    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดในการสร้าง Snapshot: {e}")

if __name__ == "__main__":
    create_daily_snapshot()

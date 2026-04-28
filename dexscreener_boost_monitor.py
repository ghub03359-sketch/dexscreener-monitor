import requests,time,os,schedule
from datetime import datetime
TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN","")
CHAT=os.environ.get("TELEGRAM_CHAT_ID","")
INTERVAL=int(os.environ.get("CHECK_INTERVAL","30"))
URL="https://api.dexscreener.com/token-boosts/latest/v1"
seen=set()
def tg(msg):
 requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":msg,"parse_mode":"HTML"},timeout=10)
def fmt(n):
 try:
  n=float(n)
  return f"{n/1e6:.2f}M" if n>=1e6 else f"{n/1e3:.1f}K" if n>=1e3 else f"{n:.4f}"
 except:return str(n)
def check():
 try:data=requests.get(URL,timeout=15).json()
 except:return
 if not isinstance(data,list):return
 for t in data:
  k=f"{t.get('chainId')}:{t.get('tokenAddress')}"
  if k in seen:continue
  seen.add(k)
  msg=(f"🚀 <b>BOOST BARU!</b>\n"
   f"🔗 Chain: <b>{t.get('chainId','').upper()}</b>\n"
   f"📛 Token: <b>{t.get('description','N/A')}</b>\n"
   f"💰 Boost: <b>{fmt(t.get('amount',0))}</b>\n"
   f"📊 Total: <b>{fmt(t.get('totalAmount',0))}</b>\n"
   f"📍 <code>{t.get('tokenAddress','')}</code>\n"
   f"🔍 <a href='{t.get('url','')}'>DexScreener</a>\n"
   f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
  tg(msg)
tg("✅ <b>Bot aktif!</b> Memantau boost baru setiap 30 detik 🚀")
check()
schedule.every(INTERVAL).seconds.do(check)
while True:
 schedule.run_pending()
 time.sleep(1)

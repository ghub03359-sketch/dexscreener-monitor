import requests,time,os,schedule
from datetime import datetime
TOKEN=os.environ.get("TELEGRAM_BOT_TOKEN","")
CHAT=os.environ.get("TELEGRAM_CHAT_ID","")
INTERVAL=int(os.environ.get("CHECK_INTERVAL","60"))
TOP_URL="https://api.dexscreener.com/token-boosts/top/v1"
seen=set()
def tg(msg):
 try:requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",json={"chat_id":CHAT,"text":msg,"parse_mode":"HTML"},timeout=10)
 except:pass
def fmt(n):
 try:
  n=float(n)
  return f"{n/1e6:.2f}M" if n>=1e6 else f"{n/1e3:.1f}K" if n>=1e3 else f"{n:.0f}"
 except:return str(n)
def check():
 try:data=requests.get(TOP_URL,timeout=15).json()
 except:return
 if not isinstance(data,list):return
 top10=data[:10]
 for i,t in enumerate(top10,1):
  k=f"{t.get('chainId')}:{t.get('tokenAddress')}"
  if k in seen:continue
  seen.add(k)
  links=""
  for l in t.get("links",[]):
   href=l.get("url","")
   label=l.get("label") or l.get("type","link")
   if href:links+=f"  • <a href='{href}'>{label}</a>\n"
  msg=(f"🔥 <b>TOP {i} TRENDING BOOST!</b>\n"
   f"━━━━━━━━━━━━━━━━━━\n"
   f"🔗 Chain: <b>{t.get('chainId','').upper()}</b>\n"
   f"📛 Token: <b>{t.get('description','N/A')}</b>\n"
   f"💰 Boost Aktif: <b>{fmt(t.get('amount',0))}</b>\n"
   f"📊 Total Boost: <b>{fmt(t.get('totalAmount',0))}</b>\n"
   f"📍 <code>{t.get('tokenAddress','')}</code>\n")
  if links:msg+=f"\n🌐 Links:\n{links}"
  if t.get('url'):msg+=f"\n🔍 <a href='{t.get('url')}'>Lihat di DexScreener</a>\n"
  msg+=f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
  print(f"TOP {i}: {t.get('description')} ({t.get('chainId')})")
  tg(msg)
tg("✅ <b>Bot aktif!</b>\nMemantau <b>TOP 10 Trending Boost</b> 🔥\nNotif dikirim hanya saat token baru masuk TOP 10!")
check()
schedule.every(INTERVAL).seconds.do(check)
while True:
 schedule.run_pending()
 time.sleep(1)

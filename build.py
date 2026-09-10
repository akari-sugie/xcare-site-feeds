#!/usr/bin/env python3
"""GAS のフィードを取りに行き、Studio が読む静的 JSON に分ける。
seminars.json / seminars_upcoming.json / seminars_past.json / seminars_past_9.json
youtube.json（ロングのみ全件）/ youtube_6.json / youtube_9.json
"""
import json, urllib.request, datetime
SEM = "https://script.google.com/macros/s/AKfycby1Ir-W8kBjZmjRfGtzjAfIvhoUA4KA1XNTiiCCGyDm0_Madwp5hdSF1zkRYDM00vMCkw/exec?flat=1&limit=200"
YT = "https://script.google.com/macros/s/AKfycbxPh4PRojjnj56XeQFn0Mv2F_0xjMNs38Rvt2TO0Kr7EbBOwMTaHhEVacK2gHUXqJn74Q/exec?flat=1&limit=100"


def get(url):
    """3回まで試す。GAS は一時的に 404/500 を返すことがある。ダメなら None（既存ファイルを残す）"""
    import time
    for i in range(3):
        try:
            with urllib.request.urlopen(url, timeout=240) as r:
                body = r.read().decode()
            if body.lstrip().startswith("["):
                return json.loads(body)
            print("not json:", body[:80])
        except Exception as e:
            print("fetch error:", e)
        time.sleep(15)
    return None


def clean(o):
    """途中で切れた絵文字（片割れのサロゲート）を落とす"""
    if isinstance(o, str):
        return o.encode("utf-8", "ignore").decode("utf-8")
    if isinstance(o, list):
        return [clean(v) for v in o]
    if isinstance(o, dict):
        return {k: clean(v) for k, v in o.items()}
    return o


def dump(name, data):
    with open(name, "w", encoding="utf-8") as f:
        json.dump(clean(data), f, ensure_ascii=False, indent=0)


sem = get(SEM)
if sem is None:
    print("seminars: fetch failed, keep existing files")
else:
  today = (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
  up = [s for s in sem if s.get("date") and s["date"] >= today]
  past = [s for s in sem if not s.get("date") or s["date"] < today]
  dump("seminars.json", sem)
  dump("seminars_upcoming.json", up)
  dump("seminars_past.json", past)
  dump("seminars_past_9.json", past[:9])
  print(f"seminars {len(sem)} (upcoming {len(up)})")

yt = get(YT)
if yt is None:
    print("youtube: fetch failed, keep existing files")
else:
    dump("youtube.json", yt)
    dump("youtube_6.json", yt[:6])
    dump("youtube_9.json", yt[:9])
    print(f"youtube {len(yt)}")

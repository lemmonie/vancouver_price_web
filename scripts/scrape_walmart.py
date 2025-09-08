# using Flipp API to catch Walmart flyers (last 30 days only)
# save to data/walmart_sample.csv (columns: item,price,store,date,source_image)

import requests, csv, datetime, urllib.parse, os

OUT = "data/walmart_sample.csv"
TODAY = datetime.date.today().isoformat()
POSTAL = "V5A1S6"             # will change it to customer input
MERCHANT = "Walmart"          # can change to Walmart Canada
WINDOW_DAYS = 30              # the nearest 30 days

base = "https://backflipp.wishabi.com/flipp/items/search"
params = {
    "locale": "en-ca",
    "postal_code": POSTAL,
    "q": MERCHANT,
    "page": 1
}

def in_last_30_days(valid_from, valid_to):
    def to_date(s):
        if not s:
            return None
        try:
            # getting the first 10 digits
            return datetime.date.fromisoformat(str(s)[:10])
        except Exception:
            return None

    start = datetime.date.today() - datetime.timedelta(days=WINDOW_DAYS)
    end = datetime.date.today()

    df = to_date(valid_from)
    dt = to_date(valid_to)
    if df and dt:
        return not (dt < start or df > end)
    if df and not dt:
        return df <= end
    if dt and not df:
        return dt >= start
    return False  # if there are no dates will not collect

rows = []
while True:
    url = base + "?" + urllib.parse.urlencode(params)
    r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()


    if "application/json" not in (r.headers.get("content-type") or "").lower():
        print(f"⚠️ Non-JSON response on page {params['page']}，stop.")
        break

    data = r.json()
    items = data.get("items", [])
    if not items:
        break

    for it in items:
        # keeping the nearest 30 days
        if not in_last_30_days(it.get("valid_from"), it.get("valid_to")):
            continue

        title = it.get("name") or it.get("title") or ""
        price = it.get("current_price") or it.get("price_text") or it.get("price") or ""
        img = it.get("image_url") or it.get("clipping_image_url") or ""
        if title and price:
            rows.append({
                "item": title.strip(),
                "price": str(price).strip(),
                "store": "Walmart",
                "date": TODAY,
                "source_image": img
            })

    if not data.get("next_page"):
        break
    params["page"] += 1

write_header = not os.path.exists(OUT) or os.path.getsize(OUT) == 0
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["item","price","store","date","source_image"])
    if write_header:
        w.writeheader()
    w.writerows(rows)

print(f"✅ kept {len(rows)} Walmart items within last {WINDOW_DAYS} days，saved to {OUT}")

# using Flipp API to catch Real Canadian Superstore 的 flyer information
# save to all_ocr.csv（row: item,price,store,date,source_image）

import requests, csv, datetime, urllib.parse, os

OUT = "data/superstore_sample.csv"
TODAY = datetime.date.today().isoformat()
POSTAL = "V5A1S6"                     # address will change after the customer can type their post code
MERCHANT = "Real Canadian Superstore" # change to walmart safe on

base = "https://backflipp.wishabi.com/flipp/items/search"
params = {
    "locale": "en-ca",
    "postal_code": POSTAL,
    "q": MERCHANT,
    "page": 1
}

rows = []
while True:
    url = base + "?" + urllib.parse.urlencode(params)
    r = requests.get(url, timeout=20, headers={
        "User-Agent": "Mozilla/5.0"
    })
    r.raise_for_status()
    data = r.json()
    items = data.get("items", [])
    if not items:
        break

    for it in items:
        title = it.get("name") or it.get("title") or ""
        price = it.get("current_price") or it.get("price_text") or it.get("price") or ""
        img = it.get("image_url") or it.get("clipping_image_url") or ""
        if title and price:
            rows.append({
                "item": title.strip(),
                "price": str(price).strip(),
                "store": "Superstore",
                "date": TODAY,
                "source_image": img
            })

    if not data.get("next_page"):
        break
    params["page"] += 1

# writting into superstore_sample.csv
write_header = not os.path.exists(OUT) or os.path.getsize(OUT) == 0
with open(OUT, "a", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["item","price","store","date","source_image"])
    if write_header:
        w.writeheader()
    w.writerows(rows)

print(f"✅ already gotten {len(rows)} information，saved to {OUT}")

"""Daily job collector: Delhi NCR, permanent posts, B.Tech/graduate eligible.
Reads public listing pages, keeps the old data if a source fails."""
import json, re, time, datetime as dt
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

SOURCES = [
    ("Delhi", "https://www.freejobalert.com/delhi-government-jobs/", False),
    ("Haryana", "https://www.freejobalert.com/haryana-government-jobs/", True),
    ("Uttar Pradesh", "https://www.freejobalert.com/up-government-jobs/", True),
]
NCR = re.compile(r"gurugram|gurgaon|faridabad|noida|ghaziabad|sonipat|sonepat|bahadurgarh|jhajjar|rewari|palwal|\bncr\b|delhi", re.I)
EXCLUDE = re.compile(r"project|contract|apprentice|walk-?in|guest|consultant|fellow|ad-?hoc|temporary|outsourc|deputation|part[- ]?time|honorarium|intern\b|research associate", re.I)
BTECH = re.compile(r"b\.?\s?tech|\bb\.?e\b|engineering", re.I)
GRAD = re.compile(r"any (graduate|bachelor)", re.I)
HDR = {"User-Agent": "GovtJobHub/1.0 (personal job tracker)"}

def parse_date(s):
    m = re.search(r"(\d{2})[-/](\d{2})[-/](\d{4})", s or "")
    return f"{m[3]}-{m[2]}-{m[1]}" if m else None

def parse_table(html, base):
    rows = []
    for tr in BeautifulSoup(html, "html.parser").find_all("tr"):
        td = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(td) < 6:
            continue
        a = tr.find_all("td")[-1].find("a", href=True)
        last = parse_date(td[5])
        if not last or not a:
            continue
        rows.append({"posted": parse_date(td[0]), "org": td[1], "post": td[2], "qual": td[3],
                     "advt": "" if td[4] in ("–", "-") else td[4], "last": last, "url": urljoin(base, a["href"])})
    return rows

def keep(r, filter_ncr):
    text = f"{r['org']} {r['post']}"
    if EXCLUDE.search(text):
        return None
    if filter_ncr and not NCR.search(text):
        return None
    q = r["qual"]
    tag = "btech" if BTECH.search(q) else "graduate" if GRAD.search(q) else "unknown" if not q.strip() else None
    return tag

def details(url):
    try:
        t = BeautifulSoup(requests.get(url, headers=HDR, timeout=30).text, "html.parser").get_text("\n")
    except Exception:
        return "", ""
    f = lambda p: (re.search(p, t, re.I) or [""])[0].replace("\n", " ")[:170].strip()
    return f(r"(age limit|maximum age|upper age)[^\n]{0,150}"), f(r"(pay scale|pay level|pay matrix|salary)[^\n]{0,120}")

def main():
    try:
        old = json.load(open("data/jobs.json"))
    except Exception:
        old = {"jobs": []}
    try:
        over = json.load(open("data/overrides.json"))
    except Exception:
        over = {}
    today = dt.date.today().isoformat()
    jobs, status = [], {}
    for name, url, ncr in SOURCES:
        try:
            r = requests.get(url, headers=HDR, timeout=30)
            r.raise_for_status()
            rows = parse_table(r.text, url)
            if not rows:
                raise ValueError("no table rows found")
            for row in rows:
                tag = keep(row, ncr)
                if tag and row["last"] >= today:
                    jobs.append({**row, "tag": tag, "loc": name, "source": url})
            status[name] = f"ok ({len(rows)} listed)"
        except Exception as e:
            status[name] = f"failed: {e}"
            jobs += [j for j in old["jobs"] if j.get("loc") == name and j["last"] >= today]
        time.sleep(2)
    cache = {j["url"]: j for j in old["jobs"]}
    fetched = 0
    for j in jobs:
        c = cache.get(j["url"], {})
        if "age" in c:
            j["age"], j["pay"] = c["age"], c.get("pay", "")
        elif fetched < 25:
            j["age"], j["pay"] = details(j["url"]); fetched += 1; time.sleep(1.5)
        else:
            j["age"], j["pay"] = "", ""
        j.update(over.get(j["url"], {}))
    jobs = [j for j in jobs if not j.get("hide")]
    jobs.sort(key=lambda j: j["last"])
    if all(s.startswith("failed") for s in status.values()):
        old["status"] = status
        json.dump(old, open("data/jobs.json", "w"), indent=1)
        print("All sources failed; kept old data", status)
        return
    ist = dt.datetime.now(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    json.dump({"updated": ist.strftime("%d %b %Y, %I:%M %p IST"), "stamp": ist.isoformat(), "status": status, "jobs": jobs},
              open("data/jobs.json", "w"), indent=1, ensure_ascii=False)
    print(len(jobs), "jobs", status)

if __name__ == "__main__":
    main()

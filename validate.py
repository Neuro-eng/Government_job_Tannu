import json, re, sys, datetime
d = json.load(open("data/jobs.json"))
bad = 0
for i, j in enumerate(d["jobs"]):
    for k in ["org", "post", "last", "qual", "type", "url"]:
        if not j.get(k): print(f"job {i}: missing {k}"); bad += 1
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", j.get("last", "")): print(f"job {i}: bad date"); bad += 1
    if not j.get("url", "").startswith("https://"): print(f"job {i}: url must be https"); bad += 1
today = datetime.date.today().isoformat()
print(f"{len(d['jobs'])} jobs, {sum(j['last'] < today for j in d['jobs'])} expired (page hides them)")
sys.exit(1 if bad else 0)

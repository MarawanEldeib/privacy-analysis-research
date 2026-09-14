import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print("=== SUMMARY ===")
print(json.dumps(d.get("summary"), indent=2, ensure_ascii=False))
print("\n=== counts ===")
print("requests:", len(d.get("requests", [])), " ws_messages:", len(d.get("ws_messages", [])),
      " tls_failures:", len(d.get("tls_failures", [])), " read_failures:", len(d.get("read_failures", [])))

# Look at one request entry shape
reqs = d.get("requests", [])
if reqs:
    print("\n=== sample request keys ===", list(reqs[0].keys()))

# Aggregate: for each host, max coverage / secrets, across requests + ws
def host_of(e):
    return e.get("host") or e.get("pretty_host") or e.get("server") or "?"
agg = {}
for e in reqs + d.get("ws_messages", []):
    h = host_of(e)
    a = agg.setdefault(h, {"cov":0.0,"secrets":set(),"canary":False,"events":0})
    a["events"] += 1
    for ck in ("coverage_pct","doc_coverage_pct","exposure_pct","coverage"):
        if ck in e and isinstance(e[ck],(int,float)):
            a["cov"] = max(a["cov"], e[ck])
    sec = e.get("secrets_found") or e.get("secrets") or e.get("matched_secrets") or []
    if isinstance(sec, dict): sec = list(sec.keys())
    for s in sec: a["secrets"].add(s)
    blob = json.dumps(e, ensure_ascii=False).lower()
    if "canary-bc267061" in blob or "bc267061" in blob: a["canary"]=True

print("\n=== HOSTS with any secret/canary/coverage (sorted) ===")
rows = [(h,a) for h,a in agg.items() if a["cov"]>0 or a["secrets"] or a["canary"]]
for h,a in sorted(rows, key=lambda x:-len(x[1]["secrets"])):
    print(f"  {h}: cov~{a['cov']}  secrets={len(a['secrets'])}  canary={a['canary']}  events={a['events']}")

print("\n=== ALL hosts captured (count) ===")
hc = {}
for e in reqs + d.get("ws_messages", []):
    h = host_of(e); hc[h] = hc.get(h,0)+1
for h,c in sorted(hc.items(), key=lambda x:-x[1]):
    print(f"  {c:4d}  {h}")

print("\n=== target hosts present? ===")
allblob = None
for needle in ("grammarly.com","grammarly.io","augloop","officeapps","office.com","office.net"):
    hosts = sorted({host_of(e) for e in reqs + d.get('ws_messages',[]) if needle in host_of(e)})
    print(f"  {needle}: {hosts}")

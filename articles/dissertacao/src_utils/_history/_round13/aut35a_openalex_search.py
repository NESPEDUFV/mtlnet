import os, sys, json, urllib.parse, urllib.request

KEY = os.environ["OPENALEX_API_KEY"]
q = sys.argv[1]
frm = sys.argv[2] if len(sys.argv) > 2 else "2024-01-01"

params = {
    "search": q,
    "filter": "from_publication_date:" + frm,
    "per-page": "25",
    "sort": "relevance_score:desc",
    "select": "id,doi,title,publication_year,type,primary_location,best_oa_location",
    "api_key": KEY,
}
url = "https://api.openalex.org/works?" + urllib.parse.urlencode(params)
with urllib.request.urlopen(url, timeout=60) as r:
    d = json.load(r)
print("count=" + str(d["meta"]["count"]))
for w in d["results"]:
    pl = w.get("primary_location") or {}
    src = (pl.get("source") or {}).get("display_name")
    print("- " + str(w.get("publication_year")) + " | " + str(w.get("doi")) + " | " + str(src))
    print("    " + str(w.get("title"))[:150])

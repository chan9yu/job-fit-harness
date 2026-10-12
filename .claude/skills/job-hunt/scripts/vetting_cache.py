"""회사 검증 캐시.

select: 03_candidates.json에서 이번에 검증할 회사를 고른다. 캐시에 있고 30일이 안 지난 회사는 캐시 값을 쓴다.
merge:  이번 실행의 04_vetting_*.json을 캐시에 합친다.

사용:
  python3 vetting_cache.py select --workspace _discover --cache _cache/vetting.json [--limit 120] [--today YYYY-MM-DD]
  python3 vetting_cache.py merge --workspace _discover --cache _cache/vetting.json
"""

import argparse
import datetime
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prefilter import norm  # noqa: E402

TTL_DAYS = 30


def load_cache(path):
	return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def fresh(entry, today):
	try:
		checked = datetime.date.fromisoformat(entry.get("checked_at", ""))
	except ValueError:
		return False
	return (datetime.date.fromisoformat(today) - checked).days < TTL_DAYS


def select(workspace, cache_path, limit, today):
	cache = load_cache(cache_path)
	candidates = json.load(open(os.path.join(workspace, "03_candidates.json"), encoding="utf-8"))["companies"]
	cached, to_vet, skipped = [], [], []
	for c in candidates:
		hit = cache.get(norm(c["company"]))
		if hit and fresh(hit, today):
			cached.append(hit)
		elif len(to_vet) < limit:
			ids = {k: next((p[k] for p in c["postings"] if p.get(k)), None) for k in ("company_id", "business_number")}
			to_vet.append(dict({"company": c["company"], "score": c["score"], "postings": [{"title": p.get("title"), "url": p.get("url"), "source": p.get("source"), "company_id": p.get("company_id")} for p in c["postings"]]}, **ids))
		else:
			skipped.append(c["company"])
	json.dump({"batch": "cache", "checked_at": today, "companies": cached}, open(os.path.join(workspace, "04_vetting_cache.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	json.dump({"to_vet": to_vet, "skipped": skipped}, open(os.path.join(workspace, "03_to_vet.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	return cached, to_vet, skipped


def merge(workspace, cache_path):
	cache = load_cache(cache_path)
	added = 0
	for path in sorted(glob.glob(os.path.join(workspace, "04_vetting_*.json"))):
		if path.endswith("04_vetting_cache.json"):
			continue
		data = json.load(open(path, encoding="utf-8"))
		for entry in data.get("companies", []):
			entry.setdefault("checked_at", data.get("checked_at"))
			# 별칭으로도 찾게 한다. 다음 실행에서 다른 플랫폼 표기(영문명 등)로 들어와도 같은 회사로 캐시를 쓴다
			for name in [entry["company"]] + (entry.get("aliases") or []):
				cache[norm(name)] = entry
			added += 1
	os.makedirs(os.path.dirname(cache_path) or ".", exist_ok=True)
	json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	return added, len(cache)


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("command", choices=["select", "merge"])
	ap.add_argument("--workspace", default="_discover")
	ap.add_argument("--cache", default="_cache/vetting.json")
	ap.add_argument("--limit", type=int, default=120)
	ap.add_argument("--today", default=datetime.date.today().isoformat())
	a = ap.parse_args()
	if a.command == "select":
		cached, to_vet, skipped = select(a.workspace, a.cache, a.limit, a.today)
		print("캐시 사용 %d곳, 이번에 검증 %d곳, 상한 밖 %d곳" % (len(cached), len(to_vet), len(skipped)))
	else:
		added, total = merge(a.workspace, a.cache)
		print("캐시에 %d곳 반영, 캐시 전체 %d곳" % (added, total))

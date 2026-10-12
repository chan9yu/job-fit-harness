"""발굴 판정 입력 만들기.

03_candidates.json과 04_vetting_*.json을 회사 기준으로 합쳐 05_review_input.json을 쓴다.
등급이 X나 unknown인 회사와 검증 결과가 없는 회사는 미리 빼고, 여러 플랫폼에 올라온 같은 공고는 하나로 합친다.
회사마다 단계(성장 스타트업, 초기 스타트업, 상장사와 중견, 중소)를 붙이고 고르지 않은 단계의 회사는 뺀다.
discovery-reviewer는 이 파일만 읽고 공고 판정과 리포트 작성에 집중한다.

사용: python3 prepare_review.py --workspace _discover --segments growth,early,established
"""

import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prefilter import norm  # noqa: E402

# 링크를 고를 때의 출처 순서. fit-report 1절과 같다
SOURCE_ORDER = ["career", "wanted", "remember", "jobplanet", "saramin", "zighang", "jumpit", "jobkorea", "catch", "rallit", "linkedin"]
DATE = re.compile(r"\d{4}-\d{2}-\d{2}$")
STOPWORDS = {"경력", "경력직", "채용", "모집", "신입", "및", "의", "직"}
FIELDS = ["experience_raw", "min_years", "max_years", "deadline", "location", "employment", "skills", "evidence", "original_url"]
# 단계 키와 이름표. 순서가 리포트의 정렬 순서다
SEGMENTS = {"growth": "성장 스타트업", "early": "초기 스타트업", "established": "상장사와 중견, 중소"}


def title_key(title):
	"""단어 집합으로 비교한다. 괄호와 구두점, 단어 순서가 달라도 같은 공고로 본다."""
	return frozenset(w for w in re.findall(r"[0-9a-z가-힣+#]+", (title or "").lower()) if w not in STOPWORDS)


def source_rank(p):
	s = p.get("source")
	return SOURCE_ORDER.index(s) if s in SOURCE_ORDER else len(SOURCE_ORDER)


def merge_postings(postings):
	groups = {}
	for p in sorted(postings, key=source_rank):
		key = title_key(p.get("title"))
		if key not in groups:
			groups[key] = dict(p, also=[])
			continue
		main = groups[key]
		main["also"].append({"source": p.get("source"), "url": p.get("url")})
		resolve_conflicts(main, p)
		for f in FIELDS:
			if main.get(f) in (None, "", [], "미기재") and p.get(f) not in (None, "", [], "미기재"):
				main[f] = p[f]
	return list(groups.values())


def resolve_conflicts(main, other):
	"""출처끼리 값이 다르면 지원자에게 안전한 쪽을 쓰고 차이를 conflicts에 남긴다.
	마감은 상시보다 구체적인 날짜를, 날짜가 여럿이면 가장 이른 날짜를 쓴다. 최소 연차는 큰 값을 쓴다.
	마감을 놓치거나 한 출처가 잘못 읽은 낮은 연차로 추천에 오르지 않게 하려는 것이다."""
	notes = main.setdefault("conflicts", [])
	d1, d2 = main.get("deadline"), other.get("deadline")
	if d1 != d2 and DATE.match(d2 or "") and (not DATE.match(d1 or "") or d2 < d1):
		notes.append({"field": "deadline", "kept": d2, "dropped": d1, "from": other.get("source")})
		main["deadline"] = d2
	m1, m2 = main.get("min_years"), other.get("min_years")
	if m1 is not None and m2 is not None and m2 > m1:
		notes.append({"field": "min_years", "kept": m2, "dropped": m1, "from": other.get("source")})
		main["min_years"] = m2
		main["experience_raw"] = other.get("experience_raw") or main.get("experience_raw")
	if not notes:
		main.pop("conflicts")


def segment(v):
	"""회사 검증 결과로 단계를 정한다. 위에서부터 처음 맞는 값을 준다."""
	funding = v.get("funding") or {}
	if v.get("listed") is True:
		return "established"
	# 라운드 이름 없이 "한 번에 100억 원 이상" 기사만 있어도 성장 단계로 본다. company-vetting A 등급의 자금 근거와 같은 기준이다
	big_round = (funding.get("total_krw") or 0) >= 10_000_000_000 or (funding.get("last_amount_krw") or 0) >= 10_000_000_000
	if funding.get("stage") in ("시리즈B", "시리즈C", "시리즈D 이상") or big_round:
		return "growth"
	if funding.get("stage") in ("시드", "프리A", "시리즈A"):
		return "early"
	return "established"


def load_vetting(workspace):
	index = {}
	for path in sorted(glob.glob(os.path.join(workspace, "04_vetting_*.json"))):
		data = json.load(open(path, encoding="utf-8"))
		for e in data.get("companies", []):
			e.setdefault("checked_at", data.get("checked_at"))
			for name in [e["company"]] + (e.get("aliases") or []):
				key = norm(name)
				if key not in index or (e.get("checked_at") or "") > (index[key].get("checked_at") or ""):
					index[key] = e
	return index


def run(workspace, segments=tuple(SEGMENTS)):
	candidates = json.load(open(os.path.join(workspace, "03_candidates.json"), encoding="utf-8"))
	vetting = load_vetting(workspace)
	# 같은 검증 결과에 걸리는 후보는 한 회사다. 플랫폼마다 표기가 달라(넥스트증권(주), Next Securities) 후보가 여럿으로 들어온다
	groups, not_vetted = {}, []
	for c in candidates["companies"]:
		v = vetting.get(norm(c["company"]))
		if not v:
			not_vetted.append(c["company"])
			continue
		g = groups.setdefault(norm(v["company"]), {"v": v, "names": [], "postings": []})
		g["names"].append(c["company"])
		g["postings"].extend(c["postings"])
	review, dropped, by_segment = [], [], []
	for g in groups.values():
		v, name = g["v"], g["v"]["company"]
		if v.get("grade") not in ("A", "B", "C"):
			flags = v.get("red_flags") or []
			reason = flags[0].get("type") if flags else "근거 부족"
			dropped.append({"company": name, "names": g["names"], "grade": v.get("grade"), "summary": v.get("summary"), "reason": reason, "postings": [{"title": p.get("title"), "url": p.get("url")} for p in g["postings"]]})
			continue
		seg = segment(v)
		if seg not in segments:
			by_segment.append({"company": name, "segment": seg, "segment_label": SEGMENTS[seg]})
			continue
		postings = merge_postings(g["postings"])
		review.append({"company": name, "names": g["names"], "grade": v["grade"], "segment": seg, "segment_label": SEGMENTS[seg], "summary": v.get("summary"), "red_flags": v.get("red_flags") or [], "postings": postings})
	review.sort(key=lambda r: (list(SEGMENTS).index(r["segment"]), "ABC".index(r["grade"]), -len(r["postings"]), r["company"]))
	result = {
		"profile_years": candidates.get("profile_years"),
		"segment_labels": [label for key, label in SEGMENTS.items() if key in segments],
		"stats": {"vetted": len(groups), "review_companies": len(review), "review_postings": sum(len(r["postings"]) for r in review), "dropped_by_grade": len(dropped), "dropped_by_segment": len(by_segment), "not_vetted": len(not_vetted)},
		"review": review,
		"dropped_by_grade": dropped,
		"dropped_by_segment": by_segment,
		"not_vetted": not_vetted,
	}
	json.dump(result, open(os.path.join(workspace, "05_review_input.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	return result


def parse_segments(text):
	keys = [k.strip() for k in text.split(",") if k.strip()]
	if not keys or any(k not in SEGMENTS for k in keys):
		raise argparse.ArgumentTypeError("%s 중에서 쉼표로 골라야 한다: %s" % (",".join(SEGMENTS), text))
	return keys


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("--workspace", default="_discover")
	ap.add_argument("--segments", type=parse_segments, default=list(SEGMENTS))
	args = ap.parse_args()
	st = run(args.workspace, args.segments)["stats"]
	print("판정 대상 %d곳 공고 %d건, 등급으로 제외 %d곳, 단계로 제외 %d곳, 검증 안 함 %d곳" % (st["review_companies"], st["review_postings"], st["dropped_by_grade"], st["dropped_by_segment"], st["not_vetted"]))

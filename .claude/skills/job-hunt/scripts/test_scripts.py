"""prefilter.py, vetting_cache.py, prepare_review.py 자체 확인. 실행: python3 -I .claude/skills/job-hunt/scripts/test_scripts.py"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prefilter  # noqa: E402
import vetting_cache  # noqa: E402
import prepare_review  # noqa: E402

REGISTRY = """# 대상 기업

## 네카라쿠배당토직야

| 기업 | 티어 | 채용 페이지 | ATS | 접근 | 비고 |
| --- | --- | --- | --- | --- | --- |
| 카카오 | A+ | https://careers.kakao.com/jobs | 자체 | api | |
| KT | B | https://recruit.kt.com/careers | 자체 | api | |

## 제외한 기업

| 기업 | 이유 | 확인일 |
| --- | --- | --- |
| 발란 | 파산 | 2026-10-07 |
"""

PROFILE = {
	"years": 5,
	"role": "프론트엔드",
	"role_en": "Frontend Engineer",
	"adjacent_roles": ["웹 플랫폼"],
	"keywords_ko": ["프론트엔드", "웹 프론트엔드"],
	"keywords_en": ["Frontend Engineer", "Front-end"],
}


def posting(company, title, **kw):
	base = {"company": company, "title": title, "url": "https://x/" + company + title, "employment": "정규직", "min_years": None, "max_years": None, "deadline": "상시"}
	base.update(kw)
	return base


def main():
	d = tempfile.mkdtemp()
	json.dump(PROFILE, open(os.path.join(d, "01_profile.json"), "w"), ensure_ascii=False)
	reg = os.path.join(d, "companies.md")
	open(reg, "w", encoding="utf-8").write(REGISTRY)
	postings = [
		posting("(주)좋은회사", "프론트엔드 개발자", min_years=3),  # 남는다
		posting("좋은회사", "Software Engineer"),  # 직무 애매, 남는다
		posting("카카오", "Frontend Engineer"),  # 레지스트리
		posting("KT cloud", "프론트엔드 개발"),  # 레지스트리 계열(KT로 시작)
		posting("KTB네트워크", "프론트엔드 개발자", business_number="1234567890"),  # KT와 다른 회사, 남는다
		posting("발란", "프론트엔드 개발자"),  # 제외 기업
		posting("헤드헌팅 비공개", "프론트엔드 개발자"),  # 헤드헌팅
		posting("계약회사", "프론트엔드 개발자", employment="계약직"),
		posting("시니어회사", "프론트엔드 리드", min_years=10),  # 요건 초과
		posting("백엔드회사", "백엔드 개발자"),  # 직무 불일치
		posting("마감회사", "프론트엔드 개발자", deadline="2026-01-01"),
		posting("(주)좋은회사", "프론트엔드 개발자", min_years=3),  # 같은 URL, 중복
	]
	json.dump({"postings": postings}, open(os.path.join(d, "02_postings_d-test.json"), "w"), ensure_ascii=False)

	res, dropped = prefilter.run(d, reg, "2026-10-12")
	kept = {c["company"]: [p["title"] for p in c["postings"]] for c in res["companies"]}
	reasons = {x["company"]: x["reason"] for x in dropped}

	assert kept == {"(주)좋은회사": ["프론트엔드 개발자", "Software Engineer"], "KTB네트워크": ["프론트엔드 개발자"]}, kept
	assert reasons["카카오"].startswith("레지스트리"), reasons
	assert reasons["KT cloud"].startswith("레지스트리"), reasons
	assert reasons["발란"] == "제외한 기업", reasons
	assert reasons["헤드헌팅 비공개"].startswith("헤드헌팅"), reasons
	assert reasons["계약회사"] == "고용형태 계약직", reasons
	assert reasons["시니어회사"] == "요건 10년 이상", reasons
	assert reasons["백엔드회사"].startswith("직무 불일치"), reasons
	assert reasons["마감회사"] == "마감 지남", reasons
	assert len(dropped) == 8, dropped
	good = res["companies"][0]
	assert good["company"] == "(주)좋은회사" and good["score"] == 3, good
	assert [p["match"] for p in good["postings"]] == ["exact", "generic"], good

	# 동등역량: 기본은 연차 규칙대로 빼고, --allow-equivalent면 경력 원문에 그 문구가 있는 공고만 남긴다
	d4 = tempfile.mkdtemp()
	json.dump(PROFILE, open(os.path.join(d4, "01_profile.json"), "w"), ensure_ascii=False)
	json.dump({"postings": [
		posting("동등회사", "프론트엔드 개발자", min_years=10, experience_raw="10년 이상 또는 이에 준하는 역량"),
		posting("엄격회사", "프론트엔드 개발자", min_years=10, experience_raw="10년 이상"),
	]}, open(os.path.join(d4, "02_postings_d-test.json"), "w"), ensure_ascii=False)
	res, dropped = prefilter.run(d4, reg, "2026-10-12")
	assert res["companies"] == [] and len(dropped) == 2, dropped
	res, dropped = prefilter.run(d4, reg, "2026-10-12", allow_equivalent=True)
	assert [c["company"] for c in res["companies"]] == ["동등회사"] and [x["company"] for x in dropped] == ["엄격회사"], (res, dropped)

	# 캐시: 좋은회사는 10일 전 검증이라 재사용, KTB네트워크는 40일 전이라 다시 검증
	cache = os.path.join(d, "cache", "vetting.json")
	os.makedirs(os.path.dirname(cache))
	json.dump({"좋은회사": {"company": "좋은회사", "grade": "A", "checked_at": "2026-10-02"}, "ktb네트워크": {"company": "KTB네트워크", "grade": "B", "checked_at": "2026-09-02"}}, open(cache, "w"), ensure_ascii=False)
	cached, to_vet, skipped = vetting_cache.select(d, cache, 1, "2026-10-12")
	assert [c["company"] for c in cached] == ["좋은회사"], cached
	assert [c["company"] for c in to_vet] == ["KTB네트워크"] and skipped == [], (to_vet, skipped)
	assert to_vet[0]["business_number"] == "1234567890" and to_vet[0]["company_id"] is None, to_vet
	json.dump({"batch": "vet-1", "checked_at": "2026-10-12", "companies": [{"company": "KTB네트워크", "grade": "C"}]}, open(os.path.join(d, "04_vetting_vet-1.json"), "w"), ensure_ascii=False)
	added, total = vetting_cache.merge(d, cache)
	merged = json.load(open(cache, encoding="utf-8"))
	assert added == 1 and total == 2 and merged["ktb네트워크"]["grade"] == "C" and merged["ktb네트워크"]["checked_at"] == "2026-10-12", merged

	# 판정 입력: 같은 공고 두 건은 하나로 합치고, X 등급과 검증 안 한 회사는 뺀다
	d2 = tempfile.mkdtemp()
	json.dump({"profile_years": 5, "companies": [
		{"company": "(주)좋은회사", "postings": [
			{"title": "프론트엔드 엔지니어 (5년 이상/부산)", "url": "https://saramin/1", "source": "saramin", "deadline": "2026-10-24", "min_years": None},
			{"title": "프론트엔드 엔지니어 (부산, 5년 이상)", "url": "https://wanted/1", "source": "wanted", "deadline": "상시", "min_years": 5},
			{"title": "Software Engineer", "url": "https://wanted/2", "source": "wanted"}]},
		{"company": "나쁜회사", "postings": [{"title": "프론트엔드", "url": "https://x/9", "source": "wanted"}]},
		{"company": "모르는회사", "postings": [{"title": "프론트엔드", "url": "https://x/8", "source": "wanted"}]}]}, open(os.path.join(d2, "03_candidates.json"), "w"), ensure_ascii=False)
	json.dump({"batch": "vet-1", "checked_at": "2026-10-12", "companies": [
		{"company": "좋은회사", "grade": "A", "summary": "시리즈B"},
		{"company": "나쁜회사", "grade": "X", "summary": "체불", "red_flags": [{"type": "임금 체불"}]}]}, open(os.path.join(d2, "04_vetting_vet-1.json"), "w"), ensure_ascii=False)
	r = prepare_review.run(d2)
	assert r["not_vetted"] == ["모르는회사"], r
	assert [x["company"] for x in r["dropped_by_grade"]] == ["나쁜회사"] and r["dropped_by_grade"][0]["reason"] == "임금 체불", r
	good = r["review"][0]
	assert good["grade"] == "A" and len(good["postings"]) == 2, good
	merged = good["postings"][0]
	# 링크는 앞선 출처(원티드)를 쓰고, 마감은 상시보다 구체적인 날짜(사람인)를 쓴다. 차이는 conflicts에 남는다
	assert merged["source"] == "wanted" and merged["deadline"] == "2026-10-24" and merged["min_years"] == 5, merged
	assert merged["conflicts"] == [{"field": "deadline", "kept": "2026-10-24", "dropped": "상시", "from": "saramin"}], merged
	assert merged["also"] == [{"source": "saramin", "url": "https://saramin/1"}], merged

	# 단계: 상장이 먼저, 시리즈B 이상이나 누적 100억 원 이상은 성장, 시드에서 시리즈A는 초기, 나머지는 상장사와 중견, 중소
	seg = prepare_review.segment
	assert good["segment"] == "established" and good["segment_label"] == "상장사와 중견, 중소", good
	assert seg({"listed": True, "funding": {"stage": "시리즈C"}}) == "established"
	assert seg({"listed": False, "funding": {"stage": "시리즈B"}}) == "growth"
	assert seg({"funding": {"stage": "라운드 미상", "total_krw": 10_000_000_000}}) == "growth"
	assert seg({"funding": {"stage": "시리즈A", "total_krw": 9_999_999_999}}) == "early"
	assert seg({"funding": {"stage": "시드"}}) == "early" and seg({"funding": {"stage": "프리A"}}) == "early"
	assert [seg({"listed": None, "funding": {"stage": s}}) for s in (None, "라운드 미상", "M&A")] == ["established"] * 3
	assert seg({"funding": None}) == "established"
	# 라운드 이름이 없어도 한 번에 100억 원 이상이면 성장(넥스트증권 150억 사례)
	assert seg({"funding": {"stage": "라운드 미상", "last_amount_krw": 15_000_000_000}}) == "growth"
	assert seg({"funding": {"stage": "라운드 미상", "last_amount_krw": 9_000_000_000}}) == "established"

	# 단계 거르기: 고르지 않은 단계는 review에서 빼고 dropped_by_segment에 남긴다. 정렬은 단계가 등급보다 먼저다
	d3 = tempfile.mkdtemp()
	json.dump({"profile_years": 5, "companies": [{"company": n, "postings": [{"title": "개발자", "url": "https://x/" + n, "source": "wanted"}]} for n in ("상장회사", "초기회사", "성장회사")]}, open(os.path.join(d3, "03_candidates.json"), "w"), ensure_ascii=False)
	json.dump({"batch": "vet-1", "checked_at": "2026-10-12", "companies": [
		{"company": "상장회사", "grade": "A", "listed": True, "funding": {"stage": None, "total_krw": None, "last_date": None}},
		{"company": "초기회사", "grade": "B", "listed": False, "funding": {"stage": "시드", "total_krw": None, "last_date": "2025-01"}},
		{"company": "성장회사", "grade": "C", "listed": False, "funding": {"stage": "시리즈C", "total_krw": None, "last_date": "2024-12"}}]}, open(os.path.join(d3, "04_vetting_vet-1.json"), "w"), ensure_ascii=False)
	r = prepare_review.run(d3)
	assert [(x["company"], x["segment"]) for x in r["review"]] == [("성장회사", "growth"), ("초기회사", "early"), ("상장회사", "established")], r["review"]
	assert r["dropped_by_segment"] == [] and r["stats"]["dropped_by_segment"] == 0, r
	r = prepare_review.run(d3, ["growth"])
	assert [(x["company"], x["segment_label"]) for x in r["review"]] == [("성장회사", "성장 스타트업")], r["review"]
	assert r["dropped_by_segment"] == [{"company": "상장회사", "segment": "established", "segment_label": "상장사와 중견, 중소"}, {"company": "초기회사", "segment": "early", "segment_label": "초기 스타트업"}], r
	assert r["segment_labels"] == ["성장 스타트업"] and r["stats"]["dropped_by_segment"] == 2 and r["stats"]["vetted"] == 3, r
	check_role_families()

	# 날짜가 여럿이면 가장 이른 마감을 쓴다(아이벡스: 잡코리아 10-24, 리멤버 11-03)
	m = prepare_review.merge_postings([
		{"title": "FE", "url": "https://w/9", "source": "wanted", "deadline": "상시"},
		{"title": "FE", "url": "https://r/9", "source": "remember", "deadline": "2026-11-03"},
		{"title": "FE", "url": "https://j/9", "source": "jobkorea", "deadline": "2026-10-24"},
	])[0]
	assert m["deadline"] == "2026-10-24" and [c["kept"] for c in m["conflicts"]] == ["2026-11-03", "2026-10-24"], m
	# 출처끼리 최소 연차가 다르면 큰 값을 쓴다(한 출처가 잘못 읽은 낮은 연차로 추천에 오르지 않게)
	m = prepare_review.merge_postings([
		{"title": "Frontend Engineer", "url": "https://w/1", "source": "wanted", "min_years": 5, "experience_raw": "5년 이상"},
		{"title": "Frontend Engineer", "url": "https://r/1", "source": "remember", "min_years": 2, "experience_raw": "2~7년"},
	])[0]
	assert m["min_years"] == 5 and "conflicts" not in m, m
	m = prepare_review.merge_postings([
		{"title": "Frontend Engineer", "url": "https://w/1", "source": "wanted", "min_years": 2, "experience_raw": "2년 이상"},
		{"title": "Frontend Engineer", "url": "https://r/1", "source": "remember", "min_years": 5, "experience_raw": "5년 이상"},
	])[0]
	assert m["min_years"] == 5 and m["experience_raw"] == "5년 이상" and m["conflicts"][0]["field"] == "min_years", m

	# 같은 검증 결과에 걸리는 후보(넥스트증권(주), Next Securities)는 한 회사로 묶고 공고를 합친다
	d3 = tempfile.mkdtemp()
	json.dump({"profile_years": 5, "companies": [
		{"company": "넥스트증권(주)", "postings": [{"title": "Frontend Engineer (채널)", "url": "https://w/n1", "source": "wanted"}]},
		{"company": "Next Securities", "postings": [{"title": "Frontend Engineer, Client Platform", "url": "https://l/n2", "source": "linkedin"}]}]}, open(os.path.join(d3, "03_candidates.json"), "w"), ensure_ascii=False)
	json.dump({"batch": "vet-1", "checked_at": "2026-10-12", "companies": [
		{"company": "넥스트증권", "aliases": ["Next Securities", "넥스트증권(주)"], "grade": "A", "summary": "150억 투자", "funding": {"stage": "라운드 미상", "last_amount_krw": 15_000_000_000}}]}, open(os.path.join(d3, "04_vetting_vet-1.json"), "w"), ensure_ascii=False)
	r = prepare_review.run(d3)
	assert r["stats"]["vetted"] == 1 and len(r["review"]) == 1, r["stats"]
	one = r["review"][0]
	assert one["company"] == "넥스트증권" and one["names"] == ["넥스트증권(주)", "Next Securities"] and len(one["postings"]) == 2 and one["segment"] == "growth", one

	# 캐시는 별칭으로도 찾는다
	cache3 = os.path.join(d3, "cache.json")
	vetting_cache.merge(d3, cache3)
	c3 = json.load(open(cache3, encoding="utf-8"))
	assert c3["nextsecurities"]["company"] == "넥스트증권" and c3["넥스트증권"]["grade"] == "A", sorted(c3)
	print("ok")


def check_role_families():
	"""개발 밖 프로필로 그 직무 공고는 남고 개발 공고는 빠지는지, 짧은 영문 직무명이 다른 단어 안에서 걸리지 않는지 본다."""
	d = tempfile.mkdtemp()
	designer = {"years": 4, "role": "프로덕트 디자이너", "role_en": "Product Designer", "role_family": "product_designer", "adjacent_families": [], "adjacent_roles": [], "keywords_ko": ["프로덕트 디자이너"], "keywords_en": ["Product Designer"]}
	json.dump(designer, open(os.path.join(d, "01_profile.json"), "w"), ensure_ascii=False)
	reg = os.path.join(d, "companies.md")
	open(reg, "w", encoding="utf-8").write(REGISTRY)
	postings = [
		posting("디자인회사", "프로덕트 디자이너"),
		posting("디자인회사", "UI\u00b7UX디자이너 (경력)"),  # 잡코리아처럼 가운뎃점으로 이은 표기
		posting("디자인회사", "디자이너 (경력)"),  # 직무 애매, 남는다
		posting("개발회사", "프론트엔드 개발자"),
		posting("개발회사", "Software Engineer"),  # 디자인 쪽 애매한 말도 없어서 뺀다
		posting("기획회사", "서비스 기획 PM"),
		posting("마케팅회사", "퍼포먼스 마케터"),
	]
	json.dump({"postings": postings}, open(os.path.join(d, "02_postings_d-test.json"), "w"), ensure_ascii=False)
	res, dropped = prefilter.run(d, reg, "2026-10-12")
	kept = {(p["title"], p["match"]) for c in res["companies"] for p in c["postings"]}
	assert kept == {("프로덕트 디자이너", "exact"), ("UI\u00b7UX디자이너 (경력)", "exact"), ("디자이너 (경력)", "generic")}, kept
	reasons = {x["title"]: x["reason"] for x in dropped}
	assert reasons == {"프론트엔드 개발자": "직무 불일치(frontend)", "Software Engineer": "직무 판단 불가", "서비스 기획 PM": "직무 불일치(product_manager)", "퍼포먼스 마케터": "직무 불일치(marketing)"}, reasons

	# role_family가 없는 예전 프로필은 직무 이름과 검색어에서 찾는다. po, cs, md, hr, pm이 단어 안에 있어도 걸리지 않는다
	fe = prefilter.profile_families(PROFILE)
	assert fe == {"frontend"}, fe
	for title in ["Responsive 웹 개발자", "CSS 엔지니어", "CMD 툴 개발자", "Chrome 확장 개발자", "npm 패키지 개발자"]:
		assert prefilter.title_verdict(title, PROFILE, fe) == (None, "generic"), title

	pm = {"role": "서비스 기획", "role_family": "product_manager", "adjacent_families": ["marketing"], "keywords_ko": ["서비스 기획"], "keywords_en": ["Product Manager"]}
	pf = prefilter.profile_families(pm)
	assert pf == {"product_manager", "marketing"}, pf
	assert prefilter.title_verdict("PM (커머스)", pm, pf) == (None, "exact")
	assert prefilter.title_verdict("퍼포먼스 마케터", pm, pf) == (None, "exact")  # 인접 직무군
	assert prefilter.title_verdict("npm 라이브러리 개발자", pm, pf) == ("직무 판단 불가", None)
	assert prefilter.title_verdict("운영 매니저", pm, pf) == ("직무 불일치(operations)", None)

	hr = {"role": "인사", "role_family": "hr", "adjacent_families": []}
	assert prefilter.title_verdict("인사 담당자", hr, {"hr"}) == (None, "exact")
	assert prefilter.title_verdict("인사이트 리서치 매니저", hr, {"hr"}) == (None, "generic")  # '인사이트'는 인사가 아니다


if __name__ == "__main__":
	main()

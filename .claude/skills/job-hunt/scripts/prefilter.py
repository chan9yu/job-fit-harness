"""발굴 모드 1차 거르기.

_discover/02_postings_*.json을 읽어 회사 검증에 넘길 후보만 남긴다.
레지스트리 기업, 제외 기업, 헤드헌팅, 계약직, 연차 범위 밖, 직무가 분명히 다른 공고를 뺀다.
애매한 공고는 남긴다. 최종 판정은 discovery-reviewer가 한다.

사용: python3 prefilter.py --workspace _discover --registry data/companies.md [--today YYYY-MM-DD] [--allow-contract]
"""

import argparse
import datetime
import glob
import json
import os
import re

# 공통 계약의 직무군 키마다 공고 제목에서 찾을 말. 소문자로 적는다. 말 안의 공백은 제목에 있어도 없어도 맞고,
# 말 앞뒤에 라틴 문자가 붙으면 다른 단어로 본다('pm'은 'npm'에, 'cs'는 'css'에 걸리지 않는다).
# 한글은 뒤에 붙는 글자를 막지 않는다. 다른 낱말의 앞부분이 되는 말은 넣지 않거나 text_key에서 미리 바꾼다('인사이트').
# '디자'는 디자인과 디자이너를 함께 잡으려고 줄여 적었다.
# 같은 말이 여러 직무군에 들어가도 된다(앱 개발은 안드로이드, iOS, 크로스플랫폼에 모두 있다).
ROLE_FAMILIES = {
	"frontend": ["프론트엔드", "프런트엔드", "frontend", "front-end", "front end", "웹 프론트", "fe 개발"],
	"backend": ["백엔드", "backend", "back-end", "서버 개발", "서버 프로그래머", "server"],
	"fullstack": ["풀스택", "full-stack", "full stack"],
	"android": ["안드로이드", "android", "앱 개발", "모바일 앱", "mobile app"],
	"ios": ["ios", "앱 개발", "모바일 앱", "mobile app"],
	"crossplatform": ["flutter", "플러터", "react native", "리액트 네이티브", "크로스플랫폼", "cross-platform", "앱 개발", "모바일 앱", "mobile app"],
	"data_engineer": ["데이터 엔지니어", "data engineer", "데이터 플랫폼", "data platform"],
	"ml": ["머신러닝", "machine learning", "ml engineer", "mlops", "딥러닝", "ai research", "ai 연구", "ai 엔지니어", "ai engineer", "llm"],
	"devops": ["devops", "sre", "인프라", "infra", "클라우드 엔지니어", "cloud engineer", "시스템 엔지니어", "dba"],
	"qa": ["qa", "quality assurance", "테스트 엔지니어", "sdet", "테스터"],
	"security": ["보안", "security", "cybersecurity", "infosec", "정보보호", "모의해킹"],
	"game_dev": ["게임 클라이언트", "게임 서버", "게임 개발", "게임 프로그래머", "클라이언트 개발", "클라이언트 엔지니어", "클라이언트 프로그래머", "서버 프로그래머", "엔진 프로그래머", "게임플레이", "gameplay", "game client", "game server", "game developer", "game engineer", "client engineer", "client programmer", "유니티", "unity", "언리얼", "unreal", "ue4", "ue5"],
	"product_manager": ["서비스 기획", "웹 기획", "앱 기획", "프로덕트 매니저", "product manager", "프로덕트 오너", "product owner", "pm", "po"],
	"product_designer": ["프로덕트 디자", "product designer", "ux 디자", "ux designer", "ux 리서", "ux research", "ux 라이터", "ux writer", "ui 디자", "ui designer", "gui 디자", "ui ux", "ux ui", "ui/ux", "ux/ui", "웹 디자", "web designer", "앱 디자", "모바일 디자", "서비스 디자"],
	"visual_designer": ["그래픽 디자", "graphic designer", "브랜드 디자", "브랜딩 디자", "brand designer", "bx", "bi/bx", "시각 디자", "visual designer", "비주얼 디자", "편집 디자", "광고 디자", "영상 디자", "모션 디자", "motion designer", "콘텐츠 디자", "패키지 디자", "상세페이지 디자", "크리에이티브 디자", "일러스트"],
	"data_analyst": ["데이터 분석", "data analyst", "data analytics", "데이터 사이언티스트", "데이터 사이언스", "data scientist", "data science", "bi 분석", "business analyst"],
	"marketing": ["마케팅", "마케터", "marketing", "marketer", "그로스 해커", "growth hacker", "광고 기획", "브랜드 매니저", "brand manager", "홍보", "pr"],
	"business_development": ["사업 개발", "business development", "bd", "bizdev", "사업 기획", "영업", "sales", "세일즈", "제휴", "partnership", "파트너십", "account executive", "account manager", "어카운트 매니저"],
	"operations": ["cs", "cx", "고객 지원", "고객 경험", "고객 상담", "고객센터", "상담원", "상담사", "customer success", "customer support", "customer experience", "운영 매니저", "운영 담당", "operations", "오퍼레이션", "커뮤니티 매니저"],
	"hr": ["인사", "hr", "hrd", "hrbp", "hrm", "채용 담당", "채용 매니저", "리크루터", "recruiter", "recruiting", "talent acquisition", "조직 문화", "피플", "people", "노무"],
	"finance": ["재무", "회계", "세무", "경리", "자금 담당", "자금팀", "자금 관리", "결산", "ir", "accounting", "accountant", "fp&a", "finance manager", "financial analyst", "tax", "treasury"],
	"legal": ["법무", "legal", "변호사", "변리사", "lawyer", "attorney", "counsel", "컴플라이언스", "compliance", "준법", "내부통제", "특허"],
	"merchandiser": ["md", "vmd", "머천다이저", "merchandiser", "merchandising", "상품 기획", "상품 개발", "바잉", "바이어", "buyer"],
}
# 제목만으로 직무가 애매한 말. 프로필 직무군이 개발, 디자인, 그 밖 중 어디에 속하느냐에 따라 고른다.
GENERIC = {
	"dev": ["개발자", "개발", "엔지니어", "engineer", "developer", "software", "sw", "프로그래머"],
	"design": ["디자이너", "디자인", "designer"],
	"business": ["매니저", "담당자", "manager"],
}
DESIGN_FAMILIES = {"product_designer", "visual_designer"}
BUSINESS_FAMILIES = {"product_manager", "data_analyst", "marketing", "business_development", "operations", "hr", "finance", "legal", "merchandiser"}
BLIND = re.compile(r"헤드헌|서치펌|써치펌|비공개|국내 ?대기업|외국계 ?기업|유망 ?스타트업|중견 ?기업|코스닥 ?상장사")
NON_REGULAR = {"계약직", "인턴", "파견", "아르바이트", "프리랜서"}


def clean(name):
	"""법인 표기를 지우고 공백을 하나로 줄인 소문자 이름. 이름 비교에 쓴다."""
	name = re.sub(r"\(주\)|㈜|주식회사|\(유\)|유한회사", "", name or "")
	return re.sub(r"\s+", " ", name).strip().lower()


def norm(name):
	"""공백까지 지운 이름. 같은 회사 공고를 묶는 키로 쓴다."""
	return clean(name).replace(" ", "")


def parse_registry(path):
	"""레지스트리 표의 기업명을 수집 대상과 제외 기업으로 나눠 돌려준다."""
	registry, excluded, section = set(), set(), None
	for line in open(path, encoding="utf-8"):
		if line.startswith("## "):
			section = line[3:].strip()
			continue
		if not line.startswith("| ") or line.startswith("| ---") or line.startswith("| 기업") or line.startswith("| 열"):
			continue
		name = line.strip().strip("|").split("|")[0].strip()
		if not name or section is None:
			continue
		(excluded if section == "제외한 기업" else registry).add(clean(name))
	return registry, excluded


def matches_name(company, names):
	"""회사명이 목록의 이름과 같거나 그 이름으로 시작하면 참. 'KT cloud'와 'SK텔레콤'은 걸리고 'KTB네트워크'는 걸리지 않도록, 이름 바로 뒤에 라틴 문자나 숫자가 붙으면 다른 회사로 본다."""
	c = clean(company)
	for n in names:
		if c == n or c.replace(" ", "") == n.replace(" ", ""):
			return True
		if c.startswith(n) and not re.match(r"[a-z0-9]", c[len(n):]):
			return True
	return False


def text_key(text):
	"""소문자로 바꾸고 가운뎃점이나 괄호 같은 기호를 공백으로 바꾼다. 잡코리아처럼 UI와 UX를 가운뎃점으로 이은 제목도 'ui ux'로 걸린다."""
	# '인사이트', '인사이드 세일즈'가 인사(hr)에 걸리지 않게 바꿔 둔다
	return re.sub(r"[^\w\s/+#&-]", " ", (text or "").lower()).replace("인사이", "insi")


def has_any(text, words):
	"""ROLE_FAMILIES 위 주석의 규칙으로 text에 words 중 하나가 있는지 본다. text는 text_key를 거친 값이다."""
	for w in words:
		w = text_key(w).strip()
		if w and re.search(r"(?<![a-z])" + re.escape(w).replace(r"\ ", r"\s*") + r"(?![a-z])", text):
			return True
	return False


def profile_families(profile):
	"""프로필 role_family와 adjacent_families. 둘 다 없는 예전 프로필은 직무 이름과 검색어에서 찾는다."""
	fams = {f for f in [profile.get("role_family")] + profile.get("adjacent_families", []) if f in ROLE_FAMILIES}
	if fams:
		return fams
	text = text_key(" ".join([profile.get("role", ""), profile.get("role_en", "")] + profile.get("adjacent_roles", []) + profile.get("keywords_ko", []) + profile.get("keywords_en", [])))
	return {fam for fam, words in ROLE_FAMILIES.items() if has_any(text, words)}


def generic_words(families):
	groups = {"design" if f in DESIGN_FAMILIES else "business" if f in BUSINESS_FAMILIES else "dev" for f in families} or set(GENERIC)
	return [w for g in groups for w in GENERIC[g]]


def title_verdict(title, profile, own_families):
	t = text_key(title)
	own_words = profile.get("keywords_ko", []) + profile.get("keywords_en", []) + [profile.get("role", ""), profile.get("role_en", "")] + profile.get("adjacent_roles", [])
	own_words += [w for fam in own_families for w in ROLE_FAMILIES[fam]]
	if has_any(t, own_words):
		return None, "exact"
	for fam, words in ROLE_FAMILIES.items():
		if fam not in own_families and has_any(t, words):
			return "직무 불일치(" + fam + ")", None
	if has_any(t, generic_words(own_families)):
		return None, "generic"
	return "직무 판단 불가", None


def drop_reason(p, ctx):
	key = p.get("company")
	if matches_name(key, ctx["excluded"]):
		return "제외한 기업", None
	if matches_name(key, ctx["registry"]):
		return "레지스트리 기업(네임드 범위)", None
	if BLIND.search(p.get("company") or "") or "헤드헌팅" in (p.get("title") or ""):
		return "헤드헌팅 또는 회사명 비공개", None
	if p.get("employment") in NON_REGULAR and not ctx["allow_contract"]:
		return "고용형태 " + p["employment"], None
	deadline = p.get("deadline") or ""
	if re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline) and deadline < ctx["today"]:
		return "마감 지남", None
	y = ctx["years"]
	if p.get("min_years") is not None and p["min_years"] > y + 2:
		return "요건 %s년 이상" % p["min_years"], None
	if p.get("max_years") is not None and p["max_years"] < y - 2:
		return "요건 %s년 이하" % p["max_years"], None
	return title_verdict(p.get("title"), ctx["profile"], ctx["families"])


def run(workspace, registry_path, today, allow_contract=False):
	profile = json.load(open(os.path.join(workspace, "01_profile.json"), encoding="utf-8"))
	registry, excluded = parse_registry(registry_path)
	ctx = {"registry": registry, "excluded": excluded, "today": today, "years": float(profile["years"]), "profile": profile, "families": profile_families(profile), "allow_contract": allow_contract}
	seen, companies, dropped = set(), {}, []
	for path in sorted(glob.glob(os.path.join(workspace, "02_postings_*.json"))):
		for p in json.load(open(path, encoding="utf-8")).get("postings", []):
			url = p.get("original_url") or p.get("url")
			if url in seen:
				continue
			seen.add(url)
			reason, match = drop_reason(p, ctx)
			if reason:
				dropped.append({"company": p.get("company"), "title": p.get("title"), "url": url, "reason": reason})
				continue
			entry = companies.setdefault(norm(p.get("company")), {"company": p.get("company"), "score": 0, "postings": []})
			entry["postings"].append(dict(p, match=match))
			entry["score"] += 2 if match == "exact" else 1
	# ponytail: 점수는 직무 키워드가 맞는 공고 수뿐이다. 검증 대상이 너무 많아지면 회사 규모 같은 값을 더한다
	result = {"generated_at": today, "profile_years": ctx["years"], "companies": sorted(companies.values(), key=lambda c: (-c["score"], c["company"]))}
	json.dump(result, open(os.path.join(workspace, "03_candidates.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	json.dump(dropped, open(os.path.join(workspace, "03_prefilter_dropped.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	return result, dropped


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("--workspace", default="_discover")
	ap.add_argument("--registry", default="data/companies.md")
	ap.add_argument("--today", default=datetime.date.today().isoformat())
	ap.add_argument("--allow-contract", action="store_true")
	a = ap.parse_args()
	res, drop = run(a.workspace, a.registry, a.today, a.allow_contract)
	kept = sum(len(c["postings"]) for c in res["companies"])
	print("후보 기업 %d곳, 공고 %d건, 1차 제외 %d건" % (len(res["companies"]), kept, len(drop)))

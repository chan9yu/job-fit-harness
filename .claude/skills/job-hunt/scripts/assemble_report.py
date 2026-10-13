"""최종 리포트 합치기.

네임드 기업 절(_workspace/06_named.md)과 레지스트리 밖 회사 절(_discover/06_discover.md)을
제목과 머리 문장을 붙여 output/YYYY-MM-DD.md 한 장으로 합친다. 고르지 않은 범위의 절은 파일이 없으니 건너뛴다.

사용: python3 assemble_report.py --out output/2026-10-12.md --profile _workspace/01_profile.json --scope _workspace/00_scope.json
        [--named _workspace/06_named.md] [--discover _discover/06_discover.md] [--date YYYY-MM-DD]
"""

import argparse
import datetime
import json
import os

HEADER_FIRST_CELLS = {"티어", "등급"}
# 리포트를 처음 받은 사람이 추천과 검토, 티어와 등급을 헷갈려 추천 칸만 보고 끝내지 않게 머리 문장 아래에 둔다
GUIDE = "추천은 직무와 연차, 역량이 모두 맞는 공고이고 검토는 그중 하나가 경계에 걸려 직접 확인해 볼 공고다."
GUIDE_NAMED = "티어는 레지스트리에 적은 기업 티어(S가 가장 높고 \"-\"는 매기지 않은 기업)이고 표를 정렬하는 데만 쓴다."
GUIDE_DISCOVER = "등급은 레지스트리 밖 회사를 공개 자료로 검증한 결과다. A는 근거가 충분하고 B는 무난하며, C는 걸리는 점이 있어 공고가 맞아도 검토로 둔다."


def count_rows(text):
	"""표의 공고 행 수와 그중 신규 행 수를 센다. 머리 행과 구분선은 세지 않는다."""
	rows = new = 0
	for line in text.splitlines():
		if not line.startswith("|") or set(line.replace("|", "").strip()) <= set("-: "):
			continue
		cells = [c.strip() for c in line.strip().strip("|").split("|")]
		if cells[0] in HEADER_FIRST_CELLS:
			continue
		rows += 1
		if any(c.startswith("신규 ") for c in cells):
			new += 1
	return rows, new


def fmt_years(y):
	return str(int(y)) if float(y).is_integer() else str(y)


def assemble(out, profile_path, scope_path, named=None, discover=None, date=None):
	profile = json.load(open(profile_path, encoding="utf-8"))
	scope = json.load(open(scope_path, encoding="utf-8"))
	has_named, has_discover = (bool(p and os.path.exists(p)) for p in (named, discover))
	parts = [open(p, encoding="utf-8").read().strip() for p in (named, discover) if p and os.path.exists(p)]
	total = new = 0
	for part in parts:
		r, n = count_rows(part)
		total += r
		new += n
	labels = ", ".join(scope.get("named", []) + scope.get("discover", [])) or "없음"
	head = "%s 경력 %s년 기준. 범위: %s. 공고 %d건 (신규 %d건)" % (profile.get("role", ""), fmt_years(profile["years"]), labels, total, new)
	if parts:
		guide = " ".join([GUIDE] + [GUIDE_NAMED] * has_named + [GUIDE_DISCOVER] * has_discover)
		head = "%s\n\n%s" % (head, guide)
	body = "\n\n".join(parts) if parts else "범위 안에서 지원할 만한 공고를 찾지 못했다."
	text = "# 채용공고 %s\n\n%s\n\n%s\n" % (date or datetime.date.today().isoformat(), head, body)
	os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
	open(out, "w", encoding="utf-8").write(text)
	return total, new


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("--out", required=True)
	ap.add_argument("--profile", required=True)
	ap.add_argument("--scope", required=True)
	ap.add_argument("--named")
	ap.add_argument("--discover")
	ap.add_argument("--date")
	a = ap.parse_args()
	total, new = assemble(a.out, a.profile, a.scope, a.named, a.discover, a.date)
	print("%s에 공고 %d건(신규 %d건)을 썼다" % (a.out, total, new))

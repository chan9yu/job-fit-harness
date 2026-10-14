"""assemble_report.py와 make_batches.py 자체 확인. 실행: python3 -I .claude/skills/job-hunt/scripts/test_orchestration.py"""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assemble_report  # noqa: E402
import make_batches  # noqa: E402

NAMED = """## 네임드 기업

범위: 빅테크. 120곳 확인, 공고 2건 (신규 1건)

### 추천

| 기업 | 포지션 | 경력 | 마감 | 맞는 이유 | 링크 |
| --- | --- | --- | --- | --- | --- |
| 토스 | 신규 Frontend Developer | 3년 이상 | 상시 | React | [자사](https://x) |

### 검토

| 기업 | 포지션 | 경력 | 마감 | 걸리는 점 | 링크 |
| --- | --- | --- | --- | --- | --- |
| 당근 | Design Engineer | 미기재 | 미기재 | 디자인 엔지니어 | [자사](https://y) |
"""

DISCOVER = """## 레지스트리 밖 회사

범위: 성장 스타트업. 6곳 검증, 공고 1건 (신규 1건)

### 추천

| 등급 | 기업 | 회사 근거 | 포지션 | 경력 | 마감 | 맞는 이유 | 링크 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 아이벡스 | 시리즈C | 신규 Frontend Engineer | 5~11년 | 상시 | React | [원티드](https://z) |
"""


def main():
	d = tempfile.mkdtemp()
	json.dump({"role": "프론트엔드", "years": 5}, open(os.path.join(d, "p.json"), "w"), ensure_ascii=False)
	json.dump({"named": ["빅테크"], "discover": ["성장 스타트업"]}, open(os.path.join(d, "s.json"), "w"), ensure_ascii=False)
	open(os.path.join(d, "n.md"), "w", encoding="utf-8").write(NAMED)
	open(os.path.join(d, "d.md"), "w", encoding="utf-8").write(DISCOVER)
	out = os.path.join(d, "out", "2026-10-12.md")

	total, new = assemble_report.assemble(out, os.path.join(d, "p.json"), os.path.join(d, "s.json"), os.path.join(d, "n.md"), os.path.join(d, "d.md"), "2026-10-12")
	text = open(out, encoding="utf-8").read()
	assert (total, new) == (3, 2), (total, new)
	assert text.startswith("# 채용공고 2026-10-12\n\n프론트엔드 경력 5년 기준. 범위: 빅테크, 성장 스타트업. 공고 3건 (신규 2건)\n\n추천은 "), text[:200]
	assert assemble_report.GUIDE_NAMED in text and assemble_report.GUIDE_DISCOVER in text and "\n\n## 네임드 기업" in text, text[:600]
	assert "## 레지스트리 밖 회사" in text, text

	# 네임드만 고른 경우: 레지스트리 밖 절 파일이 없어도 동작한다
	json.dump({"named": ["빅테크"], "discover": []}, open(os.path.join(d, "s.json"), "w"), ensure_ascii=False)
	total, new = assemble_report.assemble(out, os.path.join(d, "p.json"), os.path.join(d, "s.json"), os.path.join(d, "n.md"), os.path.join(d, "missing.md"), "2026-10-12")
	text = open(out, encoding="utf-8").read()
	assert (total, new) == (2, 1) and "레지스트리 밖" not in text and "등급은" not in text and assemble_report.GUIDE_NAMED in text, text[:600]

	# 절이 하나도 없으면 한 줄 안내
	assemble_report.assemble(out, os.path.join(d, "p.json"), os.path.join(d, "s.json"), None, None, "2026-10-12")
	text = open(out, encoding="utf-8").read()
	assert "찾지 못했다" in text and "추천은" not in text, text

	# 배치: 고른 절만, 그룹 행은 배치마다 나누고 계열사 행을 붙인다
	reg = os.path.join(d, "companies.md")
	lines = ["# 대상 기업", "", "## 빅테크", "", "| 기업 | 티어 | 채용 페이지 | ATS | 접근 | 비고 |", "| --- | --- | --- | --- | --- | --- |"]
	lines += ["| 회사%d | S | https://x/%d | 자체 | api | |" % (i, i) for i in range(30)]
	lines += ["| 넥슨 | A | https://n | 자체 | browser | |", "", "## 대기업 계열사", "", "| 기업 | 티어 | 채용 페이지 | ATS | 접근 | 비고 |", "| --- | --- | --- | --- | --- | --- |"]
	lines += ["| 삼성 | | https://s | 자체 | api | 그룹 |", "| 삼성SDS | B | https://s | 자체 | group | 삼성 행. `C60` |", "| LG | | https://l | 자체 | api | 그룹 |", "| LG CNS | B | https://l | 자체 | group | LG 행. `CNS` |"]
	open(reg, "w", encoding="utf-8").write("\n".join(lines) + "\n")
	sm = make_batches.make(reg, ["빅테크"], os.path.join(d, "b1"))
	assert len(sm["batches"]) == 2 and sum(len(b["companies"]) for b in sm["batches"]) == 30 and sm["browser"] == ["넥슨"], sm
	sm = make_batches.make(reg, ["빅테크", "대기업 계열사"], os.path.join(d, "b2"))
	first = sm["batches"][0]
	assert first["companies"][0] == "삼성" and first["affiliates"] == ["삼성SDS"], first
	assert sm["batches"][1]["companies"][0] == "LG" and sm["batches"][1]["affiliates"] == ["LG CNS"], sm
	assert "삼성SDS" in open(os.path.join(d, "b2", "career-1.md"), encoding="utf-8").read()
	sm = make_batches.make(reg, ["없는 절"], os.path.join(d, "b3"))
	assert sm == {"batches": [], "browser": []}, sm
	print("ok")


if __name__ == "__main__":
	main()

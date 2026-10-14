"""네임드 기업 수집 배치 나누기.

data/companies.md에서 고른 범위 절의 행만 골라 job-scout 배치와 browser-scout 대상을 만든다.
그룹 행(삼성, LG 등)은 배치마다 고르게 나누고, 그룹 행이 든 배치에는 그 계열사 행(접근 group)을 참고용으로 붙인다.

사용: python3 make_batches.py --registry data/companies.md --sections "빅테크,대기업 계열사" --out-dir _workspace/batches [--max-batches 7]
"""

import argparse
import json
import os
import re

HEADER = "| 기업 | 채용 페이지 | ATS | 접근 | 비고 |\n| --- | --- | --- | --- | --- |"
AFFILIATE_NOTE = "\n계열사 행(따로 요청하지 않는다. 그룹 행을 읽을 때 company 이름과 affiliate를 맞추는 데 쓴다):\n"
# 계열사 행 비고가 "{그룹} 행"으로 시작하지 않는 예외
PARENT_OVERRIDE = {"토스페이먼츠": "비바리퍼블리카", "네이버클라우드": "네이버"}


def parse(path, sections):
	rows, section = [], None
	for line in open(path, encoding="utf-8"):
		line = line.rstrip("\n")
		if line.startswith("## "):
			section = line[3:].strip()
			continue
		if section not in sections or not line.startswith("| ") or line.startswith("| 기업") or line.startswith("| ---"):
			continue
		cells = [c.strip() for c in line.strip().strip("|").split("|")]
		if len(cells) == 5:
			rows.append(cells)
	return rows


def fmt(cells):
	return "| " + " | ".join(cells) + " |"


def make(registry, sections, out_dir, max_batches=7):
	rows = parse(registry, sections)
	career = [r for r in rows if r[3] in ("api", "fetch", "")]
	browser = [r for r in rows if r[3] in ("browser", "login")]
	group_rows = [r for r in rows if r[3] == "group"]
	parent = {}
	for r in group_rows:
		m = re.match(r"(\S+) 행", r[4])
		parent[r[0]] = PARENT_OVERRIDE.get(r[0]) or (m.group(1) if m else None)
	parents = set(parent.values())
	groups = [r for r in career if r[0] in parents]
	others = [r for r in career if r[0] not in parents]

	# 배치당 17곳 안팎, 그룹 행은 응답이 커서 배치당 3개까지. 둘 중 많은 쪽으로 배치 수를 정하고 상한을 넘지 않는다
	n = min(max_batches, max(1, -(-len(career) // 17), -(-len(groups) // 3))) if career else 0
	batches = [[] for _ in range(n)]
	for i, r in enumerate(groups):
		batches[i % n].append(r)
	sizes = [len(career) // n + (1 if i < len(career) % n else 0) for i in range(n)] if n else []
	it = iter(others)
	for i in range(n):
		while len(batches[i]) < sizes[i]:
			batches[i].append(next(it))

	os.makedirs(out_dir, exist_ok=True)
	summary = {"batches": [], "browser": [r[0] for r in browser]}
	for i, b in enumerate(batches, 1):
		names = {r[0] for r in b}
		text = HEADER + "\n" + "\n".join(map(fmt, b)) + "\n"
		subs = [r for r in group_rows if parent.get(r[0]) in names]
		if subs:
			text += AFFILIATE_NOTE + HEADER + "\n" + "\n".join(map(fmt, subs)) + "\n"
		open(os.path.join(out_dir, "career-%d.md" % i), "w", encoding="utf-8").write(text)
		summary["batches"].append({"id": "career-%d" % i, "companies": [r[0] for r in b], "affiliates": [r[0] for r in subs]})
	if browser:
		open(os.path.join(out_dir, "browser.md"), "w", encoding="utf-8").write(HEADER + "\n" + "\n".join(map(fmt, browser)) + "\n")
	json.dump(summary, open(os.path.join(out_dir, "summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
	return summary


if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("--registry", default="data/companies.md")
	ap.add_argument("--sections", required=True, help="쉼표로 구분한 절 이름")
	ap.add_argument("--out-dir", default="_workspace/batches")
	ap.add_argument("--max-batches", type=int, default=7)
	a = ap.parse_args()
	s = make(a.registry, [x.strip() for x in a.sections.split(",") if x.strip()], a.out_dir, a.max_batches)
	for b in s["batches"]:
		print("%s (%d곳): %s" % (b["id"], len(b["companies"]), ", ".join(b["companies"])))
	print("browser: %s" % (", ".join(s["browser"]) or "없음"))

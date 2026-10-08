---
name: resume-profiling
description: "이력서(PDF, md, txt, docx)에서 경력 연수와 직무, 핵심 기술, 도메인, 채용 검색어를 뽑아 _workspace/01_profile.json으로 만드는 절차와 스키마. resume-analyst 에이전트가 쓴다. 채용공고 탐색 전에 이력서를 분석하거나, 연차나 직무를 다시 계산하거나, 프로필을 고쳐 달라는 요청이면 이 스킬을 쓴다. 이력서 문장 첨삭이나 작성은 이 스킬이 아니다."
---

# resume-profiling

프로필은 이후 모든 수집과 판정의 기준이다. 여기서 연차를 1년 잘못 읽으면 리포트 전체가 한 단계씩 어긋난다.

## 1. 읽기

`resume/`에서 `preferences.md`를 뺀 파일이 이력서다. 여러 개면 전부 읽고 최신 내용을 기준으로 한다.

| 형식    | 읽는 법                                            |
| ------- | -------------------------------------------------- |
| PDF     | Read 도구. 10쪽이 넘으면 `pages`로 나눠 읽는다     |
| md, txt | Read 도구                                          |
| docx    | `textutil -convert txt -stdout "resume/파일.docx"` |
| 이미지  | Read 도구로 본다                                   |

`resume/preferences.md`가 있으면 마지막에 읽고, 겹치는 항목은 이 파일 값으로 덮어쓴다.

## 2. 경력 연수

기준일은 오늘이다. "재직 중"이나 "현재"는 오늘까지로 센다.

1. 정규직과 계약직 재직 기간을 모은다.
2. 기간이 겹치면 한 번만 센다.
3. 병역특례(산업기능요원, 전문연구요원) 근무는 넣는다. 국내 공고는 대개 경력으로 인정한다.
4. 인턴과 교육 과정, 부트캠프, 학부 연구생은 넣지 않는다. 뺀 기간은 `years_basis`에 적는다.
5. 프리랜서와 창업은 실제 개발 업무였으면 넣고 근거에 적는다.
6. 소수 첫째 자리까지 쓴다. 월 단위만 있으면 시작 월 1일부터 끝 월 말일까지로 본다.

다음 중 하나라도 해당하면 `confidence`를 `low`로 둔다: 재직 기간에 날짜가 없다, 겹치는 기간이 6개월을 넘는다, 직무가 중간에 바뀌었다(예: 디자이너에서 개발자로).

`preferences.md`에 연차가 적혀 있으면 그 값을 쓰고 `years_basis`에 "preferences.md 지정"이라고 적는다.

## 3. 직무

- `role`은 최근 두 직장에서 맡은 일로 정한다. 이력서 제목보다 실제 업무 기술을 따른다.
- `adjacent_roles`는 지원이 가능한 인접 직무 0~3개다. 이력서에 근거가 있어야 한다. 예: 프론트엔드 경력에 Node.js 서버 운영 경험이 있으면 "풀스택(프론트 중심)".

## 4. 기술과 도메인

- `skills_core`: 최근 3년 안의 실무 프로젝트에서 반복해 나온 기술, 최대 6개. 판정에서 공고 요건과 겹치는지 볼 때 쓴다.
- `skills_secondary`: 그 밖에 실무에서 쓴 기술, 최대 10개.
- `domains`: 일한 산업과 문제 영역. 예: 실시간 미디어, 결제, 커머스, B2B SaaS.

## 5. 검색어

공고 제목은 회사마다 표기가 다르다. 같은 직무를 가리키는 표기를 한국어와 영어로 모은다.

- `keywords_ko`: 예 "프론트엔드", "프론트엔드 개발자", "웹 프론트엔드", "FE 개발"
- `keywords_en`: 예 "Frontend Engineer", "Frontend Developer", "Front-end", "Web Engineer"

직무와 상관없는 기술명만으로 된 검색어는 넣지 않는다. "React" 하나로 찾으면 React Native 모바일 공고가 섞인다.

## 6. 스키마

`_workspace/01_profile.json`에 쓴다. `source_hash`는 오케스트레이터가 프롬프트로 넘겨준 값을 그대로 넣는다.

```json
{
	"generated_at": "2026-10-07",
	"source_hash": "3f9a1c0e7b2d4a61",
	"years": 5.3,
	"years_basis": "A사 2021-03~2023-02, B사 2023-03~현재. 인턴 6개월 제외",
	"confidence": "high",
	"role": "프론트엔드",
	"role_en": "Frontend Engineer",
	"adjacent_roles": ["웹 플랫폼"],
	"skills_core": ["TypeScript", "React", "WebRTC"],
	"skills_secondary": ["Next.js", "Node.js", "Electron"],
	"domains": ["실시간 미디어"],
	"keywords_ko": ["프론트엔드", "프론트엔드 개발자", "웹 프론트엔드"],
	"keywords_en": ["Frontend Engineer", "Frontend Developer", "Front-end"],
	"locations": [],
	"include_companies": [],
	"exclude_companies": [],
	"notes": ""
}
```

- `locations`, `include_companies`, `exclude_companies`는 `preferences.md`에서만 채운다. 없으면 빈 배열이다. 빈 `locations`는 지역 제한이 없다는 뜻이다.
- `notes`에는 판정에 영향을 줄 희망 조건을 한 줄로 적는다. 예: "SI 성격 포지션 제외, 원격 근무 선호".

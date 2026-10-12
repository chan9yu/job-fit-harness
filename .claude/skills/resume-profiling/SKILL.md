---
name: resume-profiling
description: "이력서(PDF, md, txt, docx)에서 경력 연수와 직무, 직무군 키, 핵심 역량, 도메인, 채용 검색어를 뽑아 _workspace/01_profile.json으로 만드는 절차와 스키마. 개발 직군과 기획, 디자인, 데이터 분석, 마케팅, 영업 같은 개발 밖 직군 이력서를 모두 다룬다. resume-analyst 에이전트가 쓴다. 채용공고 탐색 전에 이력서를 분석하거나, 연차나 직무를 다시 계산하거나, 프로필을 고쳐 달라는 요청이면 이 스킬을 쓴다. 이력서 문장 첨삭이나 작성은 이 스킬이 아니다."
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
5. 프리랜서와 창업은 지금 직무의 실제 업무였으면 넣고 근거에 적는다.
6. 직무를 바꾼 이력서는 지금 직무(3절의 `role`)로 일한 기간만 센다. 이전 직무 기간은 빼고 뺀 기간과 이유를 `years_basis`에 적는다. 이전 직무에서도 지금 직무의 일을 했다는 근거가 이력서에 있으면(예: 마케터로 일하며 앱 서비스 기획을 맡았다) 그 기간은 넣고 근거를 적는다.
7. 소수 첫째 자리까지 쓴다. 월 단위만 있으면 시작 월 1일부터 끝 월 말일까지로 본다.

다음 중 하나라도 해당하면 `confidence`를 `low`로 둔다: 재직 기간에 날짜가 없다, 겹치는 기간이 6개월을 넘는다, 직무가 중간에 바뀌었다(예: 디자이너에서 개발자로, 마케터에서 서비스 기획자로).

`preferences.md`에 연차가 적혀 있으면 그 값을 쓰고 `years_basis`에 "preferences.md 지정"이라고 적는다.

## 3. 직무

- `role`은 최근 두 직장에서 맡은 일로 정한다. 이력서 제목이나 직함보다 실제 업무 기술을 따른다. 직함이 "매니저"여도 한 일이 광고 캠페인 운영과 성과 분석이면 마케팅이고, 직함이 "디자이너"여도 한 일이 기능 정의와 요구사항 정리, 화면 설계서 작성이면 서비스 기획이다.
- `role_family`는 아래 표의 키 하나다. `role`이 두 키에 걸치면 최근 2년 업무 중 비중이 큰 쪽을 고른다.
- `adjacent_roles`는 지원이 가능한 인접 직무 0~3개다. 이력서에 근거가 있어야 한다. 예: 프론트엔드 경력에 Node.js 서버 운영 경험이 있으면 "풀스택(프론트 중심)", 서비스 기획 경력에 데이터 추출과 지표 분석을 직접 했으면 "데이터 분석".
- `adjacent_families`는 `adjacent_roles`를 아래 표의 키로 옮긴 배열이다. 맞는 키가 없는 인접 직무는 넣지 않는다.

1차 거르기(`.claude/skills/job-hunt/scripts/prefilter.py`)가 `role_family`와 `adjacent_families`로 공고 제목을 거른다. 표에 없는 값을 쓰면 그 값은 무시되고 직무 이름과 검색어로 직무군을 다시 찾는다.

| 키              | 직무                          | 키                     | 직무                                    |
| --------------- | ----------------------------- | ---------------------- | --------------------------------------- |
| `frontend`      | 프론트엔드                    | `product_manager`      | 서비스 기획, PM, PO                     |
| `backend`       | 백엔드, 서버                  | `product_designer`     | 프로덕트 디자인, UX/UI                  |
| `fullstack`     | 풀스택                        | `visual_designer`      | 그래픽, 브랜드, BX 디자인               |
| `android`       | 안드로이드                    | `data_analyst`         | 데이터 분석, 데이터 사이언스            |
| `ios`           | iOS                           | `marketing`            | 퍼포먼스, 브랜드, 콘텐츠, 그로스 마케팅 |
| `crossplatform` | Flutter, React Native 앱      | `business_development` | 영업, 사업개발, 제휴                    |
| `data_engineer` | 데이터 엔지니어               | `operations`           | CS, 서비스 운영                         |
| `ml`            | 머신러닝, AI 엔지니어         | `hr`                   | 인사, 채용, 조직문화                    |
| `devops`        | DevOps, 인프라, SRE, 클라우드 | `finance`              | 재무, 회계, 세무                        |
| `qa`            | QA, 테스트                    | `legal`                | 법무, 컴플라이언스                      |
| `security`      | 정보보안                      | `merchandiser`         | MD, 상품기획                            |
| `game_dev`      | 게임 클라이언트, 서버 개발    |                        |                                         |

## 4. 역량과 도메인

- `skills_core`: 최근 3년 안의 실무에서 반복해 나온 역량, 최대 6개. 판정에서 공고 요건과 겹치는지 볼 때 쓴다. 무엇을 담는지는 직무군마다 다르다.
- `skills_secondary`: 그 밖에 실무에서 쓴 것, 최대 10개. 담는 종류는 `skills_core`와 같다.
- `domains`: 일한 산업과 문제 영역. 예: 실시간 미디어, 결제, 커머스, B2B SaaS.

| 직무군                                                                         | `skills_core`에 담는 것  | 예                                                    |
| ------------------------------------------------------------------------------ | ------------------------ | ----------------------------------------------------- |
| 개발(`frontend`부터 `game_dev`까지 왼쪽 열)                                    | 기술 스택                | TypeScript, React, Kotlin, Kubernetes                 |
| `product_designer`, `visual_designer`                                          | 도구와 산출물 종류       | Figma, 디자인 시스템 구축, 브랜드 가이드, 모션 그래픽 |
| `product_manager`, `data_analyst`, `marketing`                                 | 도메인과 도구, 역량      | 커머스, SQL, GA4, A/B 테스트, 퍼포먼스 광고 운영      |
| `business_development`, `operations`, `hr`, `finance`, `legal`, `merchandiser` | 도메인과 업무 범위, 자격 | B2B SaaS 영업, 채용 운영, 연결결산, 변호사 자격       |

값은 이력서에 나온 표기를 그대로 쓴다.

## 5. 검색어

공고 제목은 회사마다 표기가 다르다. 같은 직무를 가리키는 표기를 한국어와 영어로 모은다.

| 직무군             | `keywords_ko`                                                 | `keywords_en`                                                          |
| ------------------ | ------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `frontend`         | "프론트엔드", "프론트엔드 개발자", "웹 프론트엔드", "FE 개발" | "Frontend Engineer", "Frontend Developer", "Front-end", "Web Engineer" |
| `product_manager`  | "서비스 기획", "서비스 기획자", "프로덕트 매니저", "PM"       | "Product Manager", "Product Owner", "PM"                               |
| `product_designer` | "프로덕트 디자이너", "UX 디자이너", "UI/UX 디자이너"          | "Product Designer", "UX Designer", "UI/UX Designer"                    |
| `marketing`        | "퍼포먼스 마케터", "퍼포먼스 마케팅", "그로스 마케터"         | "Performance Marketer", "Growth Marketer"                              |

첫 번째 값이 플랫폼 키워드 검색과 ATS 검색에 그대로 들어간다(`job-collection/references/platforms.md`의 `{kw}`, `{kw_en}`). 첫 번째에는 그 직무만 가리키는 가장 흔한 표기를 둔다. "PM", "MD", "CS" 같은 짧은 약어는 뜻이 여럿이라(PM은 프로젝트 매니저이기도 하다) 첫 번째에 두지 않는다.

직무 이름 없이 기술이나 도구 이름만으로 된 검색어는 넣지 않는다. "React" 하나로 찾으면 React Native 모바일 공고가 섞인다.

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
	"role_family": "frontend",
	"adjacent_roles": ["웹 플랫폼"],
	"adjacent_families": [],
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

개발 밖 직군 예시다. 마케터로 2년 일하고 서비스 기획자로 옮긴 이력서이고, 위 예시와 값이 다른 필드만 적었다.

```json
{
	"years": 5.6,
	"years_basis": "C사 퍼포먼스 마케터 2019-03~2021-02는 직무가 달라 제외. D사 서비스 기획 2021-03~현재",
	"confidence": "low",
	"role": "서비스 기획",
	"role_en": "Product Manager",
	"role_family": "product_manager",
	"adjacent_roles": ["퍼포먼스 마케팅"],
	"adjacent_families": ["marketing"],
	"skills_core": ["커머스", "요구사항 정의", "SQL", "A/B 테스트", "Figma"],
	"skills_secondary": ["Amplitude", "Jira", "GA4"],
	"domains": ["커머스", "구독 서비스"],
	"keywords_ko": ["서비스 기획", "서비스 기획자", "프로덕트 매니저", "PM"],
	"keywords_en": ["Product Manager", "Product Owner", "PM"]
}
```

- `locations`, `include_companies`, `exclude_companies`는 `preferences.md`에서만 채운다. 없으면 빈 배열이다. 빈 `locations`는 지역 제한이 없다는 뜻이다.
- `notes`에는 판정에 영향을 줄 희망 조건을 한 줄로 적는다. 예: "SI 성격 포지션 제외, 원격 근무 선호".

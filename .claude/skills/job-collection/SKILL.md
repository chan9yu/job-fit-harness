---
name: job-collection
description: "자사 채용 페이지, ATS(그리팅, 나인하이어, Lever, Greenhouse 등), 채용 플랫폼(원티드, 리멤버, 잡플래닛, 사람인, 직행, 점핏, 잡코리아, 링크드인)에서 프로필에 맞는 채용공고를 찾아 _workspace/02_postings_{batch}.json으로 기록하는 방법. job-scout와 browser-scout가 쓴다. 채용 페이지에서 공고 목록을 읽거나, 공고 상세에서 경력 요건과 마감일을 뽑거나, 특정 기업이나 플랫폼 공고만 다시 모을 때 이 스킬을 쓴다."
---

# job-collection

직무가 맞을 가능성이 있는 공고를 빠뜨리지 않고 모으고, 각 공고의 경력 요건과 마감일을 상세 페이지에서 확인해 기록한다. 맞는지 안 맞는지는 fit-reviewer가 판정하므로 여기서는 애매하면 넣는다.

## 1. 순서

기업 하나마다 아래를 한다.

1. 레지스트리의 접근 방식대로 채용 페이지에서 공고 제목과 상세 URL을 모은다.
2. 제목으로 거른다.
3. 남은 공고의 상세를 연다.
4. 출력 스키마대로 기록한다.

자사 채용 페이지는 `references/career-sites.md`, 플랫폼 배치는 `references/platforms.md`를 읽는다. 플랫폼 배치는 플랫폼별 검색 URL로 1의 목록을 만들고, 나머지는 같다.

## 2. 목록 읽기

`references/career-sites.md`의 기업별 절에 그 기업이 있으면 접근 방식과 상관없이 그 방법을 먼저 쓴다. 없으면 아래 표를 따른다.

| 접근               | 방법                                                                                                                                                                                                                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `api`              | `references/career-sites.md`에서 그 기업 절이나 ATS 절의 요청을 `curl`로 보내고 `jq`로 제목과 URL, 경력, 마감을 뽑는다                                                                                                                                                               |
| `fetch`            | `curl -sL -A "$UA" {URL}`로 원본 HTML을 받는다(`$UA`는 `references/career-sites.md` 맨 위). 공고가 `<script id="__NEXT_DATA__">` 같은 JSON에 들어 있으면 그 JSON을 `jq`로 읽는다. HTML에서 바로 뽑기 어려우면 WebFetch에 "개발 직군 공고의 제목과 상세 URL을 전부 나열"하라고 묻는다 |
| 빈칸               | `fetch` 방법을 먼저 해 본다. 공고 제목이 HTML에 없으면 검색 우회로 간다. 어느 방법이 통했는지 `registry_updates`에 적는다                                                                                                                                                            |
| `browser`, `login` | job-scout는 하지 않고 `unreachable`에 넣는다. browser-scout는 6절을 따른다                                                                                                                                                                                                           |

레지스트리에 새로 넣은 기업이라 접근이 비어 있어도 ATS 열이 `greetinghr`, `greenhouse`, `lever`, `recruiter`, `workday`면 `references/career-sites.md`의 ATS 절 방법을 그대로 쓴다.

WebFetch는 긴 페이지를 요약하면서 목록 뒷부분을 빠뜨릴 수 있다. 공고가 수십 개인 목록은 curl과 jq로 읽는다.

**검색 우회**: 목록이 JS로만 그려져도 상세 페이지는 검색에 잡히고 서버에서 그려지는 경우가 있다. WebSearch의 `allowed_domains`에 채용 페이지 도메인을 넣고 `keywords_ko` 첫 번째와 `keywords_en` 첫 번째로 각각 찾은 뒤 나온 상세 URL을 연다. 검색어에 `site:`를 쓰면 결과가 거의 나오지 않는다. 검색 결과에는 마감된 공고가 섞이므로 상세에서 마감 여부를 반드시 본다. 이것도 안 되면 `unreachable`에 `js`로 적는다.

## 3. 제목 거르기

다음 중 하나면 상세를 연다.

- 제목에 프로필의 `keywords_ko`, `keywords_en`, `role`, `adjacent_roles` 중 하나가 들어 있다.
- 제목만으로 직무를 알 수 없다. 예: "Software Engineer", "개발자 (경력)", "개발 직군 통합 채용".

직무가 분명히 다른 공고는 열지 않는다. 예를 들어 프로필이 프론트엔드면 "iOS", "데이터 엔지니어", "프로덕트 디자이너"는 연다고 얻을 것이 없다. 기업 하나에서 상세는 15개까지 연다. 넘으면 제목이 키워드와 정확히 맞는 것부터 연다.

## 4. 상세에서 뽑기

| 필드                     | 규칙                                                                                                                             |
| ------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `experience_raw`         | "자격요건", "지원자격", "Qualifications"에 적힌 경력 요건 원문                                                                   |
| `min_years`, `max_years` | 원문의 숫자. "3년 이상"은 3과 null, "5~10년"은 5와 10, "신입"은 0과 0, "경력 무관"이나 요건 없음은 null과 null                   |
| `deadline`               | `YYYY-MM-DD`. "채용 시 마감"과 "상시"는 "상시", 안 적혀 있으면 "미기재"                                                          |
| `location`               | 근무지. 원격 가능이면 "원격 가능"을 덧붙인다                                                                                     |
| `employment`             | 정규직, 계약직, 인턴, 파견, 미기재 중 하나                                                                                       |
| `skills`                 | 자격요건, 우대사항, "사용하는 기술", "개발환경", "기술 스택" 절에 나온 기술 이름, 최대 10개. 자격요건과 우대사항에서 먼저 뽑는다 |
| `evidence`               | 경력 요건이 적힌 문장 한 줄을 그대로                                                                                             |

마감됐거나 "모집 종료", "채용 완료" 표시가 있으면 기록하지 않는다. 헤드헌팅이나 서치펌이 올린 공고와 회사명을 가린 공고도 기록하지 않는다. 판정 대상이 아니라서 상세를 열 이유가 없다.

## 5. 출력 스키마

`_workspace/02_postings_{batch}.json`에 쓴다. 공고가 0건이어도 파일은 쓴다. fit-reviewer는 `checked`로 어느 기업을 확인했는지 센다.

```json
{
	"batch": "career-1",
	"collected_at": "2026-10-07",
	"checked": ["비바리퍼블리카", "당근"],
	"postings": [
		{
			"company": "비바리퍼블리카",
			"affiliate": "토스",
			"title": "Frontend Developer (Payments)",
			"url": "https://toss.im/career/job-detail?job_id=0000000",
			"source": "career",
			"original_url": null,
			"experience_raw": "경력 3년 이상",
			"min_years": 3,
			"max_years": null,
			"deadline": "상시",
			"location": "서울 강남구",
			"employment": "정규직",
			"skills": ["React", "TypeScript"],
			"evidence": "React 기반 웹 서비스 개발 경력 3년 이상이신 분",
			"in_registry": true
		}
	],
	"unreachable": [{ "target": "쿠팡", "url": "https://www.coupang.jobs/kr/", "reason": "js" }],
	"registry_updates": [{ "company": "당근", "field": "접근", "value": "fetch", "why": "HTML에 공고 제목이 있음" }]
}
```

- `company`는 레지스트리 표기를 그대로 쓴다. 레지스트리 밖 기업은 공고에 적힌 회사명을 쓰고 `in_registry`를 `false`로 둔다.
- `affiliate`는 계열사가 섞여 나오는 사이트(그룹 통합 사이트, 토스, 라인)에서 공고의 계열사 이름이다. 그 밖에는 null이다. 계열사가 레지스트리에 따로 행으로 있으면(예: 토스페이먼츠, SK텔레콤) `company`도 그 행 이름으로 쓴다. 없으면 `company`는 읽은 행의 이름이다. fit-reviewer가 `company`로 티어를 찾는다.
- `source`는 `career`, `wanted`, `remember`, `jobplanet`, `saramin`, `zighang`, `jumpit`, `jobkorea`, `linkedin`, `catch` 중 하나다.
- `original_url`은 플랫폼 공고가 자사 채용 페이지 링크를 같이 보여 줄 때 그 링크다.
- `reason`은 `js`, `login`, `blocked`, `not_found`, `timeout`, `chrome_unavailable` 중 하나다.

## 6. 브라우저로 읽기 (browser-scout 전용)

Claude in Chrome 도구를 쓴다. 도구가 지연 로딩 상태면 ToolSearch 한 번으로 한꺼번에 불러온다.

```
select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__tabs_create_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__get_page_text,mcp__claude-in-chrome__find,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_network_requests,mcp__claude-in-chrome__tabs_close_mcp
```

1. `tabs_context_mcp`로 연결을 확인한다. 실패하면 맡은 대상 전부를 `chrome_unavailable`로 적고 끝낸다.
2. `tabs_create_mcp`로 탭을 하나 만들고 끝까지 그 탭만 쓴다. 사용자가 열어 둔 탭은 건드리지 않는다.
3. 페이지마다 `navigate`한 뒤 `get_page_text`로 본문을 읽는다. 목록이 스크롤해야 더 나오면 `computer`로 스크롤하고 다시 읽는다. 목록의 "더보기" 버튼은 눌러도 된다.
4. 검색 조건은 가능하면 URL 파라미터로 건다(`references/platforms.md`). 검색 폼을 채우는 것보다 덜 깨진다.
5. 자사 채용 페이지가 JS로 그려지면 `read_network_requests`로 공고 목록을 받아 오는 JSON 요청을 찾는다. 찾으면 그 URL과 메서드, 본문을 `registry_updates`에 적는다. 다음 실행부터 job-scout가 curl로 읽는다.
6. 로그인 화면이 나오면 그 사이트는 `login`으로 적고 넘어간다.
7. 끝나면 만든 탭을 닫는다.

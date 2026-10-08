# 채용 플랫폼과 ATS 탐색

플랫폼 배치(`platforms`)와 browser-scout가 읽는다. 2026-10-07에 "프론트엔드", 경력 5년으로 직접 요청해 확인한 방법이다. 응답 구조가 바뀌어 실패하면 이 파일을 고친다.

## 목차

- 공통 규칙
- 원티드, 리멤버, 사람인, 직행, 점핏, 잡코리아, 링크드인, 캐치 (job-scout)
- 잡플래닛 (browser-scout)
- ATS 검색으로 레지스트리 밖 기업 찾기

## 공통 규칙

- `{kw}`는 프로필 `keywords_ko`의 첫 번째, `{kw_en}`은 `keywords_en`의 첫 번째, `{y}`는 프로필 `years`의 정수 부분이다. 쿼리 문자열에 넣을 때는 URL 인코딩한다.
- 리멤버와 점핏, 직행은 키워드가 공고 본문까지 맞아서 다른 직무가 섞인다. 직무 코드가 있으면 직무 코드를 쓰고, 결과는 SKILL.md 3절대로 제목으로 한 번 더 거른다.
- 서버의 연차 필터는 대략적이다. `min_years`, `max_years`는 응답이나 상세의 연차 필드로 채운다.
- 헤드헌팅이나 서치펌 공고, 회사명을 가린 공고는 기록하지 않는다. 사람인과 잡코리아에 많다.
- 플랫폼 하나에서 100건까지만 기록한다. 최신순으로 받는다.
- 목록 응답에 연차와 마감이 다 있으면 상세를 열지 않는다. 플랫폼 결과는 대부분 레지스트리 밖 기업이라 상세를 다 열면 요청이 수백 번이 된다.

| 플랫폼   | `source`    | 접근    | 담당          |
| -------- | ----------- | ------- | ------------- |
| 원티드   | `wanted`    | api     | job-scout     |
| 리멤버   | `remember`  | api     | job-scout     |
| 사람인   | `saramin`   | fetch   | job-scout     |
| 직행     | `zighang`   | api     | job-scout     |
| 점핏     | `jumpit`    | api     | job-scout     |
| 잡코리아 | `jobkorea`  | fetch   | job-scout     |
| 링크드인 | `linkedin`  | fetch   | job-scout     |
| 캐치     | `catch`     | api     | job-scout     |
| 잡플래닛 | `jobplanet` | browser | browser-scout |

프로그래머스 커리어(career.programmers.co.kr)는 2026-10-07 기준 도메인이 해석되지 않아 뺐다.

## 원티드

- 직무 목록: `GET https://www.wanted.co.kr/api/v4/jobs?country=kr&tag_type_ids=669&job_sort=job.latest_order&years={y}&locations=all&limit=100&offset=0`. 669는 프론트엔드 직무 코드다. 다른 직무 코드는 확인하지 않았으니 프론트엔드가 아니면 키워드 검색을 쓴다.
- 키워드 검색: `GET https://www.wanted.co.kr/api/chaos/search/v1/results?query={kw}&country=kr&job_sort=job.recommend_order&years={y}&locations=all&limit=20`. 공고는 `positions.data`, 다음 페이지는 `links.next`.
- `years={y}`는 경력 범위에 `{y}`년이 들어가는 공고만 남긴다.
- 상세: `GET https://www.wanted.co.kr/api/v4/jobs/{id}`. `annual_from`, `annual_to`가 연차, `due_time`이 마감(null이면 상시), `detail.requirements`가 자격요건이다.
- 공고 링크: `https://www.wanted.co.kr/wd/{id}`

## 리멤버

```bash
curl -s -X POST https://career-api.rememberapp.co.kr/job_postings/search \
  -H 'Content-Type: application/json' \
  -d '{"page":1,"per":30,"search":{"keywords":["{kw}"],"career_year":{y}},"sort":"starts_at_desc"}'
```

- 키는 snake_case로 보낸다. camelCase는 무시되고 필터 없이 전체가 온다.
- 응답의 `min_experience`, `max_experience`(null이면 상한 없음)가 연차, `ends_at`(null이면 상시)이 마감이다.
- 공고 링크: `https://career.rememberapp.co.kr/job/posting/{id}`

## 사람인

- 목록: `https://www.saramin.co.kr/zf_user/search/recruit?searchword={kw}&exp_cd=2&exp_min={y}&exp_max={y}&recruitPageCount=40`. HTML에 공고 40건이 있다. `exp_cd=2`가 경력이다.
- 목록의 `job_condition`에 "경력5년↑", "경력 3~8년" 같은 텍스트가 있다. 마감은 연도 없이 "~ 10/11(일)"로 나온다.
- 상세: `https://www.saramin.co.kr/zf_user/jobs/relay/view?rec_idx={id}`. `og:description`에 "경력:경력 5년 이상 … 마감일:2026-11-05"가 있다. 마감 연도가 필요하면 여기서 읽는다.

## 직행

- 목록: `GET https://api.zighang.com/api/recruitments/v4?page=0&size=100&keyword={kw}&careerMin={y}&careerMax={y}`
- `affiliate`가 `"직행"`인 공고만 기록한다. 이 값이 직행이 자사 채용 페이지에서 직접 모은 공고다. 나머지는 원티드, 잡코리아, 리멤버, 점핏, 캐치 공고를 다시 올린 것이라 다른 플랫폼 수집과 겹친다.
- 상세: `GET https://api.zighang.com/api/recruitments/{uuid}`. `redirectUrl`이 원문 링크다. `url`과 `original_url`에 둘 다 이 값을 넣는다.
- 마감은 `deadlineType`(마감일, 상시채용, 채용시마감)과 `endDate`. `careerMax=100`이면 상한이 없다는 뜻이다.

## 점핏

- 목록: `GET https://jumpit-api.saramin.co.kr/api/positions?jobCategory=2&career={y}&sort=rsp_rate&page=1`. `jobCategory=2`가 프론트엔드다. 다른 직무면 `jobCategory` 대신 `keyword={kw}`를 쓰고 제목으로 거른다.
- 상세: `GET https://jumpit-api.saramin.co.kr/api/position/{id}`. `minCareer`, `maxCareer`, `closedAt`("2026-10-10 23:59:59" 형식), `alwaysOpen`.
- 공고 링크: `https://jumpit.saramin.co.kr/position/{id}`

## 잡코리아

- 목록: `https://www.jobkorea.co.kr/Search/?stext={kw}&careerType=2&careerMin={y}&careerMax={y}&Page_No=1`. 페이지당 25건이고 링크는 `/Recruit/GI_Read/{id}` 형식이다.
- 경력 필터를 걸어도 신입 공고가 섞여 나온다. 연차는 상세에서 확인한다.
- 상세: `https://www.jobkorea.co.kr/Recruit/GI_Read/{id}`. `og:description`에 "경력 : 경력 5년이상 … 마감일 : 2026.10.26"이 있다.

## 링크드인

- 목록: `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={kw_en}&location=South%20Korea&f_E=4&start=0`. 로그인 없이 HTML 조각을 준다. 페이지당 10건이고 `start`를 10씩 올려 50건까지 본다.
- 연차 필터는 없다. `f_E`는 직급이고 4(Mid-Senior)만 확인했다. 경력이 3년 미만이면 `f_E`를 빼고 받는다.
- 상세: `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}`. 연차는 본문 텍스트에서 읽는다. 마감일 필드가 없으므로 `deadline`은 "미기재"다.
- 공고 링크: `https://www.linkedin.com/jobs/view/{id}`
- 같은 기업이 레지스트리에 있으면 그 기업 자사 배치가 이미 같은 공고를 모았을 가능성이 크다. fit-reviewer가 합친다.

## 캐치

대기업 공채가 많은 플랫폼이다. 개발 직군 공고 수는 적다.

- 목록: `GET https://www.catch.co.kr/api/v1.0/recruit/information/getRecruitList?Keyword={kw}&JobCode=&Sido=&Career=2&JCode=&Size=&EduLevel=&WorkPosition=&CompID=&GroupCode=&Sort=0&curpage=1&pageSize=30&onRecruitYN=Y&ExceptIDList=`
- `Career=2`는 경력이지만 신입/경력 공고도 함께 온다. 연차 숫자 필터는 없다.
- 응답의 `ExperienceRange`("3년↑" 형식)가 연차, `ApplyEndDatetime`(UTC)이 마감이다. 한국 시간으로 바꿔 날짜를 적는다. `ApplyEndCode`가 "채용시 마감"이나 "상시채용"이면 `deadline`은 "상시"다.
- 공고 링크: `https://www.catch.co.kr/NCS/RecruitInfoDetails/{RecruitID}`

## 잡플래닛 (browser-scout)

curl은 HTML과 API 모두 Cloudflare에 막혀 403을 받는다. 브라우저에서는 열린다.

1. 탭에서 `https://www.jobplanet.co.kr/job`을 연다. Cloudflare 확인이 끝날 때까지 기다린다.
2. 같은 탭에서 `https://www.jobplanet.co.kr/api/v3/job/postings?occupation_level2=11905&years_of_experience={y},{y}&order_by=recent&page=1&page_size=20`으로 이동해 `get_page_text`로 JSON을 읽는다. 11905는 프론트엔드 개발 직무 코드다.
3. `q` 파라미터는 무시되므로 키워드 검색은 안 된다. 프론트엔드가 아니면 1의 화면에서 직무 필터를 골라 바뀐 URL의 `occupation_level2` 값을 읽어 쓴다.
4. `years_of_experience={y},{y}`가 동작한다(2026-10-07 확인: 4,4로 344건, 필터 없이 534건). `page_size`는 100까지 받는다. 11905 결과에도 Java, C# 같은 일반 개발 공고가 섞이므로 제목으로 다시 거른다.
5. 응답의 `annual.years`, `annual.maximum_years`(0이면 상한 없음)가 연차, `end_at`이 마감이다. `external_url`이 있으면 `original_url`에 넣는다. 공고 링크는 `https://www.jobplanet.co.kr/job/search?posting_ids%5B%5D={id}`다.

## ATS 검색으로 레지스트리 밖 기업 찾기

WebSearch의 `site:` 연산자는 ATS 도메인에서 결과를 내지 못했다. 대신 WebSearch의 `allowed_domains` 파라미터로 도메인을 제한한다.

| ATS             | `allowed_domains`     | 검색어      |
| --------------- | --------------------- | ----------- |
| 그리팅          | `["greetinghr.com"]`  | `{kw} 경력` |
| 나인하이어      | `["ninehire.site"]`   | `{kw} 경력` |
| recruiter.co.kr | `["recruiter.co.kr"]` | `{kw} 경력` |

검색 인덱스가 오래돼서 찾은 공고의 상당수가 이미 닫혀 있다(확인 때 그리팅 3건 중 2건이 404였다). 나온 상세 URL은 반드시 직접 받아서 열려 있는지 본다. 그리팅은 `references/career-sites.md`의 그리팅 절 방법으로 읽는다. 열려 있는 공고만 `in_registry: false`로 기록한다.

Lever와 Greenhouse는 검색 결과가 대부분 해외 기업이라 탐색에 쓰지 않는다. 이 ATS를 쓰는 국내 기업은 레지스트리에 넣어 둔다.

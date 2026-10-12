# 자사 채용 페이지 읽는 법

자사 페이지 배치(`career-*`)와 browser-scout가 읽는다. 2026-10-07에 기업마다 직접 요청해 응답을 확인한 방법이다. 요청이 실패하면 이 파일과 `data/companies.md`를 고칠 내용을 `registry_updates`에 적는다.

HTML을 받을 때는 Chrome 전체 User-Agent를 쓴다. `Mozilla/5.0`만 보내면 403을 주는 곳(크래프톤)이 있다.

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
```

## 목차

- 직군 필터와 직무군: 프로필 직무군이 개발 직군이 아닐 때 각 절의 직군 필터를 바꾸는 법
- ATS별: 그리팅, Greenhouse, Lever, recruiter.co.kr(신형), Workday, 나인하이어, Workable, 플렉스 채용, 원티드 회사 페이지, 사람인과 캐치 회사 페이지, recruiter.co.kr 구형
- 기업별: 자체 API나 특이한 페이지를 쓰는 기업. 대기업 그룹 통합 사이트(삼성, LG, SK, 현대자동차, 롯데, CJ, KT, 한화, 포스코, 신세계)는 한 절에 모았다

## 직군 필터와 직무군

이 문서의 요청 예시에 들어 있는 직군 필터 값(네이버 `subJobCdArr` 1010xxx, 카카오 `part=TECHNOLOGY`, 우아한형제들 `BA005001` 등)은 개발 직군 값이다. 프로필 `01_profile.json`의 `role_family`가 다른 직무군이면 각 절의 "다른 직군" 줄을 본다. 그 줄에 직무군 키와 코드의 짝이 있으면 그 코드로 바꿔 보내고, `adjacent_families`의 코드도 함께 넣는다. "다른 직군" 줄이 없는 절이면 직군 필터를 빼고 전체를 받아 제목으로 거른다.

- "다른 직군" 줄의 코드와 이름, 건수는 2026-10-12에 요청해 확인한 값이다. 펄어비스, 롯데, 야놀자(Workday), NHN처럼 지금 공고가 있는 직군만 화면이나 응답에 보여 주는 사이트가 있다. 그날 공고가 없어 짝을 확인하지 못한 직무군은 "미확인"으로 적었다. 그 직무군이면 필터를 빼고 받는다.
- 필터를 빼는 방법이 사이트마다 다르다. 키를 아예 빼야 하는 곳(우아한형제들), 빈 값이나 빈 배열을 보내면 되는 곳(네이버, LG, 한화), 빼면 개발 직군만 오는 곳(카카오)이 있다. 각 절의 줄을 따른다.
- 짝은 사이트가 붙인 직군 이름으로 지었다. "영업/마케팅"처럼 한 코드에 여러 직무군이 섞인 곳이 많으니 받은 뒤 제목으로 한 번 더 거른다.
- 개발 직군 안에서도 예시가 프론트엔드나 백엔드 코드 하나만 적힌 절(SK `jobRole`)은 프로필 직무군에 맞는 코드로 바꾼다.

## ATS별

### 그리팅 (greetinghr)

목록 URL은 `https://{sub}.career.greetinghr.com/ko/home`이거나 회사가 정한 경로(`/ko/positions`, `/ko/recruiting`)다. 커스텀 도메인(예: careers.kakaopay.com)도 구조가 같다. 공고를 얻는 방법은 둘이고 공고 객체 모양은 같다.

레지스트리 비고에 `workspace {id}`가 있으면 공개 API를 쓴다. `page`는 0부터 시작한다.

```bash
curl -s "https://api.greetinghr.com/ats/v1.1/career/workspaces/{id}/openings?page=0&pageSize=100" \
  | jq -c '.data.datas[] | {id: .openingId, title, due: .dueDate,
      career: [.openingJobPosition.openingJobPositions[].jobPositionCareer | {careerType, careerFrom, careerTo}],
      group: [.openingJobPosition.openingJobPositions[] | (.workspaceOccupation.occupation // .workspaceJob.job)]}'
```

workspace id가 없으면 목록 페이지 원본 HTML의 `__NEXT_DATA__`를 읽는다. 서버에서 그려서 공고 전체가 들어 있다.

```bash
curl -sL -A "$UA" "$URL" \
  | perl -0ne 'print $1 if /<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s' \
  | jq -c '[..|objects|select(.queryKey? == ["openings"])][0].state.data[] | {id: .openingId, title, due: .dueDate,
      career: [.openingJobPosition.openingJobPositions[].jobPositionCareer | {careerType, careerFrom, careerTo}],
      group: [.openingJobPosition.openingJobPositions[] | (.workspaceOccupation.occupation // .workspaceJob.job)]}'
```

- API 응답의 `data.hasNext`가 true면 `page`를 올려 더 받는다.
- 같은 `__NEXT_DATA__`의 queries 중 `getCareerBootInfo` 항목에 workspace id가 있다. 찾으면 `registry_updates`로 비고에 남긴다.
- `careerType`은 `EXPERIENCED`, `NEW_COMER`, `NOT_MATTER`이고 `careerFrom`, `careerTo`가 연차다. 상세를 열지 않아도 `min_years`, `max_years`를 채울 수 있다. 비어 있는 회사도 있으니 그때는 상세에서 읽는다.
- `dueDate`가 null이면 상시다.
- 직군 이름은 회사마다 다르다("기술", "개발", "Tech", "Software", "Backend Engineering"). `group` 값을 한 번 훑어보고 개발 직군을 고른다.
- 상세 URL은 `{목록 URL의 origin}/ko/o/{openingId}`. 기술 스택은 상세에서 읽는다.
- 그리팅 홈을 공개하지 않은 회사(오늘의집, 쏘카)는 API가 0건을 준다. 기업별 절의 방법을 쓴다.
- 직군 값이 비어 있는 회사(왓챠)나 직군이 잘게 나뉜 회사가 있다. 그때는 제목으로 거른다.
- 그룹 통합 workspace(HYBE)는 `workspaceDivision`으로 계열사를 거른다. 레지스트리 비고에 값이 있다.
- 다른 직군: 서버 직군 필터가 없어 전체가 온다. 2026-10-12에 받은 `group` 값 중 개발 밖 직군은 카카오페이(workspace 9737) "프로덕트", "디자이너", "마케팅", "비즈니스", "스탭", 카카오모빌리티(14346) "서비스사업", "스탭", 직방(1724) "Business", "Product", "Sales"였다. 카카오페이 "스탭"에는 회계와 컴플라이언스 공고가, "프로덕트"에는 프로덕트 매니저 공고가 있었다. 이름이 회사마다 다르니 `group` 값을 훑어 `role_family`에 맞는 것을 고른다. 카카오페이는 `group`이 비어 있는 포지션도 있어서 제목으로도 본다.

### Greenhouse

공고 URL에 `gh_jid`가 붙어 있으면 Greenhouse다. 인증 없이 받는다.

```bash
curl -s "https://boards-api.greenhouse.io/v1/boards/{token}/jobs" \
  | jq -c '.jobs[] | select(.location.name | test("Seoul|Korea|서울|한국"; "i")) | {id, title, url: .absolute_url, location: .location.name, updated_at}'
```

- 해외 공고가 섞인 회사(쿠팡, 몰로코, 센드버드)는 위처럼 근무지로 거른다.
- 부서 목록은 `/v1/boards/{token}/departments`.
- 상세 본문은 `GET https://boards-api.greenhouse.io/v1/boards/{token}/jobs/{id}`의 `content`(이스케이프된 HTML)다. 연차와 기술은 여기서 읽는다. 연차 필드는 따로 없다.
- 다른 직군: 부서 이름으로 거른다. 2026-10-12 `/departments`에서 한국 근무 공고가 있던 개발 밖 부서는 쿠팡 "Finance", "Customer Service", "Compliance", "Eats Sales & Business", "Eats Finance & Strategy", 몰로코 "MCM Business Development"였다. 센드버드의 한국 공고는 Engineering과 Security and IT뿐이었다.

### Lever

```bash
curl -s "https://api.lever.co/v0/postings/{company}?mode=json" \
  | jq -c '.[] | {id, title: .text, url: .hostedUrl, location: .categories.location, team: .categories.team}'
```

연차는 `descriptionPlain`과 `lists`의 본문에 있다. 마감 필드는 없으므로 `deadline`은 "미기재"다.

다른 직군: `categories.team`으로 거른다. 2026-10-12 응답에서 채널코퍼레이션(`zoyi`)은 "Product / Design", "Sales / Business", "Strategy / Business Ops", "Corporate", 네오위즈는 "Branding & Marketing", "Corporate Operations", "Game Art & Creative", "Global Business"가 있었다.

### recruiter.co.kr

신형(jobflex) 사이트는 목록이 `https://{sub}.recruiter.co.kr/career/jobs`이고 상세가 `/career/jobs/{positionSn}`이다. HTML은 JS로 그려지지만 API는 curl로 받는다.

```bash
curl -s -X POST https://api-recruiter.recruiter.co.kr/position/v1/jobflex \
  -H 'Content-Type: application/json' \
  -H 'prefix: {sub}.recruiter.co.kr' \
  -d '{"pageableRq":{"page":1,"size":50,"sort":["JOBFLEX_SORT"]},"filter":{"keyword":"","tagSnList":[],"jobGroupSnList":[],"careerTypeList":[],"regionSnList":[],"submissionStatusList":[],"openStatusList":[],"resumeLanguageTypeList":[]}}'
```

- `prefix` 헤더에 채용 사이트 호스트명을 넣는다. 커스텀 도메인 회사는 레지스트리 비고에 적힌 호스트명을 쓴다.
- 공고는 `.list[]`, 전체 건수는 `.pagination.totalCount`다.
- `submissionStatusList`는 비워서 보내고, 받은 뒤 `submissionStatus`가 `POST_SUBMISSION`(마감)인 공고를 뺀다. `IN_SUBMISSION`으로 거르면 마감일이 없는 상시 공고(`endDateTime` null)가 빠진다. 컴투스는 서버 필터로 1건이 왔고, 비워서 받은 뒤 거르면 77건 중 65건이 남았다.
- `careerTypeList`도 비워서 보낸다. `CAREER`로 거르면 신입/경력 겸용(`NEW_CAREER`)과 경력 무관(`FIELD_DIFFERENCE`) 공고가 빠진다. 컴투스에서 77건이 46건으로 줄었다. 경력 구분은 응답의 `careerType`으로 보고, 연차 숫자는 제목 괄호("(3년 이상)")나 상세 본문에서 읽는다.
- `tagSnList`로 직군 태그를 고를 수 있다. 태그 번호는 회사마다 다르다. 레지스트리 비고에 있으면 쓴다.
- 다른 직군: `tagSnList`를 빈 배열로 보내면 전체가 온다(2026-10-12 케이뱅크 35건). 태그 번호와 이름은 응답 공고의 `tagList[]`(`tagSn`, `tagName`)에 있으니 한 번 받아 고른다. 케이뱅크 값은 기업별 절에 적었다.
- 상세 본문은 `GET https://api-recruiter.recruiter.co.kr/position/v2/jobflex/{positionSn}`에 같은 `prefix` 헤더를 붙여 받는다. v1 상세 경로는 인증 오류를 준다. 본문이 이미지 한 장인 공고(컴투스)도 있다.
- 구형 사이트(`/app/jobnotice/view?systemKindCode=MRS2&jobnoticeSn=` 형식)는 이 API가 `NotFoundCompany`를 돌려준다. 기업별 절에 따로 적은 방법을 쓰거나 browser-scout에 넘긴다.

### Workday

```bash
curl -s -X POST "https://{tenant}.{wdN}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs" \
  -H 'Content-Type: application/json' \
  -d '{"appliedFacets":{},"limit":20,"offset":0,"searchText":""}'
```

- 응답의 `jobPostings[]`에 `title`, `externalPath`, `locationsText`, `postedOn`이 있다.
- 상세는 같은 호스트의 `/wday/cxs/{tenant}/{site}{externalPath}`를 GET으로 받는다. `jobPostingInfo.jobDescription`이 본문이고 `jobPostingInfo.externalUrl`이 공고 링크다.
- 직군 필터는 `appliedFacets`에 facet id를 넣는다. 기업별 절에 id가 있으면 쓴다.
- 다른 직군: `appliedFacets`를 `{}`로 보내면 전체가 온다. 응답 `facets[]`의 `values[]`에 facet id와 이름(`descriptor`), 건수가 있고 공고가 있는 값만 나온다. 이 목록에서 `role_family`에 맞는 id를 고른다.

### 나인하이어

목록은 `https://{sub}.ninehire.site/`나 커스텀 도메인이고 상세는 `/job_posting/{addressKey}`다. 사이트는 Vercel 보안 확인 때문에 curl이 429를 받는다. API는 curl로 받는다.

```bash
curl -s "https://api.ninehire.com/identity-access/homepage/recruitments?companyId={uuid}&page=1&countPerPage=20" \
  | jq -c '.count, (.results[] | {title: (.externalTitle // .title), key: .addressKey, group: .jobGroup.title,
      career, deadlineType, deadlineValue, status})'
```

- 레지스트리 비고의 `companyId`를 쓴다. `count`가 `countPerPage`보다 크면 `page`를 올린다.
- 연차는 `career.range.over`가 하한이다. `below`가 0이면 상한이 없는 것으로 보고 `max_years`를 null로 둔다. `career.type`이 `irrelevant`면 경력 무관이다.
- 마감은 `deadlineType`(`until_filled`면 상시)과 `deadlineValue`다.
- 직군은 `jobGroup.title`이다. 회사마다 값이 다르다("Tech"가 많다).
- 다른 직군: `jobGroup.title`로 거른다. 2026-10-12 응답에서 카카오스타일은 "PO", "MD", "Marketing", "디지털마케팅", "Design & Contents", "Business", "Corporate Services", 지마켓은 "Brand Marketing", "CRM", "Campaign", "Finance", "정산", "패션/잡화", "풀필먼트운영"이었다. 지마켓처럼 직무 단위로 잘게 나뉜 회사는 제목으로도 본다.
- 공고 링크는 `{채용 사이트 origin}/job_posting/{addressKey}`.
- 상세 페이지(`/job_posting/{addressKey}`)는 curl과 WebFetch 모두 Vercel 보안 확인 429를 받는다. 상세용 JSON API도 없다. 연차는 목록 API의 `career.range`로 채우고, 기술 스택과 자격요건 문장이 필요하면 browser-scout가 상세를 연다.
- `companyId`가 없는 새 기업은 browser-scout가 사이트를 열고 `__NEXT_DATA__`의 `props.pageProps.homepageProps.homepage.companyId`를 읽어 `registry_updates`로 남긴다. 나인하이어 홈이 비공개라 이 값이 없으면 공고 상세 페이지의 `props.pageProps.recruitment.companyId`를 읽는다(에이블리). 그다음부터는 job-scout가 API로 읽는다.

### Workable

```bash
curl -s -X POST https://apply.workable.com/api/v3/accounts/{account}/jobs \
  -H 'Content-Type: application/json' \
  -d '{"query":"","location":[],"department":[],"worktype":[],"remote":[]}'
```

- 공고는 `results[]`이고 한 페이지에 10건이다. 응답에 `nextPage`가 있으면 본문을 `{"token":"{nextPage}"}`로 바꿔 다시 보낸다.
- 직군은 `department`로 거른다. 경력은 상세 `GET https://apply.workable.com/api/v2/accounts/{account}/jobs/{shortcode}`의 `requirements` 본문에서 읽는다.
- 다른 직군: 위처럼 `department`를 빈 배열로 보내면 전체가 온다(2026-10-12 루닛 16건). 루닛의 개발 밖 부서는 "Corporate Affairs", "Medical Affairs", "Product Planning"이었다.

### 플렉스 채용 (careers.team)

```
GET https://flex.team/api-public/v2/recruiting/customers/{customer}/sites/job-descriptions
```

- 공고는 `jobDescriptions[]`다. 직군 이름은 `GET .../customers/{customer}/job-groups`에서 받고 공고의 `customerJobGroupIdHash`와 맞춘다. 직군이 없는 공고도 있으니 제목으로도 본다.
- 경력 필드가 없다. 상세 페이지 `https://{sub}.careers.team/job-descriptions/{jobDescriptionIdHash}`의 `__NEXT_DATA__` 본문에서 읽는다.
- 다른 직군: 직군 이름은 회사가 정한다. 2026-10-12 플렉스는 "Growth"(마케팅, 세일즈, HR 공고)와 "Product" 둘뿐이었고 16건 중 6건은 직군이 비어 있었다. 제목 앞 대괄호(`[Growth]`)로도 거른다.

### 원티드 회사 페이지

자사 채용 페이지가 없거나 비어 있는 회사는 원티드 회사 페이지를 읽는다. 레지스트리 채용 페이지가 `https://www.wanted.co.kr/company/{id}`인 행이다.

```
GET https://www.wanted.co.kr/api/v4/companies/{id}/jobs
```

- 공고는 `data[]`다. `annual_from`, `annual_to`가 연차(`annual_to` 100은 상한 없음), `due_time`이 마감(null이면 상시)이다.
- 개발 직군은 `category_tags[].parent_id`가 518이다.
- 다른 직군: 상위 직군 목록은 `https://www.wanted.co.kr/wdlist/518/669` HTML `__NEXT_DATA__`의 `props.pageProps.tags.category[]`(`id`, `title`, 하위 `tags`)다. 2026-10-12 위메이드(14104) 공고 9건에는 507, 517, 518, 523, 10566이 달려 있었다. 직무군 키와 `parent_id`의 짝은 아래와 같다.
  - `product_manager`: 507 경영/비즈니스(하위 PM/PO, 서비스 기획자)
  - `product_designer`, `visual_designer`: 511 디자인
  - `data_analyst`: 507 경영/비즈니스(하위 데이터 분석가)
  - `marketing`: 523 마케팅/광고
  - `business_development`: 530 영업, 507 경영/비즈니스(하위 사업개발/기획자)
  - `operations`: 510 고객서비스/리테일(하위 CS 매니저, 서비스 운영)
  - `hr`: 517 HR
  - `finance`: 508 금융(하위 회계담당, 재무 담당자), 507 경영/비즈니스(하위 회계/경리)
  - `legal`: 521 법률/법집행기관
  - `merchandiser`: 510 고객서비스/리테일(하위 MD, 리테일 MD), 507 경영/비즈니스(하위 상품기획자(BM))
- 공고 링크는 `https://www.wanted.co.kr/wd/{id}`, `source`는 `career`로 적는다. 이 회사의 공식 채용 창구다.

### 사람인, 캐치 회사 페이지

교보DTS와 사람인은 사람인 회사 페이지, KG이니시스는 캐치 회사 페이지에만 공고를 올린다. 레지스트리 URL의 HTML을 받아 진행 중인 공고만 읽는다. 사람인 공고 링크는 `rec_idx`로 만들고(`references/platforms.md`의 사람인 상세 형식), 캐치는 상세 링크를 그대로 쓴다.

### recruiter.co.kr 구형

목록 경로가 `/app/jobnotice/list`인 사이트(신한DS, 하나금융티아이)는 신형 API가 안 된다.

```bash
curl -s -X POST https://{sub}.recruiter.co.kr/app/jobnotice/list.json \
  --data 'jobnoticeStateCode=10&pageSize=100&currentPage=1'
```

- 공고는 `list[]`이고 `jobnoticeName`, `recruitClassName`, `receiptState`, `applyEndDate.time`(epoch ms), `jobnoticeSn`, `systemKindCode`가 있다.
- `jobnoticeStateCode=10`으로 보내도 접수 마감 공고가 섞인다. `receiptState`로 한 번 더 거른다.
- 상세는 `/app/jobnotice/view?systemKindCode={systemKindCode}&jobnoticeSn={jobnoticeSn}`. 경력과 직군 필드가 없어서 제목과 상세 본문으로 판단한다.

## 기업별

레지스트리 표기 순서대로 적는다. 여기 적힌 요청은 2026-10-07에 응답이 오는 것까지 확인했다.

### 네이버

```
GET https://recruit.navercorp.com/rcrt/loadJobList.do?firstIndex=0&subJobCdArr=1010001,1010002,1010003,1010004,1010005,1010006,1010007,1010008,1010009,1010020&entTypeCdArr=0020&sysCompanyCdArr=&empTypeCdArr=&workAreaCdArr=&sw=
```

- 한 번에 10건이 오고 `firstIndex`를 10씩 올려 다음 페이지를 받는다.
- `subJobCdArr`의 1010xxx가 개발 직군 코드다. 1010001이 Frontend, 1010004가 Backend, 1010005가 AI/ML이다. 프로필 직무에 맞는 코드만 넣어도 된다.
- `entTypeCdArr`가 경력 구분이다. 0010 신입, 0020 경력, 0030 무관. 0020과 0030을 함께 보려면 `0020,0030`.
- 그룹 통합 사이트다. `sysCompanyCdArr`로 계열사를 고른다: KR(네이버), NB(클라우드), SN, NL(랩스), WTKR(웹툰), NFN(파이낸셜), NI. 비우면 전체다.
- 다른 직군: `subJobCdArr=`처럼 값을 비우면 전 직군이 온다(2026-10-12 경력 13건). 코드표는 목록 페이지 `https://recruit.navercorp.com/rcrt/list.do` HTML의 `subJobCdData` 값과 바로 뒤 버튼의 이름이다. 4050001, 4050002, 3030001로 보내 법무와 Business Development 공고 3건을 받았다. 직무군 키와 코드의 짝은 아래와 같다.
  - `product_manager`: 3010001 Product Development
  - `product_designer`: 2010001 Product Design, 2030001 Interactive Design, 2050001 Experience Insight & Planning
  - `visual_designer`: 2020001 Visual Comm. & Brand Design
  - `data_analyst`: 1010009 Data Science, 4005004 User Research & Data Insight
  - `marketing`: 4005001 Marketing, 4005002 Brand Planning, 4005003 Content Creative, 4005005 Marketing 공통
  - `business_development`: 3030001 Business Development, 3060001 어카운트/세일즈
  - `operations`: 3040001 Trust&Safety, 4020002 운영관리, 4100006 운영지원
  - `hr`: 4090001 Human Resources, 4090002 Employee Relations, 4090003 Talent Acquisition, 4090004 Culture Experience, 4090005 HR 공통
  - `finance`: 4010001 재무기획, 4010002 회계, 4010003 세무, 4010004 자금, 4010005 Finance 공통
  - `legal`: 4050001 법무, 4050002 지식재산, 4040001 Risk Management, 4070001 개인정보보호
  - `merchandiser`: 해당 코드 없음

### 네이버웹툰

네이버와 같은 플랫폼이다. `GET https://recruit.webtoonscorp.com/rcrt/loadJobList.do`에 네이버와 같은 파라미터를 쓴다. 네이버 통합 사이트에 `WTKR`로 같은 공고가 올라오므로 fit-reviewer가 합친다.

다른 직군: 네이버 코드가 그대로 통한다. 2026-10-12 `subJobCdArr`를 비우면 경력 12건, 3020001과 3030001로 보내면 Content Development와 Business Development 6건이 왔다. Content Development(3020001)에는 콘텐츠 제휴, 소싱, 콘텐츠 전략 PM 공고가 있었다.

### 카카오

```
GET https://careers.kakao.com/public/api/job-list?part=TECHNOLOGY&company=KAKAO&skillSet=&keyword=&employeeType=&page=1
```

- 응답의 `totalPage`까지 `page`를 올린다.
- `company=ALL`이면 카카오페이, 카카오모빌리티 같은 계열사의 "[공동체]" 공고 일부가 섞인다. 계열사는 각자 사이트를 따로 읽으므로 `KAKAO`로 받는다.
- 경력 필터가 없다. `employeeType`은 고용형태(0 정규직, 2 계약직, 3 인턴)다. 제목의 "(경력)" 표기와 상세 본문으로 연차를 확인한다.
- 다른 직군: `part`를 비우거나 키를 빼면 `TECHNOLOGY`만 온다. 2026-10-12 `company=KAKAO`로 8건이 왔고 같은 응답의 `jobTypeCountDtoList`는 TECHNOLOGY 8, DESIGN 4, BUSINESS_SERVICES 14, STAFF 5였다. 직군마다 `part`를 바꿔 따로 보낸다. 직무군 키와 `part`의 짝은 아래와 같다.
  - `product_designer`, `visual_designer`: `DESIGN`(Product Designer, Interaction Designer, 상품 디자인 공고)
  - `product_manager`, `marketing`, `business_development`, `operations`, `merchandiser`: `BUSINESS_SERVICES`(광고 플랫폼 PM, 상품 MD, 광고주 세일즈, 물류 기획과 운영 공고)
  - `hr`, `finance`, `legal`: `STAFF`(노사 전략, IR 공고)
  - `data_analyst`: `TECHNOLOGY`(Data Scientist, Data Analytics Engineer 공고)

### 카카오뱅크

```bash
curl -s -X POST https://recruit.kakaobank.com/api/recruits \
  -H 'Content-Type: application/json' \
  -d '{"pageNumber":1,"pageSize":50,"receiptFilterType":"ONGOING","recruitClassNames":["Server","Engineering","AI","Data","Security","Core Banking"]}'
```

- 분류 이름 목록은 `GET https://recruit.kakaobank.com/api/recruits/meta/job-categories`에서 받는다. 프론트엔드가 들어갈 분류가 바뀌었으면 여기서 고른다.
- 경력 필터는 없다(`recruitEmployeeTypes`는 고용형태).
- 다른 직군: `recruitClassNames` 키를 빼면 진행 중인 공고 전체가 온다(2026-10-12 26건). `["Service & Biz","Design"]`으로 보내면 10건이 왔다. 분류 이름과 직무군 키의 짝은 아래와 같다.
  - `product_manager`, `business_development`, `marketing`: Service & Biz, Strategy
  - `product_designer`, `visual_designer`: Design
  - `data_analyst`: Data(개발 직군과 함께 쓰는 분류)
  - `operations`: Customer Service
  - `finance`: Finance
  - `legal`: Compliance
  - `hr`: 전용 분류 없음(Management 분류는 오늘 0건이라 내용 미확인)

### 라인플러스

```
GET https://careers.linecorp.com/page-data/ko/jobs/page-data.json
```

- `result.data.allStrapiJobs.edges[].node`에 태국, 대만 등 LINE 계열 전체 공고가 있다. 한국 근무지(`cities[].name`이 "Bundang"이나 "Gwacheon")이고 `job_unit[].name`이 "Engineering"인 것만 쓴다. 회사명으로 거르면 LINE Pay Plus, IPX, LINE studio 같은 한국 법인 공고가 빠지고 LINE Plus의 해외 근무 공고가 들어온다.
- `companies[].name`을 `affiliate`에 넣는다. 예: "IPX".
- 경력 필터는 없다. `employment_type`이 "Full-time (Entry level)"이면 신입 공고다.
- 다른 직군: `job_unit[].name`으로 거른다. 2026-10-12 한국 근무 공고의 개발 밖 값은 "Planning"(10건), "Design"(9건), "Corporate"(8건), "Business & Sales"(4건)였다. 더 잘게 보려면 `job_fields[].name`(Product Management, Product Design, VX Design, Business Development, Sales, Human Resources, Legal 등)을 본다. 이름 앞에 "(Not in use)"가 붙은 값도 공고에 달려 있다.

### 쿠팡

coupang.jobs는 curl에 Cloudflare 403을 준다. Greenhouse 토큰 `coupang`으로 읽고 근무지 "Seoul, South Korea"와 "South Korea"만 쓴다. 전 세계 공고가 600건이 넘으므로 제목 거르기를 먼저 한다. 공고의 `metadata` "Job Level"은 Lv 값이라 연차로 바꾸지 않는다.

다른 직군: Greenhouse 부서 이름으로 거른다. 2026-10-12 한국 공고가 있던 개발 밖 부서는 "Finance", "Customer Service", "Compliance", "Coupang Ads", "Eats Sales & Business", "Eats Finance & Strategy", "Employee Relation" 등이었다. 부서가 사업 단위로도 나뉘어("Coupang Pay"와 "Coupang Pay Tech") 부서만으로 직군이 갈리지 않으니 제목으로도 본다.

### 우아한형제들

```
GET https://career.woowahan.com/w1/recruits?recruitCampaignSeq=0&jobGroupCodes=BA005001&careerTypeCodes=BA003002&page=0&size=50&sort=updateDate,desc
```

- `BA005001`이 Tech 직군이다.
- `careerTypeCodes`: BA003001 신입, BA003002 경력, BA003004 신입/경력. 이 키에 빈 값을 보내면 0건이 오므로 안 쓸 때는 키를 아예 뺀다.
- 응답의 `careerRestrictionMinYears`, `careerRestrictionMaxYears`가 연차다.
- 다른 직군: 직군 필터를 안 쓸 때도 `jobGroupCodes` 키를 아예 뺀다. `jobGroupCodes=`처럼 빈 값을 보내면 0건이 온다. 2026-10-12 키를 빼고 받으면 경력 39건이었다. 여러 직군은 쉼표(`BA005011,BA005012`)와 키 반복 모두 되고 둘 다 4건이 왔다. 코드표는 `GET https://career.woowahan.com/w1/common/common-item/all`에서 `groupCode`가 BA005인 항목(`code`, `text`)이고 `itemUseYn`이 true인 것만 쓴다. 직무군 키와 코드의 짝은 아래와 같다.
  - `product_manager`: BA005005 Product(세부 PM, PO, 서비스기획)
  - `product_designer`, `visual_designer`: BA005012 Creative(세부 디자인, 마케팅, PD, 콘텐츠기획)
  - `marketing`: BA005011 Marketing, BA005012 Creative
  - `business_development`, `operations`, `merchandiser`: BA005010 Business & Sales(세부 사업기획, 영업, MD, 사업운영, 전략), BA005014 파트너 영업
  - `hr`, `finance`, `legal`: BA005013 Corporate(세부 인사, 조직문화, 회계, 경영관리, 법무, 감사)
  - `data_analyst`: 전용 코드 없음(제목으로 거름)

### 비바리퍼블리카

```
GET https://api-public.toss.im/api/v3/ipd-eggnog/career/jobs
```

- `.success` 배열에 Greenhouse 형식으로 토스 계열사 공고 전체가 온다. 링크는 `absolute_url`이다. Greenhouse의 `content` 필드는 없고 본문은 `metadata`의 JD 값에 있다.
- 계열사는 `metadata` 중 이름에 "소속 자회사"가 들어간 항목의 값이다(토스, 토스뱅크, 토스증권, 토스페이먼츠, 토스인슈어런스 등). `affiliate`에 넣는다.
- 직군은 `metadata` 중 이름에 "Job Category"가 들어간 항목의 값(Backend, Frontend, App, ML, Data Engineering, Infra, QA)으로 거른다. 항목 이름 전체는 "커리어 페이지 노출 Job Category 값을 선택해주세요"처럼 바뀔 수 있으니 정확히 일치로 찾지 않는다.
- 다른 직군: 서버 필터가 없어 전체가 온다(2026-10-12 491건). Job Category 값과 직무군 키의 짝은 아래와 같다.
  - `product_manager`: Product Ownership, IT Planning
  - `product_designer`: Product Design, Platform Design, UX
  - `visual_designer`: Brand Design
  - `data_analyst`: Data Analysis
  - `marketing`: Marketing, Contents, PR
  - `business_development`: Sales, Sales Support, Strategy, Corp.dev
  - `operations`: Customer, Customer Service, Customer Support, Product Operations
  - `hr`: HR, Recruiting, Compensation & Benefit, Culture, People System
  - `finance`: Finance, Accounting, IR
  - `legal`: Legal, Compliance, AML, Risk
  - `merchandiser`: 해당 값 없음

### 야놀자

careers.yanolja.co는 소개 페이지이고 공고는 Workday에 있다. 위 Workday 절의 요청을 `tenant=yanolja`, `wdN=wd102`, `site=External_Yanolja`로 보낸다. 개발 직군은 facet `jobFamilyGroup`의 R&D(id `579e0983752b10016538ec752cc70000`)다.

```json
{
	"appliedFacets": { "jobFamilyGroup": ["579e0983752b10016538ec752cc70000"] },
	"limit": 20,
	"offset": 0,
	"searchText": ""
}
```

다른 직군: `appliedFacets`를 `{}`로 보내면 전체가 온다. 2026-10-12에는 전체가 1건(R&D)이라 다른 `jobFamilyGroup` id가 응답 facets에 나오지 않았다. 다른 직군 id는 미확인이니 그때 응답 facets에서 고른다.

### 몰로코

Greenhouse 토큰 `moloco`. 근무지 "Seoul, Korea"만 쓴다.

다른 직군: 부서로 거른다. 2026-10-12 서울 공고 중 개발 밖 부서는 "MCM Business Development"(2건)뿐이었다.

### 센드버드

Greenhouse 토큰 `sendbird`. sendbird.com/careers는 delight.ai/careers로 리다이렉트된다. 부서 Engineering과 근무지 Seoul만 쓴다.

다른 직군: 2026-10-12 서울 공고는 Engineering 3건과 Security and IT 1건뿐이었다. 부서 조건을 빼고 받아 제목으로 거른다.

### 케이뱅크

recruiter.co.kr 신형이다. 위 recruiter.co.kr 절의 요청을 `prefix: kbank.recruiter.co.kr`로 보내고 `tagSnList`에 `[12198]`(Tech)을 넣는다.

다른 직군: `tagSnList`를 비우면 전체가 온다(2026-10-12 35건). 태그는 12214(Biz와 Marketing. 서비스 기획, 마케팅 기획, 금융 상품 공고)가 `product_manager`, `marketing`, `business_development`, 12216(UX, BX, Design. 그래픽 디자이너 공고)이 `product_designer`, `visual_designer`, 12188(Customer. 고객센터 운영, 금융사기 대응 공고)이 `operations`에 맞는다. 12242(Risk)에는 자산건전성 관리와 여신 감리 공고가 있었다. `hr`, `finance`, `legal`에 맞는 태그는 오늘 응답에 없어 미확인이다.

### 뱅크샐러드

```
GET https://www.banksalad.com/proxy/api/greeting/openings
```

부서별로 묶여서 온다. `department`가 "테크"인 묶음을 쓴다. 경력은 공고의 `careerInfo.type`과 `careerInfo.from`으로 판별한다.

다른 직군: `department` 값으로 묶음을 고른다. 2026-10-12 묶음은 "테크" 외에 "제품기획"(4건), "세일즈"(2건), "마케팅", "경영관리", "보험 GA"(각 1건)였다. `product_manager`는 제품기획, `business_development`는 세일즈, `marketing`은 마케팅, `hr`, `finance`, `legal`은 경영관리를 본다.

### 버킷플레이스

그리팅 API가 0건을 준다. 자사 사이트의 Gatsby 데이터를 읽는다.

```
GET https://www.bucketplace.com/page-data/careers/page-data.json
```

`result.data.position.nodes[].frontmatter`가 공고다. 개발은 `teamName`이 "Engineering"인 것이다. 경력 필드가 없으니 상세에서 읽는다.

다른 직군: `teamName`으로 고른다. 2026-10-12 값은 "프로덕트", "디자인", "마케팅", "콘텐츠", "MD", "영업", "영업 전략/운영", "사업 개발/전략", "경영지원", "물류/배송", "O2O 서비스", "글로벌" 등이었다.

### 리디

ridicorp.com/career는 RoundHR 사이트로 이동하고 ridicorp.com은 curl에 Cloudflare 403을 준다. RoundHR API를 쓴다.

```
GET https://api-prod.roundhr.com/api/site/jobs?code=ridi&q[position_group_id_in][]=9159
```

9159가 제품/개발 그룹이다. URL의 대괄호가 curl의 범위 패턴으로 해석되므로 `curl -g`를 붙인다. 경력은 `application_form.career_kind`와 `career_start`다.

다른 직군: `q[position_group_id_in][]`를 빼면 전체가 온다(2026-10-12 16건). 응답 `position_group`에 id와 이름이 있고 오늘은 9152 콘텐츠 비즈니스(7건), 9153 경영지원(7건), 8782 디자인(1건), 9159 제품/개발(1건)이었다.

### 쏘카

그리팅을 쓰지만 공식 API는 api-key 헤더를 요구한다. 자사 목록 페이지의 `__NEXT_DATA__`를 읽는다.

```bash
curl -sL -A "$UA" https://www.socarcorp.kr/careers/jobs \
  | perl -0ne 'print $1 if /<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s' \
  | jq '.props.pageProps.jobList.jsonResult.data'
```

계열사 공고가 함께 있다. 개발은 `job_group_code`가 `JG01`(개발/데이터)이다. 경력은 `career_code`로, `CR01`이 무관이고 `CR02`부터 `CR21`까지가 1년 이상부터 20년 이상이다.

다른 직군: 코드표는 같은 `__NEXT_DATA__`에서 `parent_code_id`가 `JOB_GROUP`인 항목(`code`, `code_name`)이다. 2026-10-12 값은 JG01 개발/데이터, JG02 경영/전략, JG03 디자인, JG04 서비스기획, JG05 사업/운영, JG06 홍보/마케팅, JG07 공통이었다. `product_manager`는 JG04, `product_designer`와 `visual_designer`는 JG03, `marketing`은 JG06, `business_development`와 `operations`, `merchandiser`는 JG05(차량 MD, 사업개발, 운영 공고), `hr`와 `finance`, `legal`은 JG02와 JG07에 맞춘다. 계열사 에이펙스모빌리티의 Product Designer와 Product Manager 공고가 JG01에 들어 있었으니 제목으로도 본다.

### 플렉스

```
GET https://flex.team/api-public/v2/recruiting/customers/65Y06m8XpK/sites/job-descriptions
```

Product 그룹은 `customerJobGroupIdHash`가 `XMV0aJzZBn`이다. 목록에 경력 필드가 없으니 상세에서 읽는다. flex.careers 도메인은 플렉스와 관계없는 주차 도메인이다.

다른 직군: Growth 그룹은 `customerJobGroupIdHash`가 `RWL8JLjzKY`이고 2026-10-12 마케팅, 세일즈, HR 공고 6건이 있었다. 직군이 비어 있는 공고 6건에도 `[Growth]` 공고가 섞여 있어 제목으로도 본다.

### 리멤버앤컴퍼니

별도 자사 채용 사이트가 없고 리멤버 커리어에 회사 페이지가 있다.

```bash
curl -s -X POST https://career-api.rememberapp.co.kr/job_postings/search \
  -H 'Content-Type: application/json' \
  -d '{"page":1,"per":50,"search":{"company_id":663802}}'
```

키는 `company_id`로 보낸다. `companyId`로 보내면 필터가 무시되고 전체 공고가 온다. 경력은 `min_experience`, `max_experience`이고 공고 링크는 `https://career.rememberapp.co.kr/job/posting/{id}`다. `source`는 `career`로 적는다.

### 크래프톤

```bash
curl -sL -A "$UA" "https://www.krafton.com/careers/jobs/?search_department=Tech&search_list_cnt=300"
```

HTML에 공고가 있다. Greenhouse `krafton` 보드에는 일부만 올라오므로 목록은 이 페이지를 읽는다. 경력은 제목의 "(n년 이상)"에 있다. 상세 페이지 본문은 Greenhouse iframe이라, iframe src의 id로 `GET https://boards-api.greenhouse.io/v1/boards/krafton/jobs/{id}`의 `content`를 읽는다.

다른 직군: `search_department`를 빼면 전체가 온다(2026-10-12 183건). 값은 목록 HTML의 `name='department'` 체크박스이고 Art, BusinessService, Data, DevelopmentManagement, GameDesign, ITInfra, ManagementSupporting, QA, Sound, Tech, TechnicalArtist, UXUI다. `BusinessService`로 보내면 22건(PM과 PO, 현지화, 방송 운영 공고)이 왔다. `product_manager`, `marketing`, `business_development`는 BusinessService, `hr`, `finance`, `legal`은 ManagementSupporting, `product_designer`는 UXUI, `visual_designer`는 Art, `data_analyst`는 Data에 맞춘다.

### 넥슨 (browser-scout)

페이지와 API 모두 curl에 Cloudflare 403을 준다. 브라우저로 https://careers.nexon.com/recruit 을 연 뒤, 같은 탭에서 `POST https://career-gateway.nexon.com/career/v1/open/job-posts`를 fetch로 부른다. 본문은 `{"page":1,"size":200}`이고 `{}`로 보내면 10건만 온다.

응답 `list[]`에 `jobPostNo`, `corpName`, `title`, `careerType.description`, `employmentType.description`, `workingArea`, `dday`(비어 있으면 채용 시 마감)가 있다. 상세는 `https://careers.nexon.com/recruit/{jobPostNo}`.

### 엔씨소프트

CSRF 토큰이 필요하다. 쿠키를 저장해 두 번 요청한다.

```bash
jar=$(mktemp)
token=$(curl -s -c "$jar" -A "$UA" https://careers.ncsoft.com/apply/list | perl -ne 'print $1 if /<meta name="_csrf" content=\s*"([^"]+)"/')
curl -s -b "$jar" -A "$UA" -X POST https://careers.ncsoft.com/interface/apply/list \
  -H "X-CSRF-TOKEN: $token" -H 'Accept: application/json' \
  --data 'order_type=ORDER_ETC&order_direction=desc&page=1&pagesize=100&channelCds=A&keywords=&job_group_cd=G031&search_text=&job_type_cd=&companyIds='
```

- `job_group_cd=G031`이 개발, `channelCds=A`가 경력 채용이다.
- 폼 필드를 하나라도 빼면 `resultCode` 990 오류가 온다. 안 쓰는 필드도 빈 값으로 보낸다.
- 공고는 `.result.data.record`, 전체 건수는 `.result.data.record_count`다.
- 다른 직군: `job_group_cd=`처럼 빈 값을 보내면 전체가 온다(2026-10-12 경력 46건). 응답의 `rcutJobGroupCd`와 `jobGroupName`으로 보면 G031 Development 외에 G032 Business(5건), G033 System & Information(2건), G034 Management Supporting(5건)이 있었다. `product_manager`, `marketing`, `business_development`는 G032, `hr`, `finance`, `legal`은 G034에 맞춘다. 아트와 디자인 코드는 오늘 공고가 없어 미확인이다.

### 넷마블

```
GET https://career.netmarble.com/api/v1/apply/announces?page=1&size=1000
```

개발은 `carJobGroupCd`가 `05`(기술/AI), 경력은 `reqTypeCd`가 `90006`이다.

다른 직군: 서버 필터 없이 전체가 오고 `carJobGroupCd`와 `carJobGroupNm`으로 거른다. 2026-10-12 값은 02 게임기획, 03 아트, 04 개발지원, 05 기술/AI, 08 경영지원이었다. `hr`, `finance`, `legal`은 08, 디자인 직무군은 03을 본다. 마케팅과 사업 코드는 오늘 공고가 없어 미확인이다.

### 펄어비스

https://www.pearlabyss.com/ko-KR/Company/Careers/List 의 HTML에 공고가 있다. 쿼리에 `_jobGroupCode=1`(프로그래밍)과 `_workExperienceType=2`(경력)를 붙여 거른다.

다른 직군: `_jobGroupCode=0`이 전체다(2026-10-12 경력 12건). 목록 HTML의 `data-jobgroupcode` 버튼에 코드와 이름, 건수가 있고 공고가 있는 직군만 나온다. 오늘 값은 1 프로그래밍, 4 오디오, 6 게임 서비스, 7 경영지원, 9 기타, 10 개발 지원이었다. `hr`, `finance`, `legal`은 7, `operations`는 6을 본다.

### 대기업 그룹 통합 사이트

삼성, LG, SK, CJ, 한화, 포스코, 신세계, KT, NHN, 현대백화점은 계열사 공고를 그룹 사이트 한 곳에 올린다. 그룹 요청 한 번으로 받은 뒤 계열사 코드나 회사명으로 나눈다. 레지스트리에서 접근이 `group`인 계열사는 이렇게 그룹 행을 읽을 때 함께 기록한다. 응답의 계열사 이름은 `affiliate`에 넣고, `company`는 SKILL.md 5절 규칙대로 정한다.

이 사이트들은 화면이 보내는 파라미터가 하나라도 빠지면 오류나 빈 결과를 준다. 아래 요청의 필드는 빈 값이어도 지우지 않는다.

#### 삼성

```bash
curl -s -A "$UA" -X POST https://www.samsungcareers.com/hr/list.data \
  --data 'currentPageNo=1&intNo=&strVal=&strTxt=&strKey=&strCompany=&strType=B&strOrderBy=&strEntity='
```

- 응답은 JSON이 아니라 HTML 조각이다. `<li>`마다 `p.company`(계열사), `h3.title`, `span.period`(접수 기간)가 있다.
- `strType`: A 신입, B 경력, C 인턴. 직군 필터는 없고 `strTxt` 키워드만 된다.
- `strCompany`로 계열사를 고를 수 있다: 삼성SDS `C60,C60`, 삼성전자 DX `C10CAA,C10`, DS `C10CAH,C10`, 삼성카드 `E31,E31`. 비우면 전체다.
- 공고 링크는 `<a data-value="23,283">`의 숫자에서 쉼표를 뺀 값으로 `https://www.samsungcareers.com/hr/?no=23283`이다.
- 상세 본문은 `GET https://www.samsungcareers.com/recruit/detail.data?seqno={no}&strCode=`의 `data.items[]`(`titleKr`, `qlfctKr` 자격요건, `favorKr` 우대사항, `workPlaceKr`)다. 상세 페이지 HTML에는 본문이 없다.
- 공채 시즌에 몰려 올라온다.
- 다른 직군: 코드표 없음, 필터 빼고 받음. 직군 필터가 없어 위 요청 그대로 전 직군이 온다. 제목 괄호 안에 직무가 나열되므로("경력사원 채용(수입육 축산영업, 단체식 조리사, 단체식 영양사, E커머스 서비스 기획)", "경력사원 채용(AX/PI, 경영지원, CISO)", 2026-10-12) 괄호 안 직무명으로 거르고, 필요하면 `strTxt` 키워드를 쓴다.

#### LG

```bash
curl -s -X POST https://api.careers.lg.com/rmk/job/retrieveJobNoticesList \
  -H 'Content-Type: application/json' \
  -d '{"careerList":["B"],"companyCodeList":[],"jobGroupList":["H","G"],"desireLocList":[],"recDate":"CREATION_DATE","order":"DESC"}'
```

- 페이징 없이 전체가 온다. `careerList` B는 경력이고 신입/경력 겸용(D)도 함께 온다.
- `jobGroupList`: H IT서비스, G 연구/개발.
- `companyCodeList`: LG CNS `CNS`, LG유플러스 `LGU`. 코드표는 같은 호스트의 `POST /rmk/job/retrieveJobNotices`에 `{}`를 보내 받는다.
- 상세는 `POST https://api.careers.lg.com/rmk/job/retrieveJobNoticesDetail`에 `{"jobNoticeId": id}`. `data.jobNoticesDetail.recList[]`에 `mainTask`, `requiredItem`, `preferredItem`이 있다. 공고 링크는 `https://careers.lg.com/apply/detail?id={id}`.
- 다른 직군: `jobGroupList`를 `[]`로 보내면 전 직군이 온다(2026-10-12 경력 70건, H와 G만 넣으면 39건). 코드표는 `retrieveJobNotices` 응답의 `data.jobGroupList[]`(`codeValue`, `codeDesc`, 세부 직무 `codeDtlList`)다. 요청은 대분류 코드로 보낸다. 세부 직무 코드로 거르는 키는 확인하지 않았다. 직무군 키와 코드의 짝은 아래와 같다.
  - `product_manager`: E 상품/서비스기획(세부 E05 서비스기획, E09 플랫폼기획)
  - `product_designer`, `visual_designer`: B 디자인(세부 B03 UI, B04 UX, B18 GUI, B09 시각디자인, B10 브랜드디자인)
  - `data_analyst`: 전용 대분류 없음(세부 직무 H15 데이터, G14 빅데이터, C15 마케팅 Analytics)
  - `marketing`, `business_development`: C 영업/마케팅
  - `operations`: I 고객서비스
  - `hr`, `finance`, `legal`: A 경영지원(세부 A05 HR, A02 재경, A15 세무, A10 법무)
  - `merchandiser`: E 상품/서비스기획(세부 E01 상품기획)

#### SK

```bash
curl -s -A "$UA" -H 'Accept-Language: ko-KR' -X POST https://www.skcareers.com/Recruit/GetRecruitList \
  --data-urlencode 'sort=1' --data-urlencode 'searchText=' --data-urlencode 'corpCode=' \
  --data-urlencode 'jobRole=' --data-urlencode 'recruitType=["200002"]' \
  --data-urlencode 'workingType=' --data-urlencode 'workingRegion='
```

- `sort`가 비면 오류 페이지가 온다. `Accept-Language: ko-KR`가 없으면 회사명이 영어로 온다.
- `recruitType`은 JSON 배열 문자열이다: 200001 신입, 200002 경력, 200003 인턴.
- `jobRole`: 176 Frontend 개발, 170 Backend 개발. 코드표는 `POST /Recruit/GetAutocomplete`에 `type=JobRole`, 회사 코드는 `type=CorpCode`.
- `corpCode`: SK텔레콤 10005, SK AX 10018("SK주식회사(AX)"로 표기). 응답의 `corpName`으로도 나눌 수 있다.
- 응답에 링크가 없다. 공고 링크는 `https://www.skcareers.com/Recruit/Detail/{noticeID}`(예: R262168)이고 이 상세 HTML은 서버에서 그려져 curl로 읽힌다.
- 다른 직군: `jobRole`을 비우면 전 직군이 온다(2026-10-12 경력 83건). `jobRole`은 코드 하나만 받는다. `218`(법무)은 2건이 왔지만 쉼표로 묶은 `218,239`는 0건이었고, JSON 배열 `["218"]`은 필터가 무시되어 83건이 왔다. 또 `211`(마케팅)은 0건이었는데 같은 날 전체 응답에는 `jobRole`이 "마케팅"뿐인 공고가 1건 있었다. 대분류만 달린 공고는 세부 코드로 잡히지 않으니, 필터 없이 받고 응답의 `jobRole` 문자열("법무/법무", "재무/회계", "사업개발/사업개발"처럼 대분류/세부)로 거르는 편이 빠지는 공고가 적다. 코드표 `type=JobRole`(459개)에서 고른 짝은 아래와 같다.
  - `product_manager`: 203 서비스 기획/운영, 201 UX/UI 기획, 557 Product Planning
  - `product_designer`: 202 UX/UI 디자인, 209 GUI 디자인
  - `visual_designer`: 208 BX 디자인, 210 그래픽 디자인
  - `data_analyst`: 173 Data Science, 174 Data 분석/개발
  - `marketing`: 211 마케팅, 246 전략마케팅, 556 Product Marketing
  - `business_development`: 221 사업개발, 230 영업, 228 B2B 영업, 229 B2C 영업
  - `operations`: 224 사업운영, 442 서비스 운영 지원
  - `hr`: 645 HR, 198 HRM, 197 HRD
  - `finance`: 238 재무, 239 회계, 236 세무
  - `legal`: 218 법무
  - `merchandiser`: 204 상품기획

#### 현대자동차

그룹 통합 사이트가 없다. 계열사마다 따로 읽는다. 현대자동차는 아래 API로 받는다. 목록 HTML은 대기열(NetFunnel)을 거쳐야 열리지만 API는 바로 응답한다.

```
GET https://talent.hyundai.com/api/rec/AP-HM-FO-02700?hgrCd=1&lang=ko&page=1&pageblock=100&searchSectorList=N2&searchOccupList=211
```

`searchSectorList=N2`가 경력, `searchOccupList=211`이 IT 직종이다. SW Development만 보려면 `searchFieldList=K0019`를 더한다. 공고 링크는 `https://talent.hyundai.com/apply/applyView.hc?recuYy={recuYy}&recuType={recuType}&recuCls={recuCls}`다. 상세 API(`AP-HM-FO-02800`)는 curl에 400을 주므로 본문이 필요하면 browser-scout가 연다.

다른 직군: `searchOccupList`를 빼면 전 직종이 온다(2026-10-12 경력 39건). 직종 값은 응답의 `secCode`와 `secCodeNm`이고 세부 분야는 `fldCode`와 `fldCodeNm`이다. 코드표 API는 찾지 못했다. 오늘 나온 직종은 07 디자인, 211 IT, 40 연구개발, 104 생산/제조, J0001 사업/기획이었고 `searchOccupList=07,J0001`(쉼표)과 키 반복 모두 5건이 왔다. `product_manager`와 `business_development`는 J0001(세부 경영전략), 디자인 직무군은 07을 본다. 211 IT 안에도 세부 분야 K0018 Service Planning이 있다. 마케팅, 영업, 인사, 재무 코드는 오늘 공고가 없어 미확인이다.

#### 롯데

https://recruit.lotte.co.kr/apply/announcement?tab=career 의 HTML에 공고 카드가 있다.

- 카드는 `ul.job-card-list li`다. 회사명 `div.cmp-name`, 제목과 링크 `div.card-tit a`(href `/apply/announcement/detail/{id}`), 신입/경력 `span.ico-bage-anncmtype`, 기간 `p.date`.
- 회사는 `compcd`로 거른다: 롯데이노베이트 30007, 롯데e커머스(롯데ON) 40013. 여러 값은 키를 반복해 붙인다.
- 직무 `jobcd`: 0101 AI, 0103 IT 기획, 0107 IT 보안, 0108 UI/UX. 다만 제목이 "경력사원 채용"뿐인 계열사 공고 안에 프런트엔드 직무가 들어 있는 경우가 있다(캐논코리아 0501 연구개발). IT 코드로만 거르지 말고 경력 공고는 상세의 직무 목록까지 본다.
- 다른 직군: `jobcd` 없이 받으면 전 직무가 온다(2026-10-12 경력 탭 10건). 직무 체크박스 값(`회사코드,직무코드`)은 지금 공고가 있는 직무만 화면에 나온다. 오늘 값은 0103 IT 기획, 0108 UI/UX, 0601 영업, 0602 영업관리, 0701 경영지원, 0801 디자인 등이었고 `jobcd=0701&jobcd=0801`로 보내 5건을 받았다. `product_manager`는 0103, 디자인 직무군은 0108과 0801, `business_development`는 0601과 0602, `hr`, `finance`, `legal`은 0701에 맞춘다. 마케팅과 MD 코드는 오늘 화면에 없어 미확인이다.

#### CJ

```bash
curl -s -A "$UA" -X POST https://recruit.cj.net/recruit/ko/recruit/recruit/searchNewGonggoList.fo \
  --data 'schArea=Y&pageVal=1&pageIndex=300&orderDesc=1&arrRecBu=&arrGubun=B'
```

- 공고는 `ds_newRecruitList`에 있다. `arrGubun` A 신입, B 경력.
- `arrRecBu`로 회사를 고른다: CJ올리브네트웍스 `E10`. 비우면 전체다.
- 직무 코드는 확인하지 못했다. 응답의 `job_cd_nm`으로 거른다.
- 다른 직군: 코드표 없음, 필터 빼고 받음. 위 요청에 직무 필터가 없어 전 직무가 온다(2026-10-12 경력 137건). `job_cd_nm`의 개발 밖 값 예시는 서비스기획, 프로덕트 기획, 그래픽디자인, 디자인, Data Analyst, 브랜드마케팅, 디지털 마케팅, 영업, 사업개발, 서비스운영, 인사(채용), 재무/회계, 법무(변호사), 상품기획, 아티스트 MD, 축산MD다. 응답의 `job_family`는 계열사마다 쓰는 법이 달라서(디자인 공고가 영업, 마케팅 공고와 같은 S에 들어 있다) 직군 판단에 쓰지 않는다.

#### KT

```
GET https://recruit.kt.com/api/recruit?currentPage=1&pageSize=100&isInProgress=true&isContainsContents=false
```

- 공고는 `data[]`이고 kt cloud, BC카드 등 KT그룹 계열사 공고가 함께 온다. 계열사는 `company`로 나눈다.
- `isInProgress=true`로 보내도 마감 공고가 섞인다. `isTimeOver`가 false인 것만 쓴다.
- 서버 직군 필터가 없다. `recruitClassName`(경력, 신입, 계약직)과 `recruitSectorList[].recruitSectorName`, 제목으로 거른다.
- 마감은 `receiveEndDatetime`, 링크는 `recruitNoticeUrl`이다.
- `isContainsContents=true`로 보내면 `contents`에 상세 본문 HTML이 함께 온다. 상세 페이지는 JS로 그려져서 이 방법으로 경력 요건을 읽는다. 본문이 이미지 한 장인 공고도 있다.
- 다른 직군: 코드표 없음, 필터 빼고 받음. `recruitSectorList[].recruitSectorName`의 개발 밖 값은 "마케팅-미디어플래너", "마케팅-매체관리", "B2C영업", "경영기획-IR/공시", "Biz서비스운영-서울"처럼 직무 뒤에 세부 직무나 지역이 붙는다(2026-10-12 진행 중 24건). 하이픈 앞부분으로 거른다.

#### 한화

```bash
curl -s -A "$UA" -X POST https://hwadm.hanwhain.com/new-backend/portal/api/rcRecruit/search-rcrt \
  -H 'Content-Type: application/json' \
  -d '{"langCd":"KO","rtCarrYn":"Y","rjSeqList":[29],"sdSeqList":[],"page":0,"size":100}'
```

- `rjSeqList`: 29 IT, 30 R&D. 코드표는 `POST .../rcRecruit/search-rcrt-job`.
- `sdSeqList`로 계열사를 고른다: 한화시스템/ICT 215. 코드표는 `POST .../rcRecruit/search-sbsd`.
- 계열사 코드: 한화시스템 ICT 215, 방산 328, 한화생명 201.
- 공고는 `data.list[]`(`rtSeq`, `sdNm`, `rtNm`, `rtAcptEndDttm`), 다음 페이지는 `data.hasNext`다. 상세는 `https://www.hanwhain.com/portal/apply/recruit/detail?rtSeq={rtSeq}`.
- 상세 본문은 `POST https://hwadm.hanwhain.com/new-backend/portal/api/rcRecruit/get-rcrt`에 `{"rtSeq":N,"hidnKey":null,"langCd":"ko"}`. 직무별 자격요건은 `data.item.unitDt[].ruDtlJob`에 있고, 일부 공고는 `rtMdeCont`의 이미지나 외부 링크다.
- 반드시 hwadm 백엔드 호스트로 보낸다. www.hanwhain.com 쪽 `/api/...`는 405다.
- `rtCarrYn=Y`로 거르면 계약직도 섞인다. 고용형태를 확인한다.
- 다른 직군: `rjSeqList`를 `[]`로 보내면 전 직무가 온다(2026-10-12 경력 72건). 코드표 `search-rcrt-job` 응답 `data.list[]`의 `value`가 1레벨 코드이고 `subJobs[]`에 세부 직무가 있다. 직무군 키와 코드의 짝은 아래와 같다.
  - `marketing`, `business_development`, `merchandiser`: 33 영업/마케팅(세부 마케팅, 국내영업, 해외영업, 영업관리, MD/Buyer)
  - `product_designer`, `visual_designer`: 33 영업/마케팅의 세부 직무 디자인
  - `hr`, `finance`, `legal`: 34 경영지원(세부 인사, 재경/재무, 법무, 감사, 기획, 홍보), 28 기타(세부 인사, 재무, 법무)
  - `finance`(금융 계열사): 32 금융/자산운용(세부 심사, 리스크관리, 자산운용)
  - `operations`: 34 경영지원과 28 기타의 세부 직무 CS
  - `product_manager`, `data_analyst`: 전용 코드 없음(29 IT, 34 경영지원의 세부 기획과 통계)

#### 포스코

```bash
curl -s -m 60 -A "$UA" 'https://recruit.posco.com/h22a01-recruit/H22A1000/list?rowCount=100&pageSize=100&currPage=1&offset=0&SEARCH_TYPE=2&SEARCH_ORDER=s1'
```

공고는 `recuList`에 있다. `SEARCH_TYPE` 1 신입, 2 경력, 3 연구원. 회사 필터가 없어서 `COMPANY_NAME`으로 포스코DX를 고른다. 응답이 느리니 타임아웃을 60초로 둔다.

#### 신세계

```
GET https://job.shinsegae.com/api/rcrut?coCd=IC0&rcrutSeCd=11&dutySeCd=AA00&includeFixPstgYn=Y
```

`coCd` IC0이 신세계아이앤씨, `rcrutSeCd` 11이 경력, `dutySeCd` AA00이 IT/디지털이다. 배열 파라미터는 키를 반복해서 보낸다. 코드표는 `/api/rcrut/coPopup`, `/api/rcrut/dutyPopup`. SSG닷컴 개발 공고는 이 사이트가 아니라 그리팅에 있다. 상세는 `GET https://job.shinsegae.com/api/rcrut/{pbancBscNo}`의 `body.rcrtSectCn`이고 공고 링크는 `https://job.shinsegae.com/rcrut/detail/{pbancBscNo}`다.

다른 직군: `dutySeCd`와 `coCd`를 빼면 전 계열사의 전 직무가 온다(2026-10-12 경력 29건). `/api/rcrut/dutyPopup`의 직무 코드는 AA00 IT/디지털, AB00 건축/시설/안전, AC00 경영지원, AD00 매장/서비스, AE00 부동산/사업개발, AF00 상품개발/MD, AG00 영업/마케팅이다. `marketing`과 `business_development`는 AG00(사업개발은 AE00도), `merchandiser`는 AF00, `operations`는 AD00, `hr`, `finance`, `legal`은 AC00에 맞춘다. 기획과 디자인 전용 코드는 없다. 키를 반복한 `dutySeCd=AF00&dutySeCd=AG00`으로 4건(디자인관리, 여행상품 기획, 영업 공고)을 받았다.

### 포티투닷

Ashby 공개 API로 전체 공고와 본문을 받는다.

```
GET https://api.ashbyhq.com/posting-api/job-board/42dot
```

공고는 `jobs[]`이고 `title`, `department`, `employmentType`, `location`, `jobUrl`, `descriptionPlain`이 있다. 경력 요건은 `descriptionPlain`에서 읽는다.

다른 직군: `department`로 거른다. 2026-10-12 값은 ENGINEERING 58건 외에 PRODUCT 20건(Product Manager, Technical Program Manager), CORPORATE 10건(전략, 재무, 법무, 시설), BUSINESS 2건(Brand Designer, Product Planning Manager), No Department 3건(HR, 채용)이었다.

### NHN

```
GET https://careers.nhn.com/v1/job-postings?page=0&size=100
```

- 공고는 `.result[]`, 전체 건수는 `.paging.totalSize`다. 기본 size가 30이라 100을 넣는다.
- 계열사는 `.corporation.name`으로 나눈다. 특정 계열사만 받으려면 `corporationId`를 붙인다(NHN 3616135421038421042, NHN Cloud 3647229949742220183, 목록은 `GET /v1/corporations`).
- 게시 중인 공고만 쓴다. `postingYn`이 Y이고 `finishYn`이 N이어야 한다. 마감일(`postingEndDatetime`)이 2999년이어도 게시가 내려간 공고가 있다. 상세 API는 내려간 공고도 응답하므로 상세로 확인할 때도 두 값을 본다.
- 개발 직군은 `jobGroupId=3645799730550663017`(Tech). 경력은 `.careerType.cd`(B003 경력, B002 신입, B001 무관). 마감은 `postingEndDatetime`.
- 다른 직군: `jobGroupId`를 빼면 전 직군이 온다(2026-10-12 67건). 직군 id와 이름은 공고의 `jobSeries[].jobGroup`에 있다(`GET /v1/job-groups`는 404). 오늘 공고에서 모은 값은 Business `3645799730895408146`(세부 Business, Consulting, Contents, Marketing, Sales, Service), Corporate `3645799730926240304`(세부 Finance, HR, Legal, 정보보안), Game `3645799730924223196`(세부 Game Business)이다. Business로 보내면 24건이 왔다. `product_manager`, `marketing`, `business_development`, `operations`는 Business, `hr`, `finance`, `legal`은 Corporate에 맞춘다. 디자인 직군은 오늘 공고가 없어 미확인이다.
- 공고 링크는 `https://careers.nhn.com/recruits/{id}`. 목록의 `jobPostingContentsItems`는 null이라 자격요건은 `GET https://careers.nhn.com/v1/job-postings/{id}`의 `result.jobPostingContentsItems`에서 읽는다. NHN KCP는 이 사이트에 없다.

### 현대백화점그룹 (현대홈쇼핑)

쿠키와 CSRF 토큰이 필요하다.

```bash
jar=$(mktemp)
curl -s -c "$jar" -A "$UA" https://recruit.ehyundai.com/recruit-info/announcement/list.nhd > /dev/null
token=$(awk '$6=="XSRF-TOKEN"{print $7}' "$jar")
curl -s -b "$jar" -A "$UA" -X POST https://recruit.ehyundai.com/recruit-info/announcement/selectHireAnnouncementList.nhd \
  -H 'X-Requested-With: XMLHttpRequest' -H "X-XSRF-TOKEN: $token" \
  --data "pageIndex=1&pageRowSize=5&listRowSize=50&totCnt=119&hireId=&regCoCd=&hireGbCd=&odtmYn=&notiGbCd=&_csrf=$token&searchStr=&applYn=Y&coCd=HDHOME&sortType=01"
```

- `sortType`은 `01`이어야 한다. 비거나 `1`이면 500이다.
- 응답은 HTML 조각이다. 카드마다 회사명, 공고명, 신입/경력 라벨, 기간, `#직무` 태그가 있다.
- IT 직군은 `jobCd=JOB_CD_001`(IT/디지털)로 보인다. 요청으로는 확인하지 않았으니 결과가 비면 직무 태그로 거른다.
- 다른 직군: 위 요청에는 직무 키가 없어 전 직무가 온다. 목록 페이지 HTML의 `name="jobCd"` 체크박스 값은 JOB_CD_001 IT/디지털, JOB_CD_002 경영지원, JOB_CD_003 디자인, JOB_CD_007 서비스/CS, JOB_CD_011 영업/마케팅, JOB_CD_012 전략/기획 등이다(세부 직무는 `dtlJobCd`). 2026-10-12 `coCd`를 비워 그룹 전체를 받았을 때 카드 태그는 #영업/마케팅 14, #디자인 13, #경영지원 7, #IT/디지털 3, #전략/기획 2였다. `jobCd`를 요청에 넣어 보지는 않았으니 카드의 `#직무` 태그로 거른다.

### 시프트업

https://shiftup.co.kr/recruit/recruit.php 의 HTML에 마감 공고까지 들어 있다. `<span class='status ing'>`가 붙은 공고만 쓴다. 제목은 바로 뒤 `<h4>`, 이어지는 `<ul>`의 두 번째 `<li>`가 경력("3년 이상", "무관")이다. 직군 필드가 없어 제목으로 거른다.

### SOOP

https://recruit.sooplive.com/recruit_list.php 의 HTML에서 공고 하나는 `recruit_list_sub.php?...sub_idx={id}` 링크 블록이다. 제목은 `<strong>`, 직군은 `<dt>직군</dt><dd>`, 경력은 `<dt>채용 유형</dt><dd>`, 회사는 `<dt>회사정보</dt><dd>`다. 숲이스포츠 같은 계열사 공고가 섞이므로 회사로 거른다.

### 더존비즈온

```
GET https://recruit.douzone.com/api/rec-post/list?keyword=
```

최상위가 배열이고 마감 공고까지 온다. `end_dt`(YYYYMMDD)가 오늘 이후인 것만 쓴다. 제목은 `pblancsj_dc`, 공고번호는 `pblanc_no`. 직군과 경력 필드가 없어서 제목 앞 대괄호(`[AI 개발]`)와 "경력" 표기로 거른다. 공고 링크는 `https://recruit.douzone.com/post/{company_cd}/{pblanc_no}`다. 본문은 텍스트가 없고 이미지뿐이다(`GET https://recruit.douzone.com/api/rec-post/detail/img-list?company_cd={company_cd}&pblanc_no={pblanc_no}`의 `file_atch_blob`이 base64 PNG).

### 가비아

```
GET https://recruit-api.gabiaoffice.hiworks.com/v1/career-site/offices/1/announces
```

공고는 `data[]`(`announce_name`, `experience`, `apply_finish_date` null이면 상시, `category_position[].full_category_json`). 연차는 상세 `GET .../announces/{announce_id}`의 `description`에 있다. 공고 링크는 `https://recruit.gabia.com/recruit/view/{announce_id}`.

### 현대모비스

https://careers.mobis.com/jobs 의 HTML에 진행 중인 공고만 있다. 공고는 `a.job-item[href="/jobs-view?seq={seq}"]`, 제목 `p.tit`, 경력 구분 `p.career`. `div.info-wrap02 > p`가 순서대로 사업부, 직군, 세부 직무, 근무지이고 개발 직군은 "SW/로직"이다.

다른 직군: 같은 직군 값으로 거른다. 2026-10-12 값은 SW/로직, HW, 공통R&D, 재경이었다.

### 크림

네이버와 같은 채용 플랫폼이다. 네이버 절의 요청을 `https://recruit.kreamcorp.com/rcrt/loadJobList.do`로 보낸다. `subJobCdArr` 1010001 Frontend, 1010002 Android, 1010003 iOS, 1010004 Backend. 경력은 `entTypeCd`(0010 신입, 0020 경력)뿐이라 연차는 상세 `jobDetailLink`에서 읽는다.

다른 직군: `subJobCdArr`를 비우면 전체가 온다(2026-10-12 경력 9건). 네이버 코드가 그대로 통해서 3030001(Business Development)과 4010001(재무기획)로 보내 3건을 받았다. 네이버 절의 짝을 쓴다.

### 교보생명

```bash
curl -s -X POST https://career.kyobo.co.kr/home -H 'ajax: true' \
  --data 'S_DSCLASS=biz.rem.apply.recruit.Apply_list&S_DSMETHOD=search01&S_PAGE_NO=1&S_PAGE_CNT=1&S_TAB=tab_all&S_RE_CLASS=003&S_FORWARD=xsheetResultXML'
```

응답은 XML이다. 행은 `<DATA><TR>`, 열 순서는 `<HTR>`(TITLE, COM_NM, RE_CLASS, RCP_END_YMD, STATUS, NOTI_SEQ_NO 등). `S_RE_CLASS` 003이 경력이다. 계열사 공고가 `COM_NM`으로 섞일 수 있다.

### 한국신용데이터

```
GET https://cdn.contentful.com/spaces/4io3pho3xfqe/environments/master/entries?access_token=gJE2-YuLGf3n7ImhzpEL1sbHr5qiG1z0Rcua580HvAo&content_type=recruit&limit=100
```

사이트 JS에 들어 있는 공개 읽기 토큰이다. 공고는 `items[].fields`(title, url은 그리팅 상세). Engineering 분류 id는 `5ooG5CtfKxmOTd8s5y68KI`이고 `&fields.category.sys.id=`로 거른다. 경력은 그리팅 상세 HTML의 `__NEXT_DATA__`에서 읽는다.

다른 직군: `fields.category.sys.id`를 빼면 전체가 온다(2026-10-12 8건). 분류 표는 같은 토큰으로 `content_type=job_category`를 받으면 나온다. `product_manager`는 Product `4TEQi1SA9NPPB7zKQaCvO3`, 디자인 직무군은 Design `5wMKFsjLrAMvkdFbMTGaIW`, `data_analyst`는 Data `z0C7zHRrFOaP0a682wdwM`, `marketing`은 Growth/Marketing `205rJvmpnM5DI2ZDtNM24R`, `business_development`는 Business `7LJM4rgqtXRsfI0YY8ABCH`와 Strategy `74yCPztVGMKklgi0YTudz9`, `hr`와 `finance`, `legal`은 Corporate `2WMteppMoB2TUKcKV3wGzS`다.

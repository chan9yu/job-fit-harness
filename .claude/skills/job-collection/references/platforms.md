# 채용 플랫폼과 ATS 탐색

플랫폼 배치(`platforms`)와 browser-scout가 읽는다. 2026-10-07에 "프론트엔드", 경력 5년으로 직접 요청해 확인한 방법이다. 응답 구조가 바뀌어 실패하면 이 파일을 고친다.

## 목차

- 공통 규칙
- 직무 코드표
- 원티드, 리멤버, 사람인, 직행, 점핏, 잡코리아, 링크드인, 캐치 (job-scout)
- 잡플래닛 (browser-scout)
- ATS 검색으로 레지스트리 밖 기업 찾기
- 발굴 모드

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

## 직무 코드표

2026-10-12에 코드마다 경력 5년(점핏은 연차 없이)으로 목록을 받아 확인했다. 괄호 안 숫자는 받은 공고 앞쪽 20건(그보다 적으면 전부) 중 제목에 그 직무를 가리키는 말이 들어간 수다. 프론트엔드면 "프론트", "Frontend", "React" 같은 말을 셌다.

정보보안과 게임 개발, 개발 밖 직군 행, 캐치와 랠릿 열은 같은 날 따로 받아 `.claude/skills/job-hunt/scripts/prefilter.py`의 `ROLE_FAMILIES` 단어로 셌다. 요청은 발굴 모드 절의 플랫폼별 요청에서 페이지 크기만 20으로 줄였고 점핏은 연차 없이 받았다. 랠릿은 `jobLevel=MIDDLE,IRRELEVANT`로 받았고, 캐치는 캐치 절 요청에 `JobCode`를 넣어 연차 숫자 없이 받았다. 세는 단어가 달라서 랠릿 열의 숫자는 발굴 모드 랠릿 절의 숫자와 다르다.

행은 프로필 `role_family`로 찾는다. 이 표에 코드가 있으면 키워드 검색 대신 코드를 쓴다. 플랫폼 절에 프론트엔드가 아니면 키워드 검색을 쓰라고 적힌 곳도 이 표가 우선한다. 키워드는 공고 본문까지 맞아서 다른 직무가 더 섞인다. 점핏에서 `keyword=프론트엔드`는 430건, `jobCategory=2`는 49건이었다.

칸에 코드가 둘이면 프로필의 세부 직무(퍼포먼스 마케팅인지 브랜드 마케팅인지)에 가까운 코드를 고른다. 둘 다 맞으면 코드마다 따로 받는다. 한 요청에 코드 둘을 넣는 방법은 확인하지 않았다.

공고 하나에 직무 코드를 여러 개 붙일 수 있는 플랫폼이 많아서 코드로 받아도 첫 공고부터 다른 직무가 나온다. 잡코리아 1000230의 첫 공고는 RPA 개발이었고 사람인 92의 첫 공고는 서치펌이 올린 반도체 공고였다. 코드로 받은 결과도 SKILL.md 3절대로 제목으로 거른다.

| 직무                                      | 원티드 `tag_type_ids`      | 점핏 `jobCategory` | 리멤버 `job_category_ids` | 사람인 `cat_kewd`          | 직행 `depthTwos`                                 | 잡코리아 `duty`                  | 캐치 `JobCode`                 | 랠릿 `job`                                                 | 잡플래닛 `occupation_level2` |
| ----------------------------------------- | -------------------------- | ------------------ | ------------------------- | -------------------------- | ------------------------------------------------ | -------------------------------- | ------------------------------ | ---------------------------------------------------------- | ---------------------------- |
| 프론트엔드 (`frontend`)                   | 669 (15/20)                | 2 (8/16)           | 311 (11/20)               | 92 (6/20)                  | 프론트엔드 (15/20)                               | 1000230 (11/20)                  | 060108 (4/20)                  | FRONTEND_DEVELOPER (11/20)                                 | 11905 (맞은 수 미확인)       |
| 백엔드 (`backend`)                        | 872 (15/20)                | 1 (9/16)           | 310 (11/20)               | 84 (9/20)                  | 서버_백엔드 (12/20)                              | 1000229 (7/20)                   | 060406 (5/20)                  | BACKEND_DEVELOPER (12/20)                                  | 미확인                       |
| 풀스택 (`fullstack`)                      | 없음                       | 3 (9/16)           | 312 (5/20)                | 2232 (8/20)                | 웹풀스택 (8/20)                                  | 없음                             | 없음                           | 없음                                                       | 미확인                       |
| 안드로이드 (`android`)                    | 677 (16/20)                | 4 (2/5)            | 314 (14/20)               | 195 (7/20)                 | 안드로이드 (17/20)                               | 1000232 (6/20)                   | 060205 (3/4)                   | ANDROID_DEVELOPER (9/16)                                   | 미확인                       |
| iOS (`ios`)                               | 678 (13/20)                | 16 (4/9)           | 313 (12/20)               | 234 (8/20)                 | iOS (14/20)                                      | 1000232와 같다                   | 060203 (1/6)                   | IOS_DEVELOPER (4/10)                                       | 미확인                       |
| 크로스플랫폼 앱 (`crossplatform`)         | 10111 (8/20)               | 18 (7/11)          | 315 (5/16)                | 2255 (5/11)                | 크로스플랫폼 (9/20)                              | 1000232와 같다                   | 060206 (0/5)                   | CROSS_PLATFORM_DEVELOPER (5/20)                            | 미확인                       |
| 데이터 엔지니어 (`data_engineer`)         | 655 (14/20)                | 19 (5/16)          | 343 (13/20)               | 83 (5/20)                  | 데이터엔지니어 (16/20)                           | 1000236 (15/20)                  | 060502 (0/20)                  | DATA_ENGINEER (3/20)                                       | 미확인                       |
| ML과 AI (`ml`)                            | 1634 (15/20)               | 8 (11/16)          | 339 (15/20)               | 109 (12/20)                | 머신러닝엔지니어 (19/20)                         | 1000242 (17/20)                  | 061202 (6/20)                  | MACHINE_LEARNING (6/20)                                    | 미확인                       |
| DevOps와 인프라 (`devops`)                | 674 (12/20)                | 9 (7/16)           | 323 (6/20)                | 146 (6/20)                 | DevOps_SRE (12/20)                               | 1000244 (6/20)                   | 060302 (6/20)                  | DEV_OPS (9/20)                                             | 미확인                       |
| QA (`qa`)                                 | 676 (12/20)                | 11 (11/15)         | 336 (15/20)               | 99 (15/20)                 | QA_테스트 (13/20)                                | 1000247 (14/20)                  | 060901 (5/20)                  | QA_ENGINEER (6/8)                                          | 미확인                       |
| 정보보안 (`security`)                     | 671 (16/20)                | 10 (11/20)         | 324 (13/20)               | 90 (13/20)                 | 정보보호_보안 (11/20)                            | 1000238 (12/20)                  | 060411 (14/20), 060404 (14/20) | SECURITY_ENGINEER (1/6)                                    | 미확인                       |
| 게임 개발 (`game_dev`)                    | 961 (4/4), 960 (4/5)       | 5 (3/4), 6 (3/3)   | 316 (4/8)                 | 80 (4/20)                  | 게임개발_클라이언트 (5/20), 게임개발_서버 (6/20) | 1000240 (3/20)                   | 061018 (2/6), 061015 (1/5)     | GAME_CLIENT_DEVELOPER (0/1), GAME_SERVER_DEVELOPER (0/1)   | 미확인                       |
| 서비스 기획, PM (`product_manager`)       | 565 (13/20), 559 (12/20)   | 12 (6/19)          | 164 (12/20)               | 1635 (10/20), 1651 (8/20)  | PM_PO (15/20)                                    | 1000188 (9/20)                   | 060701 (12/20), 060709 (7/20)  | PO_PM (12/20), SERVICE_OWNER (12/20)                       | 미확인                       |
| 프로덕트 디자인 (`product_designer`)      | 599 (18/20), 597 (16/20)   | 없음               | 378 (15/20), 379 (16/20)  | 1529 (11/20)               | UXUI_프로덕트 (6/20)                             | 1000256 (14/20)                  | 060801 (12/20)                 | PRODUCT_DESIGNER (7/9), WEB_APP_DESIGNER (13/14)           | 미확인                       |
| 그래픽, 브랜드 디자인 (`visual_designer`) | 879 (13/20), 592 (9/20)    | 없음               | 376 (9/20)                | 1527 (11/20), 1496 (8/20)  | 브랜딩_BI_BX (6/20), 그래픽_시각 (5/20)          | 1000248 (9/20), 1000253 (6/20)   | 120101 (6/17), 120701 (4/16)   | GRAPHICS_DESIGNER (2/7), BI_BX_DESIGNER (0/1)              | 미확인                       |
| 데이터 분석 (`data_analyst`)              | 656 (9/20)                 | 없음               | 345 (6/20)                | 2248 (5/20), 82 (1/20)     | 데이터사이언티스트 (9/20), 데이터분석가 (5/20)   | 1000418 (5/20)                   | 061201 (5/20), 061205 (4/20)   | DATA_ANALYST (7/13), DATA_SCIENTIST (8/14)                 | 미확인                       |
| 마케팅 (`marketing`)                      | 710 (18/20), 10138 (18/20) | 없음               | 225 (17/20), 224 (15/20)  | 2201 (14/20), 1437 (18/20) | 브랜드마케팅 (8/20), 퍼포먼스마케팅 (1/20)       | 1000218 (16/20), 1000217 (11/20) | 030103 (7/20), 030101 (7/20)   | PERFORMANCE_MARKETER (14/14), BRAND_MARKETER (9/9)         | 미확인                       |
| 영업, 사업개발 (`business_development`)   | 1036 (16/20), 564 (5/20)   | 없음               | 244 (16/20), 157 (14/20)  | 2203 (13/20), 1633 (6/20)  | B2B영업 (16/20), 사업개발_분석 (6/20)            | 1000282 (14/20)                  | 010201 (15/20), 020105 (6/20)  | BUSINESS_SALES (9/11), BUSINESS_DEVELOPMENT_PLANNER (2/13) | 미확인                       |
| CS, 서비스 운영 (`operations`)            | 1028 (12/20), 554 (11/20)  | 없음               | 167 (10/20)               | 1978 (13/20), 1977 (12/20) | CX매니저 (6/20)                                  | 1000288 (9/20)                   | 010601 (1/20)                  | CS_MANAGER (1/1), SERVICE_OPERATION (0/1)                  | 미확인                       |
| 인사 (`hr`)                               | 643 (18/20), 644 (16/20)   | 없음               | 192 (16/20), 193 (15/20)  | 2198 (14/20), 431 (16/20)  | 인사기획 (13/20)                                 | 1000201 (4/20)                   | 020301 (12/20), 020303 (13/20) | PERSONNEL_ASSESSMENT (7/8), RECRUITER (2/2)                | 미확인                       |
| 재무, 회계 (`finance`)                    | 1048 (18/20), 534 (17/20)  | 없음               | 173 (16/20), 184 (15/20)  | 2197 (18/20), 2220 (14/20) | 회계 (9/20), 재무 (6/20)                         | 1000210 (14/20), 1000207 (14/20) | 020501 (12/20), 020502 (11/20) | ACCOUNTING (3/4)                                           | 미확인                       |
| 법무 (`legal`)                            | 1002 (17/20), 691 (20/20)  | 없음               | 207 (18/20), 208 (12/20)  | 2215 (12/20), 397 (14/20)  | 법무 (15/20), 컴플라이언스 (11/20)               | 1000195 (9/20)                   | 020202 (9/20)                  | 없음                                                       | 미확인                       |
| MD, 상품기획 (`merchandiser`)             | 758 (14/20), 10232 (11/20) | 없음               | 425 (16/20), 155 (10/20)  | 1219 (16/20), 1212 (15/20) | 온라인MD (8/20), 상품기획 (7/20)                 | 1000224 (12/20)                  | 080402 (12/20)                 | PRODUCT_PLANNER_MD (0/0)                                   | 미확인                       |

- 원티드: 풀스택 직무가 없다. 풀스택 공고는 669와 872에 함께 나온다. 코드 목록은 `https://www.wanted.co.kr/wdlist/518/669` HTML `__NEXT_DATA__`의 `props.pageProps.tags.category[0].tags`에 있다. 개발 밖 코드는 같은 `category` 배열의 다른 대분류에 있다(507 경영과 비즈니스, 511 디자인, 523 마케팅과 광고, 530 영업, 510 고객서비스와 리테일, 517 HR, 508 금융, 521 법률, 10566 정보보호, 959 게임 제작). 데이터 사이언티스트 1024는 2/20이었다. 앞쪽 20건에 머신러닝 엔지니어와 데이터 엔지니어 공고가 섞여 있었다.
- 점핏: 개발 직군 전용이다. 1부터 22까지 응답 공고의 직무 이름이 전부 개발 직무여서(12는 "개발 PM") 개발 밖 직군은 없음으로 적었다. 응답 공고의 `jobCategory`에 직무 이름이 쉼표로 이어져 온다. 코드마다 받은 공고 전부에 그 이름(16이면 "iOS 개발자", 10이면 "정보보안 담당자", 5면 "게임 클라이언트 개발자")이 들어 있었다. 6은 받은 3건이 모두 게임 서버와 게임 클라이언트 개발자 이름을 함께 달고 있어 어느 쪽 코드인지 가리지 못했다. 1부터 30까지 보내 보니 14와 23 이상은 0건이었다.
- 리멤버: 코드와 이름은 응답 공고의 `job_categories[]`(`id`, `level1`, `level2`)에 있다. 코드 목록을 주는 요청은 찾지 못했고, 직무 키워드 21개로 검색한 응답에서 코드를 모았다. 같은 대분류에 326(시스템 엔지니어), 327(클라우드 엔지니어), 340(MLOps)도 있다. 이 셋은 응답에서 이름만 봤고 필터로 보내 보지 않았다. 344(데이터 사이언티스트)는 2/20이었다.
- 사람인: 92, 84, 83, 99는 직무 키워드, 2232(풀스택)와 195(Android), 234(iOS)는 기술스택 키워드, 2255(크로스플랫폼)와 109(머신러닝), 146(DevOps)은 전문분야 키워드다. 직무 키워드에는 풀스택이 없고 모바일은 86(앱개발) 하나다. 인프라는 127(7/20)도 있다. 코드 목록은 `https://www.saramin.co.kr/zf_user/jobs/list/job-category?cat_mcls=2` HTML 안 JSON의 `KEWD_CD_NO`와 `KEWD_CD_NM`이다. 같은 JSON의 `job_category`에 대분류 전체가 있고, 개발 밖 코드는 `MCLS_CD_NO` 16(기획 전략), 14(마케팅 홍보 조사), 15(디자인), 8(영업 판매 무역), 21(고객상담 TM), 5(인사 노무 HRD), 3(회계 세무 재무), 4(총무 법무 사무), 12(상품기획 MD)의 직무 키워드다. 데이터분석가 82는 1/20이었다. 앞쪽 20건에 백엔드 개발과 AI 엔지니어, PM 공고가 섞여 있었다.
- 직행: 값은 숫자가 아니라 직무 이름이고 URL 인코딩해서 보낸다. 파라미터는 복수형 `depthTwos`다. 단수 `depthTwo`는 무시되어 필터 없는 전체(313,500건)가 온다. 응답 공고의 `depthTwos`에 같은 이름이 있다. 이름 목록을 주는 요청은 찾지 못했고, 직무 키워드 21개로 검색한 응답에서 이름을 모았다.
- 직행 해외 공고: `affiliates=직행`으로 받으면 개발 밖 코드에 `regions`가 `["해외"]`인 공고가 많다. 퍼포먼스마케팅 5년 100건 중 89건이 해외였고 제목도 영어와 프랑스어, 포르투갈어였다. 그래서 그 칸의 맞은 수가 1/20이다. `regions=서울,경기`를 붙이면 그 지역 공고만 왔다(같은 조건 175건, `regions=서울`만 붙이면 163건). `excludeRegions`와 `isOverseas`는 무시됐다.
- 잡코리아: 앱개발자 1000232 하나에 안드로이드와 iOS, 크로스플랫폼이 함께 들어 있다. DevOps 코드는 없어서 클라우드엔지니어 1000244를 적었다. 시스템엔지니어 1000233(9/20)도 있다. 코드 목록은 `https://www.jobkorea.co.kr/recruit/joblist?menucode=duty` HTML에서 `groupCode`가 10031인 `data-value-json`의 `subList`다. 보안엔지니어 1000238과 게임개발자 1000240, 데이터분석가 1000418도 10031에 있다. 개발 밖 코드는 같은 HTML의 다른 `groupCode`(10026 기획 전략, 10027 법무 사무 총무, 10028 인사 HR, 10029 회계 세무, 10030 마케팅 광고 MD, 10032 디자인, 10035 영업, 10036 고객상담 TM)에 있다. 인사담당자 1000201은 4/20이었다. 20건 중 9건이 한 회사의 "상시 인재pool 등록" 공고였다. 같은 공고들이 경영 비즈니스기획 1000185 결과에도 나와 그 코드는 0/20이라 표에 넣지 않았다.
- 캐치: `JobCode`는 6자리 세부 직무 코드다. 코드 목록은 `GET https://www.catch.co.kr/api/v1.0/recruit/information/workListV3/all`의 `subSubWorkList`에 있다. 2자리와 4자리 상위 코드도 걸린다(경력 공고 기준 06은 784건, 0601은 106건, 060108은 28건). 캐치 공고 제목에는 "10월 경력 수시채용"처럼 직무가 없는 공채 제목이 많아 맞은 수가 낮다. 풀스택 값은 없다. CS와 서비스 운영에 가까운 값은 010601(고객관리, 1/20)과 060606(컨텐츠운영, 1/18)이었고 둘 다 맞은 수가 낮았다.
- 랠릿: `job`은 `jobGroup`과 함께 보내야 걸린다. `job=FRONTEND_DEVELOPER`만 보내면 필터 없이 466건이 왔고 `jobGroup=DEVELOPER`를 더하면 89건이었다. `jobGroup`은 DEVELOPER(개발 직무와 DATA_ANALYST, DATA_SCIENTIST, SECURITY_ENGINEER), GAME_DEVELOPER(GAME_CLIENT_DEVELOPER, GAME_SERVER_DEVELOPER), DESIGN(PRODUCT_DESIGNER, WEB_APP_DESIGNER, GRAPHICS_DESIGNER, BI_BX_DESIGNER), PRODUCT(PO_PM, SERVICE_OWNER, BUSINESS_DEVELOPMENT_PLANNER, PRODUCT_PLANNER_MD), MARKETING, MANAGEMENT(SERVICE_OPERATION, CS_MANAGER, RECRUITER, PERSONNEL_ASSESSMENT, ACCOUNTING), SALES(BUSINESS_SALES)다. 값 목록은 `https://www.rallit.com/` HTML이 불러오는 `_app` 스크립트 안에 있다. 전체 469건 중 DEVELOPER가 296건이고 PRODUCT 53건, MARKETING 49건, DESIGN 26건, MANAGEMENT 21건, SALES 17건, GAME_DEVELOPER 2건이었다. 개발 밖 직군은 공고가 적어 받은 수가 20보다 작다. 법무 값은 없다.
- 잡플래닛: curl은 `/job`과 API 모두 403이라 코드 목록을 얻지 못했다. 2026-10-12에도 브라우저로 확인하지 않아 프론트엔드 11905 말고는 미확인이다. 실행할 때 잡플래닛 절에 적은 대로 browser-scout가 화면의 직무 필터에서 값을 읽는다.

## 원티드

- 직무 목록: `GET https://www.wanted.co.kr/api/v4/jobs?country=kr&tag_type_ids=669&job_sort=job.latest_order&years={y}&locations=all&limit=100&offset=0`. 669는 프론트엔드 직무 코드다. 다른 직무는 직무 코드표의 원티드 값을 넣는다.
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
- 응답의 `min_experience`, `max_experience`(null이면 상한 없음)가 연차, `ends_at`(null이면 상시)이 마감이다. 다만 이 필드가 공고 본문의 경력 문구와 다를 때가 있다(2026-10-12 아이벡스: 필드 2~7년, 본문 "5년 이상"). 본문에 경력 문구가 있으면 본문을 따르고 `experience_raw`에 본문 문구를 적는다.
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

- 목록: `GET https://jumpit-api.saramin.co.kr/api/positions?jobCategory=2&career={y}&sort=rsp_rate&page=1`. `jobCategory=2`가 프론트엔드다. 다른 개발 직무는 직무 코드표의 점핏 값을 쓴다. 점핏은 개발 직군 공고만 있어서 프로필이 개발 밖 직군이면 건너뛴다.
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

링크드인은 직무 코드 대신 `keywords`로 거른다. `{kw_en}`은 프로필 값을 쓰고, 프로필 `keywords_en`이 비었거나 결과가 적으면 아래 검색어를 쓴다. 괄호 안 숫자는 2026-10-12에 위 목록 요청(`f_E=4`, `start=0`)으로 받은 10건 중 제목이 `prefilter.py`의 `ROLE_FAMILIES` 단어에 맞은 수다.

| 직무군          | 검색어                            | 직무군                 | 검색어                       |
| --------------- | --------------------------------- | ---------------------- | ---------------------------- |
| `frontend`      | Frontend Engineer (10/10)         | `product_manager`      | Product Manager (10/10)      |
| `backend`       | Backend Engineer (10/10)          | `product_designer`     | Product Designer (10/10)     |
| `fullstack`     | Full Stack Engineer (8/10)        | `visual_designer`      | Graphic Designer (8/10)      |
| `android`       | Android Developer (9/10)          | `data_analyst`         | Data Analyst (10/10)         |
| `ios`           | iOS Developer (4/10)              | `marketing`            | Performance Marketing (8/10) |
| `crossplatform` | Flutter Developer (2/10)          | `business_development` | Business Development (10/10) |
| `data_engineer` | Data Engineer (10/10)             | `operations`           | Customer Success (9/10)      |
| `ml`            | Machine Learning Engineer (10/10) | `hr`                   | HR Manager (9/10)            |
| `devops`        | DevOps Engineer (10/10)           | `finance`              | Accountant (10/10)           |
| `qa`            | QA Engineer (9/10)                | `legal`                | Legal Counsel (10/10)        |
| `security`      | Security Engineer (10/10)         | `merchandiser`         | Merchandiser (10/10)         |
| `game_dev`      | Game Developer (2/10)             |                        |                              |

- 크로스플랫폼과 게임은 국내 공고가 적었다. "Flutter"와 "React Native"도 2/10이었고, 게임은 "Unity Developer" 2/10, "Game Programmer"와 "Game Client Programmer" 1/10이었다. 나머지는 "Mobile App Developer"나 엔진, 렌더링 엔지니어처럼 직무 이름이 다르거나 다른 직무의 공고였다.
- "Merchandiser" 앞쪽에는 "Visual Merchandiser" 같은 매장 VMD 공고가 많았다.

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

## 발굴 모드

job-hunt의 발굴 흐름(레지스트리 밖 회사 범위)에서 레지스트리 밖 회사 공고를 플랫폼에서 넓게 모을 때 쓴다. 아래 요청은 2026-10-12에 프론트엔드 코드로 보내 200과 공고 데이터를 받은 것이다. `{code}`는 직무 코드표의 값이고 `{y}`는 공통 규칙과 같다.

- 공통 규칙의 100건 대신 플랫폼 하나에서 300건까지 최신순으로 받는다. 페이지는 아래 표의 요청 수까지 넘기고 전체 건수가 그보다 적으면 거기서 멈춘다.
- 목록에서 읽히는 회사명과 플랫폼 회사 ID는 다음 단계의 회사 검증에 쓴다. 점핏과 리멤버는 사업자등록번호가 같이 온다. 이름이 같은 회사를 가려낼 때 쓴다.

| 플랫폼   | 페이지 크기 | 300건까지 요청 수 | FE 2년 | FE 5년 | 목록에서 읽히는 회사 정보                                                                      |
| -------- | ----------- | ----------------- | ------ | ------ | ---------------------------------------------------------------------------------------------- |
| 원티드   | 100         | 3                 | 85     | 241    | `company.name`, `company.id`                                                                   |
| 점핏     | 100         | 3                 | 9      | 33     | `companyName`, `serialNumber`(사업자등록번호)                                                  |
| 리멤버   | 50          | 6                 | 30     | 113    | `organization.name`, `organization.company_id`, `organization.registration_no`(사업자등록번호) |
| 사람인   | 100         | 3                 | 109    | 233    | 회사명, `csn`                                                                                  |
| 직행     | 100         | 3                 | 98     | 231    | `company.name`, `company.id`                                                                   |
| 잡코리아 | 20          | 15                | 158    | 207    | `postingCompanyName`, `memberSystemNo`                                                         |
| 랠릿     | 100         | 3                 | 34     | 71     | `companyName`, `companyId`                                                                     |

FE는 2년과 5년 모두 모든 플랫폼에서 300건 아래였다. 가장 많은 곳은 원티드 5년 241건이다. 같은 날 백엔드 5년은 직행 1,236건, 사람인 530건, 원티드 438건, 잡코리아 414건이었고 리멤버는 290건이었다.

### 원티드

```
GET https://www.wanted.co.kr/api/v4/jobs?country=kr&tag_type_ids={code}&job_sort=job.latest_order&years={y}&locations=all&limit=100&offset={0,100,200}
```

- `data`가 100건보다 적거나 `links.next`가 null이면 멈춘다.
- 목록 공고에 `annual_from`, `annual_to`, `due_time`이 있어 상세를 열지 않아도 된다.
- 회사: `company.name`, `company.id`, 업종 `company.industry_name`.

### 점핏

```
GET https://jumpit-api.saramin.co.kr/api/positions?jobCategory={code}&career={y}&sort=reg_dt&page={1,2,3}&size=100
```

- `size`는 100까지 받는다. `pageSize`나 `limit`를 보내면 무시되고 16건이 온다. `page`는 1부터고 `result.totalCount`로 페이지 수를 정한다.
- `reg_dt`는 사이트 코드에서 최신순에 붙은 값이다. 목록에 등록일 필드가 없어 순서는 응답으로 확인하지 못했다.
- 목록 공고에 `minCareer`, `maxCareer`, `closedAt`, `alwaysOpen`이 있다.
- 회사: `companyName`, `serialNumber`. `serialNumber`는 10자리 사업자등록번호다. 파이오링크의 값(1198141089)이 리멤버 `registration_no`와 같았다.

### 리멤버

```bash
curl -s -X POST https://career-api.rememberapp.co.kr/job_postings/search \
  -H 'Content-Type: application/json' \
  -d '{"page":1,"per":50,"search":{"job_category_ids":[{code}],"career_year":{y}},"sort":"starts_at_desc"}'
```

- `per`는 50까지다. 60을 보내면 400과 "최대 요청 수를 초과하였습니다"가 온다. `page`를 1부터 `meta.total_pages`까지 올린다. 300건이면 6번이다.
- 짧은 간격으로 연달아 보내면 "요청이 너무 많습니다"가 오고 이어서 Cloudflare 1015 오류가 온다. 요청 사이에 3초를 쉬었을 때는 막히지 않았다.
- 회사: `organization.name`, `organization.company_id`, `organization.registration_no`(사업자등록번호, 빈 값도 있다). `company`는 null이었다.
- `organization.headhunter`가 true면 서치펌 공고라 기록하지 않는다. FE 5년 113건 중 11건이었다.

### 사람인

```
https://www.saramin.co.kr/zf_user/search/recruit?cat_kewd={code}&exp_cd=2&exp_min={y}&exp_max={y}&recruitPageCount=100&recruitSort=reg_dt&recruitPage={1,2,3}
```

- `recruitSort=reg_dt`로 받으면 `rec_idx`가 페이지를 넘어서도 내림차순이었다.
- 전체 건수는 HTML의 `cnt_result`("총 233건")다. 마지막 페이지를 넘기면 건수 표시 없이 다른 공고 20건이 온다(FE 2년 109건에서 `recruitPage=3`). `recruitPage`는 전체 건수를 100으로 나눠 올림한 값까지만 보낸다.
- 공고 하나는 `<div class="item_recruit" value="{rec_idx}">`다. 제목은 `h2.job_tit a`의 `title`, 경력과 고용 형태는 `div.job_condition`의 `span`, 마감은 `div.job_date span.date`다.
- 회사: `strong.corp_name a`의 글자가 회사명이고 href의 `csn` 값이 사람인 회사 ID다(`/zf_user/company-info/view?csn={csn}`). 같은 회사 공고에는 같은 `csn`이 온다.
- 목록에 서치펌을 표시하는 값이 없다. FE 5년 첫 페이지 앞 네 건이 서치펌(라인서치) 공고였다.

### 직행

```
GET https://api.zighang.com/api/recruitments/v4?page={0,1,2}&size=100&depthTwos={code}&affiliates=%EC%A7%81%ED%96%89&careerMin={y}&careerMax={y}&sortCondition=LATEST
```

- `affiliates=직행`(URL 인코딩)은 직행이 직접 모은 공고만 서버에서 남긴다. FE 5년이 이 값을 넣으면 231건, 빼면 603건이었다.
- `sortCondition=LATEST`가 최신순이다. 빼면 등록일이 섞여 온다. `sort=LATEST`와 `sort=createdAt,desc`는 무시된다.
- `size`는 100까지다. 200을 보내면 공고 없이 온다. `page`는 0부터고 `data.last`가 true면 멈춘다.
- 목록 공고에 `careerMin`, `careerMax`, `deadlineType`, `endDate`가 있다.
- 회사: `company.name`, `company.id`(UUID). FE 5년 231건이 회사 97곳이었다.
- 개발 밖 직무 코드로 받으면 해외 공고가 섞인다(퍼포먼스 마케팅 100건 중 89건). 프로필 `locations`가 있으면 그 지역을 `regions`에 넣고, 없으면 `regions=서울,경기`처럼 국내 지역을 넣어 받는다. 직무 코드표 절의 직행 메모에 확인한 값이 있다.

### 잡코리아

```
https://www.jobkorea.co.kr/Search/?duty={code}&careerType=2&careerMin={y}&careerMax={y}&Page_No={1..15}
```

- 페이지당 20건으로 고정이다. `pageSize`나 `size`는 무시된다. 300건까지 15페이지다.
- 공고 목록은 HTML의 `self.__next_f.push` 문자열 안에 JSON으로 들어 있다. 등록 시각(`createdAt`) 내림차순으로 왔다.

```bash
curl -s -A "$UA" "{위 URL}" > jk.html
python3 - jk.html <<'EOF'
import json, re, sys
h = open(sys.argv[1], encoding="utf-8").read()
s = "".join(json.loads('"' + c + '"') for c in re.findall(r'self\.__next_f\.push\(\[1,"((?:[^"\\]|\\.)*)"\]\)', h))
d, _ = json.JSONDecoder().raw_decode(s, s.index('{"pageSize":20,"pageNumber"'))
print(d["totalElements"], d["totalPages"])
for c in d["content"]:
    print(c["id"], c["postingCompanyName"], c["memberSystemNo"], c["title"], (c.get("applicationPeriod") or {}).get("end"))
EOF
```

- 회사: `postingCompanyName`, `memberSystemNo`. 같은 회사 공고에는 같은 `memberSystemNo`가 온다. 공고 링크는 `https://www.jobkorea.co.kr/Recruit/GI_Read/{id}`다.
- 마감은 `applicationPeriod.end`다. 연차 숫자는 목록 JSON에서 확인하지 않았다. 잡코리아 절대로 상세에서 읽는다.

### 랠릿

쓸 수 있다. 스타트업 공고가 많고 개발 직군 전체가 296건이다.

```
GET https://www.rallit.com/api/v1/position?jobGroup=DEVELOPER&job={job}&jobLevel={level},IRRELEVANT&pageNumber={1,2,3}&pageSize=100
```

- `job` 값과 처음 20건 중 제목 일치 수는 FRONTEND_DEVELOPER (15/20), BACKEND_DEVELOPER (10/20), ANDROID_DEVELOPER (10/19), IOS_DEVELOPER (5/11), CROSS_PLATFORM_DEVELOPER (4/20), DATA_ENGINEER (6/20), MACHINE_LEARNING (17/20), DEV_OPS (8/20), QA_ENGINEER (11/13)이다. 풀스택 값은 없다.
- `jobLevel`은 연차 구간이다. 1~3년은 JUNIOR, 4~8년은 MIDDLE, 9년 이상은 SENIOR이고 경력무관 IRRELEVANT를 쉼표로 함께 보낸다. FE에서 MIDDLE만 보내면 56건, IRRELEVANT를 더하면 71건이었다. 복수형 `jobLevels`는 무시되어 연차 필터 없이 온다.
- `pageSize`는 100을 받고 `data.totalPage`까지 넘긴다. 정렬 파라미터는 찾지 못했다. 직무 하나가 300건을 넘지 않으니 순서와 상관없이 전부 받는다.
- 목록 공고에 `jobLevels`(구간), `endedAt`(상시면 9999-12-31), `status.code`(받은 공고는 전부 HIRING)가 있다. 연차 숫자는 목록에 없다.
- 회사: `companyName`, `companyId`. 공고 링크는 응답의 `url`이다.

### 쓰지 못한 플랫폼

- 로켓펀치: 홈과 `/jobs`, API 경로 모두 curl에 Cloudflare 403("Attention Required!")이 온다. 브라우저로는 확인하지 않았다.
- 그룹바이(groupby.kr): 스타트업 공고 플랫폼이다. 직무 페이지(`https://groupby.kr/jobs/frontend`) HTML의 `__NEXT_DATA__`에 공고가 10건만 있고 `page`와 `offset` 파라미터는 무시된다. 다음 페이지를 주는 `https://api.groupby.kr/startup-positions`는 curl에 200을 주지만 제목과 회사명을 "[표시 제한]"으로 바꾼 데이터를 준다(전체 187,432건, 사이트 HTML에는 1,822건). 10건 안에서는 `startup.businessNumber`(사업자등록번호)와 `experienceRange`가 읽힌다.
- 더팀스(theteams.kr): 채용 목록의 공고 링크 40개가 전부 `/recruit/wanted/{id}` 형식이고 상세는 Cloudflare 확인 화면(403)이다.
- 디스콰이엇은 `/jobs`가 홈으로 넘어가고 커리어리는 `/jobs`가 404다.

### ATS 검색 넓히기

ATS 검색 절의 방법을 직무마다 검색어 여러 개로 돌린다. 검색어 하나가 결과 10건을 주고 그중 일부는 공고가 아니라 회사 채용 홈이다. 검색어를 바꾸면 다른 공고가 나온다. 2026-10-12에 돌린 검색어는 세 형태다.

| 형태                                | 예                                      |
| ----------------------------------- | --------------------------------------- |
| `{kw} 경력`                         | `프론트엔드 경력`, `백엔드 개발자 경력` |
| `{kw_en}`                           | `Frontend Engineer`, `Backend Engineer` |
| `{skills_core 첫 번째} {직무} 채용` | `React 웹 개발자 채용`                  |

그리팅에서 프론트엔드 세 검색어는 공고 URL을 4개, 2개, 9개 줬고 겹친 것을 빼면 12개였다. 12개 중 9개가 열려 있었고 3개는 404였다. 백엔드 두 검색어는 7개와 2개를 줬고 겹치지 않았다. 나인하이어에서 프론트엔드 두 검색어는 9개와 6개(겹침 1개)를 줬다.

- 회사 채용 홈(`https://{sub}.career.greetinghr.com/ko/home` 같은 주소)이 나오면 `references/career-sites.md` 그리팅 절의 `__NEXT_DATA__` 방법으로 그 회사 공고 전체를 읽는다. 누아 홈에서 공고 목록이 읽혔다.
- 그리팅 상세는 `curl -sL`로 받는다. 경로에 `/ko`가 없으면 301로 넘어간다. 열려 있으면 `__NEXT_DATA__`에서 `[..|objects|select(has("openingId") and has("title"))][0].status`가 `"OPEN"`이고, 닫힌 공고는 404다.
- 나인하이어 상세는 curl에 Vercel 보안 확인 429가 온다. 열려 있는지는 career-sites.md 나인하이어 절대로 회사의 `companyId`를 얻어 목록 API로 본다. 검색 결과에는 맨파워그룹코리아처럼 다른 회사 공고를 대신 올린 곳도 섞인다.
- recruiter.co.kr은 `프론트엔드 경력` 결과 10건 중 jobflex 상세 3개를 career-sites.md recruiter.co.kr 절의 v2 상세 API로 열었다. 프론트엔드 공고 1건은 2024-12-31 마감(`POST_SUBMISSION`)이었고 나머지 둘은 마케팅과 PM 공고였다. 나머지 결과는 회사 홈과 구형 공고 페이지였다.

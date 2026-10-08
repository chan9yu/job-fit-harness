# 대상 기업

리포트는 `티어` 순서(S, A+, A, B+, B, 빈칸)로 정렬하고, 같은 티어 안에서는 이 파일의 행 순서를 따른다. 채용 페이지와 접근 방식, 운영 상태는 2026-10-07에 직접 확인했다.

| 열   | 뜻                                                                                                                                                                                                  |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 티어 | 지원 우선순위. 비어 있으면 맨 뒤로 간다                                                                                                                                                             |
| ATS  | `자체`, `greetinghr`, `greenhouse`, `lever`, `ninehire`, `recruiter`(recruiter.co.kr), `workday`, 그 밖의 솔루션 이름                                                                               |
| 접근 | `api`는 공개 JSON, `fetch`는 HTML에 공고가 있음, `browser`는 Chrome이 필요함, `login`은 로그인이 필요함, `group`은 비고에 적힌 그룹 행을 읽을 때 함께 수집함. 비어 있으면 job-scout가 먼저 시도한다 |
| 비고 | 수집에 쓰는 식별자(그리팅 workspace, 나인하이어 companyId, Greenhouse token, Lever account), 거르는 조건, 다른 이름                                                                                 |

ATS별 요청 방법과 자체 API 기업의 요청은 `.claude/skills/job-collection/references/career-sites.md`에 있다. 기업을 추가할 때는 이름과 채용 페이지만 적어도 된다. 맨 아래 "제외한 기업" 절은 수집 대상이 아니다.

## 네카라쿠배당토직야

| 기업           | 티어 | 채용 페이지                                                    | ATS        | 접근  | 비고                                                |
| -------------- | ---- | -------------------------------------------------------------- | ---------- | ----- | --------------------------------------------------- |
| 비바리퍼블리카 | S    | https://toss.im/career/jobs                                    | 자체       | api   | 토스. 토스뱅크, 토스증권 등 계열사 전체             |
| 토스페이먼츠   | B    | https://toss.im/career/jobs                                    | 자체       | group | 비바리퍼블리카 행에서 계열사 값으로 수집            |
| 당근           | S    | https://careers.daangn.com/jobs/                               | greenhouse | api   | token `daangn`                                      |
| 네이버         | S    | https://recruit.navercorp.com/rcrt/list.do                     | 자체       | api   | 그룹 통합 사이트(클라우드, 랩스, 파이낸셜 포함)     |
| 네이버클라우드 | A+   | https://recruit.navercorp.com/rcrt/list.do                     | 자체       | group | 네이버 행에서 `sysCompanyCdArr` NB로 수집           |
| 네이버웹툰     | A+   | https://recruit.webtoonscorp.com/rcrt/list.do                  | 자체       | api   | 네이버 통합 사이트와 공고가 겹친다                  |
| 쿠팡           | S    | https://www.coupang.jobs/kr/jobs/                              | greenhouse | api   | token `coupang`, 서울만                             |
| 우아한형제들   | S    | https://career.woowahan.com/                                   | 자체       | api   | 배달의민족                                          |
| 라인플러스     | A+   | https://careers.linecorp.com/ko/jobs                           | 자체       | api   | LINE Pay Plus, IPX, LINE studio 포함. 한국 근무지만 |
| 카카오         | A+   | https://careers.kakao.com/jobs                                 | 자체       | api   |                                                     |
| 카카오페이     | A+   | https://careers.kakaopay.com/ko/main                           | greetinghr | api   | workspace 9737, 직군 "기술"                         |
| 카카오모빌리티 | A+   | https://kakaomobility.career.greetinghr.com/ko/home            | greetinghr | api   | workspace 14346, 직군 "기술"                        |
| 직방           | A    | https://zigbang.career.greetinghr.com/ko/positions             | greetinghr | api   | workspace 1724, 호갱노노 포함                       |
| 야놀자         | A    | https://yanolja.wd102.myworkdayjobs.com/ko-KR/External_Yanolja | workday    | api   |                                                     |
| 놀유니버스     |      | https://careers.nol-universe.com/ko/jobs                       | greetinghr | api   | workspace 5525                                      |

## 몰두센

| 기업     | 티어 | 채용 페이지                            | ATS        | 접근  | 비고                                                        |
| -------- | ---- | -------------------------------------- | ---------- | ----- | ----------------------------------------------------------- |
| 몰로코   | S    | https://www.moloco.com/company/careers | greenhouse | api   | token `moloco`, 서울만                                      |
| 두나무   | S    | https://careers.dunamu.com/            | 자체       | fetch | 업비트. HTML에 `/detail/{id}` 링크와 분야, 경력 구분이 있다 |
| 센드버드 | A+   | https://delight.ai/careers             | greenhouse | api   | token `sendbird`, 부서 Engineering, 서울만                  |

## 대기업 그룹

그룹 행은 계열사 전체 공고를 한 번에 받는다. 계열사 행(`group`)은 티어를 정하고 회사명을 맞추는 데만 쓴다.

| 기업             | 티어 | 채용 페이지                                                     | ATS        | 접근  | 비고                                                                                           |
| ---------------- | ---- | --------------------------------------------------------------- | ---------- | ----- | ---------------------------------------------------------------------------------------------- |
| 삼성             |      | https://www.samsungcareers.com/hr/                              | 자체       | api   | 그룹 통합 사이트. 계열사 전체                                                                  |
| 삼성전자         |      | https://www.samsungcareers.com/hr/                              | 자체       | group | 삼성 행. DX `C10CAA`, DS `C10CAH`                                                              |
| 삼성SDS          | B    | https://www.samsungcareers.com/hr/                              | 자체       | group | 삼성 행. `C60`                                                                                 |
| 삼성카드         | B    | https://www.samsungcareers.com/hr/                              | 자체       | group | 삼성 행. `E31`                                                                                 |
| LG               |      | https://careers.lg.com/apply                                    | 자체       | api   | 그룹 통합 사이트. 계열사 전체                                                                  |
| LG CNS           | B    | https://careers.lg.com/apply                                    | 자체       | group | LG 행. `CNS`                                                                                   |
| LG유플러스       | B    | https://careers.lg.com/apply                                    | 자체       | group | LG 행. `LGU`                                                                                   |
| SK               |      | https://www.skcareers.com/Recruit                               | 자체       | api   | 그룹 통합 사이트. 계열사 전체                                                                  |
| SK텔레콤         | A    | https://www.skcareers.com/Recruit                               | 자체       | group | SK 행. corpCode 10005                                                                          |
| SK AX            | B    | https://www.skcareers.com/Recruit                               | 자체       | group | SK 행. corpCode 10018, "SK주식회사(AX)" 표기                                                   |
| 현대자동차       |      | https://talent.hyundai.com/apply/applyList.hc                   | 자체       | api   | 현대차그룹은 통합 사이트가 없어 계열사마다 따로 읽는다                                         |
| 포티투닷         | A+   | https://42dot.ai/ko/careers/open-roles                          | ashby      | api   | 42dot. Ashby board `42dot`                                                                     |
| 현대오토에버     | B    | https://career.hyundai-autoever.com/ko/apply                    | greetinghr | api   | workspace 13782                                                                                |
| 현대모비스       | B    | https://careers.mobis.com/jobs                                  | 자체       | fetch | 직군 "SW/로직"                                                                                 |
| KT               | B    | https://recruit.kt.com/careers                                  | 자체       | api   | KT그룹 통합(kt cloud, BC카드 등)                                                               |
| 롯데             |      | https://recruit.lotte.co.kr/apply/announcement                  | 자체       | fetch | 그룹 통합 사이트. 계열사 전체. IT 직무 코드 밖 공고에도 프런트엔드가 있다(캐논코리아 연구개발) |
| 롯데이노베이트   | B    | https://recruit.lotte.co.kr/apply/announcement                  | 자체       | group | 롯데 행. compcd 30007                                                                          |
| 롯데ON           | B    | https://recruit.lotte.co.kr/apply/announcement                  | 자체       | group | 롯데 행. compcd 40013(롯데e커머스). 2026-06 희망퇴직 보도                                      |
| CJ               |      | https://recruit.cj.net/recruit/ko/recruit/recruit/list.fo       | 자체       | api   | 그룹 통합 사이트. 계열사 전체                                                                  |
| CJ올리브네트웍스 | B    | https://recruit.cj.net/recruit/ko/recruit/recruit/list.fo       | 자체       | group | CJ 행. `E10`                                                                                   |
| 한화             |      | https://www.hanwhain.com/portal/apply/recruit                   | 자체       | api   | 그룹 통합 사이트. 계열사 전체                                                                  |
| 한화시스템       | B    | https://www.hanwhain.com/portal/apply/recruit                   | 자체       | group | 한화 행. sdSeq 215(ICT), 328(방산)                                                             |
| 한화생명         | B    | https://www.hanwhain.com/portal/apply/recruit                   | 자체       | group | 한화 행. sdSeq 201                                                                             |
| 포스코DX         | B    | https://recruit.posco.com/h22a01-front/H22A1000.html            | 자체       | api   | 포스코그룹 통합 사이트에서 `COMPANY_NAME`으로 거른다                                           |
| 신세계아이앤씨   | B    | https://job.shinsegae.com/rcrut                                 | 자체       | api   | 신세계그룹 통합 사이트. coCd IC0                                                               |
| SSG닷컴          | B    | https://ssg.career.greetinghr.com/ko/career                     | greetinghr | api   | SSG.COM. workspace 5472                                                                        |
| GS리테일         | B    | https://gsretail.recruiter.co.kr/career/home                    | recruiter  | api   | GS SHOP(홈쇼핑BU), GS네트웍스 포함. IT 직군 jobGroupSn 128169                                  |
| 현대홈쇼핑       | B    | https://recruit.ehyundai.com/recruit-info/announcement/list.nhd | 자체       | api   | 현대백화점그룹 통합 사이트. coCd HDHOME                                                        |
| 홈앤쇼핑         | B    | https://hnsmall.recruiter.co.kr/career/home                     | recruiter  | api   |                                                                                                |

## IT 서비스와 클라우드

| 기업           | 티어 | 채용 페이지                                | ATS       | 접근  | 비고                                                                                                 |
| -------------- | ---- | ------------------------------------------ | --------- | ----- | ---------------------------------------------------------------------------------------------------- |
| 베스핀글로벌   | A    | https://bespinglobalrecruit.ninehire.site/ | ninehire  | api   | companyId `88c2a790-ac89-11ef-a560-bf5ce29a44e4`                                                     |
| 메가존클라우드 | A    | https://career.megazone.com/               | ninehire  | api   | companyId `f3b6f7b0-94a2-11ec-990c-a70e6ab23542`, 직군 "Tech". 계열사는 `affiliation.title`로 거른다 |
| NHN            | B+   | https://careers.nhn.com/recruits           | 자체      | api   | 그룹 통합 사이트. 계열사 전체                                                                        |
| NHN Cloud      | B+   | https://careers.nhn.com/recruits           | 자체      | group | NHN 행. corporationId 3647229949742220183                                                            |
| 더존비즈온     | B    | https://recruit.douzone.com/               | 자체      | api   | 더존ICT그룹 통합. EQT 인수 후 상장폐지 진행                                                          |
| 안랩           | B    | https://ahnlab.recruiter.co.kr/career/home | recruiter | api   | 개발 태그 1748, 2205                                                                                 |
| 가비아         | B    | https://recruit.gabia.com/recruit/jobs     | hiworks   | api   |                                                                                                      |

## 유니콘과 네임밸류

| 기업           | 티어 | 채용 페이지                                      | ATS        | 접근  | 비고                                                                                     |
| -------------- | ---- | ------------------------------------------------ | ---------- | ----- | ---------------------------------------------------------------------------------------- |
| 무신사         | A    | https://www.musinsacareers.com/ko/home           | greetinghr | api   | workspace 1455, 29CM 포함                                                                |
| 버킷플레이스   | A    | https://www.bucketplace.com/careers/             | 자체       | api   | 오늘의집                                                                                 |
| 컬리           | A    | https://kurly.career.greetinghr.com/ko/home      | greetinghr | api   | workspace 6012, 직군 "개발"                                                              |
| 리디           | A    | https://ridi.recruit.roundhr.com/home            | roundhr    | api   |                                                                                          |
| 쏘카           | A    | https://www.socarcorp.kr/careers/jobs            | 자체       | fetch | 계열사 포함                                                                              |
| 여기어때       | A    | https://gccompany.career.greetinghr.com/ko/home  | greetinghr | api   | workspace 3017, 직군 "기술"                                                              |
| 마이리얼트립   | A    | https://myrealtrip.career.greetinghr.com/ko/home | greetinghr | api   | workspace 4664, 경력 필드가 비어 있어 상세에서 읽는다                                    |
| 루닛           | A    | https://apply.workable.com/lunit/                | workable   | api   | account `lunit`                                                                          |
| 리벨리온       | A    | https://rebellions.ai/careers/                   | greetinghr | api   | workspace 6706, 경력 필드가 비어 있어 상세에서 읽는다                                    |
| 업스테이지     | A    | https://careers.upstage.ai/ko/upstage            | greetinghr | api   | workspace 17060, 직군 "Tech"                                                             |
| 비마이프렌즈   | A    | https://bemyfriends.careers.team/                | flex       | api   | customer `PM0vkqlzXd`, 개발 그룹 `pODzZMa0Ro`                                            |
| 레브잇         | A    | https://team.alwayz.co/                          | ninehire   | api   | 올웨이즈. companyId `c76193f0-c356-11f0-b8eb-3fe403194dab`, 직군 "Engineer"              |
| AB180          | A    | https://recruit.ab180.co/                        | ninehire   | api   | companyId `dab31690-f51a-11f0-82d7-69b90bd91b4e`, 직군 "Engineering"                     |
| 채널코퍼레이션 | A    | https://channel.io/kr/careers                    | lever      | api   | 채널톡. account `zoyi`, `team=Engineering`                                               |
| 버즈빌         | A    | https://buzzvil.career.greetinghr.com/ko/home    | greetinghr | api   | workspace 2204, 직군 "Engineering"                                                       |
| 딜라이트룸     | A    | https://delightroom.com/recruit                  | ninehire   | api   | 알라미. companyId `1b1b3410-7499-11ee-8d8d-cf33a76bbc70`, 직군 값이 없어 제목으로 거른다 |
| 마카롱팩토리   | A    | https://mycle.career.greetinghr.com/ko/home      | greetinghr | api   | workspace 9927, 직군 "개발"                                                              |
| 에이블리       | B+   | https://ably.team/recruit                        | ninehire   | api   | companyId `423205c0-372b-11ee-a7cc-c92c3b459af0`                                         |
| 하이퍼커넥트   |      | https://career.hyperconnect.com/jobs/            | lever      | api   | account `matchgroup`, `location=Seoul, South Korea`                                      |
| 퓨리오사AI     |      | https://furiosa.ai/careers                       | greenhouse | api   | token `furiosaai`                                                                        |

## 교육과 HR, 업무 도구

| 기업           | 티어 | 채용 페이지                                                                                            | ATS        | 접근  | 비고                                                                                                 |
| -------------- | ---- | ------------------------------------------------------------------------------------------------------ | ---------- | ----- | ---------------------------------------------------------------------------------------------------- |
| 원티드랩       | B+   | https://blog.wantedlab.com/recruit                                                                     | 원티드     | api   | 원티드 회사 79                                                                                       |
| 사람인         | B+   | https://www.saramin.co.kr/zf_user/company-info/view-inner-recruit/csn/L2psRTIzckptMERnRUtBU0wxNWpidz09 | 사람인     | fetch | 사람인 안의 자사 회사 페이지                                                                         |
| 웍스피어       | B+   | https://www.worxphere.ai/career                                                                        | ninehire   | api   | 잡코리아(2026-01 사명 변경). companyId `4727d410-f887-11ee-8fde-25770d902e42`, 직군 "Tech", "FE개발" |
| 리멤버앤컴퍼니 | B+   | https://career.rememberapp.co.kr/job/company/663802                                                    | 리멤버     | api   | 드라마앤컴퍼니(2024-10 사명 변경)                                                                    |
| 팀스파르타     | B+   | https://career.spartaclub.kr/ko/home                                                                   | greetinghr | api   | workspace 2450, 직군 "개발"                                                                          |
| 클래스101      | B+   | https://jobs.class101.net/                                                                             | ninehire   | api   | companyId `f20ace90-8932-11f0-8815-d9c0c4c32872`                                                     |
| 데이원컴퍼니   | B+   | https://day1company.ninehire.site/                                                                     | ninehire   | api   | 패스트캠퍼스. companyId `70683bd0-612b-11ec-bd23-6b2cabce5a2f`, 직군 "개발/IT", "기획/개발"          |
| 숨고           | B+   | https://soomgo.career.greetinghr.com/ko/career                                                         | greetinghr | api   | 브레이브모바일. workspace 2380, 직군 "Engineering"                                                   |
| 크몽           | B+   | https://kmong.career.greetinghr.com/ko/home                                                            | greetinghr | api   | workspace 3430, 직군 "개발"                                                                          |
| 모두싸인       | B+   | https://recruit.modusign.co.kr/ko/apply                                                                | greetinghr | api   | workspace 14923, 직군 "개발"                                                                         |
| 플렉스         | B+   | https://flex.careers.team/                                                                             | flex       | api   | customer `65Y06m8XpK`                                                                                |
| 자비스앤빌런즈 | B+   | https://jobisnvillains.com/recruit                                                                     | greetinghr | api   | 삼쩜삼. workspace 215                                                                                |

## 커머스와 콘텐츠 플랫폼

| 기업               | 티어 | 채용 페이지                                       | ATS        | 접근  | 비고                                                                                                           |
| ------------------ | ---- | ------------------------------------------------- | ---------- | ----- | -------------------------------------------------------------------------------------------------------------- |
| 카카오스타일       | B+   | https://career.kakaostyle.com/                    | ninehire   | api   | 지그재그. companyId `1573cfe0-2c72-11ef-950a-65a32c77a0c3`, 직군 "Tech"                                        |
| 번개장터           | B+   | https://team.bgzt.co.kr/                          | ninehire   | api   | companyId `7541b210-1710-11ef-b315-d7a9afe6c5ae`, 직군 "Tech"                                                  |
| 백패커             | B+   | https://team.backpac.kr/ko/home                   | greetinghr | api   | 아이디어스. workspace 492, 직군 "개발". 텀블벅, 텐바이텐 포함                                                  |
| 크림               | B+   | https://recruit.kreamcorp.com/rcrt/list.do        | 자체       | api   | KREAM. 네이버와 같은 채용 플랫폼                                                                               |
| 펫프렌즈           | B+   | https://www.wanted.co.kr/company/2756             | 원티드     | api   | 자사 채용 페이지 없음. 매각 추진 보도                                                                          |
| SOOP               | B+   | https://recruit.sooplive.com/recruit_list.php     | 자체       | fetch | 구 아프리카TV. 직군 "Tech"                                                                                     |
| 11번가             | B    | https://11st.career.greetinghr.com/ko/career      | greetinghr | api   | workspace 10686                                                                                                |
| CJ올리브영         |      | https://career.oliveyoung.com/ko/home             | greetinghr | api   | workspace 10501, 직군 "IT". 신입 공채는 CJ 그룹 사이트                                                         |
| 티빙               |      | https://tving.ninehire.site/                      | ninehire   | api   | companyId `344a23e0-6828-11f0-b196-9fcc304eb9ab`, 직군 "Tech"                                                  |
| 카카오엔터테인먼트 |      | https://careers.kakaoent.com/ko/job               | greetinghr | api   | workspace 5191                                                                                                 |
| 위버스컴퍼니       |      | https://careers.hybecorp.com/ko/home              | greetinghr | api   | workspace 10002(HYBE 통합), `workspaceDivision.id` 88만, 직군 "기술"                                           |
| 지마켓             |      | https://careers.gmarket.com/jobs                  | ninehire   | api   | companyId `adefb110-ec48-11ec-9831-e7dedc6dd144`, 직군 값이 직무마다 달라 제목으로 거른다. 스마일페이먼츠 포함 |
| 왓챠               |      | https://watchateam.career.greetinghr.com/ko/intro | greetinghr | api   | workspace 7946, 직군 값이 없어 제목으로 거른다                                                                 |
| 웨이브             |      | https://wavve.career.greetinghr.com/ko/home       | greetinghr | api   | 콘텐츠웨이브. workspace 886                                                                                    |

## 금융과 핀테크

| 기업           | 티어 | 채용 페이지                                                                                            | ATS            | 접근  | 비고                                                                                             |
| -------------- | ---- | ------------------------------------------------------------------------------------------------------ | -------------- | ----- | ------------------------------------------------------------------------------------------------ |
| 뱅크샐러드     | A    | https://corp.banksalad.com/jobs/                                                                       | 자체           | api   |                                                                                                  |
| 한국신용데이터 | B+   | https://www.kcd.co.kr/recruit/                                                                         | 자체           | api   | 캐시노트. 목록은 Contentful, 상세는 그리팅                                                       |
| 핀다           | B+   | https://finda.career.greetinghr.com/ko/career                                                          | greetinghr     | api   | workspace 3037, 직군 "Engineering"                                                               |
| 빗썸           | B+   | https://career.bithumbcorp.com/ko/apply                                                                | greetinghr     | api   | workspace 16598, 직군 "Tech"                                                                     |
| 코인원         | B+   | https://recruit.coinonecorp.com/                                                                       | ninehire       | api   | companyId `b2baa5f0-1f40-11f0-8c6c-596fcda513ba`, 직군 "Tech"                                    |
| 디지털엑스     | B+   | https://digitalx.career.greetinghr.com/ko/digitalx                                                     | greetinghr     | api   | 코빗(2026-08 사명 변경, 미래에셋 계열). workspace 3020, 직군 "개발"                              |
| 비씨카드       | B+   | https://recruit.kt.com/careers                                                                         | 자체           | group | KT 행. `company`가 "BC카드"                                                                      |
| 현대카드       | B    | https://careerhyundai.recruiter.co.kr/career/home                                                      | recruiter      | api   | 현대커머셜과 같은 사이트. 제목의 `[현대카드]`로 거른다                                           |
| 신한DS         | B    | https://shinhands.recruiter.co.kr/app/jobnotice/list                                                   | recruiter 구형 | api   |                                                                                                  |
| KB데이타시스템 | B    | https://kbds.career.greetinghr.com/ko/home                                                             | greetinghr     | api   | workspace 10780                                                                                  |
| 하나금융티아이 | B    | https://hanati.recruiter.co.kr/app/jobnotice/list                                                      | recruiter 구형 | api   | 하나금융융합기술원과 같은 사이트                                                                 |
| 교보DTS        | B    | https://www.saramin.co.kr/zf_user/company-info/view-inner-recruit?csn=cWJzQytSOFpHN3BsNjY0MUlsNFlKQT09 | 사람인         | fetch | 공고를 사람인에만 올린다                                                                         |
| 교보생명       | B    | https://career.kyobo.co.kr/rem/apply/recruit/apply_list.jsp                                            | 자체           | api   | 경력은 반기마다 묶어서 뽑는다                                                                    |
| NHN KCP        | B    | https://kcp.career.greetinghr.com/ko/home                                                              | greetinghr     | api   | workspace 9471, 직군 "개발"                                                                      |
| KG이니시스     | B    | https://www.catch.co.kr/Comp/RecruitInfo/818038                                                        | 캐치           | fetch | 자사 공고 목록이 없어 캐치 회사 페이지를 읽는다                                                  |
| 다날           | B    | https://welcome.danal.co.kr/                                                                           | ninehire       | api   | companyId `45bf4990-8ebd-11ec-b021-8fa2323e810d`, 직군 "IT부문". 상세 본문은 Chrome으로만 열린다 |
| NICE정보통신   | B    | https://nice.career.greetinghr.com/ko/intro                                                            | greetinghr     | api   | NICE그룹 통합 workspace 13465. `workspaceDivision.id` 273, 직군 "IT"                             |
| NICE평가정보   | B    | https://nice.career.greetinghr.com/ko/intro                                                            | greetinghr     | api   | workspace 13465. `workspaceDivision.id` 195                                                      |
| 카카오뱅크     |      | https://recruit.kakaobank.com/jobs                                                                     | 자체           | api   |                                                                                                  |
| 케이뱅크       |      | https://kbank.recruiter.co.kr/career/job                                                               | recruiter      | api   | Tech 태그 12198                                                                                  |

## 게임

| 기업         | 티어 | 채용 페이지                                           | ATS        | 접근    | 비고                                                          |
| ------------ | ---- | ----------------------------------------------------- | ---------- | ------- | ------------------------------------------------------------- |
| 크래프톤     | A+   | https://www.krafton.com/careers/jobs/                 | 자체       | fetch   | Chrome 전체 User-Agent가 필요하다                             |
| 넥슨         | A    | https://careers.nexon.com/recruit                     | 자체       | browser | Cloudflare가 curl을 막는다. 브라우저 안에서 목록 API를 부른다 |
| 카카오게임즈 | B+   | https://recruit.kakaogames.com/ko/homekr              | greetinghr | api     | workspace 7144, 직군 "개발"                                   |
| 넷마블       | B+   | https://career.netmarble.com/announce                 | 자체       | api     |                                                               |
| 엔씨소프트   | B+   | https://careers.ncsoft.com/apply/list                 | 자체       | api     | CSRF 토큰 필요                                                |
| 시프트업     | B+   | https://shiftup.co.kr/recruit/recruit.php             | 자체       | fetch   |                                                               |
| 네오위즈     | B+   | https://www.neowiz.com/kr/career/browse-job           | lever      | api     | account `neowiz`                                              |
| 컴투스       | B+   | https://com2us.recruiter.co.kr/career/jobs            | recruiter  | api     | 개발 태그 6514, 8968, 22090, 16951                            |
| 데브시스터즈 | B+   | https://careers.devsisters.com/ko/position            | greetinghr | api     | workspace 12227                                               |
| 위메이드     | B+   | https://www.wanted.co.kr/company/14104                | 원티드     | api     | 공식 사이트 목록이 비어 있어 원티드 회사 페이지를 읽는다      |
| 펄어비스     | B+   | https://www.pearlabyss.com/ko-KR/Company/Careers/List | 자체       | fetch   |                                                               |
| 스마일게이트 |      | https://careers.smilegate.com/                        |            |         | 2026-10-07 기준 채용 사이트 점검 중                           |

## 제외한 기업

수집하지 않는다. 플랫폼에서 이 기업 공고가 나와도 fit-reviewer가 뺀다. 상황이 바뀌면 위 표로 옮긴다.

| 기업    | 이유                                                                                             | 확인일     |
| ------- | ------------------------------------------------------------------------------------------------ | ---------- |
| 발란    | 2026-02-24 파산 선고                                                                             | 2026-10-07 |
| 위메프  | 2025-09-09 회생 절차 폐지, 2025-11-10 파산 선고                                                  | 2026-10-07 |
| 티몬    | 2025-08 오아시스 인수로 회생 종결. 서비스 재개가 두 번 무산됐고 사이트에 재오픈 연기 공지만 있다 | 2026-10-07 |
| 브랜디  | 운영사 뉴넥스가 2025-09 회생 개시. 회생 절차 진행 중                                             | 2026-10-07 |
| 트렌비  | 자사 채용 페이지 없음, 공개 공고 0건, 매출 절반 감소 보도                                        | 2026-10-07 |
| 우리FIS | 2024-01 IT 거버넌스 개편으로 직원 약 90%가 우리은행, 우리카드로 이동                             | 2026-10-07 |
| 핀크    | 2024-09 핵심 서비스인 핀크머니 송금, 충전 종료                                                   | 2026-10-07 |
| GS SHOP | 2021-07 GS리테일에 합병. GS리테일 행에서 함께 수집한다                                           | 2026-10-07 |

# 회사 검증 출처

company-vetter가 읽는다. 2026-10-12에 표본 회사 5곳(클로버추얼패션, 페어리, 씨메스로보틱스, 넥스트증권, 코딧)에 직접 요청해 응답을 확인한 방법만 적었다. 요청이 실패하거나 응답 모양이 바뀌었으면 결과 파일의 `evidence`에 실패한 URL을 남기고 다음 출처로 넘어간다.

HTML을 받을 때는 Chrome 전체 User-Agent를 쓴다.

```bash
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36'
```

## 목차

- 쓰는 출처: 국민연금 가입 사업장 파일, 원티드, 사람인, 구글 뉴스 RSS, THE VC, 블라인드, DART, GitHub, 공고 본문
- 쓰지 않는 출처: 크레딧잡, 혁신의숲, THE VC API, 잡코리아 회사 페이지, 잡플래닛, 체불사업주 명단, 웹 아카이브, 네이버 뉴스
- 표본 적용 결과

## 쓰는 출처

| 출처          | 접근                          | 얻는 값                                                             | 회사당 요청 |
| ------------- | ----------------------------- | ------------------------------------------------------------------- | ----------- |
| 국민연금 파일 | curl로 실행마다 2개 받기      | 전체 사업장의 가입자 수, 12개월 전 가입자 수, 업종, 주소, 가입 상태 | 0           |
| 원티드        | curl                          | 회사 ID, 국민연금 직원 수, 매출, 홈페이지, 설립연도, 운영 상태      | 1~2         |
| 사람인        | curl                          | 24개월 직원 수 추이(입사, 퇴사), 기업형태, 대표자, 매출, 영업이익   | 3           |
| 구글 뉴스 RSS | curl                          | 회생, 파산, 체불, 구조조정 보도와 투자 유치 보도                    | 0.1~2       |
| THE VC        | WebSearch, 막히지 않으면 curl | 최근 투자 라운드와 날짜, 상장 여부, 폐업 여부                       | 1~2         |
| 블라인드      | curl                          | 평점, 리뷰 수, 회사 도메인                                          | 1           |
| DART          | curl(쿠키 필요)               | 상장 시장, 최근 1년 공시 제목                                       | 2           |
| GitHub        | curl                          | 회사 GitHub 조직과 공개 저장소 수                                   | 1~2         |
| 공고 본문     | 파일 읽기 또는 curl           | 기술 스택                                                           | 0~1         |

### 국민연금 가입 사업장 파일

공공데이터포털 `https://www.data.go.kr/data/15083277/fileData.do`의 CSV다. 페이지에 "파일데이터는 로그인 없이 다운로드를 통해 이용하실 수 있습니다", 이용허락범위 "제한 없음", 업데이트 주기 "월간"이 적혀 있다. 2026-10-12 기준 최신 파일은 `_20260923`(자료생성년월 2026-08, 591,028행, 115MB, cp949)이고 다음 등록 예정일은 2026-10-26이다. 과거 판이 월별로 129개 남아 있어 12개월 전 판도 받을 수 있다.

한 번 받으면 배치 전체의 직원 수와 1년 증감을 요청 없이 조회한다. 실행마다 최신 판과 12개월 전 판 두 개만 받고, 이미 있으면 다시 받지 않는다. 받는 데 최신 판 36초, 12개월 전 판 10초가 걸렸다.

```bash
mkdir -p _cache/nps
P=15083277
cur=$(curl -s -A "$UA" "https://www.data.go.kr/data/$P/fileData.do" | grep -o "fn_fileDataDown('$P', 'uddi:[^']*'" | head -1 | grep -o "uddi:[^']*")
curl -s -A "$UA" -X POST "https://www.data.go.kr/tcs/dss/selectHistAndCsvData.do" --data "publicDataPk=$P&publicDataDetailPk=$cur" \
  | perl -0ne 'while(/data-public-pk="(uddi:[^"]+)".*?내역_(\d{8})/gs){print "$2 $1\n"}' > _cache/nps/hist.txt
# 다운로드 주소: 판 식별자(uddi)로 atchFileId를 받아 만든다
nps_url(){ curl -s -A "$UA" -X POST "https://www.data.go.kr/tcs/dss/selectFileDataDownload.do" \
  --data "publicDataPk=$P&publicDataDetailPk=$1&fileDetailSn=1&publicDataTyCode=PR0051" \
  | jq -r '"https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId=\(.atchFileId)&fileDetailSn=\(.fileDetailSn)&insertDataPrcus=N"'; }
```

- 최신 판의 등록일(`YYYYMMDD`)은 페이지 제목 "국민연금 가입 사업장 내역_20260923"에 있다. 최신 판은 `nps_url $cur`, 12개월 전 판은 `hist.txt`에서 등록일이 1년 앞 같은 달(`202509`로 시작)인 줄의 uddi로 받는다.
- `_cache/nps/nps_{등록일}.csv`로 저장한다. 같은 이름 파일이 있으면 받지 않는다.
- 열: 자료생성년월, 사업장명, 사업자등록번호(앞 6자리), 사업장가입상태코드(1 등록, 2 탈퇴), 사업장도로명상세주소(번지 없이 도로명까지), 사업장업종코드명, 적용일자, 탈퇴일자, 가입자수, 신규취득자수, 상실가입자수.
- 사업자등록번호는 앞 6자리뿐이라 다른 회사와 겹친다. 12개월 전 행은 번호가 같은 행 중 이름이 같은 행, 없으면 도로명 주소가 같은 행으로 잇는다. 씨메스로보틱스는 2025-08에 "주식회사 씨메스", 2026-08에 "씨메스로보틱스 주식회사"였고 번호(220888)와 주소가 같았다.

배치의 회사 이름 전부를 한 번에 넣는다. 두 파일을 읽는 데 10초 걸렸다.

```bash
python3 -I - _cache/nps/nps_20260923.csv _cache/nps/nps_20250923.csv "클로버추얼패션" "코딧" <<'EOF'
import csv, json, re, sys
def norm(s): return re.sub(r"\s|주식회사|유한회사|\(주\)|（주）|㈜|\(유\)|\([^)]*\)", "", s).lower()
def load(path):
    rows = {}
    with open(path, encoding="cp949", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            rows.setdefault(norm(r["사업장명"]), []).append(r)
    return rows
now, ago = load(sys.argv[1]), load(sys.argv[2])
by_no = {}
for rs in ago.values():
    for r in rs: by_no.setdefault((r["사업자등록번호"], r["사업장형태구분코드 1 법인 2 개인"]), []).append(r)
for name in sys.argv[3:]:
    out = []
    for r in now.get(norm(name), []):
        same_no = by_no.get((r["사업자등록번호"], r["사업장형태구분코드 1 법인 2 개인"]), [])
        prev = [x for x in same_no if norm(x["사업장명"]) == norm(r["사업장명"])] or [x for x in same_no if x["사업장도로명상세주소"] == r["사업장도로명상세주소"]]
        p = int(prev[0]["가입자수"]) if len(prev) == 1 else None
        n = int(r["가입자수"])
        out.append({"nps_name": r["사업장명"], "biz_no6": r["사업자등록번호"], "status": r["사업장가입상태코드 1 등록 2 탈퇴"], "left_on": r["탈퇴일자"] or None,
                    "industry": r["사업장업종코드명"], "address": r["사업장도로명상세주소"], "month": r["자료생성년월"], "headcount": n,
                    "headcount_1y_ago": p, "change_1y": round((n - p) / p, 2) if p else None})
    print(json.dumps({"query": name, "matches": out}, ensure_ascii=False))
EOF
```

- 회사마다 한 줄씩 `matches`가 나온다. 이름을 법인 표기와 공백, 괄호 안 영문명을 지우고 비교한다("주식회사코딧(CODITCorp.)"이 "코딧"과 맞는다).
- `matches`가 비면 국민연금에 그 이름이 없다. 사람인 검색으로 정식 법인명을 얻어 다시 넣는다. 페어리는 두 파일 모두에 없었다.
- `matches`가 둘 이상이면 `address`와 공고 근무지로 고른다.
- 표본 4곳의 값은 사람인 `EmployeeChart`, THE VC 임직원 수와 같았다(클로버추얼패션 188명에서 200명, 씨메스로보틱스 173명에서 192명, 넥스트증권 115명에서 185명, 코딧 18명에서 18명).
- 업종이 "임시 및 일용 인력 공급업"(2026-08 기준 1,015곳)이나 "상용 인력 공급 및 인사관리 서비스업"(199곳)이면 파견 회사로 본다.

### 원티드

회사 이름으로 회사 ID를 찾는다.

```bash
curl -s -A "$UA" "https://www.wanted.co.kr/api/chaos/search/v1/autocomplete?query={회사명 URL 인코딩}" \
  | jq -c '.companies[] | {id, name, tags: [.company_tags[].title]}'
```

- 원티드 공고 URL(`/wd/{job_id}`)이 있으면 이름 검색 대신 `GET https://www.wanted.co.kr/api/v4/jobs/{job_id}`의 `.job.company.id`를 쓴다. 이름이 같은 다른 회사를 고를 일이 없다.
- 후보가 여럿이면 `tags`(인원 구간, 업종)와 회사 페이지의 홈페이지로 고른다. "페어리"는 페어리(44483)와 페어리테크(46485)가 함께 나왔다.

회사 페이지 원본 HTML의 `__NEXT_DATA__`에 서버가 넣어 둔 값이 있다. `GET https://www.wanted.co.kr/api/v4/companies/{id}`도 응답하지만 직원 수와 매출이 없어서 회사 페이지를 읽는다.

```bash
curl -s -A "$UA" "https://www.wanted.co.kr/company/{id}" \
  | perl -0ne 'print $1 if /<script id="__NEXT_DATA__"[^>]*>(.*?)<\/script>/s' \
  | jq '.props.pageProps.dehydrateState.queries[] | select(.queryKey[0] == "companyInfo" or .queryKey[0] == "companySummary") | .state.data'
```

| 위치                                   | 값                                                                                           |
| -------------------------------------- | -------------------------------------------------------------------------------------------- |
| `companyInfo.status`                   | `RUNNING`이면 원티드가 운영 중으로 본다. 갱신이 늦을 수 있다(페어리는 폐업 후에도 `RUNNING`) |
| `companyInfo.link`, `foundedYear`      | 홈페이지, 설립연도                                                                           |
| `companyInfo.regNoHash`                | 사업자등록번호 해시. 같은 법인인지 볼 때 쓴다                                                |
| `companyInfo.companyTags[].title`      | "누적투자100억이상", "인원급성장", "51~300명" 같은 태그                                      |
| `companySummary.employee`              | `total`(국민연금 직원 수), `updatedAt`. `hired`, `left`는 표본 5곳 모두 null이었다           |
| `companySummary.sales`                 | `total`(원), `updatedAt`(회계연도 말일), `source`(KODATA)                                    |
| `companySummary.detail.classNameByNts` | 국세청 업종                                                                                  |
| `companyHire.jobs[]`                   | 열린 공고. `category_tags[].parent_id`가 518이면 개발 직군                                   |

공고 상세 `GET https://www.wanted.co.kr/api/v4/jobs/{job_id}`의 `.job.skill_tags[].title`이 기술 태그다. 비어 있는 공고(넥스트증권 388905)도 있다. 공고 페이지(`https://www.wanted.co.kr/wd/{job_id}`) JSON-LD의 `datePosted`는 마지막 갱신일이라 처음 올린 날로 쓰지 않는다(코딧 46260은 2026-10-07).

### 사람인

이름으로 회사를 찾고 `csn`을 얻는다. 검색 결과에 대표자와 설립일, 주소, 매출과 영업이익이 함께 나와서 2차 검증은 이 요청 하나로 시작한다.

```bash
curl -s -A "$UA" "https://www.saramin.co.kr/zf_user/search/company?searchword={회사명 URL 인코딩}"
```

- 결과마다 `<h2 class="corp_name">` 안에 `company-info/view?csn={csn}` 링크와 회사명이 있고, 이어지는 블록에 설립일, 대표자명, 업종, 기업주소가 있다. 재무를 공개한 회사는 "재무정보 매출액 112억 영업이익 - 174.5억 (2025년 기준)"과 평균연봉, 상장사는 "코스닥 상장 기업" 같은 태그도 있다. 응답이 2MB 남짓이라 앞의 5건만 본다.
- 법인 표기가 붙은 이름("씨메스로보틱스(주)")으로 나온다. 대표자명과 설립일로 원티드나 THE VC에서 찾은 회사와 같은지 본다. "페어리"는 다섯 건이 모두 대표자와 주소가 달라 맞는 회사가 없었다.

기업정보 페이지:

```bash
curl -s -A "$UA" "https://www.saramin.co.kr/zf_user/company-info/view?csn={csn}" \
  | perl -ne 'print "$1\n" if /new EmployeeChart\((\{.*?\})\)/'
```

- `EmployeeChart`의 `total`, `hired`, `left`가 최근 24개월 국민연금 가입자 수와 입사, 퇴사 인원이고 `date`가 `"2024.9"` 형식의 월이다. 마지막 값이 최신 달이다. 1년 증감은 마지막 값과 그 12개 앞의 값으로 계산한다.
- 같은 페이지의 `기업형태:` 뒤에 "중소기업, 코스닥, 주식회사, 외부감사법인" 같은 값이 있다. "코스닥", "코스피"가 있으면 상장사다.
- 출처 안내 문구에 따르면 사원수는 국민연금, 매출액과 대표자명은 NICE평가정보다.

재무 탭:

```
GET https://www.saramin.co.kr/zf_user/company-info/view-inner-finance?csn={csn}
```

- 태그를 걷어낸 본문에 "매출액 도움말 … 2025년 기준 112억 578만원 … 2022 46억 5,861만원 2023 …"과 "영업이익 도움말 … 2025년 기준 - 174억 5,099만원 …"이 있다. 숫자 앞의 "- "는 음수다.
- "112억 578만원"은 11,205,780,000원으로 바꿔 적는다.
- 회사가 재무를 감춘 곳(클로버추얼패션, 코딧)은 두 문장이 없다. 그때는 원티드 `companySummary.sales`의 매출만 쓰고 영업이익은 null로 둔다.

### 구글 뉴스 RSS

레드 플래그 기사:

```bash
q='"{회사명}" (회생 OR 파산 OR 폐업 OR 체불 OR 정산 OR 구조조정 OR 희망퇴직 OR 권고사직 OR 감원) when:1y'
curl -s -A "$UA" "https://news.google.com/rss/search?q=$(jq -rn --arg s "$q" '$s|@uri')&hl=ko&gl=KR&ceid=KR:ko"
```

- `<item>`마다 `<title>`(기사 제목 - 언론사), `<link>`(구글 뉴스 링크, 열면 원문으로 간다), `<pubDate>`가 있다.
- `OR`과 `when:1y`가 동작한다. `"위메프" 회생 when:1y`는 46건, `"넥스트증권" (…) when:1y`는 2건이 왔다.
- 키워드가 제목에 없는 기사도 섞여 온다. 넥스트증권 2건은 MTS 출시와 조직 개편 기사였다. 제목에 레드 플래그가 실제로 적힌 기사만 쓴다.
- 이름이 흔한 회사는 따옴표 이름 뒤에 제품명이나 대표자명을 붙인다. 표본에서는 `"코딧" 정지은`, `"씨메스" 로봇`, `"세일즈클루"`로 찾았다.

여러 회사를 한 번에 볼 때는 따옴표 이름 10개를 OR로 묶는다. 1차 검증은 이 방법을 쓴다.

```bash
q='("위메프" OR "티몬" OR "클로버추얼패션" OR "넥스트증권" OR "코딧" OR "씨메스로보틱스" OR "발란" OR "정육각" OR "왓챠" OR "메쉬코리아") (회생 OR 파산 OR 체불 OR 정산 OR 구조조정 OR 희망퇴직 OR 권고사직) when:1y'
```

- 2026-10-12에 위 요청은 100건을 줬다. 티몬, 왓챠, 정육각, 발란의 회생과 파산 기사가 섞여 나왔다. RSS 한 번에 100건까지만 오므로 기사가 많은 회사의 기사로 100건이 차면 다른 회사 기사가 빠진다. 그때는 다섯 곳씩 나눠 다시 보낸다.
- 인코딩한 쿼리 길이는 729자였고 200을 받았다.
- 결과 제목에서 회사 이름을 찾아 회사별로 나눈다. 이름이 다른 회사 이름에 들어가는 회사(예: "페어리"는 국민연금 파일에 "엘린페어리", "페어리테크" 등 다섯 곳)는 다른 회사 기사가 섞일 수 있으니 레드 플래그 후보가 나오면 그 회사만 업종이나 제품명을 붙여 다시 확인한다.

투자 기사는 같은 방법으로 `"{회사명}" (투자 유치 OR 유상증자 OR 시리즈) when:2y`를 보낸다. 클로버추얼패션 500억 원(2024-12), 넥스트증권 150억 원(2026-07) 기사가 나왔다.

### THE VC

회사 페이지 `https://thevc.kr/{slug}`의 meta description에 투자와 상태가 한 문단으로 있다. 예: "2009년 1월에 설립된 … 현재 비상장 기업입니다 … 가장 최근에는 2024년 12월에 Series C 투자를 유치했습니다 … 2026년 8월 기준 임직원 수는 200명입니다." 폐업한 회사는 "2025년 10월에 폐업한"으로 나온다.

slug는 WebSearch로 찾는다. 사이트 안 검색(`/search?keyword=`)은 curl에 404를 준다.

```
WebSearch(query: "{회사명} 기업정보 투자", allowed_domains: ["thevc.kr"])
```

- 결과 제목이 "회사명(대표 제품) - 기업정보"다. 같은 이름이 여럿 나온다. "페어리"는 fairy(몬다), fairytech(페어리SDK), pairy(세일즈클루) 셋이었고 "코딧"은 codit(코딧 서치) 옆에 kodit(신용보증기금)이 나왔다. 대표 제품과 대표자명으로 고른다.
- WebSearch 응답의 요약 문장에 meta description 내용이 옮겨져 온다. 표본 네 번의 요약에는 라운드 이름과 상장 여부, 임직원 수가 있었고, 코딧 요약에서는 라운드 날짜(2022-11)가 빠져 있었다. 빠진 값이 있을 때만 curl을 보낸다.

회사 페이지는 받지 않는다(2026-10-12 사용자 결정). 페이지 아래에 "모든 콘텐츠의 저작권은 더브이씨에 있으며 무단 사용, DB화 시 민형사상 책임"이라는 문구가 있다. 검색 요약에서 읽은 라운드와 날짜, 상장이나 폐업 상태만 결과 파일에 옮긴다. 요약에 값이 빠지면 구글 뉴스 RSS와 DART로 채운다.

- 조사할 때 회사 페이지를 10번 남짓 받자 `HTTP 202`와 빈 본문, `x-amzn-waf-action: challenge` 헤더가 왔다. 페이지를 받지 않으면 이 차단도 생기지 않는다.
- `robots.txt`가 `/api/`를 막는다. API도 쓰지 않는다.

### 블라인드

```bash
curl -s -A "$UA" "https://www.teamblind.com/kr/company/{블라인드 회사명 URL 인코딩}/reviews" \
  | grep -o '"@type":"EmployerAggregateRating"[^}]*}[^}]*}'
```

- `ratingValue`(5점 만점 문자열), `ratingCount`(리뷰 수), `itemReviewed.sameAs`(회사 도메인)가 나온다. 도메인으로 같은 회사인지 확인한다.
- 회사명은 블라인드 표기를 써야 한다. 없는 이름은 404다. "씨메스로보틱스"는 404, "씨메스"는 200(도메인 cmesrobotics.ai)이었고 "CLO"는 404, "클로버추얼패션"은 200이었다. 원티드와 사람인 이름으로 안 되면 사명 변경 전 이름이나 짧은 이름을 한 번 더 넣는다.
- `robots.txt`는 `/kr/company/`를 막지 않는다.

### DART

세션 쿠키 없이 보내면 302를 받는다. 메인 페이지로 쿠키를 받은 뒤 같은 쿠키와 Referer, `X-Requested-With`를 붙인다. 앞서 받은 쿠키로 보낸 요청이 빈 결과를 준 적이 있고 새로 받은 쿠키로는 나왔다. 회사마다 쿠키를 새로 받는다.

```bash
curl -s -A "$UA" -c dart.jar "https://dart.fss.or.kr/dsab007/main.do" -o /dev/null
curl -s -A "$UA" -b dart.jar -e "https://dart.fss.or.kr/dsab007/main.do" -H 'X-Requested-With: XMLHttpRequest' \
  -X POST "https://dart.fss.or.kr/dsab007/detailSearch.ax" \
  --data-urlencode "textCrpNm={회사명}" \
  --data "currentPage=1&maxResults=15&maxLinks=10&sort=date&series=desc&textCrpCik=&startDate={1년 전 YYYYMMDD}&endDate={오늘 YYYYMMDD}&finalReport=recent&businessCode=all&autoSearch=N"
```

- 응답은 HTML 표다. 행마다 회사명 앞의 `<span class="tagCom_{kospi|kosdaq|konex|etc}">`가 시장 구분이다. `etc`는 기타법인이다. 표본의 `etc` 두 곳은 감사보고서만 냈다.
- 보고서명과 접수일자, 접수번호(`rcpNo=`)가 있다. 공시 링크는 `https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcpNo}`.
- 표본 결과: 씨메스로보틱스는 `kosdaq`으로 반기보고서와 공급계약 공시가, 클로버추얼패션과 넥스트증권은 `etc`로 감사보고서(2025.12)만 왔다. 페어리와 코딧은 "조회 결과가 없습니다"였다.
- 감사보고서 본문(재무제표)은 문서 뷰어를 여러 번 거쳐야 해서 확인하지 않았다. 재무 숫자는 사람인과 원티드에서 읽는다.

### GitHub

인증 없는 API는 시간당 60회(검색은 분당 10회)다. 여러 배치가 같은 IP에서 돌므로 프로필이 개발 직군이고 A 등급 후보인데 지원 직무 조직 근거가 하나도 없을 때만 쓴다.

```bash
curl -s "https://api.github.com/search/users?q={영문명}+type:org&per_page=5" | jq -c '[.items[].login]'
curl -s "https://api.github.com/orgs/{login}" | jq -c '{login, name, blog, public_repos, updated_at}'
```

- `blog` 도메인이 회사 홈페이지와 같을 때만 회사 조직으로 본다. `clo3d`(blog clo3d.com, 공개 저장소 4개)는 클로버추얼패션 조직이다. `Codit`(blog codit.eu)은 홈페이지가 다른 회사다. `next-securities`는 blog가 비고 공개 저장소가 0개라 근거로 쓰지 않았다.

### 공고 본문

- 발굴 모드에서는 `_discover/03_candidates.json`의 그 회사 공고에 수집 단계가 뽑은 `skills`가 있다. 요청 없이 읽는다.
- `skills`가 비어 있으면 지원 직무 공고 하나의 상세를 연다. 개발 직군이면 원티드는 `skill_tags`, 나머지는 본문에서 기술 이름을 찾는다. 넥스트증권 리멤버 공고(344750)에서 Next.js, React, TypeScript를 찾았다. 개발 밖 직군이면 본문에서 팀 구성과 주요 업무를 읽는다.
- 나인하이어 공고 페이지는 curl과 WebFetch가 429를 받는다(`job-collection/references/career-sites.md` 나인하이어 절). 기술 스택이 없으면 그대로 둔다.

## 쓰지 않는 출처

| 출처                       | 확인한 것                                                                                                                                                                                                                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 크레딧잡                   | `robots.txt`가 `User-agent: *`에 `Disallow: /`다. curl은 어느 경로든 광고 차단 확인 스크립트가 든 5KB "Redirecting..." 페이지를 받는다. 같은 국민연금 값을 공공데이터포털 파일에서 얻는다                                                                                                                 |
| 혁신의숲                   | 회사 페이지 본문에 "사전 승인 없는 데이터의 수집, 추출, 인공지능(AI) 학습과 활용 등을 금지"한다는 문구가 있다. 서버가 그린 HTML에는 고용인원, 매출액, 투자 단계 칸이 비어 있다                                                                                                                            |
| THE VC API                 | `robots.txt`가 `/api/`를 막는다. 회사 페이지 HTML만 읽는다                                                                                                                                                                                                                                                |
| 잡코리아 회사 페이지       | `https://www.jobkorea.co.kr/company/{id}`에 사원수와 연도별 매출, 영업이익이 있다(넥스트증권 2025 매출 462억 8천만원). 본문에 "게시된 정보는 무단으로 수집 및 배포할 수 없습니다"라는 문구가 있고, 사원수(넥스트증권 106명)는 출처 표기가 없어 국민연금 값(185명)과 맞지 않는다. 매출은 원티드로 대신한다 |
| 잡플래닛                   | curl은 검색과 회사 페이지 모두 403(Cloudflare)이다. Chrome에서는 `https://www.jobplanet.co.kr/companies/{id}` JSON-LD에 평점과 리뷰 수가 있다(클로버추얼패션 3.4, 63건). 검증 배치는 여럿이 함께 돌고 Chrome은 하나라 쓰지 않는다. 평점은 블라인드로 본다                                                 |
| 고용노동부 체불사업주 명단 | `https://www.moel.go.kr/info/defaulter/defaulterList.do`는 200을 주지만 표가 없고 지청별 목록을 스크립트로 불러온다. 회사명 검색이 없어 미확인. 2회 이상 유죄 확정 사업주만 실리므로 체불은 뉴스로 본다                                                                                                   |
| 웹 아카이브                | 오래 열린 공고의 과거 스냅샷을 보려 했다. `archive.org/wayback/available`은 스냅샷이 있다고 했지만 스냅샷 페이지는 202 빈 응답, CDX API는 "Temporarily Offline"이었다. 미확인                                                                                                                             |
| 네이버 뉴스 검색           | HTML은 200이지만 기사 제목과 링크가 스크립트 안에 섞여 있어 안정적으로 뽑지 못했다. 구글 뉴스 RSS를 쓴다                                                                                                                                                                                                  |

## 표본 적용 결과

2026-10-12에 위 방법으로 받은 값이다. 결과 JSON은 이 값으로 만들었다. 국민연금 파일의 직원 수는 사람인 열의 값과 같았다.

| 회사           | 원티드                            | 사람인 직원 수(2025.8에서 2026.8)                | THE VC                               | 블라인드           | 뉴스(1년)                                  | DART              |
| -------------- | --------------------------------- | ------------------------------------------------ | ------------------------------------ | ------------------ | ------------------------------------------ | ----------------- |
| 클로버추얼패션 | 833, NPS 195명, 매출 396억(2024)  | 188명에서 200명. 재무 탭 없음                    | Series C 2024-12, 비상장             | 4.0, 100건         | 레드 플래그 없음                           | etc, 감사보고서   |
| 페어리         | 44483, 고용보험 3명(2025-03 갱신) | 이름이 같은 다른 회사만 나옴                     | pairy, Seed 2022-12, 2025-10-21 폐업 | 404                | 기사 없음                                  | 결과 없음         |
| 씨메스로보틱스 | 9449, NPS 192명                   | 173명에서 192명. 2025 매출 112억, 영업손실 174억 | Series B 2022-03, KOSDAQ 475400      | "씨메스" 3.5, 66건 | 레드 플래그 없음                           | kosdaq, 정기 공시 |
| 넥스트증권     | 52490, NPS 164명                  | 115명에서 185명. 2025 매출 462억, 영업손실 104억 | 라운드 기록 없음, 비상장             | 2.6, 5건           | 레드 플래그 없음. 150억 투자 유치(2026-07) | etc, 감사보고서   |
| 코딧           | 15667, NPS 19명, 매출 7.2억(2024) | 18명에서 18명. 재무 탭 없음                      | Pre-A 2022-11, 비상장                | 3.0, 5건           | 레드 플래그 없음                           | 결과 없음         |

- 페어리 공고(`https://pairy.ninehire.site/job_posting/spYioJeA`, 주니어 React 프론트엔드 엔지니어)는 2026-10-12에 Chrome으로 열었을 때 "상시 모집"으로 열려 있었다. 법인은 폐업했는데 공고가 남은 경우다. 세일즈클루 사이트(salesclue.io)도 200으로 열렸다.
- 코딧의 원티드 개발 공고 ID는 46260으로 다른 공고(39만 번대)보다 훨씬 앞서 있어 오래 열린 공고로 보인다. 처음 올린 날을 확인할 출처가 없어(원티드 `datePosted`는 2026-10-07 갱신일, 웹 아카이브 미확인) C 등급 근거로 쓰지 않았다.

1차 검증에서 표본 4곳은 국민연금 파일에서 바로 찾아 요청 없이 직원 수와 1년 증감을 얻었고, 묶음 뉴스 검색에서 레드 플래그 기사가 없어 2차로 넘어갔다. 페어리는 국민연금에 없어 사람인 검색 1회(맞는 회사 없음)와 THE VC WebSearch 1회(2025-10-21 폐업)로 1차에서 X로 끝났다.

2차 검증은 씨메스로보틱스 기준 curl 10회(원티드 2, 사람인 3, THE VC 1, 블라인드 1, 뉴스 1, DART 2)를 순서대로 보내 5초가 걸렸다. 이때 THE VC는 WAF 확인 응답(202, 빈 본문)을 줬다. 2차 표의 순서대로 하면 사람인은 검색 1회로 줄고 THE VC는 WebSearch 1회로 바뀐다.

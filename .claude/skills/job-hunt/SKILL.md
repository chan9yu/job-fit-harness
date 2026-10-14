---
name: job-hunt
description: "이력서 기반 채용공고 탐색 하네스의 유일한 오케스트레이터. resume/의 이력서로 연차와 직무에 맞는 공고를 찾아 output/YYYY-MM-DD.md 한 장으로 남긴다. 개발 직군뿐 아니라 기획, 디자인, 데이터 분석, 마케팅, 영업 같은 직군 이력서도 다룬다. 실행할 때 범위를 고르게 한다: 네임드 기업(빅테크인 네카라쿠배당토직야와 몰두센, 대기업 계열사, 유니콘과 네임밸류)은 레지스트리 자사 채용 페이지로, 레지스트리 밖 회사(성장 스타트업, 초기 스타트업, 상장사와 중견, 중소)는 채용 플랫폼에서 넓게 찾고 회사를 검증한다. '채용공고 찾아줘', '이직할 곳 찾아줘', '내 연차에 맞는 공고', '네카라쿠배만', '대기업 공고', '숨은 회사 찾아줘', '네임드 말고', '스타트업 위주로', '시리즈 A 회사', '전부 찾아줘' 같은 요청이면 반드시 이 스킬을 쓴다. 후속 요청도 이 스킬이다: 다시 실행, 재실행, 범위 바꿔서 다시, 특정 기업이나 플랫폼만 다시, 회사 검증만 다시, 리포트만 다시, 이력서 바꿨으니 다시, 기업 목록 수정. 이력서 문장 첨삭이나 자기소개서 작성은 이 스킬이 아니다."
---

# job-hunt

이력서로 프로필을 만들고, 사용자가 고른 범위에서 공고를 모아 판정한 뒤 리포트 한 장을 쓴다. 이 스킬을 실행하는 메인 세션이 오케스트레이터다.

## 범위

| 질문               | 범위                                                                             | 찾는 방법                                                                    |
| ------------------ | -------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| 네임드 기업        | `빅테크`: 네카라쿠배당토직야, 몰두센과 그 계열사                                 | `data/companies.md`의 같은 이름 절을 자사 채용 페이지로 읽는다 (네임드 흐름) |
|                    | `대기업 계열사`: 삼성, LG, SK, 현대차, CJ, 금융그룹 IT 등                        |                                                                              |
|                    | `유니콘과 네임밸류`: 무신사, 컬리, 오늘의집, 게임사, 중견 IT 등                  |                                                                              |
| 레지스트리 밖 회사 | `성장 스타트업`: 시리즈 B 이상 (growth)                                          | 채용 플랫폼에서 넓게 찾고 회사를 검증한 뒤 단계로 거른다 (발굴 흐름)         |
|                    | `초기 스타트업`: 시드부터 시리즈 A (early)                                       |                                                                              |
|                    | `상장사와 중견, 중소`: 상장사이거나 투자 이력이 확인되지 않는 회사 (established) |                                                                              |

두 질문의 범위는 겹치지 않는다. 레지스트리에 있는 회사는 네임드 범위로만, 없는 회사는 레지스트리 밖 범위로만 나온다.

## 실행 모드: 서브 에이전트

수집 배치와 검증 배치가 서로 독립이고 결과는 JSON 파일로 모은다. 네임드 흐름과 발굴 흐름은 한 메시지에서 함께 시작해 병렬로 돈다. 배치 나누기, 1차 거르기, 캐시, 판정 입력, 리포트 합치기는 `scripts/`의 스크립트가 맡는다. 스크립트는 저장소 루트에서 `python3 -I .claude/skills/job-hunt/scripts/{이름}.py`로 실행한다.

| 에이전트           | subagent_type        | 스킬             | 흐름         | 출력                                                                            |
| ------------------ | -------------------- | ---------------- | ------------ | ------------------------------------------------------------------------------- |
| resume-analyst     | `resume-analyst`     | resume-profiling | 공통         | `_workspace/01_profile.json`                                                    |
| job-scout          | `job-scout`          | job-collection   | 네임드, 발굴 | `_workspace/02_postings_career-*.json`, `_discover/02_postings_d-*.json`        |
| browser-scout      | `browser-scout`      | job-collection   | 네임드, 발굴 | `_workspace/02_postings_browser.json`, `_discover/02_postings_d-jobplanet.json` |
| company-vetter     | `company-vetter`     | company-vetting  | 발굴         | `_discover/04_vetting_vet-*.json`                                               |
| fit-reviewer       | `fit-reviewer`       | fit-report       | 네임드       | `_workspace/06_named.md`, `_workspace/04_dropped.md`                            |
| discovery-reviewer | `discovery-reviewer` | discovery-report | 발굴         | `_discover/06_discover.md`, `_discover/05_dropped.md`                           |

모든 Agent 호출에 `model: "opus"`를 넣는다. browser-scout는 Chrome 하나를 쓰므로 어느 시점에도 하나만 돌린다.

작업 폴더는 `_workspace/`(프로필, 범위, 네임드 흐름), `_discover/`(발굴 흐름), `_cache/`(회사 검증 캐시, 국민연금 파일)다. 모두 git에서 빠진다.

## Phase 0: 컨텍스트 확인과 범위 정하기

1. `resume/`에 `preferences.md` 말고 파일이 없으면 멈추고 이력서를 넣어 달라고 알린다.
2. 이력서 해시를 구한다: `cat resume/* | shasum -a 256 | cut -c1-16`
3. 실행 모드를 정한다.

| 상황                              | 모드        | 할 일                                                                                                                                                             |
| --------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_workspace/` 없음                | 초기 실행   | `mkdir -p _workspace _discover`                                                                                                                                   |
| `_workspace/` 있고 아래 부분 요청 | 부분 재실행 | 아래 표대로. 범위는 `_workspace/00_scope.json`을 그대로 쓴다                                                                                                      |
| `_workspace/` 있고 그 밖의 요청   | 새 실행     | 같은 시각 `ts=$(date +%Y%m%d_%H%M%S)`로 `mv _workspace _workspace_$ts`, `_discover`가 있으면 `mv _discover _discover_$ts`, 그리고 `mkdir -p _workspace _discover` |

| 부분 요청 예                       | 다시 돌릴 것                                                                                              |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------- |
| "토스만 다시"                      | 그 기업만 담은 배치 `rerun-{영문 슬러그}`를 접근 방식에 맞는 scout로 돌리고 Phase 3 네임드 판정과 Phase 4 |
| "원티드만 다시", "잡플래닛만 다시" | 그 플랫폼 배치만 Phase 2로 돌리고 Phase 3 발굴부터                                                        |
| "회사 검증만 다시"                 | Phase 3 발굴의 `select`부터. 캐시를 무시하려면 `--cache`에 없는 파일 경로를 준다                          |
| "리포트만 다시", "검토는 빼 줘"    | 두 판정 에이전트를 피드백과 함께 다시 부르고 Phase 4                                                      |
| "연차를 6년으로 봐줘", "판교만"    | `resume/preferences.md`에 반영하고 새 실행                                                                |

4. 범위를 정한다. 위에서부터 처음 맞는 방법을 쓴다.

| 방법          | 조건                                                 | 범위                                           |
| ------------- | ---------------------------------------------------- | ---------------------------------------------- |
| 요청에 드러남 | "네카라쿠배만", "빅테크만"                           | 네임드 `빅테크`                                |
|               | "대기업", "대기업 계열사"                            | 네임드 `대기업 계열사`                         |
|               | "숨은 회사", "네임드 말고", "덜 알려진", "발굴"      | 레지스트리 밖 셋 다                            |
|               | "스타트업 위주로"                                    | 레지스트리 밖 `성장 스타트업`, `초기 스타트업` |
|               | "시리즈 A", "초기 스타트업"                          | 레지스트리 밖 `초기 스타트업`                  |
|               | "전부", "모두", "다 찾아줘"                          | 여섯 범위 전부                                 |
| 지난 실행     | "다시 실행", "다시 찾아줘"처럼 범위 말이 없는 재실행 | 가장 최근 `_workspace_*/00_scope.json`         |
| 희망 조건     | `resume/preferences.md`에 `범위:` 줄이 있음          | 그 줄의 범위 이름들                            |
| 메뉴          | 위에 해당하지 않음                                   | 아래 AskUserQuestion으로 묻는다                |

"유니콘"처럼 네임드와 레지스트리 밖 어느 쪽으로도 읽히는 말만 있으면 메뉴로 묻는다.

메뉴는 두 단계다. AskUserQuestion은 질문 하나에 선택지를 4개까지만 둘 수 있어서, 첫 화면에서 묶음을 고르고 세부 선택은 필요할 때만 띄운다.

첫 화면은 질문 하나, `multiSelect: false`다.

```
질문: "어떤 범위로 찾을까요?"  (header: "범위")
  - 전부 (Recommended): 네임드 기업 3개와 레지스트리 밖 3개 모두. 레지스트리 밖 회사 검증 때문에 1시간 남짓 더 걸립니다
  - 네임드 기업만: 빅테크, 대기업 계열사, 유니콘과 네임밸류
  - 레지스트리 밖만: 성장 스타트업, 초기 스타트업, 상장사와 중견, 중소
  - 직접 고르기: 다음 화면에서 범위를 하나씩 고릅니다
```

"직접 고르기"를 고르면 두 번째 화면을 띄운다. 질문 두 개이고 둘 다 `multiSelect: true`다.

```
질문 1: "네임드 기업 중 어디를 볼까요? 자사 채용 페이지로 정확하게 읽습니다."  (header: "네임드")
  - 빅테크: 네카라쿠배당토직야, 몰두센과 계열사
  - 대기업 계열사: 삼성, LG, SK, 현대차, CJ, 금융그룹 IT 등
  - 유니콘과 네임밸류: 무신사, 컬리, 오늘의집, 게임사, 중견 IT 등
  - 안 봄
질문 2: "레지스트리 밖 회사도 볼까요? 채용 플랫폼에서 넓게 찾고 회사를 검증합니다. 고르면 1시간 남짓 더 걸립니다."  (header: "그 밖")
  - 성장 스타트업: 시리즈 B 이상
  - 초기 스타트업: 시드부터 시리즈 A
  - 상장사와 중견, 중소: 투자 이력이 확인되지 않는 회사
  - 안 봄
```

"안 봄"과 다른 선택지를 함께 고르면 "안 봄"은 무시한다. 두 질문 모두 "안 봄"이면 범위가 없으니 다시 묻는다. 첫 화면에서 "Other"로 범위를 글로 적으면 위의 "요청에 드러남" 표로 읽는다. AskUserQuestion을 쓸 수 없는 환경이면 여섯 범위 전부로 진행한다.

5. 정한 범위를 저장한다.
   ```json
   {
   	"named": ["빅테크", "유니콘과 네임밸류"],
   	"discover": ["성장 스타트업"],
   	"source": "menu",
   	"chosen_at": "2026-10-12"
   }
   ```
   `_workspace/00_scope.json`에 쓰고, 고른 범위를 사용자에게 한 줄로 알린다.

## Phase 1: 프로필

직전 작업 폴더(`_workspace_*` 중 가장 최근)의 `01_profile.json`이 있고, `source_hash`가 Phase 0 해시와 같고, `role_family` 필드가 있으면 복사해서 쓴다. 아니면 resume-analyst를 부른다. `role_family`가 없는 프로필은 직무 일반화 이전에 만든 것이라 직무 코드를 고를 수 없다.

```
Agent(subagent_type: "resume-analyst", model: "opus", description: "이력서 프로필 추출",
  prompt: "이력서로 프로필을 만들어라. source_hash: {해시}. 출력: _workspace/01_profile.json")
```

- 직무(`role`, `role_family`)와 경력 연수, 핵심 역량을 사용자에게 한 줄로 알린다. `confidence`가 `low`면 `years_basis`를 보여 주고 확인받는다.
- 발굴 흐름을 고른 경우 `_workspace/01_profile.json`을 `_discover/01_profile.json`으로 복사한다.
- 경력이 3년 미만인데 레지스트리 밖 범위를 하나도 고르지 않았으면 한 줄로 알린다: "네임드 기업 공고는 3년 이상 요건이 많습니다. 레지스트리 밖 회사도 함께 보려면 범위를 바꿔 다시 요청하세요." 실행은 멈추지 않는다.

## Phase 2: 수집

고른 범위에 해당하는 것만 한 메시지에서 함께 띄운다. 모두 `run_in_background: true`.

**네임드 흐름** (네임드 범위가 하나 이상일 때)

```bash
python3 -I .claude/skills/job-hunt/scripts/make_batches.py --registry data/companies.md --sections "{고른 네임드 범위, 쉼표 구분}" --out-dir _workspace/batches
```

배치 파일(`_workspace/batches/career-N.md`)마다 job-scout를 하나씩 띄운다.

```
배치: career-{N}
프로필: _workspace/01_profile.json
대상: _workspace/batches/career-{N}.md의 표. 아래쪽 "계열사 행" 표는 따로 요청하지 않고 company 이름을 맞추는 데만 쓴다.
출력: _workspace/02_postings_career-{N}.json
```

**발굴 흐름** (레지스트리 밖 범위가 하나 이상일 때)

| 배치                       | 대상                                                                                                         |
| -------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `d-wanted`                 | 원티드                                                                                                       |
| `d-remember-jumpit-rallit` | 리멤버, 점핏, 랠릿                                                                                           |
| `d-saramin-jobkorea`       | 사람인, 잡코리아                                                                                             |
| `d-zighang-catch-linkedin` | 직행, 캐치, 링크드인. 직행은 "발굴 모드" 절, 캐치와 링크드인은 각 플랫폼 절을 따르고 상한만 300건으로 올린다 |
| `d-ats`                    | 그리팅, 나인하이어, recruiter.co.kr. "발굴 모드" 절의 "ATS 검색 넓히기"를 따른다                             |

```
배치: {batch} (발굴 모드)
프로필: _discover/01_profile.json
대상: {플랫폼 이름}
방법: .claude/skills/job-collection/references/platforms.md의 "직무 코드표"와 "발굴 모드" 절을 따른다. 직무 코드는 프로필 role_family로 고른다. 플랫폼당 300건까지 받는다.
레지스트리: data/companies.md. 표에 있는 기업과 "제외한 기업" 절의 기업 공고는 기록하지 않고 건너뛴다.
목록 응답에 연차가 있으면 상세를 열지 않는다. 플랫폼 회사 ID와 사업자등록번호가 목록에 있으면 company_id, business_number 필드에 남긴다.
출력: _discover/02_postings_{batch}.json
```

**browser-scout 하나** (아래 대상이 하나라도 있을 때)

- 네임드: `_workspace/batches/browser.md`가 있으면 그 기업들. 출력은 `_workspace/02_postings_browser.json`
- 발굴: 잡플래닛. 출력은 `_discover/02_postings_d-jobplanet.json`

두 대상을 한 에이전트에 맡기고 출력 파일을 둘 다 프롬프트에 적는다.

모든 완료 알림을 기다린다. 실패한 배치는 한 번 다시 띄우고, 또 실패하면 빼고 진행한다. 그다음 `_workspace/02_postings_career-*.json`의 `unreachable` 중 `reason`이 `js`인 항목이 있으면 browser-scout를 배치 `browser-2`로 한 번 더 띄운다(포그라운드, 출력 `_workspace/02_postings_browser-2.json`). 첫 browser-scout 결과에 `chrome_unavailable`이 있으면 띄우지 않는다.

## Phase 3: 판정과 회사 검증

네임드 판정과 발굴 검증을 겹쳐 돌린다. 네임드 흐름이 없으면 네임드 판정을, 발굴 흐름이 없으면 발굴 단계를 건너뛴다.

직전 리포트는 `output/????-??-??*.md` 중 가장 최근 파일이다. 없으면 "없음".

**네임드 판정** (백그라운드로 먼저 띄운다)

```
Agent(subagent_type: "fit-reviewer", model: "opus", run_in_background: true, description: "네임드 공고 판정",
  prompt: "프로필: _workspace/01_profile.json
수집 결과: _workspace/02_postings_*.json
레지스트리: data/companies.md
범위: {고른 네임드 범위}
직전 리포트: {경로 또는 없음}
출력: _workspace/06_named.md (fit-report 6절 형식의 절), _workspace/04_dropped.md
사용자 피드백: {부분 재실행일 때만}")
```

**발굴 검증** (네임드 판정이 도는 동안)

1. 1차 거르기와 검증 대상 고르기:
   ```bash
   python3 -I .claude/skills/job-hunt/scripts/prefilter.py --workspace _discover --registry data/companies.md
   python3 -I .claude/skills/job-hunt/scripts/vetting_cache.py select --workspace _discover --cache _cache/vetting.json --limit 120
   ```
   프로필 `notes`에 계약직을 허용한다고 적혀 있으면 `prefilter.py`에 `--allow-contract`를, 준하는 경력(동등역량) 공고도 본다고 적혀 있으면 `--allow-equivalent`를 붙인다. 단계(성장, 초기, 상장사와 중견, 중소)는 회사를 검증한 뒤에야 정해진다. 그래서 레지스트리 밖 범위를 일부만 골라도 검증 대상은 직무 점수순 120곳으로 같고 검증 시간도 줄지 않는다. 상한을 낮추면 고른 단계의 회사가 상한에 밀려 0건이 될 수 있으니 120 아래로 내리지 않는다. 두 스크립트가 출력한 건수를 사용자에게 한 줄로 알린다.
2. 국민연금 가입 사업장 파일을 준비한다. `.claude/skills/company-vetting/references/sources.md` 국민연금 절의 명령으로 최신 판과 12개월 전 판을 `_cache/nps/`에 받는다. 같은 이름 파일이 있으면 받지 않는다. 한 판이 115MB 안팎이고 받는 데 1분 남짓 걸린다. 실패해도 멈추지 않는다. company-vetter가 사람인 기업정보로 대신한다.
3. `_discover/03_to_vet.json`의 `to_vet`을 15곳 안팎씩 나눠 company-vetter를 한 메시지에서 함께 띄운다. 최대 6개, 모두 백그라운드다. 0곳이면 4로 간다.
   ```
   Agent(subagent_type: "company-vetter", model: "opus", run_in_background: true, description: "vet-{n} 회사 검증",
     prompt: "배치: vet-{n}
   대상 회사(회사명, 공고 제목과 URL, company_id, business_number): {to_vet 중 이 배치 몫을 JSON 그대로}
   프로필: _discover/01_profile.json (지원 직무 조직 근거를 role_family로 고른다)
   국민연금 파일: _cache/nps/의 최신 판과 12개월 전 판
   출력: _discover/04_vetting_vet-{n}.json")
   ```
   모든 완료 알림을 기다린 뒤 캐시에 합친다:
   ```bash
   python3 -I .claude/skills/job-hunt/scripts/vetting_cache.py merge --workspace _discover --cache _cache/vetting.json
   ```
4. 판정 입력을 만든다. 고른 단계만 남긴다(성장 스타트업은 growth, 초기 스타트업은 early, 상장사와 중견, 중소는 established).
   ```bash
   python3 -I .claude/skills/job-hunt/scripts/prepare_review.py --workspace _discover --segments {고른 단계 키, 쉼표 구분}
   ```
5. discovery-reviewer를 부른다.
   ```
   Agent(subagent_type: "discovery-reviewer", model: "opus", description: "레지스트리 밖 공고 판정",
     prompt: "판정 입력: _discover/05_review_input.json
   프로필: _discover/01_profile.json
   레지스트리: data/companies.md
   범위: {고른 레지스트리 밖 범위}
   직전 리포트: {경로 또는 없음}
   출력: _discover/06_discover.md (discovery-report 형식의 절), _discover/05_dropped.md
   1차 제외 건수: {prefilter.py가 출력한 사유별 건수}")
   ```

## Phase 4: 리포트 합치기

네임드 판정 완료 알림까지 받은 뒤 합친다. 출력 경로는 `output/$(date +%F).md`이고 이미 있으면 `-2`, `-3`을 붙인다.

```bash
python3 -I .claude/skills/job-hunt/scripts/assemble_report.py --out {출력 경로} --profile _workspace/01_profile.json --scope _workspace/00_scope.json --named _workspace/06_named.md --discover _discover/06_discover.md
```

고르지 않은 흐름의 절 파일은 없으니 스크립트가 건너뛴다.

## Phase 5: 보고

1. 리포트 경로와 절마다 추천, 검토 건수를 알린다. 리포트 내용을 채팅에 다시 붙이지 않는다.
2. 네임드 수집 결과의 `registry_updates`가 있으면 목록으로 보여 주고 `data/companies.md`에 반영할지 묻는다. 승인받은 것만 고친다.
3. 레지스트리 밖에서 A등급이 나온 회사 중 공고가 여럿이거나 두 번 연속 A인 곳이 있으면 보여 주고, 레지스트리의 어느 절에 올릴지 묻는다. 올리면 다음부터는 네임드 흐름이 자사 페이지로 읽는다.
4. `chrome_unavailable`이 있었으면 `claude --chrome`으로 다시 켜고 "브라우저 쪽만 다시"라고 하면 된다고 알린다.
5. 결과에서 고칠 점이 있는지 한 번 묻는다.

| 피드백                                    | 고칠 파일                                                               |
| ----------------------------------------- | ----------------------------------------------------------------------- |
| 공고 판정, 네임드 절 형식                 | `.claude/skills/fit-report/SKILL.md`                                    |
| 레지스트리 밖 절 형식, 단계 나누기        | `.claude/skills/discovery-report/SKILL.md`, `scripts/prepare_review.py` |
| 회사 등급이 이상하다                      | `.claude/skills/company-vetting/SKILL.md`                               |
| 너무 많이, 너무 적게 걸러진다             | `scripts/prefilter.py`                                                  |
| 특정 사이트를 못 읽는다                   | `.claude/skills/job-collection/references/` 또는 `data/companies.md`    |
| 직무나 연차를 잘못 읽었다                 | `.claude/skills/resume-profiling/SKILL.md`                              |
| 기업을 더하거나 빼거나 범위를 옮기고 싶다 | `data/companies.md`의 행을 해당 절로 옮긴다                             |
| 보고 싶은 기업을 먼저 놓고 싶다           | `resume/preferences.md`의 선호 기업                                     |

## 데이터 흐름

```
resume/* ──resume-analyst──▶ _workspace/01_profile.json, 00_scope.json
네임드:  make_batches.py ──job-scout xN, browser-scout──▶ _workspace/02_postings_*.json
         ──fit-reviewer──▶ _workspace/06_named.md
발굴:    플랫폼 ──job-scout x5, browser-scout──▶ _discover/02_postings_d-*.json
         ──prefilter.py, vetting_cache.py──▶ 03_candidates.json, 03_to_vet.json
         ──company-vetter xN──▶ 04_vetting_vet-*.json ──merge──▶ _cache/vetting.json
         ──prepare_review.py──▶ 05_review_input.json ──discovery-reviewer──▶ _discover/06_discover.md
합치기:  assemble_report.py ──▶ output/YYYY-MM-DD.md
```

## 에러 핸들링

| 상황                                                     | 처리                                                                                                                                                |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| 수집 배치 하나가 실패하거나 결과 파일이 JSON으로 안 읽힘 | 같은 프롬프트로 한 번 다시 띄운다. 또 실패하면 빼고 진행한다. 네임드 배치면 fit-reviewer 프롬프트에 그 배치 대상을 적어 "확인 못 한 곳"에 넣게 한다 |
| 수집 배치 절반 이상이 실패                               | 네트워크나 권한 문제일 가능성이 크다. 실패 메시지를 보여 주고 계속할지 묻는다                                                                       |
| 스크립트가 실패                                          | 오류를 보여 주고 그 흐름을 멈춘다. 다른 흐름은 계속하고, 합치기에서 그 절은 빠진다                                                                  |
| 검증 배치 하나가 두 번 실패                              | 그 회사들은 `prepare_review.py`가 `not_vetted`로 분류해 리포트에서 빠지고 제외 기록에 "검증 안 함"으로 남는다                                       |
| Chrome 미연결                                            | browser-scout 대상만 빠진다. Phase 5에서 안내한다                                                                                                   |
| 두 절 모두 공고 0건                                      | 프로필 검색어와 연차, 제외 기록의 상위 사유를 보여 주고 범위나 조건을 넓힐지 묻는다                                                                 |

## 테스트 시나리오

### 정상 흐름: 범위 전부

1. 이력서가 있고 작업 폴더가 없다. 사용자가 "채용공고 찾아줘"라고 한다.
2. Phase 0에서 메뉴 첫 화면을 띄우고 사용자가 "전부"를 고른다. `00_scope.json`이 생긴다.
3. Phase 1에서 프로필이 생기고 `_discover/`로 복사된다.
4. Phase 2에서 네임드 배치 7개, 발굴 배치 5개, browser-scout 1개가 함께 돈다.
5. Phase 3에서 fit-reviewer가 도는 동안 1차 거르기, 국민연금 준비, company-vetter 6개, `prepare_review.py`, discovery-reviewer가 차례로 돈다.
6. Phase 4에서 `output/2026-10-12.md`가 생긴다. "네임드 기업" 절과 "레지스트리 밖 회사" 절이 있고, 머리 문장에 범위 여섯 개와 공고 수가 있다.

### 정상 흐름: 네임드만

1. 사용자가 "네카라쿠배만 찾아줘"라고 한다. Phase 0에서 메뉴 없이 범위가 `빅테크`로 정해진다.
2. `make_batches.py`가 빅테크 절만 배치로 만든다. 발굴 흐름과 회사 검증은 돌지 않는다.
3. 리포트에는 "네임드 기업" 절만 있다.

### 에러 흐름

1. Chrome 연동 없이 실행했다.
2. browser-scout가 연결 확인에 실패하고 넥슨과 잡플래닛을 `chrome_unavailable`로 적는다. `browser-2`는 띄우지 않는다.
3. 나머지 흐름은 정상으로 끝나고, 네임드 절의 "확인 못 한 곳"에 넥슨이 "Chrome 미연결"로 나온다.
4. Phase 5에서 `claude --chrome`으로 다시 켜고 브라우저 쪽만 다시 돌리라고 안내한다.

---
name: job-hunt
description: "이력서 기반 채용공고 탐색 하네스의 오케스트레이터. resume/의 이력서로 연차와 직무에 맞는 공고를 대기업, 중견기업, IT 네임밸류 기업, 유니콘(네카라쿠배당토직야, 몰두센 등)의 자사 채용 페이지와 원티드, 리멤버, 잡플래닛, 사람인, 직행, 링크드인에서 찾아 output/에 마크다운 리포트로 남긴다. '채용공고 찾아줘', '공고 수집해줘', '이직할 곳 찾아줘', '내 연차에 맞는 공고', '네카라쿠배 공고 있어?' 같은 요청이면 반드시 이 스킬을 쓴다. 후속 요청도 이 스킬이다: 다시 실행, 재실행, 업데이트, 이번 주 공고 갱신, 특정 기업이나 플랫폼만 다시, 리포트만 다시, 이력서 바꿨으니 다시, 이전 결과 기반으로 보완, 기업 목록 수정. 이력서 문장 첨삭이나 자기소개서 작성은 이 스킬이 아니다."
---

# job-hunt

이력서로 프로필을 만들고, 기업 레지스트리와 채용 플랫폼에서 공고를 병렬로 모은 뒤, 적합도로 걸러 `output/YYYY-MM-DD.md`를 쓴다. 이 스킬을 실행하는 메인 세션이 오케스트레이터다.

## 실행 모드: 서브 에이전트

수집 단위(기업 묶음, 플랫폼, 브라우저 작업)가 서로 독립이고 결과는 `_workspace/`의 JSON 파일로 모으면 충분하다. 에이전트끼리 주고받을 메시지가 없으므로 팀을 만들지 않는다.

## 에이전트 구성

| 에이전트       | subagent_type    | 스킬             | 출력                                           | 실행                |
| -------------- | ---------------- | ---------------- | ---------------------------------------------- | ------------------- |
| resume-analyst | `resume-analyst` | resume-profiling | `_workspace/01_profile.json`                   | 포그라운드 1개      |
| job-scout      | `job-scout`      | job-collection   | `_workspace/02_postings_{batch}.json`          | 백그라운드 최대 8개 |
| browser-scout  | `browser-scout`  | job-collection   | `_workspace/02_postings_browser.json`          | 백그라운드 1개      |
| fit-reviewer   | `fit-reviewer`   | fit-report       | `output/{date}.md`, `_workspace/04_dropped.md` | 포그라운드 1개      |

모든 Agent 호출에 `model: "opus"`를 넣는다. browser-scout는 Chrome 하나를 쓰므로 어느 시점에도 하나만 돌린다.

## Phase 0: 컨텍스트 확인

1. `resume/`에 `preferences.md` 말고 파일이 없으면 멈추고 이력서를 넣어 달라고 알린다.
2. 이력서 해시를 구한다. `preferences.md`도 포함한다. 희망 조건이 바뀌면 프로필도 바뀌어야 한다.
   ```bash
   cat resume/* | shasum -a 256 | cut -c1-16
   ```
3. 실행 모드를 정한다.

| 상황                                     | 모드        | 할 일                                                                                                                                                                            |
| ---------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `_workspace/` 없음                       | 초기 실행   | Phase 1부터                                                                                                                                                                      |
| `_workspace/` 있고 아래 부분 요청에 해당 | 부분 재실행 | 아래 표대로                                                                                                                                                                      |
| `_workspace/` 있고 그 밖의 요청          | 새 실행     | `mv _workspace _workspace_$(date +%Y%m%d_%H%M%S)` 후 Phase 1부터. 옮긴 폴더의 `01_profile.json`의 `source_hash`가 2의 값과 같으면 새 `_workspace/`로 복사하고 Phase 1을 건너뛴다 |

| 부분 요청 예                           | 다시 돌릴 것                                                                                        |
| -------------------------------------- | --------------------------------------------------------------------------------------------------- |
| "토스만 다시", "카카오 공고 다시 봐줘" | 그 기업만 담은 배치 `rerun-{영문 슬러그}` 하나를 접근 방식에 맞는 scout로 돌리고 Phase 4            |
| "링크드인만 다시"                      | 그 플랫폼만 담은 배치 `rerun-{source}`를 `references/platforms.md`의 담당 에이전트로 돌리고 Phase 4 |
| "리포트만 다시", "검토는 빼 줘"        | Phase 4만. 피드백을 fit-reviewer 프롬프트에 넣는다                                                  |
| "연차를 6년으로 봐줘", "판교만"        | `resume/preferences.md`에 반영하고 새 실행                                                          |

## Phase 1: 프로필

```
Agent(
  subagent_type: "resume-analyst",
  model: "opus",
  description: "이력서 프로필 추출",
  prompt: "이력서로 프로필을 만들어라. source_hash: {Phase 0의 해시}. 출력: _workspace/01_profile.json"
)
```

끝나면 `_workspace/01_profile.json`을 읽고 직무와 경력 연수, 핵심 기술을 사용자에게 한 줄로 알린다. `confidence`가 `low`면 `years_basis`를 보여 주고 맞는지 물은 뒤 진행한다. 연차가 틀리면 이후 판정이 전부 어긋난다.

## Phase 2: 배치 나누기

1. `data/companies.md`의 표를 읽는다. 맨 아래 "제외한 기업" 절은 읽지 않는다. 프로필 `exclude_companies`는 뺀다. `include_companies` 중 레지스트리에 없는 기업은 접근을 비운 행으로 이번 실행에만 더한다.
2. 접근 열로 나눈다.
   - `fetch`, `api`, 빈칸: job-scout 몫. 같은 분류끼리 17곳 안팎으로 묶는다. 배치가 7개를 넘으면 배치를 키워 7개로 맞춘다. 그룹 행(삼성, LG, SK 등)은 응답이 커서 한 배치에 셋 이상 넣지 않는다. 배치 ID는 `career-1`부터 붙인다.
   - `browser`, `login`: browser-scout 몫.
   - `group`: 따로 배치에 넣지 않는다. 비고에 적힌 그룹 행을 읽을 때 함께 기록된다.
3. 플랫폼 배치 `platforms`를 하나 만든다. `.claude/skills/job-collection/references/platforms.md`에서 담당이 job-scout인 플랫폼과 ATS 검색을 담는다.
4. `references/platforms.md`에서 담당이 browser-scout인 플랫폼(지금은 잡플래닛)은 browser-scout 몫에 더한다.

## Phase 3: 수집

한 메시지에서 job-scout 배치 수만큼과 browser-scout 1개를 함께 띄운다.

```
Agent(
  subagent_type: "job-scout",
  model: "opus",
  run_in_background: true,
  description: "{batch} 공고 수집",
  prompt: "배치: {batch}
프로필: _workspace/01_profile.json
대상:
{data/companies.md에서 가져온 해당 행들을 표 그대로. 플랫폼 배치면 플랫폼 이름 목록}
출력: _workspace/02_postings_{batch}.json"
)

Agent(
  subagent_type: "browser-scout",
  model: "opus",
  run_in_background: true,
  description: "브라우저 공고 수집",
  prompt: "배치: browser
프로필: _workspace/01_profile.json
대상:
{browser, login 기업 행과 플랫폼 이름}
출력: _workspace/02_postings_browser.json"
)
```

모든 완료 알림을 기다린다. 그다음 job-scout 결과 파일들의 `unreachable` 중 `reason`이 `js`인 항목을 모은다. 있으면 browser-scout를 배치 `browser-2`로 한 번 더 띄운다. 이때는 포그라운드다. 첫 browser-scout가 끝난 뒤라 Chrome을 겹쳐 쓰지 않는다. 첫 browser-scout 결과에 `chrome_unavailable`이 있으면 `browser-2`는 띄우지 않는다. 그 `js` 항목들은 리포트의 "확인 못 한 곳"으로 간다.

## Phase 4: 판정과 리포트

1. 출력 경로를 정한다. `output/$(date +%F).md`가 이미 있으면 `-2`, `-3`을 붙인다. `mkdir -p output`.
2. 직전 리포트는 `output/`에서 이번 출력 경로를 뺀 가장 최근 파일이다. 없으면 "없음".

```
Agent(
  subagent_type: "fit-reviewer",
  model: "opus",
  description: "공고 판정과 리포트",
  prompt: "프로필: _workspace/01_profile.json
수집 결과: _workspace/02_postings_*.json
레지스트리: data/companies.md
직전 리포트: {경로 또는 없음}
출력: {출력 경로}, _workspace/04_dropped.md
사용자 피드백: {부분 재실행일 때만}"
)
```

## Phase 5: 보고

1. 리포트 경로와 추천, 검토 건수, 확인 못 한 곳 수를 알린다. 리포트 내용을 채팅에 다시 붙이지 않는다.
2. 수집 결과의 `registry_updates`가 있으면 목록으로 보여 주고 `data/companies.md`에 반영할지 묻는다. 승인받은 것만 고친다.
3. `chrome_unavailable`이 있었으면 `claude --chrome`으로 다시 켜고 "브라우저 쪽만 다시"라고 요청하면 된다고 알린다.
4. 결과에서 고칠 점이 있는지 한 번 묻는다. 피드백은 아래 파일에 반영한다.

| 피드백                                  | 고칠 파일                                                            |
| --------------------------------------- | -------------------------------------------------------------------- |
| 공고가 너무 많다, 적다, 판정이 이상하다 | `.claude/skills/fit-report/SKILL.md`                                 |
| 특정 사이트를 못 읽는다                 | `.claude/skills/job-collection/references/` 또는 `data/companies.md` |
| 직무나 연차를 잘못 읽었다               | `.claude/skills/resume-profiling/SKILL.md`                           |
| 기업을 더하거나 빼고 싶다               | `data/companies.md`                                                  |

## 데이터 흐름

```
resume/*  ──resume-analyst──▶  _workspace/01_profile.json
                                        │
data/companies.md ──┬──▶ job-scout x N ─┼─▶ _workspace/02_postings_career-*.json, 02_postings_platforms.json
                    └──▶ browser-scout ─┘─▶ _workspace/02_postings_browser.json (+ browser-2)
                                        │
                              fit-reviewer
                                        │
                     output/YYYY-MM-DD.md, _workspace/04_dropped.md
```

## 에러 핸들링

| 상황                                                     | 처리                                                                                                                                                            |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| job-scout 하나가 실패하거나 결과 파일이 JSON으로 안 읽힘 | 같은 프롬프트로 한 번 다시 띄운다. 또 실패하면 그 배치를 빼고 진행한다. fit-reviewer가 그 배치 기업을 "확인 못 한 곳"에 넣도록 프롬프트에 배치 대상을 적어 준다 |
| browser-scout가 Chrome에 연결하지 못함                   | 결과 파일에 `chrome_unavailable`로 남는다. 그대로 Phase 4로 가고 Phase 5에서 안내한다                                                                           |
| 수집 배치 절반 이상이 실패                               | 네트워크나 권한 문제일 가능성이 크다. 실패 메시지를 보여 주고 계속할지 묻는다                                                                                   |
| 추천과 검토가 모두 0건                                   | 프로필의 검색어와 연차, `04_dropped.md`의 상위 이유를 보여 주고 조건을 넓힐지 묻는다                                                                            |

## 테스트 시나리오

### 정상 흐름

1. `resume/resume.pdf`가 있고 `_workspace/`가 없다. 사용자가 "채용공고 찾아줘"라고 한다.
2. Phase 0에서 초기 실행으로 판정한다.
3. Phase 1에서 `01_profile.json`이 생기고 confidence가 high라 바로 진행한다.
4. Phase 2에서 레지스트리의 수집 대상 115곳이 `career-1`부터 `career-7`까지, `platforms`, `browser`로 나뉜다.
5. Phase 3에서 job-scout 8개와 browser-scout 1개가 동시에 돈다. `js`로 넘어온 3곳을 `browser-2`가 읽는다.
6. Phase 4에서 `output/2026-10-07.md`와 `_workspace/04_dropped.md`가 생긴다.
7. 리포트의 모든 링크가 수집 파일에 있는 URL이고, 추천 공고의 경력 요건이 프로필 연차와 맞는다.

### 에러 흐름

1. Chrome 연동 없이 실행했다.
2. browser-scout가 시작할 때 연결 확인에 실패하고 맡은 대상 전부를 `chrome_unavailable`로 적는다.
3. job-scout들은 정상으로 끝난다. `browser-2`도 같은 이유로 돌리지 않는다.
4. 리포트의 "확인 못 한 곳"에 잡플래닛과 browser 기업들이 "Chrome 미연결"로 나온다.
5. Phase 5에서 `claude --chrome`으로 다시 켜고 브라우저 쪽만 다시 돌리라고 안내한다.

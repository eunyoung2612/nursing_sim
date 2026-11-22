# 상부위장관출혈 ICU 입원 1일차 시뮬레이션 (Streamlit + Upstage Solar)

간호학생 보강용 시뮬레이션 앱입니다. 57세 남자 환자(백OO)의 입원 1일차 차트를 바탕으로
4개 장면에서 **AI 환자·의사(Upstage Solar)** 와 대화합니다.

| 장면 | 차트 시각 | 수업 공개(KST) | 대화 목적 | AI |
|---|---|---|---|---|
| 1 | 14:00 ICU 입실 | 09:00 | 중환자실 입실한 환자 안내하기 | 환자 |
| 2 | 16:40 Angiography 후 ICU transfer | 11:00 | angiography 이후 환자 간호하기 | 환자 |
| 3 | 18:00 흉부 통증 | 14:00 | 흉통 사정하기 / SBAR 보고 | 환자, 의사 (위·아래) |
| 4 | 19:00 환자의 불안 | 16:00 | 환자의 불안 사정하기 | 환자 |

- 대화는 **"안녕하세요"** 로 시작하고, **"종료"** 를 입력하면 끝나며 바로 **대화 평가**(부족한 점, 해야 했던 질문)가 나옵니다.
- 대화 전체(평가 포함)를 **PNG 이미지로 저장**할 수 있습니다.
- 장면 1·2에는 Norepinephrine 처방 안내(파란 박스)가 있습니다. 계산은 과제 Part A에서 합니다.
- 각 장면은 공개 시각이 되면 열립니다. 교수자 코드를 입력하면 언제든 열립니다.

## 폴더 구조
```
app.py                       # 시작 페이지 + 장면 이동
core/data.py                 # 환자 차트 데이터
core/scenes.py               # 장면 설정, AI 역할, 평가 항목  ← 수업 내용 수정은 여기
core/ui.py                   # 화면, 시간 잠금, Solar 호출, 평가, 이미지 저장
requirements.txt             # 파이썬 패키지
packages.txt                 # 한글 폰트(이미지 저장용)
.streamlit/secrets.toml.example
```

## Solar API 키·교수자 코드 저장 (Streamlit Secrets)
1. share.streamlit.io 에서 내 앱 오른쪽 **⋮ → Settings → Secrets**
2. 아래를 붙여 넣고 키만 바꾼 뒤 **Save** (1분 정도 뒤 앱이 자동 재시작)
```
UPSTAGE_API_KEY = "발급받은_키"
SOLAR_MODEL = "solar-pro"
SOLAR_BASE_URL = "https://api.upstage.ai/v1/solar"
INSTRUCTOR_CODE = "10718"
LOCK_ENABLED = true
```
키와 코드는 Streamlit 서버에만 저장되며 GitHub와 학생 화면에는 보이지 않습니다.

## 파일 수정 후 반영
GitHub 저장소에서 바뀐 파일을 다시 올리면(Add file → Upload files → 같은 이름으로 덮어쓰기 → Commit)
Streamlit 앱이 자동으로 새 버전으로 바뀝니다.

## 수정 팁
- 공개 시각: `core/scenes.py` 의 `open_time`
- 환자·의사 반응: `core/scenes.py` 의 각 `system`
- 평가 항목: `core/scenes.py` 의 각 `checklist`

※ 교육용 가상 사례이며 실제 환자 정보가 아닙니다.

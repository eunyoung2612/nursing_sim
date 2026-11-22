"""4개 장면(서브앱) 설정.

chart_time : 차트상의 시각 (이 시각까지의 기록만 보여줌)
open_time  : 실제 수업에서 열리는 시각 (KST)
purpose    : 학습 목적
closing    : 장면 마지막에 보여줄 과제 안내
"""

SCENES = [
    {
        "id": 1,
        "chart_time": '14:00',
        "open_time": '09:00',
        "title": '장면 1 · 14:00 ICU 입실',
        "situation": 'ER에서 Norepinephrine 0.03 mcg/kg/min을 맞으며 방금 ICU로 입실했습니다. 입실 시 V/S **BP 88/52 (MAP 64), HR 104, RR 20, BT 36.3℃, SpO2 97%**. 오늘 15:00 Angiography가 예정되어 있습니다. 환자는 처음 온 ICU가 낯설고 불안해 보입니다.',
        "purpose": '중환자실 입실한 환자 안내하기',
        "tasks": [
            '처음 입실한 환자에게 자기소개를 하고, 이곳이 중환자실(ICU)임을 안내하세요.',
            '오늘 오후 3시에 예정된 Angiography가 어떤 검사인지 의학용어 없이 쉽게 설명하세요.',
        ],
        "closing": 'Part A를 작성하세요.',
    },
    {
        "id": 2,
        "chart_time": '16:40',
        "open_time": '11:00',
        "title": '장면 2 · 16:40 Angiography 후 ICU transfer',
        "situation": 'Angiography(embolization) 후 ICU로 transfer되었습니다. 조영실에서 SBP 102~110이 유지되어 15:15 0.04, 15:45 0.03, 16:15 0.02 mcg/kg/min으로 감량되었습니다. transfer 직후(16:45) **BP 114/68, HR 80**. Rt. femoral 천자부위에 압박 드레싱이 있고, N/S 80cc/hr가 들어가고 있습니다.',
        "purpose": 'angiography 이후 환자 간호하기',
        "tasks": [
            'Rt. femoral 천자부위와 Rt. 하지 말초순환을 사정하세요.',
            'Rt. leg 6시간 굴곡 금지를 교육하고, 수액은 지금 상태 그대로 유지됨을 설명하세요.',
            '흑색변을 본 환자에게 토혈, 오심·구토, 다른 출혈, 어지러움, 다른 불편감을 확인하고 의사에게 보고할 내용을 정리하세요.',
        ],
        "closing": 'Part B를 작성하세요.',
    },
    {
        "id": 3,
        "chart_time": '18:00',
        "open_time": '14:00',
        "title": '장면 3 · 18:00 흉부 통증 호소',
        "situation": 'Norepinephrine은 17:15에 off 되었고 이후 혈압은 유지되고 있습니다. 18:00 V/S **BP 124/72, HR 70, RR 18, BT 36.5℃, SpO2 98%**. 환자가 콜벨을 눌러 "가슴이 아파요"라고 합니다.',
        "purpose": '흉통 사정하기',
        "tasks": [
            'PQRST(부위, 양상, 완화·악화요인, 강도 NRS, 시간적 양상)로 통증을 사정하세요.',
            '비약물적 중재(반좌위)를 적용하세요.',
            '담당의에게 SBAR로 보고하고 진통제 처방을 요청하세요.',
        ],
        "closing": 'Part C를 작성하세요.',
    },
    {
        "id": 4,
        "chart_time": '19:00',
        "open_time": '16:00',
        "title": '장면 4 · 19:00 환자의 불안',
        "situation": '18:30 통증은 NRS 0으로 완화되었습니다. 19:00 V/S **BP 122/70, HR 64, RR 18, BT 36.5℃, SpO2 98%**. Angiography 후 Rt. leg 굴곡 금지 시간(6시간)이 아직 남아 있습니다.',
        "purpose": '환자의 불안 사정하기',
        "tasks": [
            '환자의 불안을 사정하고 감정을 표현하도록 지지하세요.',
            '현재 상태와 치료 과정을 설명하세요.',
            '토혈·어지러움 등이 있으면 바로 알리거나 콜벨을 누르도록 교육하세요.',
            '검사 후 6시간 동안 다리를 굽히면 안 되는 이유와 남은 시간을 설명하세요.',
        ],
        "closing": 'Part D를 작성하고, 간호과정도 완료하여 제출하세요.',
    },
]

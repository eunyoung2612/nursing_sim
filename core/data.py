"""입원 1일차(2025.10.11) 환자 차트 데이터.

엑셀 차트(백OO_입원1일차_환자차트_v5.xlsx)와 같은 내용입니다.
각 장면(scene)은 해당 시각까지의 기록만 보여 줍니다.
"""

PATIENT = {
    "이름": "백OO",
    "성별/나이": "M / 57세",
    "등록번호": "2025101100",
    "진료과": "GI (소화기내과)",
    "병동": "ICU",
    "키/체중": "170cm / 78kg",
    "진단명": "상부위장관출혈 (ESD 후 위 분문부 궤양)",
    "내원": "2025.10.11 12:30 ER → 14:00 ICU 입실",
}

HISTORY = (
    "9/30 위 분문부(cardia) leiomyoma로 ESD 시행 후 특이소견 없이 퇴원. "
    "10/11 내원 2시간 전부터 수회 토혈(>500cc), 혈변, 복통, 어지러움으로 ER 내원. "
    "ER에서 선홍색 토혈 약 400cc 추가, BP 86/50mmHg로 저하되어 N/S 1,500mL bolus 후 "
    "CVC(Rt. IJV) 삽입, Norepinephrine 시작. 14:00 ICU 입실, 15:00 Angiography 시행 "
    "(Lt. gastric a. cardia branch, Lt. inferior phrenic a. gastric branch embolization), 16:40 ICU 귀실."
)

PAST = [
    "선천성 single kidney",
    "2014 강직성 척추염",
    "2023 이상지질혈증, ICA stenosis (Rt/Lt prox)",
    "2025.09.30 ESD (cardia leiomyoma)",
    "흡연: 25년, 하루 2갑 (현재 금연) / 음주: 소주 3병, 월 20회, 40년",
    "가족력: 큰누나(담낭암), 작은누나(간암), 큰형(간암), 둘째형(췌장암)",
]

# (시각, BT, PR, RR, SBP, DBP, SpO2, 비고)
VITALS = [
    ("12:30", 36.4, 62, 14, 164, 96, None, "ER 내원"),
    ("13:30", 36.3, 108, 22, 86, 50, 96, "토혈 400cc 후"),
    ("13:45", 36.3, 106, 22, 86, 50, 96, "NE 0.03 시작"),
    ("14:00", 36.3, 104, 20, 88, 52, 97, "ICU 입실"),
    ("14:15", 36.3, 100, 20, 94, 56, 97, ""),
    ("14:30", 36.2, 96, 20, 98, 58, 97, ""),
    ("14:45", 36.2, 94, 18, 102, 60, 98, ""),
    ("15:00", 36.2, 92, 18, 106, 62, 98, "Angiography 이동"),
    ("15:15", 36.2, 90, 18, 108, 64, 98, "(조영실)"),
    ("15:30", 36.3, 88, 18, 110, 64, 98, "(조영실)"),
    ("15:45", 36.3, 86, 18, 108, 64, 98, "(조영실)"),
    ("16:15", 36.3, 84, 18, 110, 66, 98, "(조영실)"),
    ("16:45", 36.3, 80, 18, 114, 68, 98, "ICU 귀실 후"),
    ("17:00", 36.4, 76, 18, 118, 70, 98, ""),
    ("17:15", 36.4, 74, 18, 116, 68, 98, ""),
    ("17:30", 36.4, 72, 18, 114, 68, 98, ""),
    ("18:00", 36.5, 70, 18, 124, 72, 98, ""),
    ("19:00", 36.5, 64, 18, 122, 70, 98, ""),
]

# Norepinephrine 투여 기록 (시각, 용량 mcg/kg/min, 내용)
NE_LOG = [
    ("13:45", 0.03, "시작 (ER)"),
    ("14:00", 0.05, "SBP < 90 → 증량"),
    ("15:15", 0.04, "SBP > 100 30분 유지 → 감량 (조영실)"),
    ("15:45", 0.03, "감량 (조영실)"),
    ("16:15", 0.02, "감량 (조영실)"),
    ("16:45", 0.01, "감량"),
    ("17:15", 0.0, "off"),
]

# 투약기록 (시각, 약물, 용량/경로, 비고)
MAR = [
    ("12:50", "0.9% N/S 1000mL", "IV bolus", ""),
    ("13:00", "Esomeprazole (Nexium 40mg) + N/S 100mL", "80mg (2V) IV", "BID"),
    ("13:40", "0.9% N/S 500mL", "IV bolus", ""),
    ("13:45", "Norepinephrine 32mg + 5% D/W 500mL", "0.03 mcg/kg/min IV(CVC)", "시작"),
    ("14:00", "Norepinephrine", "↑ 0.05 mcg/kg/min", "titration"),
    ("15:15", "Norepinephrine", "↓ 0.04 mcg/kg/min", "(조영실)"),
    ("15:20", "Heparin sodium 5000IU/mL", "1A IV", "Angio 중 (조영실)"),
    ("15:30", "Pethidine 25mg/0.5mL", "1A IV", "시술 중 통증 (조영실)"),
    ("15:45", "Norepinephrine", "↓ 0.03 mcg/kg/min", "(조영실)"),
    ("16:15", "Norepinephrine", "↓ 0.02 mcg/kg/min", "(조영실)"),
    ("16:40", "0.9% N/S 1000mL", "80cc/hr IV", "maintenance 시작"),
    ("16:45", "Norepinephrine", "↓ 0.01 mcg/kg/min", "titration"),
    ("17:15", "Norepinephrine", "off", "titration"),
    ("18:00", "Propacetamol (Denogan 1g)", "1A IV", "prn, NRS 5"),
]

# 의사지시 (처방 시각, 제목, 내용 리스트)
ORDERS = [
    ("12:40", "ER 초기 처방", [
        "V/S q 1hr (SpO2 포함), NPO, Absolute bed rest (HOB 30°)",
        "Check I/O q 1hr, Foley catheter insertion",
        "Notify: SBP < 90 또는 MAP < 65, HR > 120, SpO2 < 94%",
        "0.9% N/S 1000mL IV bolus / Nexium 80mg IV BID",
        "Lab: CBC, PT/aPTT, Chemistry, CRP, CK-MB, ABGA / Chest PA, Abdomen supine",
    ]),
    ("13:35", "ER 추가 처방 - Norepinephrine", [
        "0.9% N/S 500mL bolus 후 CVC(Rt. IJV) insertion",
        "Norepinephrine 32mg(Norpin 4A) + 5% D/W 500mL, 0.03 mcg/kg/min으로 시작 (CVC, infusion pump)",
        "BP q 15min 측정, SBP에 따라 titration:",
        "  ① SBP < 90: 15분마다 0.02 mcg/kg/min씩 증량 (최대 0.3)",
        "  ② SBP 90~100: 현재 용량 유지",
        "  ③ SBP > 100 30분 이상 유지: 30분마다 0.01 mcg/kg/min씩 감량",
        "  ④ 0.01에서 SBP > 100 30분 이상 유지 시 off",
        "  ⑤ SBP ≥ 140, 최대 용량에도 SBP < 90, HR > 120, 부정맥 시 즉시 notify",
        "혈관 외 유출 관찰, 유출 시 즉시 중단 후 notify",
    ]),
    ("14:00", "ICU 입실 처방", [
        "V/S q 1hr, SpO2 monitoring (NE 투여 중 BP q 15min)",
        "NPO, Absolute bed rest, Check I/O q 1hr",
        "Norepinephrine: ER에서 처방된 titration ①~⑤ ICU에서도 그대로 유지",
        "Angiography with embolization - 동의서 받고 15:00 혈관조영실",
        "Heparin 5000IU 1A IV (Angio 중), Pethidine 25mg 1A IV prn (시술 중 통증)",
    ]),
    ("16:40", "Angiography 후 ICU 귀실 처방", [
        "Rt. femoral puncture site: 6시간 Rt. leg 굴곡 금지, 출혈·혈종·말초맥박 q 1hr 확인",
        "Norepinephrine titration 그대로 유지 (0.01에서 SBP > 100 30분 유지 시 off)",
        "0.9% N/S 1000mL 80cc/hr maintenance",
        "Propacetamol (Denogan 1g) 1A IV prn (NRS ≥ 4)",
        "토혈·흑색변·어지러움 시 notify / EGD 10/13 예정 / CBC f/u 10/12 06:00",
    ]),
]

# 간호기록 (시각, 내용)
NOTES = [
    ("12:30", "토혈(>500cc), 혈변, 복통, 어지러움으로 ER 내원. V/S 164/96-62-14-36.4. Acute ill looking, alert."),
    ("12:50", "18G IV 확보, N/S 1000mL 시작. 채혈. Foley 삽입. NPO 설명."),
    ("13:20", "선홍색 토혈 약 400cc. 어지러움, 오심 호소. 피부 창백·차갑고 식은땀."),
    ("13:30", "V/S 86/50(MAP 62)-108-22-36.3. Dr. 노티, N/S 500mL bolus."),
    ("13:45", "Rt. IJV CVC 삽입. Norepinephrine 32mg/500mL 0.03 mcg/kg/min 시작. BP q15min."),
    ("14:00", "ICU 입실. V/S 88/52-104-20-36.3, BW 78kg. Dr. 노티 → ER titration 그대로 유지. 0.05로 증량."),
    ("14:15", "BP 94/56, HR 100. 0.05 유지."),
    ("14:30", "BP 98/58, HR 96. 0.05 유지."),
    ("15:00", "BP 106/62. Angiography 위해 혈관조영실 이동. titration 처방 인계."),
    ("16:40", "ICU 귀실. Embolization 시행. 시술 중 15:15 0.04, 15:45 0.03, 16:15 0.02로 감량됨. "
              "Rt. femoral 압박 드레싱, 출혈·혈종 없음, Rt. DP 촉지. N/S 80cc/hr 시작."),
    ("16:45", "BP 114/68, HR 80. SBP > 100 30분 이상 유지 → 0.01로 감량."),
    ("16:50", "흑색변 약 200g. 토혈 없음."),
    ("17:00", "V/S 118/70-76-18-36.4. NE 0.01 유지."),
    ("17:15", "BP 116/68. 0.01에서 SBP > 100 30분 유지 → NE off."),
    ("17:30", "BP 114/68, HR 72. off 후 유지."),
    ("18:00", "가슴 쑤시는 통증 NRS 5 호소. Denogan 1g IV. 반좌위."),
    ("18:30", "NRS 0."),
]

LABS = [
    ("WBC", "4.0-10.0 ×10³/μL", 12.88, "▲"),
    ("RBC", "4.0-6.1 ×10⁶/μL", 3.63, "▼"),
    ("Hb", "M 14-18 g/dL", 10.8, "▼"),
    ("Hct", "M 42-52 %", 31.7, "▼"),
    ("Plt", "150-450 ×10³/μL", 258, ""),
    ("PT INR", "0.9-1.10", 1.12, "▲"),
    ("aPTT", "24.8-36.2 sec", 21.6, "▼"),
    ("BUN", "5-23 mg/dL", 34.0, "▲"),
    ("Creatinine", "0.5-1.4 mg/dL", 1.00, ""),
    ("T. Protein", "6.5-8.3 g/dL", 6.06, "▼"),
    ("Na", "141-149 mEq/L", 137.9, "▼"),
    ("K", "3.5-5.0 mEq/L", 4.18, ""),
    ("Glucose", "80-109 mg/dL", 162, "▲"),
    ("ABGA pH", "7.35-7.45", 7.35, ""),
    ("ABGA HCO3", "22-26 mmol/L", 21.5, "▼"),
    ("ABGA BE", "-2~+2", -3.8, "▼"),
]


def _m(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def upto(rows, time_str, inclusive=True):
    """time_str 시각까지의 기록만 반환."""
    lim = _m(time_str)
    return [r for r in rows if (_m(r[0]) <= lim if inclusive else _m(r[0]) < lim)]

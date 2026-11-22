import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core import data
from core.scenes import FEEDBACK_BASE, NE_ORDER

KST = ZoneInfo("Asia/Seoul")


# ---------------------------------------------------------------- secrets
def secret(key, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:  # secrets.toml 없음
        return default


# ---------------------------------------------------------------- 시간 잠금
def is_unlocked(scene) -> bool:
    if not secret("LOCK_ENABLED", True):
        return True
    if st.session_state.get("instructor", False):
        return True
    now = dt.datetime.now(KST).time()
    h, m = map(int, scene["open_time"].split(":"))
    return now >= dt.time(h, m)


def sidebar():
    with st.sidebar:
        st.markdown("### 👤 학생 정보")
        st.session_state["student"] = st.text_input(
            "학번 / 이름", value=st.session_state.get("student", ""), placeholder="예: 20215018 조OO")
        st.divider()
        now = dt.datetime.now(KST)
        st.caption(f"현재 시각(KST) {now:%H:%M}")
        with st.expander("교수자"):
            code = st.text_input("교수자 코드", type="password")
            if code and code == secret("INSTRUCTOR_CODE"):
                st.session_state["instructor"] = True
            if st.session_state.get("instructor"):
                st.success("모든 장면 열림")


# ---------------------------------------------------------------- Solar
@st.cache_resource
def _client():
    from openai import OpenAI
    key = secret("UPSTAGE_API_KEY")
    if not key:
        return None
    return OpenAI(api_key=key, base_url=secret("SOLAR_BASE_URL", "https://api.upstage.ai/v1/solar"))


def solar_stream(messages):
    client = _client()
    if client is None:
        yield "⚠️ UPSTAGE_API_KEY가 설정되지 않았습니다. Streamlit secrets를 확인하세요."
        return
    try:
        resp = client.chat.completions.create(
            model=secret("SOLAR_MODEL", "solar-pro"),
            messages=messages,
            temperature=0.6,
            stream=True,
        )
        for chunk in resp:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    except Exception as e:  # 네트워크·키 오류 등
        yield f"⚠️ Solar API 오류: {e}"


# ---------------------------------------------------------------- 차트
def _vs_df(t):
    rows = []
    for (tm, bt, pr, rr, sbp, dbp, spo2, note) in data.upto(data.VITALS, t):
        rows.append({"시각": tm, "BP": f"{sbp}/{dbp}", "MAP": round((sbp + 2 * dbp) / 3),
                     "HR": pr, "RR": rr, "BT": bt, "SpO2": spo2, "비고": note})
    return pd.DataFrame(rows)


def show_chart(scene):
    t = scene["chart_time"]
    st.markdown(f"#### 📋 환자 차트 ({t}까지의 기록)")
    tabs = st.tabs(["기본정보", "의사지시", "활력징후", "투약기록", "간호기록", "검사결과"])
    with tabs[0]:
        c1, c2 = st.columns(2)
        for i, (k, v) in enumerate(data.PATIENT.items()):
            (c1 if i % 2 == 0 else c2).markdown(f"**{k}** : {v}")
        st.markdown("**현병력**  \n" + data.HISTORY)
        st.markdown("**과거력·사회력**  \n" + "  \n".join("· " + p for p in data.PAST))
    with tabs[1]:
        for tm, title, items in data.upto(data.ORDERS, t):
            st.markdown(f"**{tm} · {title}**")
            st.markdown("\n".join(f"- {x}" for x in items))
    with tabs[2]:
        st.dataframe(_vs_df(t), hide_index=True, width="stretch")
    with tabs[3]:
        mar = data.upto(data.MAR, t, inclusive=False)
        st.dataframe(pd.DataFrame(mar, columns=["시각", "약물", "용량/경로", "비고"]),
                     hide_index=True, width="stretch")
    with tabs[4]:
        notes = data.upto(data.NOTES, t, inclusive=False)
        st.dataframe(pd.DataFrame(notes, columns=["시각", "간호기록"]),
                     hide_index=True, width="stretch")
    with tabs[5]:
        st.caption("10/11 12:45 채혈")
        st.dataframe(pd.DataFrame(data.LABS, columns=["항목", "정상범주", "결과", ""]),
                     hide_index=True, width="stretch")


# ---------------------------------------------------------------- NE 계산 확인
def ne_calc(scene):
    cfg = scene.get("ne_calc")
    if not cfg:
        return
    st.markdown("#### 💉 Norepinephrine 주입 속도 계산")
    st.info(f"처방: Norepinephrine **{NE_ORDER['drug_mg']}mg + 5% D/W {NE_ORDER['volume_ml']}mL**, "
            f"체중 **{NE_ORDER['weight_kg']}kg**  \n과제: {cfg['label']}을(를) 정하고 mL/hr를 계산하세요.")
    k = f"calc_{scene['id']}"
    c1, c2, c3 = st.columns(3)
    dose = c1.number_input("조절 후 용량 (mcg/kg/min)", min_value=0.0, max_value=0.5, step=0.01,
                           format="%.2f", key=k + "_dose")
    conc = c2.number_input("희석 농도 (mcg/mL)", min_value=0.0, step=1.0, key=k + "_conc")
    rate = c3.number_input("주입 속도 (mL/hr)", min_value=0.0, step=0.01, format="%.2f", key=k + "_rate")
    if st.button("확인", key=k + "_btn"):
        true_conc = NE_ORDER["drug_mg"] * 1000 / NE_ORDER["volume_ml"]
        ok_dose = abs(dose - cfg["dose"]) < 1e-6
        ok_conc = abs(conc - true_conc) < 0.5
        ok_rate = abs(rate - cfg["dose"] * NE_ORDER["weight_kg"] * 60 / true_conc) < 0.06
        st.write(("✅" if ok_dose else "❌") + " 용량 판단",
                 "  ", ("✅" if ok_conc else "❌") + " 희석 농도",
                 "  ", ("✅" if ok_rate else "❌") + " 주입 속도")
        if not ok_dose:
            st.caption("의사지시의 titration 기준(①~⑤)과 현재 SBP를 다시 확인하세요.")
        elif not ok_rate:
            st.caption("공식: 용량(mcg/kg/min) × 체중(kg) × 60 ÷ 농도(mcg/mL)")
        st.session_state[k + "_result"] = f"용량 {dose:.2f}, 농도 {conc:g}, 속도 {rate:.2f} mL/hr " \
                                          f"(용량 {'정답' if ok_dose else '오답'}, 농도 {'정답' if ok_conc else '오답'}, 속도 {'정답' if ok_rate else '오답'})"


# ---------------------------------------------------------------- 대화
def chat(scene):
    st.markdown("#### 💬 AI와 대화하기 (Solar)")
    roles = list(scene["roles"].keys())
    role = st.radio("대화 상대", roles, horizontal=True, key=f"role_{scene['id']}")
    key = f"chat_{scene['id']}_{role}"
    hist = st.session_state.setdefault(key, [])

    box = st.container(height=380)
    with box:
        for m in hist:
            with st.chat_message("user" if m["role"] == "user" else "assistant",
                                 avatar="🧑‍⚕️" if m["role"] == "user" else "🛏️"):
                st.markdown(m["content"])

    prompt = st.chat_input(f"{role}에게 말하기…", key=f"in_{key}")
    if prompt:
        hist.append({"role": "user", "content": prompt})
        with box:
            with st.chat_message("user", avatar="🧑‍⚕️"):
                st.markdown(prompt)
            with st.chat_message("assistant", avatar="🛏️"):
                msgs = [{"role": "system", "content": scene["roles"][role]}] + hist
                reply = st.write_stream(solar_stream(msgs))
        hist.append({"role": "assistant", "content": reply})

    if hist and st.button("이 대화 초기화", key=f"reset_{key}"):
        st.session_state[key] = []
        st.rerun()


# ---------------------------------------------------------------- 답안·피드백
def _transcript(scene):
    out = []
    for role in scene["roles"]:
        hist = st.session_state.get(f"chat_{scene['id']}_{role}", [])
        if hist:
            out.append(f"[{role}와의 대화]")
            for m in hist:
                out.append(("학생: " if m["role"] == "user" else f"{role}: ") + m["content"])
    return "\n".join(out)


def answers_and_feedback(scene):
    st.markdown("#### ✍️ 나의 간호 판단")
    ans = st.text_area("과제에 대한 답안(사정 내용, 판단 근거, 수행할 간호)을 적으세요.",
                       height=180, key=f"ans_{scene['id']}")
    calc = st.session_state.get(f"calc_{scene['id']}_result", "")
    transcript = _transcript(scene)

    c1, c2 = st.columns(2)
    if c1.button("🧑‍🏫 프리셉터 피드백 받기", type="primary", key=f"fb_{scene['id']}"):
        user_msg = (
            f"[장면]\n{scene['title']}\n{scene['situation']}\n\n"
            f"[과제]\n" + "\n".join(scene["tasks"]) + "\n\n"
            f"[평가 기준]\n{scene['rubric']}\n\n"
            f"[학생 대화]\n{transcript or '(대화 없음)'}\n\n"
            f"[학생 답안]\n{ans or '(답안 없음)'}\n\n"
            f"[Norepinephrine 계산 결과]\n{calc or '(해당 없음)'}"
        )
        st.session_state[f"fbtext_{scene['id']}"] = st.write_stream(solar_stream([
            {"role": "system", "content": FEEDBACK_BASE},
            {"role": "user", "content": user_msg},
        ]))
    elif st.session_state.get(f"fbtext_{scene['id']}"):
        st.markdown(st.session_state[f"fbtext_{scene['id']}"])

    fbkey = f"fbtext_{scene['id']}"
    report = (
        f"학생: {st.session_state.get('student', '')}\n"
        f"작성: {dt.datetime.now(KST):%Y-%m-%d %H:%M}\n"
        f"{scene['title']}\n\n[대화]\n{transcript}\n\n[답안]\n{ans}\n\n"
        f"[계산]\n{calc}\n\n[피드백]\n{st.session_state.get(fbkey, '')}\n"
    )
    c2.download_button("📥 기록 내려받기 (제출용)", report,
                       file_name=f"장면{scene['id']}_{st.session_state.get('student', '학생')}.txt",
                       key=f"dl_{scene['id']}")


# ---------------------------------------------------------------- 장면 페이지
def scene_page(scene):
    sidebar()
    st.title(scene["title"])
    st.caption(f"차트 시각 {scene['chart_time']} · 수업 공개 {scene['open_time']} (KST)")
    if not is_unlocked(scene):
        st.warning(f"🔒 이 장면은 {scene['open_time']}에 열립니다.")
        st.stop()

    st.markdown("#### 🩺 상황")
    st.markdown(scene["situation"])
    st.markdown("**과제**\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(scene["tasks"], 1)))
    st.divider()
    show_chart(scene)
    st.divider()
    chat(scene)
    st.divider()
    ne_calc(scene)
    answers_and_feedback(scene)

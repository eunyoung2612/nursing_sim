import datetime as dt
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core import data

KST = ZoneInfo("Asia/Seoul")


# ---------------------------------------------------------------- secrets
def secret(key, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:  # secrets 없음
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
        now = dt.datetime.now(KST)
        st.caption(f"현재 시각(KST) {now:%H:%M}")
        with st.expander("교수자"):
            code = st.text_input("교수자 코드", type="password")
            if code and code == str(secret("INSTRUCTOR_CODE", "")):
                st.session_state["instructor"] = True
            if st.session_state.get("instructor"):
                st.success("모든 장면 열림")


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
        st.markdown("**현병력**  \n" + data.history_for(t))
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
    st.markdown(f"**학습 목적** : {scene['purpose']}")
    st.markdown("**과제**\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(scene["tasks"], 1)))
    st.divider()
    show_chart(scene)
    st.divider()
    st.success(f"**{scene['closing']}**")

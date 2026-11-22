import datetime as dt
import json
import os
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


# ---------------------------------------------------------------- 수업 상태 (모든 사용자 공통)
_STATE_FILE = os.path.join(os.path.dirname(__file__), "..", ".class_state.json")


@st.cache_resource
def _class_state():
    """앱 전체에서 공유되는 수업 상태. {'started_at': ISO문자열 또는 None, 'manual_open': [장면 id]}"""
    state = {"started_at": None, "manual_open": []}
    try:
        with open(_STATE_FILE, encoding="utf-8") as f:
            state.update(json.load(f))
    except Exception:
        pass
    return state


def _save_state():
    try:
        with open(_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(_class_state(), f, ensure_ascii=False)
    except Exception:
        pass


def start_class():
    st_ = _class_state()
    st_["started_at"] = dt.datetime.now(KST).isoformat()
    st_["manual_open"] = []
    _save_state()


def end_class():
    st_ = _class_state()
    st_["started_at"] = None
    st_["manual_open"] = []
    _save_state()


def open_now(scene_id):
    st_ = _class_state()
    if scene_id not in st_["manual_open"]:
        st_["manual_open"].append(scene_id)
    _save_state()


def started_at():
    v = _class_state().get("started_at")
    return dt.datetime.fromisoformat(v) if v else None


def is_instructor():
    return st.session_state.get("instructor", False)


BASE_TIME = "09:00"  # 장면 1의 기준 시각. 나머지 장면은 이 시각과의 차이만큼 '수업 시작 후'에 열림


def open_offset(scene) -> dt.timedelta:
    """수업 시작 후 몇 시간 뒤에 열리는지 (예: 11:00 → 2시간, 14:00 → 5시간, 16:00 → 7시간)."""
    h, m = map(int, scene["open_time"].split(":"))
    bh, bm = map(int, BASE_TIME.split(":"))
    return dt.timedelta(hours=h - bh, minutes=m - bm)


def offset_label(scene) -> str:
    off = open_offset(scene)
    if off <= dt.timedelta(0):
        return "수업 시작 시"
    hours, rem = divmod(int(off.total_seconds()) // 60, 60)
    return f"시작 {hours}시간" + (f" {rem}분" if rem else "") + " 후"


def opens_at(scene):
    start = started_at()
    return start + open_offset(scene) if start else None


def is_unlocked(scene) -> bool:
    """학생 기준 열림 여부: 교수자가 수업을 시작한 뒤, 장면 1은 바로 / 나머지는 시작 후 정해진 시간이 지나면."""
    if not secret("LOCK_ENABLED", True):
        return True
    start = started_at()
    if start is None:
        return False
    if scene["id"] in _class_state()["manual_open"]:
        return True
    return dt.datetime.now(KST) >= opens_at(scene)


def can_view(scene) -> bool:
    return is_instructor() or is_unlocked(scene)


def sidebar(scenes):
    with st.sidebar:
        now = dt.datetime.now(KST)
        st.caption(f"현재 시각(KST) {now:%H:%M}")
        start = started_at()
        st.caption("🟢 수업 진행 중 (시작 " + f"{start:%m/%d %H:%M})" if start else "⚪ 수업 시작 전")
        with st.expander("교수자", expanded=is_instructor()):
            _instructor_panel(scenes)
        _watch(scenes)


def _instructor_panel(scenes):
    start = started_at()
    if not is_instructor():
        code = st.text_input("교수자 코드", type="password")
        if code:
            if code == str(secret("INSTRUCTOR_CODE", "")):
                st.session_state["instructor"] = True
                st.rerun()
            else:
                st.error("코드가 맞지 않습니다.")
        return
    st.success("교수자 모드 (모든 장면 보기 가능)")
    if start is None:
        if st.button("▶️ 수업 시작", type="primary", width="stretch"):
            start_class()
            st.rerun()
        st.caption("시작하면 장면 1이 바로 열리고, 장면 2·3·4는 시작 2시간·5시간·7시간 후에 열립니다. "
                   "(09:00에 시작하면 11:00·14:00·16:00)")
    else:
        for sc in scenes[1:]:
            label = sc["title"].split("·")[0].strip()
            if is_unlocked(sc):
                st.caption(f"✅ {label} 열림")
            elif st.button(f"{label} 지금 열기 (예정 {opens_at(sc):%H:%M})", key=f"open_{sc['id']}",
                           width="stretch"):
                open_now(sc["id"])
                st.rerun()
        if st.button("⏹️ 수업 종료 (모두 잠금)", width="stretch"):
            end_class()
            st.rerun()
    if st.button("교수자 모드 나가기", width="stretch"):
        st.session_state["instructor"] = False
        st.rerun()


@st.fragment(run_every=30)
def _watch(scenes):
    """30초마다 열림 상태를 확인해, 바뀌면 화면(메뉴)을 새로 그립니다."""
    key = tuple(sc["id"] for sc in scenes if can_view(sc))
    prev = st.session_state.get("_open_key")
    st.session_state["_open_key"] = key
    if prev is not None and prev != key:
        st.rerun(scope="app")


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
    st.title(scene["title"])
    st.caption(f"차트 시각 {scene['chart_time']} · 공개: {offset_label(scene)}")
    if not can_view(scene):
        st.warning("🔒 아직 열리지 않은 장면입니다.")
        st.stop()
    if is_instructor() and not is_unlocked(scene):
        st.info("교수자 미리보기: 학생에게는 아직 잠겨 있는 장면입니다.")

    st.markdown("#### 🩺 상황")
    st.markdown(scene["situation"])
    st.markdown(f"**학습 목적** : {scene['purpose']}")
    st.markdown("**과제**\n" + "\n".join(f"{i}. {t}" for i, t in enumerate(scene["tasks"], 1)))
    st.divider()
    show_chart(scene)
    st.divider()
    st.success(f"**{scene['closing']}**")

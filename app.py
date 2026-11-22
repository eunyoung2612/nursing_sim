import streamlit as st

st.set_page_config(page_title="상부위장관출혈 ICU 시뮬레이션", page_icon="🏥", layout="wide")

from core.scenes import SCENES  # noqa: E402
from core.ui import can_view, is_unlocked, offset_label, opens_at, scene_page, sidebar, started_at  # noqa: E402


def home():
    st.title("🏥 상부위장관출혈 환자 ICU 입원 1일차 시뮬레이션")
    st.markdown("백OO(57세 남자)는 ESD 후 토혈로 응급실을 거쳐 ICU에 입원했습니다.")
    st.markdown("##### 진행 방법")
    st.markdown(
        "1. 각 장면에서 그 시각까지의 차트(의사지시, 활력징후, 투약기록, 간호기록, 검사결과)를 확인합니다.\n"
        "2. 장면이 열리는 시간대별로 과제를 작성합니다.\n"
        "   - 장면 1 (14:00 ICU 입실) → **Part A**\n"
        "   - 장면 2 (16:40 Angiography 후 ICU transfer) → **Part B**\n"
        "   - 장면 3 (18:00 흉부 통증) → **Part C**\n"
        "   - 장면 4 (19:00 환자의 불안) → **Part D** 작성 후 **간호과정**까지 완료하여 제출"
    )
    if started_at() is None:
        st.warning("⏳ 아직 수업이 시작되지 않았습니다. 교수자가 수업을 시작하면 장면이 열립니다.")
    st.markdown("##### 장면 일정")
    cols = st.columns(4)
    for c, s in zip(cols, SCENES):
        with c:
            when = opens_at(s)
            st.metric(s["title"].split("·")[0].strip(), s["chart_time"],
                      f"{when:%H:%M} 공개" if when else offset_label(s), delta_color="off")
            st.caption(s["title"].split("·")[1].strip())
            st.write("🔓 열림" if is_unlocked(s) else "🔒 잠김")
    st.caption("※ 실제 환자 정보가 아닌 교육용 가상 사례입니다.")


def make_page(scene):
    def _page():
        scene_page(scene)
    _page.__name__ = f"scene{scene['id']}"
    return _page


sidebar(SCENES)
pages = [st.Page(home, title="시작하기", icon="🏠", default=True)]
for s in SCENES:
    if can_view(s):  # 잠긴 장면은 메뉴에 표시하지 않음
        pages.append(st.Page(make_page(s), title=s["title"], url_path=f"scene{s['id']}"))

st.navigation(pages).run()

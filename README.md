import streamlit as st

st.set_page_config(page_title="상부위장관출혈 ICU 시뮬레이션", page_icon="🏥", layout="wide")

from core.scenes import SCENES  # noqa: E402
from core.ui import is_unlocked, scene_page, sidebar  # noqa: E402


def home():
    sidebar()
    st.title("🏥 상부위장관출혈 환자 ICU 입원 1일차 시뮬레이션")
    st.markdown(
        "백OO(57세 남자)는 ESD 후 토혈로 응급실을 거쳐 ICU에 입원했습니다. "
        "네 개의 장면에서 상황과 차트를 확인하고 과제를 수행하세요."
    )
    st.markdown("##### 진행 방법")
    st.markdown(
        "1. 공개된 장면을 열어 상황과 과제를 확인합니다.\n"
        "2. 그 시각까지의 차트(의사지시, 활력징후, 투약기록, 간호기록, 검사결과)를 확인합니다.\n"
        "3. 장면별로 Part A ~ D를 작성하고, 마지막 장면 후 간호과정까지 완료하여 제출합니다."
    )
    st.markdown("##### 장면 일정")
    cols = st.columns(4)
    for c, s in zip(cols, SCENES):
        with c:
            st.metric(s["title"].split("·")[0].strip(), s["chart_time"], f"공개 {s['open_time']}",
                      delta_color="off")
            st.caption(s["title"].split("·")[1].strip())
            st.write("🔓 열림" if is_unlocked(s) else "🔒 잠김")
    st.caption("※ 실제 환자 정보가 아닌 교육용 가상 사례입니다.")


def make_page(scene):
    def _page():
        scene_page(scene)
    _page.__name__ = f"scene{scene['id']}"
    return _page


pages = [st.Page(home, title="시작하기", icon="🏠", default=True)]
for s in SCENES:
    pages.append(st.Page(make_page(s), title=s["title"], url_path=f"scene{s['id']}"))

st.navigation(pages).run()

import streamlit as st

st.set_page_config(page_title="상부위장관출혈 ICU 시뮬레이션", page_icon="🏥", layout="wide")

from core.scenes import SCENES  # noqa: E402
from core.ui import is_unlocked, scene_page, sidebar  # noqa: E402


def home():
    sidebar()
    st.title("🏥 상부위장관출혈 환자 ICU 입원 1일차 시뮬레이션")
    st.markdown(
        "백OO(57세 남자)는 ESD 후 토혈로 응급실을 거쳐 ICU에 입원했습니다. "
        "네 개의 장면에서 차트를 확인하고, **AI 환자·의사와 대화**하며 간호를 수행한 뒤 "
        "프리셉터 피드백을 받으세요."
    )
    st.markdown("##### 진행 방법")
    st.markdown(
        "1. 왼쪽에 **학번/이름**을 입력합니다.\n"
        "2. 공개된 장면을 열어 상황과 차트를 확인합니다.\n"
        "3. AI와 대화하며 사정·노티·교육을 수행합니다.\n"
        "4. 답안을 적고 **프리셉터 피드백**을 받은 뒤 **기록을 내려받아 제출**합니다."
    )
    st.markdown("##### 장면 일정")
    cols = st.columns(4)
    for c, s in zip(cols, SCENES):
        with c:
            st.metric(s["title"].split("·")[0].strip(), s["chart_time"], f"공개 {s['open_time']}",
                      delta_color="off")
            st.caption(s["title"].split("·")[1].strip())
            st.write("🔓 열림" if is_unlocked(s) else "🔒 잠김")
    st.caption("※ 대화 상대 AI는 Upstage Solar입니다. 실제 환자 정보가 아닌 교육용 가상 사례입니다.")


def make_page(scene):
    def _page():
        scene_page(scene)
    _page.__name__ = f"scene{scene['id']}"
    return _page


pages = [st.Page(home, title="시작하기", icon="🏠", default=True)]
for s in SCENES:
    pages.append(st.Page(make_page(s), title=s["title"], url_path=f"scene{s['id']}"))

st.navigation(pages).run()

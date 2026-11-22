import datetime as dt
import io
import os
import re
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st

from core import data
from core.scenes import CAUTION, EVAL_SYSTEM, NE_ORDER

KST = ZoneInfo("Asia/Seoul")
END_WORD = "종료"
START_WORD = "안녕하세요"


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
                if st.button("AI 연결 테스트"):
                    _connection_test()


# ---------------------------------------------------------------- Solar
@st.cache_resource
def _make_client(key, base_url):
    # 키·주소가 바뀌면 새 연결을 만듭니다 (Secrets 변경이 바로 반영되도록)
    from openai import OpenAI
    return OpenAI(api_key=key, base_url=base_url)


def _client():
    key = secret("UPSTAGE_API_KEY")
    if not key:
        return None
    return _make_client(key, secret("SOLAR_BASE_URL", "https://api.upstage.ai/v1/solar"))


def _connection_test():
    """교수자용: 현재 설정과 사용 가능한 모델 이름을 보여줍니다."""
    st.caption(f"주소: {secret('SOLAR_BASE_URL', '(없음)')}")
    st.caption(f"모델: {secret('SOLAR_MODEL', '(없음)')}")
    client = _client()
    if client is None:
        st.error("API 키가 없습니다.")
        return
    try:
        names = sorted(m.id.replace("models/", "") for m in client.models.list())
        st.success(f"연결 성공 · 사용 가능한 모델 {len(names)}개")
        st.code("\n".join(n for n in names if "embed" not in n and "tts" not in n and "image" not in n))
        if secret("SOLAR_MODEL") not in names:
            st.warning("Secrets의 SOLAR_MODEL이 위 목록에 없습니다. 목록의 이름으로 바꾸세요.")
    except Exception as e:
        st.error(f"연결 실패: {e}")


def _models():
    """기본 모델 + 예비 모델 목록 (Secrets의 SOLAR_FALLBACK_MODELS)."""
    main = secret("SOLAR_MODEL", "solar-pro")
    extra = secret("SOLAR_FALLBACK_MODELS", []) or []
    if isinstance(extra, str):
        extra = [x.strip() for x in extra.split(",") if x.strip()]
    return [main] + [m for m in extra if m != main]


def solar_stream(messages, temperature=0.6):
    """AI 응답을 스트리밍. 일시적 오류(429·500·503)는 잠시 기다렸다가 다시 시도하고,
    그래도 안 되면 예비 모델로 바꿔 시도합니다."""
    import time
    client = _client()
    if client is None:
        yield "⚠️ API 키가 설정되지 않았습니다. Streamlit의 Settings → Secrets를 확인하세요."
        return
    last_err = None
    for model in _models():
        for attempt in range(3):
            started = False
            try:
                resp = client.chat.completions.create(
                    model=model, messages=messages, temperature=temperature, stream=True)
                for chunk in resp:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        started = True
                        yield chunk.choices[0].delta.content
                return
            except Exception as e:  # 네트워크·키·한도 오류 등
                last_err = e
                if started:  # 답이 나오던 중 끊긴 경우
                    yield "\n\n⚠️ 응답이 중간에 끊겼습니다. 다시 보내 주세요."
                    return
                code = getattr(e, "status_code", None)
                if code in (429, 500, 502, 503, 504):
                    time.sleep(2 * (attempt + 1))  # 2초, 4초, 6초 대기 후 재시도
                    continue
                break  # 404(모델 없음) 등은 다음 모델로
    code = getattr(last_err, "status_code", "")
    hint = {503: "AI 서버가 일시적으로 붐빕니다. 잠시 후 다시 보내 주세요.",
            429: "무료 사용 한도에 걸렸습니다. 1분쯤 뒤 다시 보내 주세요.",
            404: "모델 이름을 찾을 수 없습니다. 교수자 메뉴의 'AI 연결 테스트'로 확인하세요."}.get(code, "")
    yield f"⚠️ AI 응답 오류 {code}. {hint}\n\n({last_err})"


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


# ---------------------------------------------------------------- NE 파란 박스 (입력칸 없음)
def ne_box(scene):
    label = scene.get("ne_box")
    if not label:
        return
    st.markdown("#### 💉 Norepinephrine")
    st.info(f"처방: Norepinephrine **{NE_ORDER['drug_mg']}mg + 5% D/W {NE_ORDER['volume_ml']}mL**, "
            f"체중 **{NE_ORDER['weight_kg']}kg**  \n과제: {label}을(를) 정하고 주입 속도(mL/hr)를 계산하세요.")


# ---------------------------------------------------------------- 이미지 저장
_FONT_CANDIDATES = [
    os.path.join(os.path.dirname(__file__), "..", "fonts", "NanumGothic.ttf"),
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
]


def _font(size):
    from PIL import ImageFont
    for p in _FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size, index=1 if p.endswith(".ttc") else 0)
            except Exception:
                continue
    return ImageFont.load_default()


def _wrap(draw, text, font, width):
    lines = []
    for para in text.split("\n"):
        line = ""
        for ch in para:
            if draw.textlength(line + ch, font=font) <= width:
                line += ch
            else:
                lines.append(line)
                line = ch
        lines.append(line)
    return lines


def _plain(md):
    md = re.sub(r"\*\*(.+?)\*\*", r"\1", md)
    md = re.sub(r"^#+\s*", "", md, flags=re.M)
    md = re.sub("[\u2600-\u27BF\uFE0F\U0001F000-\U0001FFFF]\\s?", "", md)  # 이미지에 안 그려지는 이모지 제거
    return md.strip()


def conversation_png(title, label, purpose, hist, evaluation):
    from PIL import Image, ImageDraw
    W, PAD, BUB = 900, 32, 600
    f_title, f_sub, f_txt, f_name = _font(26), _font(17), _font(19), _font(15)
    tmp = ImageDraw.Draw(Image.new("RGB", (W, 10)))

    blocks = []  # (kind, payload)
    y = PAD
    head = [title, f"{label}" + (f"  ·  {purpose}" if purpose else ""),
            f"저장: {dt.datetime.now(KST):%Y-%m-%d %H:%M}"]
    y += 40 + 2 * 28 + 20
    for m in hist:
        lines = _wrap(tmp, m["content"], f_txt, BUB - 32)
        h = 28 * len(lines) + 24
        blocks.append((m["role"], lines, h))
        y += h + 34
    ev_lines = _wrap(tmp, _plain(evaluation), f_txt, W - 2 * PAD - 32) if evaluation else []
    ev_h = (28 * len(ev_lines) + 70) if ev_lines else 0
    H = y + ev_h + PAD

    img = Image.new("RGB", (W, H), "#F4F6FA")
    d = ImageDraw.Draw(img)
    d.text((PAD, PAD), head[0], font=f_title, fill="#1F2A44")
    d.text((PAD, PAD + 42), head[1], font=f_sub, fill="#2F5597")
    d.text((PAD, PAD + 70), head[2], font=f_sub, fill="#7A8299")
    y = PAD + 40 + 2 * 28 + 20
    d.line((PAD, y - 10, W - PAD, y - 10), fill="#D0D6E2", width=2)
    for role, lines, h in blocks:
        mine = role == "user"
        bw = max(tmp.textlength(ln, font=f_txt) for ln in lines) + 32 if lines else 60
        bw = min(max(bw, 80), BUB)
        x = W - PAD - bw if mine else PAD
        d.text((x if not mine else W - PAD - tmp.textlength("간호학생", font=f_name), y),
               "간호학생" if mine else label.split(" ·")[0], font=f_name, fill="#7A8299")
        y += 22
        d.rounded_rectangle((x, y, x + bw, y + h), radius=14,
                            fill="#2F5597" if mine else "#FFFFFF", outline=None if mine else "#D0D6E2")
        ty = y + 12
        for ln in lines:
            d.text((x + 16, ty), ln, font=f_txt, fill="#FFFFFF" if mine else "#1F2A44")
            ty += 28
        y += h + 12
    if ev_lines:
        y += 10
        d.rounded_rectangle((PAD, y, W - PAD, y + ev_h - 10), radius=14, fill="#FFF8E5", outline="#F0C36D")
        d.text((PAD + 16, y + 12), "대화 평가", font=f_sub, fill="#8A5A00")
        ty = y + 46
        for ln in ev_lines:
            d.text((PAD + 16, ty), ln, font=f_txt, fill="#3A2E10")
            ty += 28
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# ---------------------------------------------------------------- 대화창
def _evaluate(chat_cfg, hist, eval_note):
    transcript = "\n".join(("학생: " if m["role"] == "user" else "AI: ") + m["content"] for m in hist)
    checklist = "\n".join(f"- {c}" for c in chat_cfg["checklist"])
    user = (f"[대화 상대]\n{chat_cfg['label']}\n\n[확인 항목]\n{checklist}\n\n"
            f"[추가 지시]\n{eval_note}\n\n[대화 기록]\n{transcript}")
    return [{"role": "system", "content": EVAL_SYSTEM}, {"role": "user", "content": user}]


def chat_panel(scene, cfg):
    key = f"chat_{scene['id']}_{cfg['key']}"
    hist = st.session_state.setdefault(key, [])
    ended = st.session_state.get(key + "_ended", False)

    st.markdown(f"##### {cfg['avatar']} {cfg['label']}")
    if cfg.get("purpose"):
        st.markdown(f"**{cfg['purpose']}**")
    st.caption(CAUTION)

    box = st.container(height=380, border=True)
    with box:
        if not hist:
            st.caption('"안녕하세요"로 대화를 시작하세요.')
        for m in hist:
            with st.chat_message("user" if m["role"] == "user" else "assistant",
                                 avatar="🧑‍⚕️" if m["role"] == "user" else cfg["avatar"]):
                st.markdown(m["content"])

    prompt = st.chat_input("대화가 종료되었습니다." if ended else "메시지를 입력하세요…",
                           key=f"in_{key}", disabled=ended)
    if prompt and not ended:
        text = prompt.strip()
        if text == END_WORD or text.startswith(END_WORD):
            if not hist:
                st.warning("대화를 먼저 시작하세요.")
            else:
                st.session_state[key + "_ended"] = True
                with st.spinner("대화를 평가하는 중…"):
                    ev = "".join(solar_stream(_evaluate(cfg, hist, scene["eval_note"]), temperature=0.2))
                st.session_state[key + "_eval"] = ev
                st.rerun()
        elif not hist and START_WORD not in text:
            st.warning('대화는 "안녕하세요"로 시작해 주세요.')
        else:
            hist.append({"role": "user", "content": text})
            with box:
                with st.chat_message("user", avatar="🧑‍⚕️"):
                    st.markdown(text)
                with st.chat_message("assistant", avatar=cfg["avatar"]):
                    reply = st.write_stream(solar_stream(
                        [{"role": "system", "content": cfg["system"]}] + hist))
            hist.append({"role": "assistant", "content": reply})

    ev = st.session_state.get(key + "_eval")
    if ended and ev:
        with st.container(border=True):
            st.markdown("**📝 대화 평가**")
            st.markdown(ev)

    c1, c2 = st.columns([1, 1])
    if hist:
        png = conversation_png(scene["title"], cfg["label"], cfg.get("purpose"), hist, ev if ended else "")
        c1.download_button("🖼️ 대화 전체 이미지로 저장 (PNG)", png,
                           file_name=f"장면{scene['id']}_{cfg['key']}_대화.png", mime="image/png",
                           key=f"png_{key}", width="stretch")
        if c2.button("대화 다시 하기", key=f"reset_{key}", width="stretch"):
            for k in (key, key + "_ended", key + "_eval"):
                st.session_state.pop(k, None)
            st.rerun()


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
    st.markdown("#### 💬 AI와 대화하기 (Solar)")
    for i, cfg in enumerate(scene["chats"]):
        if i:
            st.write("")
        with st.container(border=True):  # 대화창을 위아래로 배치 (입력창도 각 박스 안에 표시)
            chat_panel(scene, cfg)
    st.divider()
    ne_box(scene)
    st.success("**과제 Part A를 작성하여 제출하세요.**")

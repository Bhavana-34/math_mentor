import os
import sys
import json
import tempfile
import time
from pathlib import Path

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from orchestrator import Orchestrator
from utils.ocr import extract_text_from_image
from utils.audio import transcribe_audio

st.set_page_config(
    page_title="Math Mentor — JEE AI Tutor",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

_CSS = """
<style>
.agent-step {background:#f0f4ff;border-left:4px solid #4c72ff;padding:8px 14px;margin:4px 0;border-radius:4px;font-size:0.88rem;}
.agent-step.warn {border-left-color:#f0a500;background:#fffbf0;}
.hitl-box {background:#fff3cd;border:1px solid #ffc107;padding:14px;border-radius:8px;margin:10px 0;}
.conf-high {color:#2ca02c;font-weight:bold;}
.conf-med {color:#f0a500;font-weight:bold;}
.conf-low {color:#d62728;font-weight:bold;}
.answer-box {background:#e8f5e9;border:2px solid #2ca02c;padding:16px;border-radius:8px;font-size:1.1rem;}
.source-chip {display:inline-block;background:#e3e8ff;padding:2px 10px;border-radius:12px;font-size:0.8rem;margin:2px;}
</style>
"""
st.markdown(_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading AI agents...")
def get_orchestrator():
    return Orchestrator()


def confidence_badge(conf: float) -> str:
    pct = int(conf * 100)
    cls = "conf-high" if conf >= 0.8 else ("conf-med" if conf >= 0.5 else "conf-low")
    return f'<span class="{cls}">{pct}%</span>'


def render_sidebar(orc: Orchestrator):
    st.sidebar.title("🧮 Math Mentor")
    st.sidebar.markdown("JEE AI Tutor · RAG + Agents + Memory")
    st.sidebar.divider()
    stats = orc.memory.get_stats()
    st.sidebar.metric("Problems Solved", stats["total"])
    st.sidebar.metric("Marked Correct ✅", stats["correct"])
    st.sidebar.metric("Marked Incorrect ❌", stats["incorrect"])
    st.sidebar.divider()
    with st.sidebar.expander("📚 Rebuild Knowledge Index"):
        if st.button("Rebuild Vector Index"):
            with st.spinner("Rebuilding..."):
                orc.rag.rebuild_index()
            st.success("Index rebuilt!")
    with st.sidebar.expander("🗃️ Recent Memory"):
        records = orc.memory.get_all_records()[-5:][::-1]
        if not records:
            st.write("No records yet.")
        for r in records:
            pq = r.get("parsed_question", {})
            fb = r.get("user_feedback", "pending")
            emoji = "✅" if fb == "correct" else ("❌" if fb == "incorrect" else "⏳")
            st.markdown(f"{emoji} **{pq.get('topic','?')}** — {pq.get('problem_text','')[:50]}...")
    st.sidebar.divider()
    st.sidebar.caption("Built with OpenAI GPT-4o · FAISS · Streamlit")


def render_input_section():
    st.header("📥 Submit a Math Problem")
    mode = st.radio(
        "Input Mode",
        ["✏️ Text", "🖼️ Image (OCR)", "🎙️ Audio (ASR)"],
        horizontal=True,
        key="input_mode",
    )
    return mode


def handle_text_input():
    text = st.text_area(
        "Type your math problem",
        height=120,
        placeholder="e.g. Find the roots of x^2 - 5x + 6 = 0",
        key="text_input",
    )
    return text, 1.0, False


def handle_image_input():
    uploaded = st.file_uploader("Upload image (JPG/PNG)", type=["jpg", "jpeg", "png"], key="img_upload")
    if uploaded is None:
        return "", 0.0, False, None

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(tmp_path, caption="Uploaded Image", use_container_width=True)
    with col2:
        with st.spinner("Running OCR..."):
            extracted, conf, needs_hitl = extract_text_from_image(tmp_path)

        st.markdown(f"**OCR Confidence:** {confidence_badge(conf)}", unsafe_allow_html=True)
        if needs_hitl:
            st.warning("⚠️ Low OCR confidence — please review and correct the text below.")

        corrected = st.text_area("Extracted / Corrected Text", value=extracted, height=120, key="ocr_corrected")

    return corrected, conf, needs_hitl, tmp_path


def handle_audio_input():
    uploaded = st.file_uploader("Upload audio (MP3/WAV/M4A)", type=["mp3", "wav", "m4a", "ogg"], key="audio_upload")
    if uploaded is None:
        return "", 0.0, False

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as tmp:
        tmp.write(uploaded.read())
        tmp_path = tmp.name

    with st.spinner("Transcribing audio..."):
        transcript, conf, needs_hitl = transcribe_audio(tmp_path)

    st.markdown(f"**ASR Confidence:** {confidence_badge(conf)}", unsafe_allow_html=True)
    if needs_hitl:
        st.warning("⚠️ Low transcription confidence — please review and correct below.")

    corrected = st.text_area("Transcript / Corrected Text", value=transcript, height=100, key="asr_corrected")
    return corrected, conf, needs_hitl


def render_agent_trace(trace: list):
    with st.expander("🔄 Agent Trace", expanded=False):
        for step in trace:
            cls = "agent-step warn" if "⚠️" in step.get("status", "") else "agent-step"
            st.markdown(
                f'<div class="{cls}"><b>{step["agent"]}</b> {step["status"]} — {step["summary"]}</div>',
                unsafe_allow_html=True,
            )


def render_retrieved_context(chunks: list):
    with st.expander(f"📚 Retrieved Context ({len(chunks)} chunks)", expanded=False):
        if not chunks:
            st.info("No context retrieved.")
            return
        for i, chunk in enumerate(chunks):
            score = chunk.get("score", 0)
            source = chunk.get("source", "unknown")
            st.markdown(f'**Chunk {i+1}** <span class="source-chip">{source}</span> Score: {score:.3f}', unsafe_allow_html=True)
            st.text(chunk.get("text", "")[:300] + "...")
            st.divider()


def render_solution(result: dict):
    solution = result.get("solution", {})
    verification = result.get("verification", {})
    explanation = result.get("explanation", "")
    conf = result.get("confidence", 0)

    st.subheader("📊 Solution")

    col1, col2, col3 = st.columns(3)
    col1.metric("Confidence", f"{int(conf*100)}%")
    col2.metric("Verified", "✅ Yes" if verification.get("is_correct") else "❌ No")
    col3.metric("Topic", result.get("parsed_problem", {}).get("topic", "?").capitalize())

    st.markdown(f'<div class="answer-box">🎯 <b>Final Answer:</b> {solution.get("answer", "N/A")}</div>', unsafe_allow_html=True)

    steps = solution.get("solution_steps", [])
    if steps:
        st.subheader("🪜 Solution Steps")
        for step in steps:
            step_num = step.get("step", "")
            desc = step.get("description", "")
            comp = step.get("computation", "")
            res = step.get("result", "")
            with st.expander(f"Step {step_num}: {desc}", expanded=True):
                if comp:
                    st.code(comp, language="")
                if res:
                    st.success(f"Result: {res}")

    if explanation:
        st.subheader("💡 Explanation")
        st.markdown(explanation)

    issues = verification.get("issues_found", [])
    if issues:
        st.subheader("⚠️ Verification Issues")
        for issue in issues:
            st.warning(issue)


def render_feedback(record_id: str, orc: Orchestrator):
    st.subheader("📣 Feedback")
    col1, col2 = st.columns([1, 2])
    with col1:
        feedback = st.radio("Was this solution correct?", ["✅ Correct", "❌ Incorrect"], key=f"fb_{record_id}")
    with col2:
        comment = st.text_area("Comment / Correction (optional)", key=f"cmt_{record_id}", height=80)

    if st.button("Submit Feedback", key=f"submit_fb_{record_id}"):
        fb_value = "correct" if "Correct" in feedback else "incorrect"
        orc.memory.update_feedback(record_id, fb_value, comment)
        st.success("Thank you! Feedback saved and will improve future responses.")


def render_hitl_panel(result: dict, raw_input: str, input_type: str, orc: Orchestrator):
    st.markdown('<div class="hitl-box">', unsafe_allow_html=True)
    st.subheader("🙋 Human Review Required")
    st.warning(f"**Reason:** {result.get('hitl_reason', 'Review needed')}")

    with st.form("hitl_form"):
        corrected_text = st.text_area(
            "Edit/confirm the problem statement:",
            value=result.get("parsed_problem", {}).get("problem_text", raw_input),
            height=100,
        )
        override_topic = st.selectbox(
            "Topic",
            ["auto", "algebra", "probability", "calculus", "linear_algebra", "other"],
        )
        proceed = st.form_submit_button("✅ Proceed with this input")

    if proceed:
        parsed_override = result.get("parsed_problem", {}).copy()
        parsed_override["problem_text"] = corrected_text
        parsed_override["needs_clarification"] = False
        if override_topic != "auto":
            parsed_override["topic"] = override_topic

        hitl_override = {"parsed_problem": parsed_override}
        with st.spinner("Re-running with your corrections..."):
            new_result = orc.run(
                raw_input=corrected_text,
                input_type=input_type,
                hitl_override=hitl_override,
            )
        st.session_state["result"] = new_result
        st.session_state["hitl_resolved"] = True
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def main():
    orc = get_orchestrator()
    render_sidebar(orc)

    if "result" not in st.session_state:
        st.session_state["result"] = None
    if "hitl_resolved" not in st.session_state:
        st.session_state["hitl_resolved"] = False

    mode = render_input_section()

    raw_input = ""
    input_type = "text"
    ocr_conf = 1.0
    needs_hitl_pre = False

    st.divider()

    if mode == "✏️ Text":
        raw_input, ocr_conf, needs_hitl_pre = handle_text_input()
        input_type = "text"
    elif mode == "🖼️ Image (OCR)":
        result_ocr = handle_image_input()
        if len(result_ocr) == 4:
            raw_input, ocr_conf, needs_hitl_pre, _ = result_ocr
        input_type = "image"
    elif mode == "🎙️ Audio (ASR)":
        raw_input, ocr_conf, needs_hitl_pre = handle_audio_input()
        input_type = "audio"

    st.divider()

    col_solve, _ = st.columns([1, 4])
    solve_clicked = col_solve.button("🚀 Solve Problem", type="primary", disabled=not raw_input.strip())

    if solve_clicked and raw_input.strip():
        st.session_state["hitl_resolved"] = False
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(msg: str, pct: int):
            progress_bar.progress(pct)
            status_text.text(msg)

        with st.spinner("Running agents..."):
            result = orc.run(
                raw_input=raw_input,
                input_type=input_type,
                progress_callback=update_progress,
            )
        st.session_state["result"] = result
        progress_bar.empty()
        status_text.empty()

    result = st.session_state.get("result")
    if result is None:
        st.info("👆 Enter a problem above and click **Solve Problem** to get started.")
        st.markdown("""
**Supported topics:**
- Algebra (quadratics, sequences, binomial theorem, logs)
- Probability (combinatorics, Bayes, distributions)
- Calculus (limits, derivatives, optimization)
- Linear Algebra (matrices, determinants, eigenvalues)

**Input modes:** type text, upload an image/screenshot, or upload audio
        """)
        return

    render_agent_trace(result.get("trace", []))
    render_retrieved_context(result.get("retrieved_chunks", []))

    if result.get("needs_hitl") and not st.session_state.get("hitl_resolved"):
        render_hitl_panel(result, raw_input, input_type, orc)

    if result.get("solution") and result["solution"].get("answer"):
        render_solution(result)

    if result.get("record_id") and result.get("solution", {}).get("answer"):
        render_feedback(result["record_id"], orc)


if __name__ == "__main__":
    main()
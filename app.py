import uuid
import time
import streamlit as st
import requests

st.set_page_config(page_title="Sales Bot", layout="wide")

API_URL = "http://localhost:8001"

# ---------------------------
# Session State Defaults
# ---------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Flag: True only while the backend is actively processing
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# -----------------------------------------------------------------------
# Progress cache — stores last known values so the fragment can render
# them INSTANTLY on each re-run before fetching the backend.
# This eliminates the "blank flash" that occurs between Streamlit clearing
# the fragment output and the next render call.
# -----------------------------------------------------------------------
if "prog_pct" not in st.session_state:
    st.session_state.prog_pct = 0
if "prog_msg" not in st.session_state:
    st.session_state.prog_msg = "Processing..."
# Persisted metrics shown permanently after processing finishes
if "last_metrics" not in st.session_state:
    st.session_state.last_metrics = {}

@st.fragment(run_every=1)
def progress_bar_fragment():
    placeholder = st.empty()

    # ── State 1: COMPLETED — render metrics from session state cache ──────
    # Fragment re-runs every 1s but reads from session state = instant, no blink.
    # Metrics persist here until the next upload starts.
    if st.session_state.last_metrics and not st.session_state.is_processing:
        m = st.session_state.last_metrics
        with placeholder.container():
            st.success("✅ Documents ingested successfully!")
            st.markdown("### ⏱️ Last Processing Timings")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Docs Loaded",       m.get("loading",   "N/A"))
            c2.metric("Text Chunked",      m.get("chunking",  "N/A"))
            c3.metric("Embeddings Stored", m.get("embedding", "N/A"))
            c4.metric("Total Time",        m.get("total",     "N/A"))
            st.markdown("---")
        return  # No network call needed when already done

    # ── State 2: IDLE — nothing to show ──────────────────────────────────
    if not st.session_state.is_processing:
        return

    # ── State 3: PROCESSING — cache-first render, then fetch & update ────
    # Render cached values first (instant → no blank frame visible)
    with placeholder.container():
        st.info(f"🔁 {st.session_state.prog_msg}")
        st.progress(int(st.session_state.prog_pct) / 100.0)

    try:
        resp = requests.get(f"{API_URL}/metrics", timeout=3)
        if resp.status_code != 200:
            return  # Keep showing cached values; retry next cycle

        backend_state = resp.json()
        status = backend_state.get("status")

        if status == "processing":
            new_pct = int(backend_state.get("progress", 0))
            new_msg = backend_state.get("message", "Processing…")

            # Cache the new values for the next fragment cycle
            st.session_state.prog_pct = new_pct
            st.session_state.prog_msg = new_msg

            # Update placeholder in-place with fresh values
            with placeholder.container():
                st.info(f"🔁 {new_msg}")
                st.progress(new_pct / 100.0)

        elif status == "done":
            st.session_state.is_processing = False
            st.session_state.prog_pct = 0
            st.session_state.prog_msg = "Processing..."
            metrics = backend_state.get("metrics", {})
            if metrics:
                st.session_state.last_metrics = metrics  # Persist for all future cycles

            # Render metrics immediately in this very cycle (no wait for next rerun)
            m = st.session_state.last_metrics
            with placeholder.container():
                st.success("✅ Documents ingested successfully!")
                st.markdown("### ⏱️ Last Processing Timings")
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Docs Loaded",       m.get("loading",   "N/A"))
                c2.metric("Text Chunked",      m.get("chunking",  "N/A"))
                c3.metric("Embeddings Stored", m.get("embedding", "N/A"))
                c4.metric("Total Time",        m.get("total",     "N/A"))
                st.markdown("---")

        elif status == "failed":
            st.session_state.is_processing = False
            st.session_state.prog_pct = 0
            st.session_state.prog_msg = "Processing..."
            error_msg = backend_state.get("metrics", {}).get("error", "Unknown error")
            placeholder.error(f"❌ Processing failed: {error_msg}")

        else:
            # Backend is idle
            st.session_state.is_processing = False
            placeholder.empty()

    except Exception:
        pass  # Keep showing cached values if backend unreachable

progress_bar_fragment()


# ---------------------------
# File Upload Section
# ---------------------------
st.title("🤖 AI Sales Bot Playground")
st.header("📤 Upload Documents")

col1, col2 = st.columns(2)
with col1:
    uploaded_files = st.file_uploader(
        "Upload PDF / DOCX / TXT",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
with col2:
    strategy     = st.selectbox("Chunking Strategy", ["Recursive", "Sentence", "Token", "Semantic", "Fixed"])
    chunk_size   = st.number_input("Chunk Size",    value=512, step=64)
    chunk_overlap = st.number_input("Chunk Overlap", value=64,  step=16)

if st.button("Upload"):
    if uploaded_files:
        files = [("files", (file.name, file.getvalue())) for file in uploaded_files]
        data  = {"strategy": strategy, "chunk_size": chunk_size, "chunk_overlap": chunk_overlap}
        try:
            response = requests.post(f"{API_URL}/upload", files=files, data=data)
            # Set the flag BEFORE rerun so the fragment starts polling immediately
            st.session_state.is_processing = True
            st.rerun()  # Single controlled rerun — starts the progress fragment loop
        except Exception as e:
            st.error(f"Error connecting to backend: {e}")
    else:
        st.warning("Please upload at least one file first.")

# ---------------------------
# Chat Section
# ---------------------------
st.header("💬 Chat with Sales Bot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for role, msg, *meta in st.session_state.messages:
    if role == "user":
        st.chat_message("user").write(msg)
    else:
        st.chat_message("assistant").write(msg)
        
        ret_time = None
        gen_time = None
        
        if meta:
            if len(meta) == 1:
                gen_time = meta[0]
            elif len(meta) >= 2:
                ret_time = meta[0]
                gen_time = meta[1]

        timing_parts = []
        if ret_time is not None:
            timing_parts.append(f"🔍 Retrieved in {ret_time:.2f}s")
        if gen_time is not None:
            timing_parts.append(f"⚡ Generated in {gen_time:.2f}s")
            
        if timing_parts:
            timing_str = " | ".join(timing_parts)
            st.markdown(
                f'<p style="text-align:right; color:#888; font-size:0.75rem; margin-top:-8px;">'
                f'{timing_str}</p>',
                unsafe_allow_html=True
            )

user_input = st.chat_input("Ask something...")

if user_input:
    st.session_state.messages.append(("user", user_input))
    st.chat_message("user").write(user_input)

    with st.spinner("Thinking..."):
        response = requests.get(
            f"{API_URL}/chat",
            params={"query": user_input, "session_id": st.session_state.session_id}
        )


    if response.status_code == 200:
        data = response.json()
        answer = data.get("answer", "")
        _ret_time = data.get("retrieval_time")
        _gen_time = data.get("generation_time")
    else:
        answer = f"⚠️ Error {response.status_code}: {response.text}"
        _ret_time = None
        _gen_time = None

    st.session_state.messages.append(("bot", answer, _ret_time, _gen_time))
    st.chat_message("assistant").write(answer)
    
    timing_parts = []
    if _ret_time is not None:
        timing_parts.append(f"🔍 Retrieved in {_ret_time:.2f}s")
    if _gen_time is not None:
        timing_parts.append(f"⚡ Generated in {_gen_time:.2f}s")
        
    if timing_parts:
        timing_str = " | ".join(timing_parts)
        st.markdown(
            f'<p style="text-align:right; color:#888; font-size:0.75rem; margin-top:-8px;">'
            f'{timing_str}</p>',
            unsafe_allow_html=True
        )


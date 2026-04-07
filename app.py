import streamlit as st
import boto3
import uuid
import json
from datetime import datetime
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Customer Care Agent",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Agent constants ───────────────────────────────────────────────────────────
AGENT_ID  = "UWZCBSKJMY"
ALIAS_ID  = "FDCDBWWB6O"
REGION    = "eu-north-1"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

:root {
    --bg:        #0f1117;
    --surface:   #1a1d27;
    --border:    #2a2d3e;
    --accent:    #6c63ff;
    --accent2:   #00d4aa;
    --text:      #e8eaf0;
    --muted:     #7a7f9a;
    --user-bg:   #1e2235;
    --agent-bg:  #161922;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif;
    color: var(--text);
}
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
#MainMenu, footer, header { visibility: hidden; }

.top-bar {
    display: flex; align-items: center; gap: 14px;
    padding: 18px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 24px;
}
.top-bar .logo {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, var(--accent), var(--accent2));
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
}
.top-bar h1 {
    margin: 0; font-size: 1.35rem; font-weight: 600;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.top-bar .subtitle { font-size: 0.78rem; color: var(--muted); margin-top: 2px; }

.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 500;
    background: rgba(0,212,170,0.12); color: var(--accent2);
    border: 1px solid rgba(0,212,170,0.25);
}
.status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent2); animation: pulse 2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

.chat-wrapper {
    max-height: 520px; overflow-y: auto; padding-right: 4px;
    scrollbar-width: thin; scrollbar-color: var(--border) transparent;
}
.msg-row { display: flex; margin-bottom: 18px; gap: 12px; animation: fadeUp 0.3s ease; }
@keyframes fadeUp { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.msg-row.user { flex-direction: row-reverse; }
.avatar {
    width: 34px; height: 34px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; flex-shrink: 0; margin-top: 2px;
}
.avatar.user  { background: linear-gradient(135deg, var(--accent), #9c63ff); }
.avatar.agent { background: linear-gradient(135deg, var(--accent2), #00a8ff); }
.bubble {
    max-width: 72%; padding: 12px 16px; border-radius: 14px;
    font-size: 0.9rem; line-height: 1.6;
}
.bubble.user  { background: var(--user-bg); border: 1px solid rgba(108,99,255,0.3); border-top-right-radius: 4px; }
.bubble.agent { background: var(--agent-bg); border: 1px solid var(--border); border-top-left-radius: 4px; }
.bubble .ts   { font-size: 0.68rem; color: var(--muted); margin-top: 6px; display: block; }

.trace-box {
    background: #0d0f18; border: 1px solid var(--border); border-radius: 10px;
    padding: 12px 16px; margin-top: 8px;
    font-family: 'DM Mono', monospace; font-size: 0.75rem; color: #9da8c7;
    max-height: 200px; overflow-y: auto;
}

.stat-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 14px; padding: 18px 20px; text-align: center;
}
.stat-card .val {
    font-size: 2rem; font-weight: 600;
    background: linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-card .lbl { font-size: 0.78rem; color: var(--muted); margin-top: 4px; }

.stTextInput input {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important; padding: 12px 16px !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15) !important;
}

.stButton > button {
    background: linear-gradient(135deg, var(--accent), #9c63ff) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important; font-weight: 500 !important;
    padding: 10px 22px !important; transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.session-badge {
    font-family: 'DM Mono', monospace; font-size: 0.72rem;
    background: rgba(108,99,255,0.1); border: 1px solid rgba(108,99,255,0.25);
    color: var(--accent); padding: 3px 10px; border-radius: 6px;
    display: inline-block; margin-top: 4px;
}
hr { border-color: var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# ── Bedrock client (picks up ~/.aws/credentials or IAM role automatically) ───
@st.cache_resource
def get_bedrock_client():
    return boto3.client(
        "bedrock-agent-runtime",
        region_name=REGION,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )


def invoke_agent(user_input: str, session_id: str):
    client = get_bedrock_client()
    response = client.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=ALIAS_ID,
        sessionId=session_id,
        inputText=user_input,
        enableTrace=True,
    )
    full_text = ""
    traces = []
    for event in response.get("completion", []):
        if "chunk" in event:
            chunk = event["chunk"]
            if "bytes" in chunk:
                full_text += chunk["bytes"].decode("utf-8")
        if "trace" in event:
            trace_data = event["trace"].get("trace", {})
            if trace_data:
                traces.append(trace_data)
    return full_text, traces


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎧 Customer Care Agent")
    st.markdown("---")

    st.markdown("**Session**")
    st.markdown(
        f'<span class="session-badge">{st.session_state.session_id[:18]}…</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🔄 New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

    show_traces = st.toggle("Show Agent Traces", value=False)

    st.markdown("---")
    st.caption("Powered by Amazon Bedrock · Built with Streamlit")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-bar">
  <div class="logo">🎧</div>
  <div>
    <h1>Customer Care Agent</h1>
    <div class="subtitle">Amazon Bedrock · eu-north-1</div>
  </div>
  <div style="margin-left:auto">
    <div class="status-pill"><div class="status-dot"></div> Live</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Stats row ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="stat-card"><div class="val">{len(st.session_state.messages)}</div><div class="lbl">Messages</div></div>', unsafe_allow_html=True)
with c2:
    turns = sum(1 for m in st.session_state.messages if m["role"] == "user")
    st.markdown(f'<div class="stat-card"><div class="val">{turns}</div><div class="lbl">Turns</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="stat-card"><div class="val">{st.session_state.session_id[:6].upper()}</div><div class="lbl">Session</div></div>', unsafe_allow_html=True)
with c4:
    trace_count = sum(len(m.get("traces", [])) for m in st.session_state.messages)
    st.markdown(f'<div class="stat-card"><div class="val">{trace_count}</div><div class="lbl">Trace Events</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Chat display ──────────────────────────────────────────────────────────────
chat_html = '<div class="chat-wrapper" id="chat-scroll">'

if not st.session_state.messages:
    chat_html += """
    <div style="text-align:center; padding: 60px 0; color: var(--muted);">
      <div style="font-size:2.5rem; margin-bottom:12px;">💬</div>
      <div style="font-size:0.95rem;">Send a message to start the conversation</div>
    </div>"""
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        avatar = "👤" if role == "user" else "🤖"
        bubble_cls = "user" if role == "user" else "agent"
        row_cls = "user" if role == "user" else ""
        ts = msg.get("ts", "")
        chat_html += f"""
        <div class="msg-row {row_cls}">
          <div class="avatar {bubble_cls}">{avatar}</div>
          <div class="bubble {bubble_cls}">
            {msg["content"]}
            <span class="ts">{ts}</span>
          </div>
        </div>"""

chat_html += "</div>"
st.markdown(chat_html, unsafe_allow_html=True)

# ── Traces (optional) ─────────────────────────────────────────────────────────
if show_traces:
    for msg in st.session_state.messages:
        if msg.get("traces") and msg["role"] == "assistant":
            with st.expander(f"🔍 Traces — {msg.get('ts', '')}"):
                st.markdown(
                    f'<div class="trace-box">{json.dumps(msg["traces"], indent=2, default=str)}</div>',
                    unsafe_allow_html=True,
                )

st.markdown("---")

# ── Input ─────────────────────────────────────────────────────────────────────
col_inp, col_btn = st.columns([5, 1])
with col_inp:
    user_input = st.text_input(
        "Message",
        label_visibility="collapsed",
        placeholder="Ask the customer care agent anything…",
        key="user_input_field",
    )
with col_btn:
    send = st.button("Send ➤")

# ── Handle send ───────────────────────────────────────────────────────────────
if send and user_input.strip():
    now = datetime.now().strftime("%H:%M")

    st.session_state.messages.append({
        "role": "user",
        "content": user_input.strip(),
        "ts": now,
        "traces": [],
    })

    try:
        with st.spinner("Agent is thinking…"):
            reply, traces = invoke_agent(user_input.strip(), st.session_state.session_id)

        st.session_state.messages.append({
            "role": "assistant",
            "content": reply or "*(No response received)*",
            "ts": datetime.now().strftime("%H:%M"),
            "traces": traces,
        })

    except Exception as e:
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"⚠️ Error: {str(e)}",
            "ts": datetime.now().strftime("%H:%M"),
            "traces": [],
        })

    st.rerun()

# Auto-scroll JS
st.markdown("""
<script>
const chatEnd = window.parent.document.getElementById("chat-end");
if(chatEnd){ chatEnd.scrollTop = chatEnd.scrollHeight; }
</script>
""", unsafe_allow_html=True)
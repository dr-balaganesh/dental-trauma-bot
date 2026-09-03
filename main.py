import streamlit as st
from openai import OpenAI
import os
import re

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DentalTraumaBot",
    page_icon="🦷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ============================================================
# HTML RENDER HELPER
# ============================================================
#
# Streamlit's st.markdown() runs content through a Markdown
# parser before applying unsafe_allow_html. Markdown treats any
# line indented by 4+ spaces (especially after a blank line) as
# a literal "indented code block" and prints it verbatim instead
# of parsing it as HTML. Since our HTML strings are written with
# nested Python-style indentation, that trap fires constantly and
# raw tags leak onto the page.
#
# Fix: strip leading whitespace from every line before handing
# the string to st.markdown, so nothing looks like a code block.
# ============================================================

def render_html(html: str):
    lines = [line.strip() for line in html.strip().split("\n")]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


# ============================================================
# OPENAI CLIENT
# ============================================================

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("OPENAI_API_KEY is not configured.")
    st.stop()

client = OpenAI(api_key=api_key)

# ============================================================
# LANGUAGE CONFIGURATION
# ============================================================

LANGUAGES = {
    "English": {"code": "en", "native": "English", "flag": "🇬🇧"},
    "Hindi": {"code": "hi", "native": "हिंदी", "flag": "🇮🇳"},
    "Tamil": {"code": "ta", "native": "தமிழ்", "flag": "🇮🇳"},
    "Telugu": {"code": "te", "native": "తెలుగు", "flag": "🇮🇳"},
    "Kannada": {"code": "kn", "native": "ಕನ್ನಡ", "flag": "🇮🇳"},
    "Malayalam": {"code": "ml", "native": "മലയാളം", "flag": "🇮🇳"},
    "Bengali": {"code": "bn", "native": "বাংলা", "flag": "🇮🇳"},
    "Marathi": {"code": "mr", "native": "मराठी", "flag": "🇮🇳"},
    "Gujarati": {"code": "gu", "native": "ગુજરાતી", "flag": "🇮🇳"},
    "Punjabi": {"code": "pa", "native": "ਪੰਜਾਬੀ", "flag": "🇮🇳"}
}

# ============================================================
# VIDEO LIBRARY
# ============================================================
#
# IMPORTANT:
# Videos are selected by the application, NOT by GPT.
#
# Tamil -> Tamil video
# All other languages -> English video
#

VIDEO_LIBRARY = {

    # --------------------------------------------------------
    # AVULSION - Tooth completely knocked out
    # --------------------------------------------------------
    "avulsion": {
        "ta": {
            "url": "https://www.youtube.com/watch?v=waI7tWEP-lg",
            "title": "கீழே விழுந்த முழு பல்லுக்கு என்ன செய்ய வேண்டும்?"
        },
        "default": {
            "url": "https://www.youtube.com/watch?v=vQycgeoMCgk",
            "title": "What to do when a tooth is completely knocked out"
        }
    },

    # --------------------------------------------------------
    # INTRUSION / EXTRUSION - Tooth pushed inward or outward
    # --------------------------------------------------------
    "intrusion_extrusion": {
        "ta": {
            "url": "https://www.youtube.com/watch?v=PTs25AGAO9c",
            "title": "பல் உள்ளே அல்லது வெளியே தள்ளப்பட்டால் என்ன செய்ய வேண்டும்?"
        },
        "default": {
            "url": "https://www.youtube.com/watch?v=aBOAfOfFE2M",
            "title": "What to do when a tooth is pushed inward or outward"
        }
    },

    # --------------------------------------------------------
    # CONCUSSION / SUBLUXATION / LATERAL LUXATION
    # --------------------------------------------------------
    "concussion_subluxation_lateral": {
        "ta": {
            "url": "https://www.youtube.com/watch?v=Sr9-eXlC56o",
            "title": "பல் அடிபட்டால் — அசையாத பல், அசையும் பல் அல்லது பக்கமாக நகர்ந்த பல்"
        },
        "default": {
            "url": "https://www.youtube.com/watch?v=W2pQTN2sLz4",
            "title": "Dental trauma — concussion, subluxation and lateral luxation"
        }
    }
}


def get_video_for_scenario(scenario, language_code):
    if scenario not in VIDEO_LIBRARY:
        return None

    video_group = VIDEO_LIBRARY[scenario]

    if language_code == "ta":
        return video_group["ta"]

    return video_group["default"]


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: radial-gradient(circle at top, #172554 0%, #0f172a 35%, #020617 100%);
    color: #f8fafc;
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 7rem;
}

/* HEADER */
.app-header {
    text-align: center;
    padding: 10px 0 25px 0;
}

.logo-circle {
    width: 76px;
    height: 76px;
    margin: auto;
    border-radius: 24px;
    background: linear-gradient(135deg, #2563eb, #06b6d4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 42px;
    box-shadow: 0 15px 40px rgba(37, 99, 235, 0.35);
}

.app-title {
    font-size: 34px;
    font-weight: 700;
    margin-top: 15px;
    letter-spacing: -1px;
}

.app-subtitle {
    color: #94a3b8;
    font-size: 15px;
    margin-top: 5px;
}

/* LANGUAGE CARD */
.language-card {
    background: rgba(15, 23, 42, 0.82);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 24px;
    padding: 28px;
    margin: 20px 0;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
}

.language-title {
    text-align: center;
    font-size: 21px;
    font-weight: 600;
    margin-bottom: 5px;
}

.language-subtitle {
    text-align: center;
    color: #94a3b8;
    font-size: 14px;
    margin-bottom: 20px;
}

/* BUTTONS */
div.stButton > button {
    width: 100%;
    min-height: 54px;
    border-radius: 14px;
    border: 1px solid rgba(148, 163, 184, 0.18);
    background: rgba(30, 41, 59, 0.8);
    color: #f8fafc;
    font-size: 15px;
    font-weight: 500;
    transition: all 0.2s ease;
}

div.stButton > button:hover {
    border-color: #3b82f6;
    background: rgba(37, 99, 235, 0.18);
    transform: translateY(-1px);
}

/* CHAT */
.chat-wrapper {
    margin-top: 20px;
}

.message-user {
    display: flex;
    justify-content: flex-end;
    margin: 16px 0;
}

.message-assistant {
    display: flex;
    justify-content: flex-start;
    margin: 16px 0;
}

.user-bubble {
    max-width: 75%;
    padding: 13px 17px;
    border-radius: 20px 20px 5px 20px;
    background: linear-gradient(135deg, #2563eb, #1d4ed8);
    color: white;
    font-size: 15px;
    line-height: 1.55;
    box-shadow: 0 8px 25px rgba(37, 99, 235, 0.20);
}

.bot-bubble {
    max-width: 78%;
    padding: 16px 18px;
    border-radius: 20px 20px 20px 5px;
    background: rgba(30, 41, 59, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.12);
    color: #e2e8f0;
    font-size: 15px;
    line-height: 1.65;
}

.bot-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #2563eb, #06b6d4);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 10px;
    flex-shrink: 0;
    font-size: 21px;
}

/* URGENCY CARDS */
.urgency-emergency {
    background: linear-gradient(135deg, rgba(127, 29, 29, 0.95), rgba(69, 10, 10, 0.95));
    border: 1px solid rgba(248, 113, 113, 0.5);
    border-radius: 18px;
    padding: 18px;
    margin: 18px 0;
}

.urgency-urgent {
    background: linear-gradient(135deg, rgba(120, 53, 15, 0.95), rgba(67, 20, 7, 0.95));
    border: 1px solid rgba(251, 191, 36, 0.4);
    border-radius: 18px;
    padding: 18px;
    margin: 18px 0;
}

.urgency-nonurgent {
    background: linear-gradient(135deg, rgba(20, 83, 45, 0.95), rgba(5, 46, 22, 0.95));
    border: 1px solid rgba(74, 222, 128, 0.35);
    border-radius: 18px;
    padding: 18px;
    margin: 18px 0;
}

/* VIDEO CARD */
.video-card {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid rgba(148, 163, 184, 0.15);
    border-radius: 22px;
    padding: 20px;
    margin: 25px 0;
}

.video-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 5px;
}

.video-subtitle {
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 15px;
}

/* DISCLAIMER */
.disclaimer {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 999;
    background: rgba(2, 6, 23, 0.96);
    backdrop-filter: blur(15px);
    border-top: 1px solid rgba(148, 163, 184, 0.15);
    padding: 11px 20px;
    text-align: center;
    color: #94a3b8;
    font-size: 12px;
}

.disclaimer strong {
    color: #fbbf24;
}

/* CHAT INPUT */
.stChatInputContainer {
    background: rgba(15, 23, 42, 0.95);
}
</style>
""",
    unsafe_allow_html=True
)

# ============================================================
# SESSION STATE
# ============================================================

if "language" not in st.session_state:
    st.session_state.language = None

if "language_code" not in st.session_state:
    st.session_state.language_code = None

if "messages" not in st.session_state:
    st.session_state.messages = []

if "scenario" not in st.session_state:
    st.session_state.scenario = None

if "urgency" not in st.session_state:
    st.session_state.urgency = None


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are DentalTraumaBot, a virtual assistant that educates and guides people
who have experienced dental trauma, and helps them understand the urgency of
their condition.

ROLE AND SCOPE

You are NOT a dentist. Do not provide a definitive diagnosis.

Never provide medication names or dosages.

Only respond to questions related to dental trauma. For any other topic, reply
exactly with:

"I'm sorry, I'm only trained to help with dental injuries and trauma. Please consult a relevant professional."

Use simple, clear, non-technical language suitable for the general public.

Stay calm and reassuring at all times.

Do not mention videos. The application selects and displays videos separately.

Always include this exact reminder in every single response you send (in
each language section, if there are two):

"This tool does not replace a dentist. A professional dental evaluation is necessary."

LANGUAGE HANDLING

The application has already asked the user for their preferred language
BEFORE this conversation begins. You will be told the selected language and
its language code in a separate system message on every turn. Because of
this:

- Do NOT ask the user which language they prefer.
- Do NOT repeat the introduction after the first message.
- Do NOT ask the user to confirm or re-select their language at any point.

If the selected language is English, respond only in English, in a single
section.

If the selected language is NOT English, every response you send — including
the very first message of the conversation — MUST be structured into exactly
two clearly separated sections, in this exact order:

1. A section written entirely in the selected language, starting with the
   heading: "🌐 [language name written in that language]"
2. A section written entirely in English, starting with the heading:
   "🇬🇧 English"

Both sections must convey the exact same medical meaning: the same urgency
classification, the same instructions, the same warnings, the same
reassurance, and the same closing question. Never summarize one section
differently from the other, never add extra content to only one section, and
never omit something from one section that appears in the other. Generate
both sections freshly for every response — do not reuse earlier phrasing
verbatim.

Never mix languages within a single sentence. Never use transliteration (for
example, no "Tanglish" such as "unga tooth loose ah irukka"). Always use the
proper native script for the selected language (Tamil script, Hindi script,
Devanagari, etc.), and keep the English section grammatically correct and
complete.

If the user switches language mid-conversation, switch immediately, continue
the assessment from the current step, and do not restart the conversation or
repeat the introduction.

CONVERSATION START (first message of a conversation only)

- Briefly introduce yourself.
- Explain that you help people understand what to do after a dental injury.
- Ask: "Is the injured tooth a permanent (adult) tooth or a baby tooth?"

Do not ask about language in this step — the application has already handled
language selection before you were called.

FOLLOW-UP QUESTIONS

Once you know whether it is a permanent or baby tooth, ask only for whatever
information is still missing (never re-ask something the user already told
you) to determine:

- Did the tooth break, chip, or fall out completely?
- Is the tooth loose?
- Is there bleeding?
- Was the tooth pushed inward or outward?
- Is there pain when biting?
- When did the injury happen?

URGENCY CLASSIFICATION

EMERGENCY:
- Tooth completely knocked out
- Tooth pushed inward or outward
- Heavy bleeding
- Severe pain
- Suspected jaw injury

URGENT:
- Tooth fracture with sensitivity
- Loose tooth
- Mild bleeding
- Pain when biting

NON-URGENT:
- Small enamel chip
- No pain
- No mobility

RESPONSE STRUCTURE

Once you have enough information to classify urgency, structure the response,
in order:

1. What likely happened (simple explanation)
2. Immediate steps to take
3. What NOT to do
4. Urgency and when to see a dentist:
   - EMERGENCY: "Seek dental care immediately. The sooner treatment begins, the better the chance of saving the tooth."
   - URGENT: "Visit a dentist within 24 hours."
   - NON-URGENT: "Schedule a dental visit soon for evaluation."
5. Reassurance

KNOCKED-OUT PERMANENT TOOTH (special handling)

- Hold the tooth by the crown only. Never touch the root.
- Rinse gently if dirty.
- Place it in milk or inside the cheek if possible.
- Go to a dentist immediately, ideally within 30–60 minutes.

BABY TEETH

- Never attempt to reinsert a baby tooth.
- Tell the patient to contact a dentist.

CLOSING

End every response (every section, if there are two) with this question,
translated into the selected language where applicable:

"Would you like tips on how to care for the tooth until you see a dentist?"

Keep responses concise. Do not make them unnecessarily long.
"""


# ============================================================
# HEADER
# ============================================================

render_html(
    """
<div class="app-header">
    <div class="logo-circle">🦷</div>
    <div class="app-title">DentalTraumaBot</div>
    <div class="app-subtitle">AI-assisted guidance after dental injuries</div>
</div>
"""
)


# ============================================================
# LANGUAGE SELECTION
# ============================================================

if st.session_state.language is None:

    render_html(
        """
<div class="language-card">
<div class="language-title">🌐 Choose your language</div>
<div class="language-subtitle">Select the language you would like to use</div>
</div>
"""
    )

    language_names = list(LANGUAGES.keys())

    # 2 columns
    for row_start in range(0, len(language_names), 2):

        cols = st.columns(2)

        for index, col in enumerate(cols):

            position = row_start + index

            if position >= len(language_names):
                continue

            language = language_names[position]
            info = LANGUAGES[language]

            with col:

                if st.button(
                    f"{info['flag']}  {info['native']}",
                    key=f"language_{info['code']}",
                    use_container_width=True
                ):
                    st.session_state.language = language
                    st.session_state.language_code = info["code"]
                    st.session_state.messages = []
                    st.rerun()

    # Footer disclaimer
    render_html(
        """
<div class="disclaimer">
⚠️ <strong>Medical disclaimer:</strong>
This tool does not replace a dentist.
A professional dental evaluation is necessary.
</div>
"""
    )

    st.stop()


# ============================================================
# LANGUAGE HEADER
# ============================================================

selected_language = st.session_state.language

col1, col2 = st.columns([5, 1])

with col1:
    render_html(
        f"""
<div style="color:#94a3b8; font-size:13px; margin-bottom:10px;">
🌐 Language: <strong style="color:#f8fafc;">{LANGUAGES[selected_language]['native']}</strong>
</div>
"""
    )

with col2:
    if st.button("↻", help="Start over"):
        st.session_state.language = None
        st.session_state.language_code = None
        st.session_state.messages = []
        st.session_state.scenario = None
        st.session_state.urgency = None
        st.rerun()


# ============================================================
# FIRST QUESTION
# ============================================================

FALLBACK_FIRST_MESSAGE = (
    "Hello! I'm DentalTraumaBot 🦷\n\n"
    "I can help you understand what to do after a dental injury.\n\n"
    "Is the injured tooth a **permanent (adult) tooth** or a **baby tooth**?"
)


def generate_first_message(language_name, language_code):
    """
    Generates the opening greeting through the model itself, in the
    selected language, instead of using a hardcoded English string.

    This is the actual fix for "clicking another language still shows
    English": previously the very first message in the chat was a
    static English string that never went through the model at all,
    so no language selection could ever change it.
    """

    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                f"The user's selected language is: {language_name} "
                f"({language_code}). Language selection is already complete "
                f"— do not ask about language again. This is the very first "
                f"message of the conversation: introduce yourself, briefly "
                f"explain that you help people understand what to do after "
                f"a dental injury, and ask whether the injured tooth is a "
                f"permanent (adult) tooth or a baby tooth. Follow the "
                f"LANGUAGE HANDLING rules for how to structure this message."
            )
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=api_messages,
            max_tokens=900,
            temperature=0.2
        )

        return response.choices[0].message.content

    except Exception as e:

        st.error(f"OpenAI error: {e}")

        return FALLBACK_FIRST_MESSAGE


if not st.session_state.messages:

    with st.spinner("DentalTraumaBot is starting..."):

        first_reply = generate_first_message(
            selected_language,
            st.session_state.language_code
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": first_reply
        }
    )


# ============================================================
# SCENARIO DETECTION
# ============================================================

def detect_scenario(text):

    text_lower = text.lower()

    # AVULSION
    avulsion_words = [
        "fallen out", "fell out", "knocked out", "completely out",
        "came out", "lost the tooth", "tooth is out", "tooth fell"
    ]

    if any(word in text_lower for word in avulsion_words):
        return "avulsion", "EMERGENCY"

    # INTRUSION / EXTRUSION
    intrusion_words = [
        "pushed inward", "pushed inside", "went inside", "intruded",
        "intrusion", "tooth is inside", "tooth pushed in"
    ]

    extrusion_words = [
        "pushed outward", "pushed out", "coming out", "extruded",
        "extrusion", "tooth is sticking out"
    ]

    if any(word in text_lower for word in intrusion_words + extrusion_words):
        return "intrusion_extrusion", "EMERGENCY"

    # LATERAL LUXATION
    lateral_words = [
        "sideways", "side way", "moved sideways", "pushed sideways",
        "tooth moved to the side", "tooth is sideways"
    ]

    if any(word in text_lower for word in lateral_words):
        return "concussion_subluxation_lateral", "URGENT"

    # SUBLUXATION
    mobile_words = [
        "loose", "mobile", "moving", "moves", "shaking", "wobbly", "wobbles"
    ]

    if any(word in text_lower for word in mobile_words):
        return "concussion_subluxation_lateral", "URGENT"

    # CONCUSSION
    concussion_words = [
        "hit", "hit the tooth", "bumped", "impact", "injury",
        "not mobile", "not loose", "doesn't move", "does not move"
    ]

    if any(word in text_lower for word in concussion_words):
        return "concussion_subluxation_lateral", "URGENT"

    return None, None


# ============================================================
# DISPLAY CHAT
# ============================================================

for msg in st.session_state.messages:

    if msg["role"] == "assistant":

        content = msg["content"]

        content_html = re.sub(
            r"\*\*(.*?)\*\*",
            r"<strong>\1</strong>",
            content
        )

        content_html = content_html.replace("\n", "<br>")

        render_html(
            f"""
<div class="message-assistant">
    <div class="bot-avatar">🦷</div>
    <div class="bot-bubble">{content_html}</div>
</div>
"""
        )

    elif msg["role"] == "user":

        content = msg["content"].replace("\n", "<br>")

        render_html(
            f"""
<div class="message-user">
    <div class="user-bubble">{content}</div>
</div>
"""
        )


# ============================================================
# VIDEO
# ============================================================

if st.session_state.scenario:

    video = get_video_for_scenario(
        st.session_state.scenario,
        st.session_state.language_code
    )

    if video:

        render_html(
            """
<div class="video-card">
    <div class="video-title">🎥 Helpful video</div>
    <div class="video-subtitle">Watch this short video for guidance about this type of dental injury.</div>
</div>
"""
        )

        st.video(video["url"])


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input("Describe what happened to the tooth...")


if user_input:

    # ADD USER MESSAGE
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    # DETECT SCENARIO
    #
    # The new conversation flow asks several separate follow-up
    # questions ("Is it loose?" -> "yes", "Was it pushed inward?" ->
    # "no") instead of one open question answered in a single message.
    # Scanning only the newest message misses trigger words that were
    # given in an earlier turn, so the video never appeared. Scanning
    # the full accumulated user conversation instead keeps detection
    # working across multi-turn Q&A.
    all_user_text = " ".join(
        message["content"]
        for message in st.session_state.messages
        if message["role"] == "user"
    )

    scenario, urgency = detect_scenario(all_user_text)

    if scenario:
        st.session_state.scenario = scenario
        st.session_state.urgency = urgency

    # PREPARE GPT MESSAGES
    api_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                f"The user's selected language is: "
                f"{selected_language} ({st.session_state.language_code})."
            )
        }
    ]

    for message in st.session_state.messages:
        api_messages.append(
            {"role": message["role"], "content": message["content"]}
        )

    # GPT REQUEST
    try:

        with st.spinner("DentalTraumaBot is thinking..."):

            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=api_messages,
                max_tokens=900,
                temperature=0.2
            )

        reply = response.choices[0].message.content

    except Exception as e:

        reply = (
            "I'm sorry, I couldn't process that request right now. "
            "Please try again or contact a dentist."
        )

        st.error(f"OpenAI error: {e}")

    # SAVE RESPONSE
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    # RERUN TO DISPLAY
    st.rerun()


# ============================================================
# FIXED MEDICAL DISCLAIMER
# ============================================================

render_html(
    """
<div class="disclaimer">
⚠️ <strong>Medical disclaimer:</strong>
This tool does not replace a dentist.
A professional dental evaluation is necessary.
</div>
"""
)

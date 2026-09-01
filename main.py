
import streamlit as st
from openai import OpenAI
import os

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
    "English": {
        "code": "en",
        "native": "English",
        "flag": "🇬🇧"
    },
    "Hindi": {
        "code": "hi",
        "native": "हिंदी",
        "flag": "🇮🇳"
    },
    "Tamil": {
        "code": "ta",
        "native": "தமிழ்",
        "flag": "🇮🇳"
    },
    "Telugu": {
        "code": "te",
        "native": "తెలుగు",
        "flag": "🇮🇳"
    },
    "Kannada": {
        "code": "kn",
        "native": "ಕನ್ನಡ",
        "flag": "🇮🇳"
    },
    "Malayalam": {
        "code": "ml",
        "native": "മലയാളം",
        "flag": "🇮🇳"
    },
    "Bengali": {
        "code": "bn",
        "native": "বাংলা",
        "flag": "🇮🇳"
    },
    "Marathi": {
        "code": "mr",
        "native": "मराठी",
        "flag": "🇮🇳"
    },
    "Gujarati": {
        "code": "gu",
        "native": "ગુજરાતી",
        "flag": "🇮🇳"
    },
    "Punjabi": {
        "code": "pa",
        "native": "ਪੰਜਾਬੀ",
        "flag": "🇮🇳"
    }
}

# ============================================================
# YOUTUBE VIDEO LIBRARY
# ============================================================

VIDEO_LIBRARY = {

    # ========================================================
    # AVULSION
    # Completely knocked-out tooth
    # ========================================================

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

    # ========================================================
    # INTRUSION / EXTRUSION
    # ========================================================

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

    # ========================================================
    # CONCUSSION / SUBLUXATION / LATERAL LUXATION
    # ========================================================

    "concussion_subluxation_lateral": {
        "ta": {
            "url": "https://www.youtube.com/watch?v=Sr9-eXlC56o",
            "title": "பல் அடிபட்டால் என்ன செய்ய வேண்டும்?"
        },

        "default": {
            "url": "https://www.youtube.com/watch?v=W2pQTN2sLz4",
            "title": "Dental trauma: concussion, subluxation and lateral luxation"
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

/* ==========================================================
   GLOBAL
========================================================== */

.stApp {

    background:
        radial-gradient(
            circle at 50% -10%,
            #172554 0%,
            #0f172a 38%,
            #020617 100%
        );

    color: #f8fafc;
}

.block-container {

    max-width: 900px;

    padding-top: 2rem;

    padding-bottom: 7rem;
}

/* ==========================================================
   HEADER
========================================================== */

.app-header {

    text-align: center;

    padding:
        10px 0 25px 0;
}

.logo-circle {

    width: 78px;

    height: 78px;

    margin: auto;

    border-radius: 24px;

    background:
        linear-gradient(
            135deg,
            #2563eb,
            #06b6d4
        );

    display: flex;

    align-items: center;

    justify-content: center;

    font-size: 42px;

    box-shadow:
        0 15px 45px
        rgba(37, 99, 235, 0.35);
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

/* ==========================================================
   LANGUAGE CARD
========================================================== */

.language-card {

    background:
        rgba(15, 23, 42, 0.85);

    border:
        1px solid rgba(148, 163, 184, 0.15);

    border-radius: 24px;

    padding: 28px;

    margin: 15px 0 25px 0;

    box-shadow:
        0 20px 60px
        rgba(0, 0, 0, 0.25);
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

    margin-bottom: 22px;
}

/* ==========================================================
   LANGUAGE BUTTONS
========================================================== */

div.stButton > button {

    width: 100%;

    min-height: 52px;

    border-radius: 14px;

    border:
        1px solid rgba(148, 163, 184, 0.18);

    background:
        rgba(30, 41, 59, 0.75);

    color: #f8fafc;

    font-size: 15px;

    font-weight: 500;

    transition:
        all 0.2s ease;
}

div.stButton > button:hover {

    border-color: #3b82f6;

    background:
        rgba(37, 99, 235, 0.18);

    transform:
        translateY(-1px);
}

/* ==========================================================
   LANGUAGE INDICATOR
========================================================== */

.language-indicator {

    display: inline-block;

    background:
        rgba(30, 41, 59, 0.8);

    border:
        1px solid rgba(148, 163, 184, 0.15);

    padding:
        7px 12px;

    border-radius: 12px;

    color: #cbd5e1;

    font-size: 13px;

    margin-bottom: 15px;
}

/* ==========================================================
   VIDEO CARD
========================================================== */

.video-card {

    background:
        rgba(15, 23, 42, 0.9);

    border:
        1px solid rgba(148, 163, 184, 0.15);

    border-radius: 22px;

    padding: 20px;

    margin:
        25px 0 10px 0;

    box-shadow:
        0 15px 45px
        rgba(0, 0, 0, 0.20);
}

.video-title {

    font-size: 18px;

    font-weight: 600;

    color: #f8fafc;

    margin-bottom: 5px;
}

.video-subtitle {

    color: #94a3b8;

    font-size: 13px;

    margin-bottom: 15px;
}

/* ==========================================================
   URGENCY
========================================================== */

.urgency-emergency {

    background:
        rgba(127, 29, 29, 0.35);

    border:
        1px solid rgba(248, 113, 113, 0.45);

    border-radius: 18px;

    padding: 16px;

    margin: 15px 0;

    color: #fecaca;
}

.urgency-urgent {

    background:
        rgba(120, 53, 15, 0.35);

    border:
        1px solid rgba(251, 191, 36, 0.4);

    border-radius: 18px;

    padding: 16px;

    margin: 15px 0;

    color: #fde68a;
}

.urgency-nonurgent {

    background:
        rgba(20, 83, 45, 0.35);

    border:
        1px solid rgba(74, 222, 128, 0.35);

    border-radius: 18px;

    padding: 16px;

    margin: 15px 0;

    color: #bbf7d0;
}

/* ==========================================================
   CHAT
========================================================== */

[data-testid="stChatMessage"] {

    background:
        transparent;

    border:
        none;
}

/* Assistant message */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-assistant"]
) {

    background:
        rgba(30, 41, 59, 0.65);

    border:
        1px solid rgba(148, 163, 184, 0.10);

    border-radius: 20px;

    padding: 4px 8px;

    margin:
        12px 0;
}

/* User message */

[data-testid="stChatMessage"]:has(
    [data-testid="chatAvatarIcon-user"]
) {

    background:
        rgba(37, 99, 235, 0.16);

    border:
        1px solid rgba(59, 130, 246, 0.12);

    border-radius: 20px;

    padding: 4px 8px;

    margin:
        12px 0;
}

/* ==========================================================
   CHAT INPUT
========================================================== */

[data-testid="stChatInput"] {

    border-radius: 18px;
}

/* ==========================================================
   DISCLAIMER
========================================================== */

.disclaimer {

    position: fixed;

    bottom: 0;

    left: 0;

    right: 0;

    z-index: 999;

    background:
        rgba(2, 6, 23, 0.97);

    backdrop-filter:
        blur(15px);

    border-top:
        1px solid rgba(148, 163, 184, 0.15);

    padding:
        11px 20px;

    text-align: center;

    color: #94a3b8;

    font-size: 12px;
}

.disclaimer strong {

    color: #fbbf24;
}

/* ==========================================================
   MOBILE
========================================================== */

@media (max-width: 600px) {

    .block-container {

        padding-left: 1rem;

        padding-right: 1rem;
    }

    .app-title {

        font-size: 28px;
    }

    .logo-circle {

        width: 68px;

        height: 68px;

        font-size: 36px;
    }

    .disclaimer {

        font-size: 10px;

        padding:
            9px 10px;
    }
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
You are DentalTraumaBot.

You are a dental trauma education and triage assistant.

Your purpose is to help the general public understand what to do after a dental injury.

You must use simple, clear, non-technical language.

IMPORTANT SAFETY RULES:

You are not a dentist.

Do not provide a definitive diagnosis.

Do not provide medication names or dosages.

Do not give false reassurance.

When red-flag symptoms are present, clearly emphasize the need for urgent dental care.

The application displays the medical disclaimer separately.
DO NOT include a medical disclaimer in your response.

TOPIC RESTRICTION:

Only answer questions related to dental trauma.

If the user asks about an unrelated topic, respond:

"I'm sorry, I'm only trained to help with dental injuries and trauma. Please consult a relevant professional."

LANGUAGE:

The user's selected language will be provided separately.

Respond in the selected language.

If the selected language is not English, provide:

1. The complete response in the selected language.
2. The complete English equivalent.

Do not mix languages in sentences.

Do not use transliteration.

Do not ask the user to select their language again.

Do not repeat the introduction after the initial response.

ASSESSMENT:

Important dental trauma categories include:

CONCUSSION:
The tooth has been hit but is not mobile and has not been displaced.

SUBLUXATION:
The tooth is mobile but has not been displaced.

LATERAL LUXATION:
The tooth has been displaced sideways.

INTRUSION:
The tooth has been pushed inward into the socket.

EXTRUSION:
The tooth has been partially pushed outward from the socket.

AVULSION:
The tooth has completely fallen out.

URGENCY:

EMERGENCY:
- Completely knocked-out permanent tooth
- Intrusion
- Extrusion
- Heavy bleeding
- Severe pain
- Suspected jaw injury

URGENT:
- Tooth fracture with sensitivity
- Subluxation / loose tooth
- Lateral luxation
- Mild bleeding
- Pain when biting
- Concussion after significant trauma

NON-URGENT:
- Small enamel chip
- No pain
- No mobility
- No displacement

AVULSED PERMANENT TOOTH:

Explain:

- Hold the tooth by the crown.
- Do not touch the root.
- If dirty, rinse gently.
- Do not scrub the root.
- If appropriate, keep it in milk or inside the cheek.
- Seek dental care immediately.
- The sooner treatment begins, the better the chance of saving the tooth.

BABY TOOTH:

Never attempt to reinsert a baby tooth.

Tell the patient to contact a dentist.

RESPONSE STRUCTURE:

When appropriate, organize the response into:

What may have happened

What to do now

What NOT to do

When to see a dentist

Reassurance

Do not make responses unnecessarily long.

End every response with:

"Would you like tips on how to care for the tooth until you see a dentist?"

Do not mention the YouTube videos.

The application selects the appropriate educational video separately.
"""


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="app-header">

        <div class="logo-circle">
            🦷
        </div>

        <div class="app-title">
            DentalTraumaBot
        </div>

        <div class="app-subtitle">
            AI-assisted guidance after dental injuries
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LANGUAGE SELECTION SCREEN
# ============================================================

if st.session_state.language is None:

    st.markdown(
        """
        <div class="language-card">

            <div class="language-title">
                🌐 Choose your language
            </div>

            <div class="language-subtitle">
                Select the language you would like to continue in
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    language_names = list(LANGUAGES.keys())

    # Two-column language buttons

    for row in range(0, len(language_names), 2):

        cols = st.columns(2)

        for i, col in enumerate(cols):

            index = row + i

            if index >= len(language_names):
                continue

            language = language_names[index]

            info = LANGUAGES[language]

            with col:

                if st.button(
                    f"{info['flag']}  {info['native']}",
                    key=f"language_button_{info['code']}",
                    use_container_width=True
                ):

                    st.session_state.language = language

                    st.session_state.language_code = info["code"]

                    st.session_state.messages = []

                    st.session_state.scenario = None

                    st.session_state.urgency = None

                    st.rerun()

    # Footer

    st.markdown(
        """
        <div class="disclaimer">

            ⚠️ <strong>Medical disclaimer:</strong>
            This tool does not replace a dentist.
            A professional dental evaluation is necessary.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.stop()


# ============================================================
# LANGUAGE INDICATOR
# ============================================================

selected_language = st.session_state.language

col1, col2 = st.columns([5, 1])

with col1:

    st.markdown(
        f"""
        <div class="language-indicator">

            🌐 {LANGUAGES[selected_language]['native']}

        </div>
        """,
        unsafe_allow_html=True
    )

with col2:

    if st.button(
        "↻",
        help="Start a new conversation"
    ):

        st.session_state.language = None

        st.session_state.language_code = None

        st.session_state.messages = []

        st.session_state.scenario = None

        st.session_state.urgency = None

        st.rerun()


# ============================================================
# INITIAL QUESTION
# ============================================================

if len(st.session_state.messages) == 0:

    initial_message = (
        "Hello! I'm DentalTraumaBot 🦷\n\n"
        "I can help you understand what to do after a dental injury.\n\n"
        "Is the injured tooth a **permanent (adult) tooth** "
        "or a **baby tooth**?"
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": initial_message
        }
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "assistant":

        with st.chat_message(
            "assistant",
            avatar="🦷"
        ):

            st.markdown(
                message["content"]
            )

    elif message["role"] == "user":

        with st.chat_message(
            "user",
            avatar="👤"
        ):

            st.markdown(
                message["content"]
            )


# ============================================================
# VIDEO DISPLAY
# ============================================================

if st.session_state.scenario:

    video = get_video_for_scenario(
        st.session_state.scenario,
        st.session_state.language_code
    )

    if video:

        st.markdown(
            f"""
            <div class="video-card">

                <div class="video-title">
                    🎥 Helpful video
                </div>

                <div class="video-subtitle">
                    {video['title']}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        st.video(video["url"])


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Describe what happened to the tooth..."
)


if user_input:

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # ========================================================
    # BASIC SCENARIO DETECTION
    # ========================================================

    text = user_input.lower()

    detected_scenario = None
    detected_urgency = None

    # --------------------------------------------------------
    # AVULSION
    # --------------------------------------------------------

    if any(
        phrase in text
        for phrase in [
            "fallen out",
            "fell out",
            "knocked out",
            "completely out",
            "came out",
            "tooth is out",
            "tooth fell"
        ]
    ):

        detected_scenario = "avulsion"

        detected_urgency = "EMERGENCY"

    # --------------------------------------------------------
    # INTRUSION / EXTRUSION
    # --------------------------------------------------------

    elif any(
        phrase in text
        for phrase in [
            "pushed inward",
            "pushed inside",
            "went inside",
            "intruded",
            "intrusion",
            "tooth pushed in",
            "pushed outward",
            "pushed out",
            "extruded",
            "extrusion",
            "sticking out"
        ]
    ):

        detected_scenario = "intrusion_extrusion"

        detected_urgency = "EMERGENCY"

    # --------------------------------------------------------
    # LATERAL LUXATION
    # --------------------------------------------------------

    elif any(
        phrase in text
        for phrase in [
            "sideways",
            "side way",
            "moved sideways",
            "pushed sideways",
            "moved to the side",
            "tooth is sideways"
        ]
    ):

        detected_scenario = (
            "concussion_subluxation_lateral"
        )

        detected_urgency = "URGENT"

    # --------------------------------------------------------
    # SUBLUXATION
    # --------------------------------------------------------

    elif any(
        phrase in text
        for phrase in [
            "loose",
            "mobile",
            "moving",
            "moves",
            "shaking",
            "wobbly",
            "wobbles"
        ]
    ):

        detected_scenario = (
            "concussion_subluxation_lateral"
        )

        detected_urgency = "URGENT"

    # --------------------------------------------------------
    # CONCUSSION
    # --------------------------------------------------------

    elif any(
        phrase in text
        for phrase in [
            "hit the tooth",
            "hit",
            "bumped",
            "impact",
            "injury",
            "not mobile",
            "not loose",
            "doesn't move",
            "does not move"
        ]
    ):

        detected_scenario = (
            "concussion_subluxation_lateral"
        )

        detected_urgency = "URGENT"

    # --------------------------------------------------------
    # SAVE DETECTION
    # --------------------------------------------------------

    if detected_scenario:

        st.session_state.scenario = detected_scenario

        st.session_state.urgency = detected_urgency

    # ========================================================
    # BUILD OPENAI MESSAGE HISTORY
    # ========================================================

    api_messages = [

        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },

        {
            "role": "system",
            "content": (
                "The user selected language: "
                f"{selected_language} "
                f"({st.session_state.language_code})."
            )
        }

    ]

    # Add conversation

    for message in st.session_state.messages:

        api_messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )

    # ========================================================
    # OPENAI REQUEST
    # ========================================================

    try:

        with st.spinner(
            "DentalTraumaBot is thinking..."
        ):

            response = client.chat.completions.create(

                model="gpt-4.1-mini",

                messages=api_messages,

                max_tokens=900,

                temperature=0.2
            )

        reply = response.choices[0].message.content

    except Exception as error:

        st.error(
            "Unable to connect to the AI service."
        )

        reply = (
            "I'm sorry, I couldn't process your request "
            "right now. Please try again or contact a dentist."
        )

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply
        }
    )

    # ========================================================
    # REFRESH
    # ========================================================

    st.rerun()


# ============================================================
# FIXED DISCLAIMER
# ============================================================

st.markdown(
    """
    <div class="disclaimer">

        ⚠️ <strong>Medical disclaimer:</strong>
        This tool does not replace a dentist.
        A professional dental evaluation is necessary.

    </div>
    """,
    unsafe_allow_html=True
)


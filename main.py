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
# SCENARIO TAG PARSING
# ============================================================
#
# GPT is instructed (see SYSTEM_PROMPT below) to append a hidden
# [SCENARIO:value] tag to the end of every response. This is what
# selects the video — it replaces scanning the user's raw text for
# a fixed list of English keywords, which broke both across
# multi-turn Q&A and for any non-English conversation. Defined
# here, early in the file, since generate_first_message() (further
# down) needs it the moment the script runs.
# ============================================================

SCENARIO_TAG_PATTERN = re.compile(
    r"\[SCENARIO:\s*(avulsion|intrusion_extrusion|concussion_subluxation_lateral|none)\s*\]",
    re.IGNORECASE
)

SCENARIO_URGENCY_MAP = {
    "avulsion": "EMERGENCY",
    "intrusion_extrusion": "EMERGENCY",
    "concussion_subluxation_lateral": "URGENT",
}


def extract_scenario_tag(reply_text):
    """
    Pulls the [SCENARIO:value] tag out of a reply, strips it from the
    text shown to the user, and returns (cleaned_text, scenario_or_None).
    """

    match = SCENARIO_TAG_PATTERN.search(reply_text)

    cleaned = SCENARIO_TAG_PATTERN.sub("", reply_text).rstrip()

    scenario_value = None

    if match:
        value = match.group(1).lower()
        if value != "none":
            scenario_value = value

    return cleaned, scenario_value


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
You are DentalTraumaBot, an AI-assisted dental trauma guidance
assistant for members of the general public.

Your purpose is to help a person understand what may have happened
after a dental injury, determine the likely type and urgency of the
injury through conversational triage, provide appropriate immediate
first-aid guidance, and encourage timely professional dental care.

Your responses must be understandable to a layperson and should
follow established dental trauma guidance.

============================================================
1. ROLE AND SAFETY
============================================================

You are NOT a dentist.

You must not provide a definitive diagnosis.

You must not claim certainty when the information provided by the
patient is insufficient.

Use language such as:

"This may be consistent with..."
"This sounds like..."
"Based on what you have described..."

Do not provide medication names or dosages.

Do not give unnecessary technical terminology.

If a technical dental term is useful, explain it immediately in
simple language.

Stay calm, reassuring, and concise.

Do not frighten the patient unnecessarily.

Do not provide information unrelated to dental trauma.

If the user asks about something unrelated to dental trauma,
respond:

"I'm sorry, I'm only trained to help with dental injuries and
trauma. Please consult a relevant professional."

============================================================
2. LANGUAGE
============================================================

The application has already asked the patient to select a language.

The selected language and language code will be provided to you by
the application.

NEVER ask the patient to select a language again.

NEVER repeat the language-selection question.

NEVER restart the conversation when the language changes.

If the selected language is English:

Respond only in English.

If the selected language is not English:

Provide exactly TWO sections:

1. The complete response in the selected language.
2. The complete equivalent response in English.

The two sections must contain exactly the same medical meaning.

They must contain the same:

- assessment
- urgency
- instructions
- warnings
- reassurance
- closing question

Do not summarize one language differently.

Do not add information to only one language.

Do not omit information from either language.

Do not mix languages within sentences.

Do not use transliteration.

Use the correct native writing system.

============================================================
3. CONVERSATIONAL TRIAGE
============================================================

The interaction must be progressive.

Do NOT ask every question at once.

Ask only the next question needed to identify the injury.

Do NOT repeat information that the patient has already provided.

The conversation should progressively determine:

A. Tooth type
B. What happened to the tooth
C. Whether the tooth is displaced
D. Whether the tooth is mobile
E. Whether the tooth is fractured
F. Whether there is bleeding
G. Whether there is pain
H. Whether there is pain when biting
I. When the injury occurred
J. Whether there may be associated jaw, lip, cheek, or gum injury

============================================================
4. FIRST QUESTION
============================================================

At the beginning of the conversation:

Briefly introduce yourself.

Explain that you help people understand what to do after a dental
injury.

Then ask:

"Is the injured tooth a permanent (adult) tooth or a baby tooth?"

Do not ask the language question because the application has
already handled language selection.

============================================================
5. TRAUMA IDENTIFICATION
============================================================

After determining the tooth type, progressively identify what
happened.

Ask simple questions that a patient can understand.

Examples:

"Did the tooth completely come out, or is it still in your mouth?"

"Does the tooth look like it has been pushed inward?"

"Does the tooth look longer or pushed outward?"

"Has the tooth moved sideways?"

"Is the tooth loose or moving?"

"Was the tooth hit but does not appear loose or displaced?"

"Is part of the tooth broken or chipped?"

"Is there bleeding?"

"Does it hurt when you bite?"

"How long ago did the injury happen?"

Only ask questions that are still necessary.

============================================================
6. TRAUMA CATEGORIES
============================================================

Use the patient's description to identify the most likely category.

------------------------------------------------------------
CONCUSSION
------------------------------------------------------------

The tooth was hit but:

- is not loose
- is not displaced
- remains in its normal position

If appropriate, explain:

"The tooth may have been affected by the impact even though it has
not moved or become loose."

------------------------------------------------------------
SUBLUXATION
------------------------------------------------------------

The tooth is:

- loose or mobile
- still in approximately its normal position
- not pushed inward, outward, or sideways

Explain that the supporting tissues around the tooth may have been
affected.

------------------------------------------------------------
LATERAL LUXATION
------------------------------------------------------------

The tooth has:

- moved sideways
- been pushed away from its normal position

This requires prompt professional assessment.

------------------------------------------------------------
INTRUSION
------------------------------------------------------------

The tooth has been:

- pushed inward
- pushed deeper into the gum/socket
- appears shorter than before

This is an emergency dental injury.

------------------------------------------------------------
EXTRUSION
------------------------------------------------------------

The tooth has:

- been pushed partly outward
- appears longer than before
- appears partially pulled out of its socket

This is an emergency dental injury.

------------------------------------------------------------
AVULSION
------------------------------------------------------------

The tooth has:

- completely fallen out
- been knocked completely out of the mouth

Treat a completely knocked-out PERMANENT tooth as an emergency.

============================================================
7. IMPORTANT DISTINCTION
============================================================

Do not confuse:

"tooth is loose"

with:

"tooth has moved sideways"

with:

"tooth has been pushed inward"

with:

"tooth has been pushed outward"

with:

"tooth has completely fallen out."

Use the patient's description to distinguish these conditions.

============================================================
8. URGENCY CLASSIFICATION
============================================================

EMERGENCY:

- Permanent tooth completely knocked out
- Tooth pushed inward
- Tooth pushed outward
- Heavy bleeding
- Severe pain
- Suspected jaw injury

URGENT:

- Tooth is loose
- Tooth moved sideways
- Tooth fracture with sensitivity
- Mild bleeding
- Pain when biting
- Significant dental trauma

NON-URGENT:

- Small enamel chip
- No pain
- No mobility
- No displacement
- No other concerning symptoms

When the information is insufficient, do not force a classification.

Continue the triage by asking the next relevant question.

============================================================
9. RESPONSE AFTER TRAUMA IDENTIFICATION
============================================================

Once enough information has been obtained to identify the likely
trauma and urgency, provide guidance specific to that injury.

Use this structure:

1. WHAT MAY HAVE HAPPENED

Explain the likely injury in simple language.

2. WHAT TO DO NOW

Give immediate first-aid guidance appropriate to that injury.

3. WHAT NOT TO DO

Give the most important things the patient should avoid.

4. WHEN TO SEE A DENTIST

Clearly state the appropriate urgency.

5. REASSURANCE

Give brief, calm reassurance without minimizing the injury.

Do not provide a generic response when a trauma-specific response
is possible.

============================================================
10. AVULSION — PERMANENT TOOTH
============================================================

If a permanent tooth has completely fallen out:

Clearly state that this is an emergency.

Tell the patient:

- Hold the tooth only by the crown.
- Do not touch the root.
- If the tooth is dirty, rinse it gently.
- Do not scrub the root.
- If possible, place the tooth in milk or inside the cheek.
- Seek dental care immediately.
- Ideally reach a dentist within approximately 30–60 minutes.

Emphasize:

"The sooner treatment begins, the better the chance of saving the
tooth."

Do not provide unnecessary technical explanations.

============================================================
11. AVULSION — BABY TOOTH
============================================================

If a baby tooth has completely fallen out:

NEVER advise the patient to put the tooth back into the socket.

Tell the patient to contact a dentist.

============================================================
12. INTRUSION / EXTRUSION
============================================================

If the tooth has been pushed inward or outward:

Explain that the tooth has been displaced from its normal position.

Advise prompt emergency dental assessment.

Do not tell the patient to force the tooth back into position.

============================================================
13. LATERAL LUXATION
============================================================

If the tooth has moved sideways:

Explain that the tooth has been displaced.

Advise prompt dental assessment.

Do not instruct the patient to force the tooth back into position.

============================================================
14. SUBLUXATION
============================================================

If the tooth is loose but has not changed position:

Explain that the tooth may have been injured even though it remains
in approximately its normal position.

Advise dental assessment, preferably within 24 hours.

Avoid unnecessary manipulation of the tooth.

============================================================
15. CONCUSSION
============================================================

If the tooth was hit but is not loose or displaced:

Explain that the tooth may have been affected by the impact even
though it remains in position.

Recommend dental evaluation, especially if pain, tenderness, or
bite changes develop.

============================================================
16. FRACTURED / CHIPPED TOOTH
============================================================

If the tooth has broken or chipped:

Determine whether:

- the fracture is small
- there is sensitivity
- there is significant pain
- the tooth structure is substantially broken
- there is bleeding

If sensitivity or significant fracture is present, recommend prompt
dental assessment.

For a small enamel chip without pain or other concerning findings,
recommend a dental appointment for evaluation.

============================================================
17. BLEEDING
============================================================

Determine whether bleeding is:

- absent
- mild
- heavy or difficult to control

Heavy or uncontrolled bleeding should be treated as an emergency.

============================================================
18. PAIN
============================================================

Determine whether pain is:

- absent
- mild
- severe
- triggered by biting

Severe pain or significant pain associated with trauma requires
urgent professional assessment.

Do not prescribe medications.

============================================================
19. ASSOCIATED INJURIES
============================================================

Ask about associated injuries when appropriate:

- jaw pain
- difficulty opening or closing the mouth
- change in the bite
- significant lip or cheek injury
- severe gum injury
- uncontrolled bleeding

If a jaw injury is suspected, classify the situation as an
emergency and recommend immediate professional care.

============================================================
20. TIME OF INJURY
============================================================

Always determine when the injury occurred once the basic trauma
type is understood.

For a knocked-out permanent tooth, the time since injury is
particularly important.

============================================================
21. COMMUNICATION STYLE
============================================================

Use short paragraphs.

Use bullet points when listing instructions.

Avoid long medical explanations.

Do not overwhelm the patient.

Ask one or a small number of clear questions at a time.

Use terminology that a member of the general public can understand.

The interaction should feel like a calm, structured triage conversation.

============================================================
22. DO NOT REPEAT QUESTIONS
============================================================

Maintain awareness of everything the patient has already told you.

For example:

If the patient says:

"My front tooth is loose."

Do NOT ask:

"Is the tooth loose?"

Instead ask the next missing question, such as:

"Has the tooth also moved sideways, or is it still in its usual
position?"

============================================================
23. VIDEO HANDLING
============================================================

Do NOT mention YouTube.

Do NOT mention videos.

Do NOT tell the patient that the application is selecting a video.

The application independently displays an educational video after
the trauma category has been identified.

============================================================
24. MACHINE-READABLE SCENARIO TAG
============================================================

At the very end of EVERY response, add exactly ONE machine-readable
scenario tag.

The tag must be the final line.

It must never be translated.

It must never be explained.

It must never be mentioned to the patient.

Valid tags are:

[SCENARIO:avulsion]

[SCENARIO:intrusion_extrusion]

[SCENARIO:concussion_subluxation_lateral]

[SCENARIO:none]

Use:

[SCENARIO:none]

when there is not enough information to classify the injury.

Use:

[SCENARIO:avulsion]

when the tooth has completely fallen out.

Use:

[SCENARIO:intrusion_extrusion]

when the tooth has been pushed inward or outward.

Use:

[SCENARIO:concussion_subluxation_lateral]

when the injury is consistent with:

- concussion
- subluxation
- lateral luxation

The scenario tag must appear exactly once.

Nothing may appear after the scenario tag.

============================================================
25. CLOSING
============================================================

After providing the appropriate guidance, end the visible response
with:

"Would you like tips on how to care for the tooth until you see a
dentist?"

Translate this question into the selected language when the
conversation is in a non-English language.

For non-English conversations, the English section must contain the
English equivalent.

Remember:

The machine-readable [SCENARIO:...] tag comes AFTER the closing
question and is the final line.

============================================================
26. MOST IMPORTANT PRINCIPLE
============================================================

Follow this overall workflow:

TRAUMA EVENT
↓
IDENTIFY TOOTH TYPE
↓
CONVERSATIONAL TRAUMA IDENTIFICATION
↓
IDENTIFY THE MOST LIKELY TRAUMA CATEGORY
↓
ASSESS URGENCY
↓
PROVIDE TRAUMA-SPECIFIC IMMEDIATE CARE
↓
EXPLAIN WHAT NOT TO DO
↓
ADVISE WHEN TO SEE A DENTIST
↓
REASSURE
↓
CLOSE THE CONVERSATION

Do not jump directly to a final diagnosis when information is
missing.

Use progressive conversational triage.

The goal is clear, objective, accessible first-aid guidance for a
person experiencing dental trauma.
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

        raw_reply = response.choices[0].message.content

        cleaned_reply, _ = extract_scenario_tag(raw_reply)

        return cleaned_reply

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

        raw_reply = response.choices[0].message.content

        # DETECT SCENARIO
        #
        # Parse the hidden [SCENARIO:value] tag GPT was instructed to
        # append. This works no matter what language the conversation
        # is in and no matter how many turns it took to gather enough
        # information, unlike the old English-keyword scan.
        reply, detected_scenario = extract_scenario_tag(raw_reply)

        if detected_scenario:
            st.session_state.scenario = detected_scenario
            st.session_state.urgency = SCENARIO_URGENCY_MAP.get(detected_scenario)

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

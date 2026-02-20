import streamlit as st
from openai import OpenAI
import os
import time

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(page_title="DentalTraumaBot", page_icon="🦷", layout="wide")

# =========================================
# OPENAI CLIENT
# =========================================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================================
# CHATGPT STYLE CSS
# =========================================

st.markdown("""
<style>

html, body, [class*="css"] {
    background-color: #0f172a;
    color: white;
}

.chat-container {
    max-width: 900px;
    margin: auto;
}

.user-bubble {
    background-color: #2563eb;
    color: white;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
    width: fit-content;
    max-width: 75%;
    margin-left: auto;
    font-size: 15px;
}

.bot-bubble {
    background-color: #1e293b;
    color: white;
    padding: 12px 16px;
    border-radius: 18px;
    margin: 10px 0;
    width: fit-content;
    max-width: 75%;
    font-size: 15px;
}

.emergency-bubble {
    background-color: #7f1d1d;
    color: white;
    padding: 14px 18px;
    border-radius: 18px;
    margin: 10px 0;
    max-width: 75%;
    font-size: 16px;
    border: 2px solid red;
}

.avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    margin-right: 8px;
}

.row {
    display: flex;
    align-items: flex-start;
}

.thinking {
    font-style: italic;
    color: #9ca3af;
    margin-left: 10px;
}

</style>
""", unsafe_allow_html=True)

# =========================================
# LOGO
# =========================================

logo_url = "https://github.com/dr-balaganesh/dental-trauma-bot/blob/main/ChatGPT%20Image%20Feb%2019%2C%202026%2C%2008_04_50%20PM.png"

st.markdown(
    f"""
    <div style="text-align:center;">
        <img src="{logo_url}" 
             style="max-width:500px; width:100%; height:auto; 
                    border-radius:12px;">
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<h2 style='text-align:center;'>DentalTraumaBot</h2>
<p style='text-align:center;color:gray;'>
AI assistant for dental injury guidance
</p>
""", unsafe_allow_html=True)
# =========================================
# AVATARS
# =========================================

bot_icon = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
user_icon = "https://cdn-icons-png.flaticon.com/512/847/847969.png"

# =========================================
# SYSTEM PROMPT
# =========================================

condicoes = """ DentalTraumaBot – Final Corrected Prompt

You are a virtual assistant called DentalTraumaBot.

Your goal is to educate and guide people who have experienced dental trauma and help them understand the urgency of their condition.

Use simple, clear, non-technical language suitable for the general public.

Only respond to questions related to dental trauma. For any other topic, reply:
“I’m sorry, I’m only trained to help with dental injuries and trauma. Please consult a relevant professional.”

Always include this reminder in every response:
“This tool does not replace a dentist. A professional dental evaluation is necessary.”

Conversation Start (Mandatory)

Start every conversation by:

Introducing yourself

Explaining that you help people after dental injuries

Asking preferred conversation language

Default language is English.

Ask:
“Which language would you like to continue in?”

Show options:

English

Hindi

Tamil

Telugu

Kannada

Malayalam

Bengali

Marathi

Gujarati

Punjabi



Language Behavior Rules

Default language is English.

If the user selects another language, respond in two clearly separated sections:

Section 1: Full response in the selected language
Section 2: Full response in English

Both sections must contain the exact same updated medical guidance.

The English section must always match the selected language section in meaning.

Never reuse previous responses in one language.

Generate both language sections fresh each time.

Do NOT mix languages within a sentence.

Do NOT write transliteration (no Tanglish like “unga tooth loose ah irukka”).

Use proper script only (Tamil script, Hindi script, etc.).

English must remain grammatically correct and complete.

If the patient changes language during the conversation:

Switch language immediately.

Continue the assessment from the current step.

Do NOT restart the conversation.

Do NOT repeat the introduction.

After language selection:

Do NOT ask the user again which language they prefer.

Do NOT repeat the introduction.

Do NOT repeat the language selection prompt.

Continue directly with the triage question.

If Tamil (or any other language) is selected:

Generate the full medical response first in English internally.

Then translate that exact same response into Tamil.

Ensure both sections contain identical medical meaning.

Do NOT summarize one version differently.

Do NOT add extra lines in one language.

Do NOT omit any lines in one language.

Both sections must include:

Same urgency classification

Same instructions

Same warnings

Same reassurance

Same closing question

first Ask:

“Is the injured tooth a permanent (adult) tooth or a baby tooth?”

Then after input ask:

1.Did the tooth break or chip?

2.Is the tooth loose?

3.Is there bleeding?

4.Was the tooth pushed inward or outward?

5.Did the tooth completely fall out?

6.Is there pain when biting?

7.When did the injury happen?

Urgency Classification
EMERGENCY

Tooth completely knocked out

Tooth pushed inward or outward

Heavy bleeding

Severe pain

Jaw injury suspected

URGENT

Tooth fracture with sensitivity

Loose tooth

Mild bleeding

Pain when biting

NON-URGENT

Small enamel chip

No pain

No mobility

After Classification Always Provide:

What likely happened (simple explanation)

Immediate steps to take

What NOT to do

When to see a dentist

Reassurance

Emergency Guidance

If EMERGENCY say:

“Seek dental care immediately. The sooner treatment begins, the better the chance of saving the tooth.”

If URGENT say:

“Visit a dentist within 24 hours.”

If NON-URGENT say:

“Schedule a dental visit soon for evaluation.”

Special Handling – Knocked-Out Tooth

Hold the tooth by the crown

Do not touch the root

Rinse gently if dirty

Place in milk or inside the cheek

Go to a dentist immediately (within 30–60 minutes)

Baby Teeth Rules

Never try to reinsert a baby tooth

Contact a dentist

Safety Rules

Do not diagnose definitively — guide only.

Do not provide medication names or dosages.

Always emphasize urgency when red-flag symptoms appear.

Stay calm and reassuring.

Mandatory Closing Question (Every Interaction)

End every response with:

“Would you like tips on how to care for the tooth until you see a dentist?”
"""

# =========================================
# SESSION MEMORY
# =========================================

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": condicoes}]

# =========================================
# GPT CALL WITH THINKING INDICATOR
# =========================================

def call_openai(messages):
    with st.spinner("DentalTraumaBot is thinking..."):
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            max_tokens=800
        )
    return response.choices[0].message.content

# =========================================
# CHAT INPUT
# =========================================

user_input = st.chat_input("Describe what happened to the tooth...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    reply = call_openai(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": reply})

# =========================================
# CHAT RENDER
# =========================================

st.markdown('<div class="chat-container">', unsafe_allow_html=True)

for msg in st.session_state.messages[1:]:
    content = msg["content"]

    if msg["role"] == "assistant":

        # EMERGENCY highlight detection
        if "EMERGENCY" in content.upper():
            bubble_class = "emergency-bubble"
        else:
            bubble_class = "bot-bubble"

        # typing animation
        placeholder = st.empty()
        typed_text = ""

        for char in content:
            typed_text += char
            placeholder.markdown(f"""
            <div class="row">
                <img src="{bot_icon}" class="avatar">
                <div class="{bubble_class}">{typed_text}</div>
            </div>
            """, unsafe_allow_html=True)
            time.sleep(0.002)

    else:
        st.markdown(f"""
        <div class="row" style="justify-content:flex-end">
            <div class="user-bubble">{content}</div>
            <img src="{user_icon}" class="avatar">
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

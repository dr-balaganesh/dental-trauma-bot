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

logo_url = "ChatGPT Image Feb 19, 2026, 08_04_50 PM.png"
st.image(logo_url, use_column_width=True)

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

condicoes = """ 
 You are a virtual assistant called DentalTraumaBot.

Your goal is to educate and guide patients who have experienced dental trauma and help them understand the urgency of their condition.

Use simple, clear, non-technical language suitable for the general public.

Only respond to questions related to dental trauma. For any other topic, reply that you are not qualified to answer.

Always include a reminder that this tool does not replace a dentist and professional evaluation is necessary.

Respond in the same language used by the user in their first message.

Start every conversation by:
1. Introducing yourself
2. Explaining that you help people after dental injuries
3. Asking:
   “Is the injured tooth a permanent (adult) tooth or a baby tooth?”

Then continue assessment using simple triage questions:
• Did the tooth break or chip?
• Is the tooth loose?
• Is there bleeding?
• Was the tooth pushed inward or outward?
• Did the tooth completely fall out?
• Is there pain when biting?
• When did the injury happen?

Based on answers, classify urgency into one of three categories:

EMERGENCY:
- Tooth completely knocked out
- Tooth pushed inside or outside
- Heavy bleeding
- Severe pain
- Jaw injury suspected

URGENT:
- Tooth fracture with sensitivity
- Loose tooth
- Mild bleeding
- Pain on biting

NON-URGENT:
- Small enamel chip
- No pain
- No mobility

After classification, provide:

1. What likely happened (simple explanation)
2. Immediate steps to take
3. What NOT to do
4. When to see a dentist
5. Reassurance

If EMERGENCY:
Use strong guidance:
“Seek dental care immediately. The sooner treatment begins, the better the chance of saving the tooth.”

If URGENT:
“Visit a dentist within 24 hours.”

If NON-URGENT:
“Schedule a dental visit soon for evaluation.”

Special handling — knocked-out tooth:
• Hold tooth by the crown
• Do not touch root
• Rinse gently if dirty
• Place in milk or inside cheek
• Go to dentist immediately (within 30–60 min)

Baby teeth:
• Never reinsert
• Contact dentist

End every interaction by asking:
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

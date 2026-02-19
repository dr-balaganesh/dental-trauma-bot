import streamlit as st
from openai import OpenAI
from streamlit_chat import message as msg
import os

# ==============================
# OPENAI KEY
# ==============================

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# URL da imagem do logo no repositório do GitHub
logo_url = "ChatGPT Image Feb 19, 2026, 08_04_50 PM.png"
logo_url3 = "ChatGPT Image Feb 19, 2026, 08_04_50 PM.png"

# Exibindo a imagem de logo
st.sidebar.image(logo_url3, use_column_width=True)
st.image(logo_url, use_column_width=True)

abertura = st.write(
"Hello! I am an AI-powered chatbot here to assist you with the guidance and management of dental trauma."
)

st.sidebar.title("References")

text_input_center = st.chat_input("Chat with me by typing in the field below")

# ==============================
# YOUR ORIGINAL PROMPT (UNCHANGED)
# ==============================

condicoes = """ You are a virtual assistant called DentalTraumaBot.

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

# ==============================
# CHAT MEMORY
# ==============================

if 'hst_conversa' not in st.session_state:
    st.session_state.hst_conversa = [{"role": "system", "content": condicoes}]

# ==============================
# CHAT FUNCTION
# ==============================

def call_openai(messages):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages,
        max_tokens=900
    )
    return response.choices[0].message.content

# ==============================
# USER INPUT
# ==============================

if text_input_center:
    st.session_state.hst_conversa.append(
        {"role": "user", "content": text_input_center}
    )

    resposta = call_openai(st.session_state.hst_conversa)

    st.session_state.hst_conversa.append(
        {"role": "assistant", "content": resposta}
    )

# ==============================
# RENDER CHAT
# ==============================

def render_chat(hst_conversa):
    for i in range(1, len(hst_conversa)):
        if i % 2 == 0:
            msg("**DentalTraumaBot**:" + hst_conversa[i]['content'], key=f"bot_msg_{i}")
        else:
            msg("**You**:" + hst_conversa[i]['content'], is_user=True, key=f"user_msg_{i}")

if len(st.session_state.hst_conversa) > 1:
    render_chat(st.session_state.hst_conversa)

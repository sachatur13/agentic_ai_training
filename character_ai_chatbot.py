import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_SECRET_KEY"))

# defining character personas
personas = {
    "Sheldon Cooper (The Big Bang Theory)": "You are Sheldon Cooper from The Big Bang Theory. Highly intelligent, extremely logical, and obsessed with precision. Explain topics in a structured, scientific way, breaking ideas into clear logical steps. Occasionally sound slightly condescending and point out when something is 'obvious'.",

    "Michael Scott (The Office)": "You are Michael Scott from The Office. Energetic, overly confident, and loves using funny workplace analogies. Explain topics in a casual, entertaining way with jokes, awkward humor, and relatable office examples.",

    "Tyrion Lannister (Game of Thrones)": "You are Tyrion Lannister from Game of Thrones. Clever, witty, and insightful. Explain ideas using sharp metaphors, strategic thinking, and sarcastic humor while sounding intelligent and thoughtful.",

    "Ted Lasso (Ted Lasso)": "You are Ted Lasso from Ted Lasso. Optimistic, friendly, and encouraging. Explain ideas in a simple and uplifting way using sports metaphors and positive energy, making complex ideas feel easy and motivating."
}

st.title("🎭 Character AI Chatbot")
st.write("Chat with your favorite TV characters dynamically!")

# Select character
selected_character = st.selectbox("Select a Character Persona:", list(personas.keys()))
instructions = personas[selected_character]

# Enter message
message = st.text_area("Enter your message to the character:")

# Get response
if st.button("Send Message"):
    if message.strip():
        with st.spinner(f"Waiting for {selected_character.split(' ')[0]} to reply..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": message}
                    ]
                )
                st.subheader(f"{selected_character.split(' ')[0]}'s Response:")
                st.info(response.choices[0].message.content)
            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a message before sending.")
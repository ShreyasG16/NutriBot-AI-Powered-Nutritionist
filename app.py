import streamlit as st
import streamlit.components.v1 as components
import os
import requests
import json
import asyncio
import aiohttp
import base64
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import google.generativeai as genai
from fpdf import FPDF
import re
import unicodedata

st.set_page_config(page_title="NutriBot", layout="wide")

load_dotenv()

QWEN_API_KEY = st.secrets["QWEN_API_KEY"]
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False
if "show_chatbot" not in st.session_state:
    st.session_state.show_chatbot = False
if "show_meal_plan" not in st.session_state:  
    st.session_state.show_meal_plan = False


#chatbot response from Qwen 2.5 API
async def get_qwen_response(prompt):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {QWEN_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "qwen/qwen2.5-vl-72b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}]
                }
            ) as response:
                result = await response.json()
                return result.get("choices", [{}])[0].get("message", {}).get("content", "No response received.")
    except Exception as e:
        return f"An error occurred: {str(e)}"

# meal analysis from Gemini
def get_gemini_response(image, prompt):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content([image[0], prompt])
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        return [{"mime_type": uploaded_file.type, "data": bytes_data}]
    else:
        raise FileNotFoundError("No file uploaded")

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def clean_text(text):
    text = unicodedata.normalize("NFKD", text)
    return ''.join(c for c in text if unicodedata.category(c)[0] != 'C')

def generate_pdf(meal_plan: str, goals_str: str, additional_req: str):
    pdf = FPDF(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "NutriBot Prescription", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 6, f"Goals: {clean_text(goals_str)}", ln=True)
    pdf.cell(0, 6, f"Additional Requirements: {clean_text(additional_req or 'None')}", ln=True)
    pdf.ln(5)

    lines = meal_plan.split("\n")
    for line in lines:
        stripped = line.strip()
        stripped = re.sub(r'^#+\s*', '', stripped)
        stripped = re.sub(r'\*\*(.*?)\*\*', r'\1', stripped)

        is_heading = (
            len(stripped) <= 100
            and re.match(r'^[A-Z][A-Za-z0-9\s\(\)\-:]*$', stripped)
            and not stripped.startswith(("-", "•"))
        )

        if is_heading:
            pdf.set_font("Arial", "B", 14)
        else:
            pdf.set_font("Arial", "", 12)

        cleaned = clean_text(stripped)
        pdf.multi_cell(0, 6, cleaned)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Authorized by Dr. NutriBot", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "I", 12)
    pdf.cell(0, 6, clean_text("𝔑𝔲𝔱𝔯𝔦𝔅𝔬𝔱"), ln=True, align="C") 
    pdf.ln(5)

    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "Made with ❤️ by Shreyas", ln=True, align="C")  
    pdf_bytes = pdf.output(dest="S").encode("latin1")

    st.download_button(
        label="📥 Download Prescription",
        data=pdf_bytes,
        file_name="mealPlan.pdf",
        mime="application/pdf"
    )



user_icon = get_base64_image("boy.png")
bot_icon = get_base64_image("robot.png")


if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False
if "show_chatbot" not in st.session_state:
    st.session_state.show_chatbot = False
if "show_meal_plan" not in st.session_state:  
    st.session_state.show_meal_plan = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        background-color: #000000;
    }
    div.stButton > button:first-child {
        background-color: #2a9d8f; 
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        width: 100%; 
        height: 50px; 
        font-size: 16px;
    }
    div.stButton > button:hover {
        background-color: #264653; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Pick the Service ⚙️")
if st.sidebar.button("🍲 Analyse My Meal"):
    st.session_state.show_uploader = True
    st.session_state.show_chatbot = False
    st.session_state.show_meal_plan = False
    st.rerun()
if st.sidebar.button("💬 Chat with NutriBot"):
    st.session_state.show_chatbot = True
    st.session_state.show_uploader = False
    st.session_state.show_meal_plan = False
    st.rerun()
if st.sidebar.button("✍️ Get Meal Plan"):  
    st.session_state.show_meal_plan = True
    st.session_state.show_uploader = False
    st.session_state.show_chatbot = False
    st.rerun()


if not st.session_state.show_uploader and not st.session_state.show_chatbot and not st.session_state.show_meal_plan:
    with open("background.html", "r") as f:
        background_html = f.read()
    components.html(background_html, height=800, width=2000)

# Meal Analysis Page (Gemini)
if st.session_state.show_uploader:
    st.header("Let's Analyse Your Meal! 🍽️")
    uploaded_file = st.file_uploader("Upload Your Meal Image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", width=400)
    submit = st.button("Analyse ✨")
    input_prompt = """
    Role:
    You are a highly skilled nutritionist with expertise in analyzing meals based on images. Your task is to assess the meal, break down its nutritional content, and provide insightful feedback.
    Instructions:
    Identify Meal Components
    List all visible food items in the image.
    Estimate the quantity of each item if possible.
    Calorie Breakdown
    Provide the calorie count for each identified item in the following format:
    Item 1: XX calories
    Item 2: XX calories
    Total Calories: XX kcal
    Health Insights
    Highlight nutritional benefits and potential concerns.
    Personalized Recommendations
    Suggest modifications if the meal is imbalanced.
    Next Steps:
    For more insights, choose 💬 Chat with NutriBot.
    If you want a personalized plan, choose ✍️ Get Meal Plan.
    """
    if submit and uploaded_file:
        image_data = input_image_setup(uploaded_file)
        response = get_gemini_response(image_data, input_prompt)
        st.subheader("Your Report 📋")
        st.write(response)
    if st.button("⬅️ Back to Main Page"):
        st.session_state.show_uploader = False
        st.session_state.show_chatbot = False
        st.session_state.show_meal_plan = False
        st.rerun()

if st.session_state.show_meal_plan:
    st.header("Personalized Meal Plan ✍️")

    user_goals = st.multiselect(
        "Select Your Goals:", 
        ["None","Weight Loss","Weight Gain","Muscle Gain", "Maintenance", "Improve Digestion", "Increase Energy"], 
        help="Select one or more goals that match your dietary needs."
    )

    additional_req = st.text_area(
        "Any Additional Requirements?",
        placeholder="E.g., vegetarian diet, high protein intake, avoid sugar, etc."
    )

    submit_meal_plan = st.button("🚀 Generate Meal Plan", key="meal_plan")

    if submit_meal_plan:

        goals_str = ", ".join(user_goals) if user_goals else "General Health"

        # Meal Plan Prompt for Qwen API
        meal_plan_prompt = f"""
        You are a professional nutritionist. Create a detailed meal plan for a person whose goals are: {goals_str}.
        
        The meal plan should only include:
        - Breakfast
        - Lunch
        - Snacks
        - Dinner
        - Estimated Total Calories

        Additional user requirements: {additional_req if additional_req else 'None'}

        Make sure everything not exceeds 1 A4 size page.

        Can give Additional Advice if space available.
        """

        response = asyncio.run(get_qwen_response(meal_plan_prompt))

        st.subheader("Your Personalized Meal Plan 📋")
        st.write(response)

        generate_pdf(response, goals_str, additional_req)

    if st.button("⬅️ Back to Main Page", key="back_meal"):
        st.session_state.show_meal_plan = False
        st.session_state.show_uploader = False
        st.session_state.show_chatbot = False
        st.rerun()


# Chatbot Page (Qwen 2.5 API)
if st.session_state.show_chatbot:
    st.header("Chat with NutriBot 💬")

    st.markdown(f"""
        <style>
        .chat-container {{ width: 100%; display: flex; flex-direction: column; margin-top: 10px; }}
        .chat-user {{ align-self: flex-end; background-color: #2a9d8f; padding: 12px; border-radius: 10px; max-width: 60%; 
                     margin: 10px; text-align: right; color: white; }}
        .chat-assistant {{ align-self: flex-start; background-color: #264653; padding: 12px; border-radius: 10px; 
                          max-width: 60%; margin: 10px; text-align: left; color: white; }}
        .chat-message {{ display: flex; align-items: center; gap: 8px; margin-bottom: 5px; }}
        .chat-user img, .chat-assistant img {{ width: 10px; height: 10px; border-radius: 50%; }} /* Smaller icons */
        .back-button {{ margin-top: 20px; }}
        </style>
    """, unsafe_allow_html=True)

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
                <div class='chat-container'>
                    <div class='chat-message' style='justify-content: flex-end;'>
                        <div class='chat-user'>{message['content']}</div>
                        <img src='data:image/png;base64,{user_icon}' alt='User' width='32' height='32'>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='chat-container'>
                    <div class='chat-message' style='justify-content: flex-start;'>
                        <img src='data:image/png;base64,{bot_icon}' alt='Bot' width='32' height='32'>
                        <div class='chat-assistant'>{message['content']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    user_query = st.chat_input("Ask me anything about health, diet, and nutrition...")
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        response = asyncio.run(get_qwen_response(user_query))
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()
    
    st.markdown("<br><br>", unsafe_allow_html=True)

    if st.button("⬅️ Back to Main Page", key="back_button"):
        st.session_state.show_uploader = False
        st.session_state.show_chatbot = False  
        st.rerun()

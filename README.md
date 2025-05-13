# NutriBot: AI Powered Nutritionist

NutriBot is an AI-driven web application designed to provide personalized nutritional assistance using advanced generative models and image analysis. The application aims to empower users to make informed dietary decisions by leveraging cutting-edge AI tools in an easy-to-use Streamlit interface.

---

## 🔍 Features

- **AI-Powered Meal Analysis**  
  Upload a photo of your meal and get **real-time calorie estimates** and **dietary concern analysis** using **Gemini-Flash-1.0**.

- **Personalized Meal Planning**  
  Generate **custom meal plans** tailored to user goals (e.g., weight loss, muscle gain, diabetic-safe, etc.) powered by **Qwen 2.5**.

- **PDF Export**  
  Download customized meal plans and prescriptions in **PDF format** for easy access and sharing.

- **Virtual Nutrition Assistant**  
  Interact with a real-time **chat assistant** built on **Qwen 2.5**, capable of answering nutrition-related queries and providing expert dietary advice.

---

## 🛠️ Tools & Technologies

- **Frontend**: [Streamlit](https://streamlit.io/)
- **AI Models**:
  - Gemini-Flash-1.0 (Image Analysis & Calorie Estimation)
  - Qwen 2.5 (Diet Plan Generation & Chat Assistant)
- **Backend**: Python
- **Output Formats**: PDF

---

## 🚀 How to Run Locally

1. **Clone the Repository**
   
   ```bash
   git clone https://github.com/yourusername/NutriBot-AI-Nutritionist.git
   cd NutriBot-AI-Nutritionist
   
2. **Create a Virtual Environment**
   
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
3. **Install Dependencies**
   
   ```bash
   pip install -r requirements.txt
   
4. **Run the App**

   ```bash
   streamlit run app.py


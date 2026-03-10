import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from PIL import Image
import base64
import io
import json

# Load environment variables
load_dotenv()

# Custom CSS for modern UI design
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0f172a; /* Slate 900 */
        color: #f8fafc; /* Slate 50 */
        font-family: 'Inter', sans-serif;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #38bdf8; /* Light blue 400 */
        font-weight: 700;
        letter-spacing: -0.025em;
    }
    
    /* Subheaders and text */
    p {
        color: #cbd5e1; /* Slate 300 */
        line-height: 1.6;
    }
    
    /* File uploader and camera input styling */
    .stFileUploader > div > div {
        background-color: #1e293b; /* Slate 800 */
        border: 2px dashed #475569; /* Slate 600 */
        border-radius: 12px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    .stFileUploader > div > div:hover {
        border-color: #38bdf8;
        background-color: #1e293b;
    }
    
    /* Result Cards */
    .food-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid #334155; /* Slate 700 */
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .food-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
    }
    
    /* Typography inside cards */
    .food-title {
        color: #fbbf24; /* Amber 400 */
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 12px;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }
    .food-detail {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        color: #e2e8f0;
    }
    .food-label {
        font-weight: 600;
        color: #94a3b8; /* Slate 400 */
    }
    .food-value {
        font-weight: 500;
    }
    
    /* Total Calories Box */
    .total-box {
        background: linear-gradient(135deg, #0ea5e9, #2563eb); /* Ocean blue gradient */
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        margin-top: 30px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.5);
    }
    .total-label {
        color: #e0f2fe; /* Light blue 100 */
        font-size: 1.25rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 10px;
    }
    .total-value {
        color: #ffffff;
        font-size: 3.5rem;
        font-weight: 800;
        text-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    
    /* Notes section */
    .notes-section {
        background-color: #1e293b;
        border-left: 4px solid #f59e0b; /* Amber 500 */
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-top: 24px;
        font-style: italic;
        color: #94a3b8;
    }
    
    /* Confidence Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-high {
        background-color: rgba(34, 197, 94, 0.2); /* Green */
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .badge-medium {
        background-color: rgba(245, 158, 11, 0.2); /* Amber */
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    .badge-low {
        background-color: rgba(239, 68, 68, 0.2); /* Red */
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Button Styles */
    .stButton > button {
        background: linear-gradient(135deg, #38bdf8, #2563eb);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #7dd3fc, #3b82f6);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        transform: translateY(-1px);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 0;
        border-bottom: 2px solid transparent;
        padding: 10px 16px;
        font-weight: 600;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        color: #38bdf8 !important;
        border-bottom-color: #38bdf8 !important;
    }
    
</style>
""", unsafe_allow_html=True)

# Helper functions
def encode_pil_image_to_base64(image):
    """Converts a PIL Image to a base64 encoded string"""
    buffered = io.BytesIO()
    # Convert image to RGB if it has an alpha channel (like PNGs might) to avoid errors saving to JPEG
    if image.mode != 'RGB':
        image = image.convert('RGB')
    image.save(buffered, format="JPEG")
    encoded_string = base64.b64encode(buffered.getvalue())
    return encoded_string.decode('utf-8')

def query_openai_image_model(client, image, prompt, model='gpt-4o', max_tokens=1000):
    """Queries OpenAI Vision API with a PIL image and prompt"""
    base64_image = encode_pil_image_to_base64(image)
    try:
        message = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "data:image/jpeg;base64," + base64_image
                    }
                }
            ]
        }]    

        # API call
        response = client.chat.completions.create(
            model=model,
            messages=message,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content
    except Exception as e:
        return str(e)

# Prompt definition
PROMPT = """You are a nutrition analysis assistant.

Your task is to analyze the food image provided and estimate the calorie content.

Steps to follow:
1. Identify all visible food items in the image.
2. Estimate the portion size for each item (grams, pieces, cups, etc.).
3. Estimate calories for each food item using common nutritional knowledge.
4. Calculate the total calorie estimate for the entire meal.
5. If you are uncertain, provide a reasonable estimate and mark confidence as low.

Guidelines:
- Assume typical restaurant or home serving sizes if exact quantities are unclear.
- Use standard nutrition references for calorie estimates.
- Do not invent ingredients that are not visible.
- If multiple foods are present, list each separately.

Return the output strictly in this JSON format. Do not use markdown wrappers like ```json at the beginning or end, just return the raw JSON string:

{
  "food_items": [
    {
      "name": "food name",
      "estimated_portion": "portion description",
      "estimated_weight_g": number,
      "calories": number,
      "confidence": "high | medium | low"
    }
  ],
  "total_estimated_calories": number,
  "notes": "any assumptions or uncertainties"
}"""


# --- Streamlit UI App ---

# Rate limiting using session state (Limit to 5 requests per session to stop spamming)
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0

MAX_UPLOADS = 5 
MAX_FILE_SIZE_MB = 5

# Sidebar for configuration
st.sidebar.title("⚙️ Security & Settings")
st.sidebar.markdown(f"**Rate Limit:** {st.session_state.analysis_count}/{MAX_UPLOADS} requests used.")
st.sidebar.markdown("For security and to manage API costs, you can provide your own OpenAI API Key.")
user_api_key = st.sidebar.text_input("OpenAI API Key (Optional)", type="password")

# Use User's key if provided, else fallback to env key
effective_api_key = user_api_key if user_api_key else os.getenv("OPEN_AI_SECRET_KEY")

# Initialize client based on available key
openai_client = None
if effective_api_key:
    openai_client = OpenAI(api_key=effective_api_key)

# Header section
st.title("🍽️ AI Calorie Tracker")
st.markdown("Snap a picture of your meal or upload an image to instantly estimate its nutritional value powered by GPT-4o Vision.")
st.markdown("---")

# Navigation Tabs: Upload vs Camera
tab1, tab2 = st.tabs(["📸 Take a Photo", "📂 Upload Image"])

image = None

with tab1:
    if not st.session_state.get('camera_active', False):
        if st.button("Open Camera"):
            st.session_state.camera_active = True
            st.rerun()
    else:
        if st.button("Close Camera"):
            st.session_state.camera_active = False
            st.rerun()
            
        camera_photo = st.camera_input("Take a picture of your food")
        if camera_photo is not None:
            # File size limit check (approximate byte size of uploaded file)
            if camera_photo.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                st.error(f"⚠️ Security Error: Image size exceeds the {MAX_FILE_SIZE_MB}MB limit. Please take a lower resolution photo.")
            else:
                image = Image.open(camera_photo)
                st.success("Photo captured successfully!")

with tab2:
    uploaded_file = st.file_uploader("Choose an image file", type=["jpg", "jpeg", "png", "webp"])
    if uploaded_file is not None:
        # File size limit check
        if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.error(f"⚠️ Security Error: Uploaded image size exceeds the {MAX_FILE_SIZE_MB}MB limit. Please upload a smaller image.")
        else:
            image = Image.open(uploaded_file)
            st.success("Image uploaded successfully!")
            
            # Display preview for uploaded files (camera input already shows preview)
            st.image(image, caption="Uploaded Image", use_column_width=True)

st.markdown("---")

# Process button
if image is not None:
    if st.button("🔍 Analyze Calories Now"):
        
        # Security checks before processing
        if not openai_client:
            st.error("⚠️ Security Error: No OpenAI API key found. Please input one in the sidebar.")
        elif st.session_state.analysis_count >= MAX_UPLOADS:
            st.error("🚫 Rate Limit Exceeded: You have reached the maximum allowed analyses for this session.")
        else:
            with st.spinner("Analyzing image... The AI is identifying your food and calculating calories..."):
                # Run the model
                raw_response = query_openai_image_model(openai_client, image, PROMPT)
                
                # Try parsing the JSON response
                try:
                    # Clean the response in case the model added markdown blocks despite instructions
                    cleaned_response = raw_response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]
                    if cleaned_response.startswith("```"):
                        cleaned_response = cleaned_response[3:]
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]
                        
                    data = json.loads(cleaned_response)
                    
                    # Basic Prompt Injection/Output Sanitization validation:
                    if not isinstance(data, dict) or "food_items" not in data or "total_estimated_calories" not in data:
                        raise ValueError("Unexpected JSON structure returned. The AI may have been compromised or confused.")
                    
                    # Update rate limiting counter
                    st.session_state.analysis_count += 1
                    
                    # Display Results
                    st.markdown("## 📊 Analysis Results")
                    
                    # Layout with columns
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown("### 🥗 Identified Food Items")
                        
                        for item in data.get("food_items", []):
                            
                            # Determine badge class based on confidence
                            conf = item.get("confidence", "low").lower()
                            if conf == "high":
                                badge_class = "badge-high"
                            elif conf == "medium":
                                badge_class = "badge-medium"
                            else:
                                badge_class = "badge-low"
                                
                            # Render individual food cards
                            st.markdown(f"""
                            <div class="food-card">
                                <div class="food-title">{item.get('name', 'Unknown Item')}</div>
                                <div class="food-detail">
                                    <span class="food-label">Portion Size:</span>
                                    <span class="food-value">{item.get('estimated_portion', 'Unknown')} ({item.get('estimated_weight_g', 0)}g)</span>
                                </div>
                                <div class="food-detail">
                                    <span class="food-label">Estimated Calories:</span>
                                    <span class="food-value" style="color: #38bdf8; font-weight: 700;">{item.get('calories', 0)} kcal</span>
                                </div>
                                <div style="margin-top: 12px; text-align: right;">
                                    <span class="badge {badge_class}">Confidence: {conf.upper()}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with col2:
                        # Total calories display
                        st.markdown(f"""
                        <div class="total-box">
                            <div class="total-label">Total Estimate</div>
                            <div class="total-value">{data.get('total_estimated_calories', 0)}</div>
                            <div style="color: rgba(255,255,255,0.7); font-weight: 600; margin-top: 5px;">KCALS</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Notes display
                        if "notes" in data and data["notes"]:
                            st.markdown(f"""
                            <div class="notes-section">
                                <strong>💡 AI Notes:</strong><br/>
                                {data['notes']}
                            </div>
                            """, unsafe_allow_html=True)
                            
                except json.JSONDecodeError:
                    st.error("Failed to parse the response from the AI. It might have been improperly formatted.")
                    st.write(raw_response)
                except ValueError as e:
                    st.error(f"Validation Error: {str(e)}")
                except Exception as e:
                    st.error(f"An error occurred while displaying results: {str(e)}")
else:
    st.info("👆 Please upload an image or take a photo to get started.")
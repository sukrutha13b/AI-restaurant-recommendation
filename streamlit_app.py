import os
import streamlit as st
from typing import List

from data.loader import load_restaurants
from core.preferences import UserPreferences
from core.pipeline import run_pipeline
from llm.client import GeminiRecommender, LLMError

# Page Config
st.set_page_config(
    page_title="AI Restaurant Recommender",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🍽️ AI Restaurant Recommender")
st.markdown(
    "Find your perfect dining spot using **statistical data** and **Gemini AI**. "
    "Fill in your preferences in the sidebar and let the AI find and explain the best matches for you!"
)

# Load Metadata
@st.cache_data
def get_metadata():
    restaurants = load_restaurants()
    cities = set()
    cuisines = set()
    for r in restaurants:
        if r.city:
            cities.add(r.city.strip())
        if r.cuisines:
            for c in r.cuisines:
                cuisines.add(c.strip())
    return sorted(list(cities)), sorted(list(cuisines))

try:
    available_cities, available_cuisines = get_metadata()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# --- Sidebar UI ---
st.sidebar.header("Your Preferences")

selected_cities = st.sidebar.multiselect(
    "Cities (Leave empty for all)", 
    options=available_cities, 
    default=[]
)

selected_cuisines = st.sidebar.multiselect(
    "Cuisines (Leave empty for all)", 
    options=available_cuisines, 
    default=[]
)

min_rating = st.sidebar.slider(
    "Minimum Rating", 
    min_value=0.0, max_value=5.0, value=3.5, step=0.1
)

max_price = st.sidebar.selectbox(
    "Max Price Bucket", 
    options=[1, 2, 3, 4], 
    index=3, 
    format_func=lambda x: "💰" * x
)

top_n = st.sidebar.number_input(
    "Number of Results", 
    min_value=1, max_value=20, value=5
)

st.sidebar.markdown("---")
st.sidebar.header("AI Settings")

use_ai = st.sidebar.checkbox("Enable AI Re-ranking (Gemini)", value=True)
model_name = st.sidebar.selectbox(
    "Model", 
    options=["gemini-1.5-flash", "gemini-1.5-pro"]
)

api_key = st.sidebar.text_input(
    "Gemini API Key", 
    type="password", 
    help="Leave empty to use the environment variable (if set in .env)."
)

# --- Action ---
if st.sidebar.button("Find Restaurants", type="primary", use_container_width=True):
    with st.spinner("Searching for the best spots..."):
        try:
            # Resolve API Key
            actual_api_key = api_key or os.getenv("GEMINI_API_KEY") 
            if not actual_api_key and "GEMINI_API_KEY" in st.secrets:
                actual_api_key = st.secrets["GEMINI_API_KEY"]
                
            llm_client = None
            if use_ai:
                if not actual_api_key:
                    st.error("Gemini API Key is required for AI re-ranking. Provide it in the sidebar or via `.env`.")
                    st.stop()
                llm_client = GeminiRecommender(api_key=actual_api_key, model_name=model_name)
                
            # Build Preferences
            prefs = UserPreferences.from_raw(
                cities=selected_cities if selected_cities else None,
                cuisines=selected_cuisines if selected_cuisines else None,
                min_rating=min_rating,
                max_price_bucket=max_price,
                top_n=top_n,
                model_name=model_name
            )
            
            # Execute Pipeline
            all_r = load_restaurants()
            results = run_pipeline(all_r, prefs, llm_client=llm_client)
            
            # --- Rendering Results ---
            if not results:
                st.warning("No restaurants found matching your criteria. Try loosening your filters!")
            else:
                st.success(f"Found {len(results)} great restaurants!")
                
                for r in results:
                    with st.container(border=True):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.subheader(f"{r.name}")
                            st.write(f"🗺️ **Location:** {r.area}, {r.city}")
                            st.write(f"🍝 **Cuisines:** {', '.join(r.cuisines)}")
                        with col2:
                            st.write(f"⭐ **{r.rating or 'N/A'}** ({r.votes or 0} votes)")
                            st.write(f"{'💰' * (r.price_range or 1)}")
                            if use_ai and r.llm_score is not None:
                                st.write(f"🧠 **AI Score:** {r.llm_score}/10")
                        
                        if use_ai and r.llm_explanation:
                            st.info(f"**Why this matches you:** {r.llm_explanation}")

        except LLMError as e:
            st.error(f"AI Service Error: {str(e)}")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

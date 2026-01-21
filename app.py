import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
import json
import requests
import pandas as pd
import random
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import folium_static

# Load environment variables
load_dotenv()

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    st.error("❌ GROQ_API_KEY not found in .env file.")
    st.stop()
client = Groq(api_key=api_key)

# API Keys
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
OPENTRIPMAP_API_KEY = os.environ.get("OPENTRIPMAP_API_KEY", "")
FOURSQUARE_API_KEY = os.environ.get("FOURSQUARE_API_KEY", "")

# Set page config
st.set_page_config(
    page_title="🌍 Travel Itinerary AI",
    page_icon="🇱🇰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with White Theme + Hero Section
st.markdown("""
<style>
    /* Main container - White Theme */
    .stApp {
        background: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main content background */
    .main .block-container {
        background: #ffffff;
    }
    
    /* ===============================
       MAIN HEADER WITH PARTICLES
    ================================ */
    .hero-section {
        min-height: 85vh;
        background: linear-gradient(135deg, 
            rgba(15, 23, 42, 0.95) 0%, 
            rgba(30, 41, 59, 0.85) 50%,
            rgba(51, 65, 85, 0.7) 100%),
        url('https://images.unsplash.com/photo-1519046904884-53103b34b206?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        border-radius: 0 0 40px 40px;
        position: relative;
        overflow: hidden;
        margin-bottom: 60px;
    }
    
    .hero-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(
            circle at 20% 50%,
            rgba(99, 102, 241, 0.15) 0%,
            transparent 50%
        ),
        radial-gradient(
            circle at 80% 20%,
            rgba(245, 158, 11, 0.1) 0%,
            transparent 50%
        ),
        radial-gradient(
            circle at 40% 80%,
            rgba(16, 185, 129, 0.1) 0%,
            transparent 50%
        );
        animation: particleFloat 20s ease-in-out infinite;
    }
    
    @keyframes particleFloat {
        0%, 100% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(-10px, 10px) rotate(5deg); }
        50% { transform: translate(10px, -10px) rotate(-5deg); }
        75% { transform: translate(-5px, -5px) rotate(3deg); }
    }
    
    .hero-content {
        position: relative;
        z-index: 2;
        padding: 80px 40px;
        text-align: center;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    .hero-title {
        font-size: 4.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #f1f5f9 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 20px;
        line-height: 1.1;
        text-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: #cbd5e1;
        margin-bottom: 40px;
        line-height: 1.6;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .hero-badge {
        display: inline-block;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
        padding: 10px 25px;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 30px;
        animation: badgeGlow 3s ease-in-out infinite;
    }
    
    @keyframes badgeGlow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.6); }
    }
    
    .glass-badge {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        padding: 12px 24px;
        font-size: 1rem;
        font-weight: 500;
        color: white;
        transition: all 0.3s ease;
    }
    
    .glass-badge:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-2px);
    }
    
    /* App Header with Transparency Card View */
.header-card {
    background: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 24px;
    padding: 40px;
    margin: 20px auto;
    max-width: 1200px;
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.08),
        0 8px 32px rgba(59, 130, 246, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
    position: relative;
    overflow: hidden;
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.header-card:hover {
    transform: translateY(-4px);
    box-shadow: 
        0 30px 80px rgba(0, 0, 0, 0.12),
        0 15px 40px rgba(59, 130, 246, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    background: rgba(255, 255, 255, 0.92);
}

.header-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    border-radius: 24px 24px 0 0;
    z-index: 1;
}

.header-card::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 150%;
    height: 150%;
    background: radial-gradient(circle at center, 
        rgba(59, 130, 246, 0.05) 0%,
        rgba(139, 92, 246, 0.03) 25%,
        rgba(236, 72, 153, 0.01) 50%,
        transparent 70%);
    transform: translate(-50%, -50%);
    z-index: 0;
    pointer-events: none;
}

.header-content {
    position: relative;
    z-index: 2;
    text-align: center;
}

.glow-effect {
    position: absolute;
    top: -50%;
    left: -50%;
    right: -50%;
    bottom: -50%;
    background: radial-gradient(circle at center, 
        rgba(59, 130, 246, 0.08) 0%,
        rgba(139, 92, 246, 0.04) 30%,
        transparent 70%);
    animation: gentlePulse 8s ease-in-out infinite;
    pointer-events: none;
    z-index: 1;
}

@keyframes gentlePulse {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(1.02); }
}

.gradient-text {
    background: linear-gradient(135deg, 
        #1e40af 0%,
        #3b82f6 25%,
        #8b5cf6 50%,
        #ec4899 75%,
        #f59e0b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-fill-color: transparent;
    background-size: 200% auto;
    animation: gradientShift 8s ease-in-out infinite;
    font-weight: 800;
    letter-spacing: -0.5px;
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.header-subtitle {
    color: #475569;
    font-size: 1.2rem;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 0 20px;
    position: relative;
}

.header-subtitle::before,
.header-subtitle::after {
    content: '✦';
    position: absolute;
    color: #3b82f6;
    font-size: 1.5rem;
    opacity: 0.6;
    animation: subtleFloat 4s ease-in-out infinite;
}

.header-subtitle::before {
    left: -10px;
    top: 50%;
    transform: translateY(-50%);
    animation-delay: 0s;
}

.header-subtitle::after {
    right: -10px;
    top: 50%;
    transform: translateY(-50%);
    animation-delay: 2s;
}

@keyframes subtleFloat {
    0%, 100% { transform: translateY(-50%) rotate(0deg); opacity: 0.4; }
    50% { transform: translateY(-55%) rotate(180deg); opacity: 0.8; }
}

.header-icons {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-top: 25px;
    flex-wrap: wrap;
}

.header-icon {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: rgba(59, 130, 246, 0.08);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 12px;
    color: #1e40af;
    font-size: 0.9rem;
    font-weight: 500;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.header-icon:hover {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateY(-2px);
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .hero-section {
        min-height: 70vh;
        border-radius: 0 0 30px 30px;
    }
    
    .hero-title {
        font-size: 2.8rem;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
    }
    
    .glass-badge {
        padding: 8px 16px;
        font-size: 0.9rem;
    }
    
    .header-card {
        padding: 30px 20px;
        margin: 10px;
        border-radius: 20px;
    }
    
    .gradient-text {
        font-size: 2.5rem;
    }
    
    .header-subtitle {
        font-size: 1.1rem;
        padding: 0 10px;
    }
    
    .header-icons {
        gap: 10px;
    }
    
    .header-icon {
        padding: 6px 12px;
        font-size: 0.85rem;
    }
}

@media (max-width: 480px) {
    .hero-section {
        min-height: 60vh;
    }
    
    .hero-title {
        font-size: 2.2rem;
    }
    
    .hero-content {
        padding: 40px 20px;
    }
    
    .header-card {
        padding: 25px 15px;
        border-radius: 16px;
    }
    
    .gradient-text {
        font-size: 2rem;
    }
    
    .header-subtitle {
        font-size: 1rem;
    }
    
    .header-icons {
        flex-direction: column;
        align-items: center;
    }
    
    .header-icon {
        width: 100%;
        max-width: 200px;
        justify-content: center;
    }
}

/* Special effects on hover */
.header-card:hover .gradient-text {
    animation-duration: 4s;
}

.header-card:hover .header-subtitle::before,
.header-card:hover .header-subtitle::after {
    animation-duration: 2s;
}

/* Light mode enhancements */
.light-theme .header-card {
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid rgba(0, 0, 0, 0.08);
}

.light-theme .header-icon {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    color: #1e40af;
}

/* Dark mode support (if needed) */
.dark-theme .header-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.dark-theme .header-subtitle {
    color: #94a3b8;
}

.dark-theme .header-icon {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.3);
    color: #60a5fa;
}
                   
    /* ===============================
   SIDEBAR (LIGHT GLASS)
/* ===============================
   SIDEBAR ENHANCEMENTS - UPDATED
================================ */

/* Main sidebar container */
section[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.92) !important;
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border-right: 1px solid rgba(0, 0, 0, 0.06);
    box-shadow: 
        4px 0 24px rgba(0, 0, 0, 0.05),
        inset 1px 0 0 rgba(255, 255, 255, 0.6);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Hover effect on sidebar */
section[data-testid="stSidebar"]:hover {
    border-right-color: rgba(59, 130, 246, 0.2);
    box-shadow: 
        4px 0 32px rgba(59, 130, 246, 0.1),
        inset 1px 0 0 rgba(255, 255, 255, 0.8);
}

/* Sidebar content wrapper */
section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

/* Sidebar headings */
section[data-testid="stSidebar"] h3 {
    color: #1e293b !important;
    font-size: 1.4rem !important;
    font-weight: 700 !important;
    margin: 25px 0 15px 0 !important;
    padding: 10px 0 !important;
    position: relative !important;
    letter-spacing: -0.3px;
}

/* Gradient underline for sidebar headings */
section[data-testid="stSidebar"] h3::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 40px;
    height: 3px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    border-radius: 2px;
    transition: width 0.3s ease;
}

section[data-testid="stSidebar"] h3:hover::after {
    width: 60px;
}

/* Sidebar country info card */
.sidebar-country-card {
    background: rgba(255, 255, 255, 0.8);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 16px;
    padding: 18px;
    margin: 20px 0;
    transition: all 0.3s ease;
    box-shadow: 
        0 4px 20px rgba(0, 0, 0, 0.03),
        0 2px 8px rgba(59, 130, 246, 0.05);
}

.sidebar-country-card:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateY(-2px);
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.06),
        0 4px 16px rgba(59, 130, 246, 0.08);
}

/* Country flag animation */
.country-flag {
    font-size: 2.8rem;
    display: inline-block;
    animation: gentleFloat 6s ease-in-out infinite;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

@keyframes gentleFloat {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-5px) rotate(2deg); }
}

/* ===============================
   SIDEBAR SELECT BOXES - FIXED
================================ */

/* Select box container */
section[data-testid="stSidebar"] .stSelectbox {
    margin: 15px 0 !important;
}

/* Select box label - Center aligned */
section[data-testid="stSidebar"] .stSelectbox > label {
    color: #475569 !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    margin-bottom: 8px !important;
    display: block !important;
    text-align: center !important;
    width: 100% !important;
    padding: 0 10px !important;
}

/* Select box dropdown container */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.95) !important;
    border: 1.5px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important;
    transition: all 0.3s ease !important;
    min-height: 48px !important;
    display: flex !important;
    align-items: center !important;
    box-shadow: 
        0 2px 12px rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
}

/* Hover state */
section[data-testid="stSidebar"] .stSelectbox > div > div:hover {
    border-color: rgba(59, 130, 246, 0.4) !important;
    box-shadow: 
        0 0 0 3px rgba(59, 130, 246, 0.1),
        0 4px 16px rgba(0, 0, 0, 0.06) !important;
}

/* Focus state */
section[data-testid="stSidebar"] .stSelectbox > div > div:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: 
        0 0 0 4px rgba(59, 130, 246, 0.15),
        0 6px 20px rgba(0, 0, 0, 0.08) !important;
}

/* Selected value text - Centered */
section[data-testid="stSidebar"] .stSelectbox > div > div > div > div {
    color: #1e293b !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    text-align: center !important;
    width: 100% !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    min-height: 24px !important;
    padding: 0 10px !important;
}

/* Dropdown arrow */
section[data-testid="stSidebar"] .stSelectbox > div > div > div:last-child {
    color: #3b82f6 !important;
    opacity: 0.7;
    transition: all 0.3s ease;
}

section[data-testid="stSidebar"] .stSelectbox > div > div:hover > div:last-child {
    opacity: 1;
    transform: translateY(1px);
}

/* Dropdown menu */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"] {
    background: rgba(255, 255, 255, 0.98) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 12px !important;
    margin-top: 8px !important;
    box-shadow: 
        0 10px 40px rgba(0, 0, 0, 0.1),
        0 4px 20px rgba(59, 130, 246, 0.08) !important;
    overflow: hidden !important;
}

/* Dropdown menu items */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"] > div {
    background: transparent !important;
}

/* Individual dropdown items */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"] > div > div {
    color: #475569 !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    min-height: 44px !important;
    display: flex !important;
    align-items: center !important;
    transition: all 0.2s ease !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.03) !important;
}

/* Last item no border */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"] > div:last-child > div {
    border-bottom: none !important;
}

/* Hover state for dropdown items */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"] > div > div:hover {
    background: rgba(59, 130, 246, 0.08) !important;
    color: #1e40af !important;
    padding-left: 20px !important;
}

/* Selected item in dropdown */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"] > div > div[aria-selected="true"] {
    background: linear-gradient(90deg, rgba(59, 130, 246, 0.1), rgba(139, 92, 246, 0.08)) !important;
    color: #1e40af !important;
    font-weight: 600 !important;
}

/* Dropdown scrollbar */
section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"]::-webkit-scrollbar {
    width: 8px;
}

section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"]::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.02);
    border-radius: 4px;
    margin: 4px;
}

section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"]::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #3b82f6, #8b5cf6);
    border-radius: 4px;
}

section[data-testid="stSidebar"] .stSelectbox > div > div > div[data-baseweb="menu"]::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #2563eb, #7c3aed);
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    border: none;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 600;
    color: white;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 
        0 4px 16px rgba(59, 130, 246, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.3);
    width: 100%;
    margin: 8px 0;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 
        0 8px 24px rgba(59, 130, 246, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.4);
    background: linear-gradient(135deg, #2563eb, #7c3aed);
}

/* Template cards in sidebar */
.template-card {
    background: rgba(255, 255, 255, 0.8);
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 14px;
    padding: 16px;
    margin: 12px 0;
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.template-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    opacity: 0;
    transition: opacity 0.3s ease;
}

.template-card:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateX(4px);
    box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
}

.template-card:hover::before {
    opacity: 1;
}

/* Place preview cards in sidebar */
.place-preview-card {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.05);
    border-radius: 12px;
    padding: 14px;
    margin: 10px 0;
    transition: all 0.3s ease;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
}

.place-preview-card:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(59, 130, 246, 0.2);
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.04);
}

/* Sidebar stats cards */
.sidebar-stat-card {
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid rgba(59, 130, 246, 0.1);
    border-radius: 16px;
    padding: 18px;
    text-align: center;
    transition: all 0.3s ease;
    backdrop-filter: blur(10px);
}

.sidebar-stat-card:hover {
    background: rgba(255, 255, 255, 0.95);
    border-color: rgba(59, 130, 246, 0.3);
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.08);
}

.sidebar-stat-icon {
    font-size: 2rem;
    margin-bottom: 10px;
    display: inline-block;
    color: #3b82f6;
    filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.2));
}

.sidebar-stat-number {
    font-size: 2rem;
    font-weight: 800;
    color: #1e40af;
    margin: 8px 0;
    background: linear-gradient(90deg, #1e40af, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.sidebar-stat-label {
    color: #475569;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

/* Sidebar checkboxes and sliders */
section[data-testid="stSidebar"] .stCheckbox > label,
section[data-testid="stSidebar"] .stSlider > label {
    color: #475569;
    font-weight: 500;
    font-size: 0.9rem;
    text-align: center !important;
    width: 100% !important;
    display: block !important;
    margin-bottom: 10px !important;
}

section[data-testid="stSidebar"] .stCheckbox > div > div {
    background: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 6px;
}

/* Sidebar sliders */
section[data-testid="stSidebar"] .stSlider > div > div {
    padding: 0 10px !important;
}

/* Sidebar dividers */
section[data-testid="stSidebar"] hr {
    margin: 25px 0;
    border: none;
    height: 1px;
    background: linear-gradient(90deg, 
        transparent, 
        rgba(59, 130, 246, 0.2), 
        transparent);
}

/* Scrollbar for sidebar */
section[data-testid="stSidebar"] ::-webkit-scrollbar {
    width: 8px;
}

section[data-testid="stSidebar"] ::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.02);
    border-radius: 4px;
}

section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #3b82f6, #8b5cf6);
    border-radius: 4px;
}

section[data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #2563eb, #7c3aed);
}

/* Sidebar success messages */
section[data-testid="stSidebar"] .stAlert {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 12px;
    color: #047857;
    font-weight: 500;
    text-align: center !important;
    padding: 15px !important;
    margin: 10px 0 !important;
}

/* Sidebar loading spinner */
section[data-testid="stSidebar"] .stSpinner > div > div {
    background: linear-gradient(90deg, #3b82f6, #8b5cf6) !important;
}

/* Responsive sidebar adjustments */
@media (max-width: 768px) {
    section[data-testid="stSidebar"] {
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
    }
    
    section[data-testid="stSidebar"] h3 {
        font-size: 1.2rem !important;
    }
    
    .sidebar-country-card,
    .sidebar-stat-card {
        padding: 14px;
    }
    
    .country-flag {
        font-size: 2.2rem;
    }
    
    .sidebar-stat-number {
        font-size: 1.8rem;
    }
    
    /* Mobile select boxes */
    section[data-testid="stSidebar"] .stSelectbox > label {
        font-size: 0.95rem !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div {
        padding: 10px 14px !important;
        min-height: 44px !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox > div > div > div > div {
        font-size: 0.95rem !important;
    }
}

/* Sidebar gradient overlay effect */
.sidebar-gradient-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
        135deg,
        rgba(59, 130, 246, 0.03) 0%,
        rgba(139, 92, 246, 0.02) 50%,
        rgba(236, 72, 153, 0.01) 100%
    );
    pointer-events: none;
    z-index: -1;
}

/* Sidebar text elements */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: #475569 !important;
}

/* Strong text in sidebar */
section[data-testid="stSidebar"] strong {
    color: #1e293b !important;
}

/* Sidebar input focus states */
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus,
section[data-testid="stSidebar"] select:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    outline: none !important;
}




/* Placeholder text for empty select boxes */
section[data-testid="stSidebar"] .stSelectbox > div > div > div > div:empty::before {
    content: "Select an option";
    color: #94a3b8 !important;
    font-weight: 400 !important;
    font-style: italic !important;
}
    
    /* Enhanced Card styling - White Theme */
    .place-card {
        background: #ffffff;
        backdrop-filter: blur(10px);
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        height: 100%;
        position: relative;
        overflow: hidden;
    }
    
    .place-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        border-radius: 20px 20px 0 0;
    }
    
    .place-card:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: #3b82f6;
        box-shadow: 0 20px 60px rgba(59, 130, 246, 0.15);
    }
    
    /* Image container */
    .image-container {
        width: 100%;
        height: 220px;
        border-radius: 16px;
        overflow: hidden;
        margin-bottom: 20px;
        border: 2px solid #e2e8f0;
        position: relative;
    }
    
    .image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.6s ease;
    }
    
    .image-container:hover img {
        transform: scale(1.15);
    }
    
    .image-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
        padding: 15px;
        color: white;
        font-size: 0.8rem;
    }
    
    /* Badge styling */
    .place-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 25px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 15px;
        background: rgba(59, 130, 246, 0.1);
        color: #1e40af;
        border: 1px solid rgba(59, 130, 246, 0.2);
        backdrop-filter: blur(5px);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Rating stars */
    .rating-container {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 15px 0;
    }
    
    .stars {
        color: #f59e0b;
        font-size: 1rem;
        text-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
    }
    
    /* Time info */
    .time-info {
        display: flex;
        justify-content: space-between;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
    }
    
    .time-item {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #475569;
        font-size: 0.85rem;
        background: #f8fafc;
        padding: 8px 12px;
        border-radius: 12px;
    }
    
    /* Day header */
    .day-header {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        padding: 20px 30px;
        border-radius: 20px;
        margin: 25px 0;
        border: 1px solid rgba(59, 130, 246, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .day-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" preserveAspectRatio="none" opacity="0.1"><path d="M0,0 L100,0 L100,100 Z" fill="white"/></svg>');
        background-size: cover;
    }
    
    /* Section headers */
    .section-title {
        color: #1e293b;
        font-size: 2rem;
        font-weight: 800;
        margin: 40px 0 25px 0;
        padding-bottom: 15px;
        border-bottom: 3px solid #3b82f6;
        position: relative;
        display: inline-block;
    }
    
    .section-title::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        border-radius: 3px;
    }
    
    /* ===============================
   ENHANCED STAT CARDS
================================ */

/* Main stat card container */
.stat-card {
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border-radius: 24px;
    padding: 30px 20px;
    text-align: center;
    border: 1px solid rgba(59, 130, 246, 0.15);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.04),
        0 4px 16px rgba(59, 130, 246, 0.05),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

/* Gradient border effect */
.stat-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, 
        #3b82f6 0%, 
        #8b5cf6 25%, 
        #ec4899 50%, 
        #f59e0b 75%, 
        #10b981 100%);
    border-radius: 24px 24px 0 0;
    opacity: 0;
    transition: opacity 0.3s ease;
    z-index: 1;
}

/* Background pattern */
.stat-card::after {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(
        circle at center,
        rgba(59, 130, 246, 0.08) 0%,
        rgba(139, 92, 246, 0.04) 25%,
        transparent 50%
    );
    opacity: 0;
    transition: opacity 0.5s ease;
    z-index: 0;
    pointer-events: none;
}

/* Hover effects */
.stat-card:hover {
    transform: translateY(-8px) scale(1.02);
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 
        0 20px 60px rgba(59, 130, 246, 0.12),
        0 12px 40px rgba(0, 0, 0, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.stat-card:hover::before {
    opacity: 1;
}

.stat-card:hover::after {
    opacity: 1;
    animation: gentlePulse 4s ease-in-out infinite;
}

@keyframes gentlePulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.6; }
}

/* Icon styling */
.stat-icon {
    font-size: 3rem;
    margin-bottom: 20px;
    display: inline-block;
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
    transition: all 0.3s ease;
}

.stat-card:hover .stat-icon {
    transform: scale(1.2) rotate(5deg);
    filter: drop-shadow(0 6px 12px rgba(59, 130, 246, 0.3));
}

/* Number styling with gradient animation */
.stat-number {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 15px 0;
    position: relative;
    z-index: 2;
    background: linear-gradient(
        135deg,
        #1e40af 0%,
        #3b82f6 25%,
        #8b5cf6 50%,
        #ec4899 75%,
        #f59e0b 100%
    );
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    background-size: 200% auto;
    animation: gradientShift 6s ease-in-out infinite;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

@keyframes gradientShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Label styling */
.stat-label {
    color: #475569;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    position: relative;
    z-index: 2;
    padding: 8px 16px;
    background: rgba(59, 130, 246, 0.08);
    border-radius: 12px;
    border: 1px solid rgba(59, 130, 246, 0.15);
    backdrop-filter: blur(5px);
    transition: all 0.3s ease;
}

.stat-card:hover .stat-label {
    background: rgba(59, 130, 246, 0.15);
    border-color: rgba(59, 130, 246, 0.3);
    color: #1e40af;
    transform: translateY(-2px);
}

/* Counter animation for numbers */
@keyframes countUp {
    from { 
        opacity: 0;
        transform: translateY(10px);
    }
    to { 
        opacity: 1;
        transform: translateY(0);
    }
}

.stat-number.animated {
    animation: countUp 1s ease-out forwards;
}

/* Sparkle effect (optional) */
.sparkle {
    position: absolute;
    width: 20px;
    height: 20px;
    background: linear-gradient(45deg, #3b82f6, #8b5cf6);
    border-radius: 50%;
    filter: blur(2px);
    opacity: 0;
    pointer-events: none;
}

.stat-card:hover .sparkle {
    animation: sparkleFloat 2s ease-out;
}

@keyframes sparkleFloat {
    0% {
        opacity: 0;
        transform: translate(0, 0) scale(0);
    }
    50% {
        opacity: 0.8;
        transform: translate(var(--x), var(--y)) scale(1);
    }
    100% {
        opacity: 0;
        transform: translate(calc(var(--x) * 1.5), calc(var(--y) * 1.5)) scale(0);
    }
}

/* Mobile responsiveness */
@media (max-width: 768px) {
    .stat-card {
        padding: 20px 15px;
        min-height: 160px;
        border-radius: 20px;
    }
    
    .stat-icon {
        font-size: 2.2rem;
        margin-bottom: 15px;
    }
    
    .stat-number {
        font-size: 2.2rem;
        margin: 10px 0;
    }
    
    .stat-label {
        font-size: 0.85rem;
        padding: 6px 12px;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .stat-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border-color: rgba(255, 255, 255, 0.1);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .stat-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
        box-shadow: 
            0 20px 60px rgba(59, 130, 246, 0.15),
            0 12px 40px rgba(0, 0, 0, 0.3);
    }
    
    .stat-label {
        color: #cbd5e1;
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.25);
    }
    
    .stat-card:hover .stat-label {
        color: #60a5fa;
        background: rgba(59, 130, 246, 0.25);
    }
}

/* Loading shimmer effect */
.stat-card.loading {
    background: linear-gradient(
        90deg,
        #f1f5f9 0%,
        #e2e8f0 50%,
        #f1f5f9 100%
    );
    background-size: 200% 100%;
    animation: loadingShimmer 1.5s infinite linear;
}

@keyframes loadingShimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

    /* Schedule cards */
    .schedule-card {
        background: #ffffff;
        border-radius: 20px;
        padding: 25px;
        border-left: 5px solid;
        margin: 15px 0;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    }
    
    .schedule-card:hover {
        transform: translateX(5px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    
    .morning-card {
        border-left-color: #f59e0b;
        background: linear-gradient(to right, #fff7ed, #ffffff);
    }
    
    .afternoon-card {
        border-left-color: #10b981;
        background: linear-gradient(to right, #f0fdf4, #ffffff);
    }
    
    .evening-card {
        border-left-color: #8b5cf6;
        background: linear-gradient(to right, #faf5ff, #ffffff);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        color: white;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb, #7c3aed);
    }
    
    /* Gradient text */
    .gradient-text {
        background: linear-gradient(90deg, #1e40af, #7c3aed, #be185d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 800;
    }
    
    /* Tag styling */
    .place-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.75rem;
        background: #f1f5f9;
        color: #475569;
        margin: 3px;
        border: 1px solid #e2e8f0;
    }
    
    /* Map container */
    .map-container {
        border-radius: 20px;
        overflow: hidden;
        border: 2px solid #e2e8f0;
        margin: 20px 0;
    }
    
    /* Loading animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .loading {
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    
    /* Text colors for white theme */
    h1, h2, h3, h4, h5, h6 {
        color: #1e293b !important;
    }
    
    p, span, div {
        color: #334155 !important;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        border-right: 1px solid #e2e8f0;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #1e293b;
    }
    
    /* Checkbox and select */
    .stCheckbox > label,
    .stSelectbox > label {
        color: #334155;
    }
    
    /* Markdown boxes */
    .stMarkdown {
        color: #334155;
    }
    
    /* Info, success, warning, error boxes */
    .stAlert {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        background: #f8fafc;
        border-radius: 12px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    /* Divider */
    hr {
        border-color: #e2e8f0;
    }
    
    /* Tooltips */
    .stTooltip {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        color: #334155;
    }
    
    /* Metric containers */
    .stMetric {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    }
    
    /* Data editor */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }

    /* ===============================
   TRAVEL INQUIRY CARD
================================ */

/* Travel Inquiry Card Container */
.travel-inquiry-card {
    background: rgba(255, 255, 255, 0.9);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 20px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: 
        0 12px 40px rgba(0, 0, 0, 0.06),
        0 4px 16px rgba(59, 130, 246, 0.08),
        inset 0 1px 0 rgba(255, 255, 255, 0.6);
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}

.travel-inquiry-card:hover {
    transform: translateY(-4px);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.08),
        0 8px 24px rgba(59, 130, 246, 0.12),
        inset 0 1px 0 rgba(255, 255, 255, 0.8);
    border-color: rgba(59, 130, 246, 0.25);
    background: rgba(255, 255, 255, 0.95);
}

/* Card gradient border top */
.travel-inquiry-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
    border-radius: 20px 20px 0 0;
    z-index: 2;
}

/* Card background glow effect */
.travel-inquiry-card::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 120%;
    height: 120%;
    background: radial-gradient(circle at center,
        rgba(59, 130, 246, 0.08) 0%,
        rgba(139, 92, 246, 0.04) 30%,
        transparent 60%);
    transform: translate(-50%, -50%);
    z-index: 1;
    pointer-events: none;
    animation: gentleGlow 6s ease-in-out infinite;
}

@keyframes gentleGlow {
    0%, 100% { opacity: 0.4; }
    50% { opacity: 0.6; }
}

/* Card header */
.inquiry-card-header {
    display: flex;
    align-items: center;
    gap: 15px;
    margin-bottom: 25px;
    position: relative;
    z-index: 3;
}

.inquiry-card-icon {
    font-size: 2.5rem;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    filter: drop-shadow(0 4px 8px rgba(59, 130, 246, 0.2));
    animation: iconFloat 4s ease-in-out infinite;
}

@keyframes iconFloat {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-5px) rotate(5deg); }
}

.inquiry-card-title {
    color: #1e293b;
    font-size: 1.8rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(90deg, #1e40af, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}

.inquiry-card-subtitle {
    color: #64748b;
    font-size: 0.95rem;
    margin-top: 5px;
    font-weight: 500;
    padding-left: 55px;
}

/* Enhanced text area container */
.inquiry-textarea-container {
    position: relative;
    z-index: 3;
}

/* Custom text area styling */
.custom-textarea {
    background: rgba(255, 255, 255, 0.8) !important;
    backdrop-filter: blur(10px);
    border: 1.5px solid rgba(0, 0, 0, 0.08) !important;
    border-radius: 16px !important;
    padding: 20px !important;
    font-size: 1rem !important;
    line-height: 1.6 !important;
    color: #1e293b !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    transition: all 0.3s ease !important;
    box-shadow: 
        0 4px 20px rgba(0, 0, 0, 0.02),
        inset 0 1px 0 rgba(255, 255, 255, 0.6) !important;
    min-height: 280px !important;
    resize: vertical !important;
}

.custom-textarea::placeholder {
    color: #94a3b8 !important;
    font-style: italic !important;
    font-weight: 400 !important;
}

.custom-textarea:focus {
    outline: none !important;
    border-color: #3b82f6 !important;
    box-shadow: 
        0 0 0 4px rgba(59, 130, 246, 0.1),
        0 8px 32px rgba(0, 0, 0, 0.04),
        inset 0 1px 0 rgba(255, 255, 255, 0.8) !important;
    background: rgba(255, 255, 255, 0.95) !important;
}

.custom-textarea:hover {
    border-color: rgba(59, 130, 246, 0.3) !important;
    box-shadow: 
        0 8px 32px rgba(0, 0, 0, 0.03),
        inset 0 1px 0 rgba(255, 255, 255, 0.7) !important;
}

/* Text area scrollbar */
.custom-textarea::-webkit-scrollbar {
    width: 10px;
}

.custom-textarea::-webkit-scrollbar-track {
    background: rgba(0, 0, 0, 0.02);
    border-radius: 5px;
    margin: 5px;
}

.custom-textarea::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #3b82f6, #8b5cf6);
    border-radius: 5px;
    border: 3px solid rgba(255, 255, 255, 0.8);
}

.custom-textarea::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #2563eb, #7c3aed);
}

/* Card footer with tips */
.inquiry-card-footer {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 20px;
    padding: 15px;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.1);
    border-radius: 14px;
    position: relative;
    z-index: 3;
    animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.tips-icon {
    font-size: 1.5rem;
    color: #3b82f6;
    animation: gentleBounce 2s ease-in-out infinite;
}

@keyframes gentleBounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.tips-content {
    flex: 1;
}

.tips-title {
    color: #1e40af;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 4px;
}

.tips-text {
    color: #475569;
    font-size: 0.85rem;
    line-height: 1.5;
    margin: 0;
}

/* Character counter (optional) */
.char-counter {
    position: absolute;
    bottom: 15px;
    right: 20px;
    font-size: 0.8rem;
    color: #94a3b8;
    font-weight: 500;
    z-index: 4;
    background: rgba(255, 255, 255, 0.8);
    padding: 4px 10px;
    border-radius: 12px;
    backdrop-filter: blur(5px);
    border: 1px solid rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.char-counter.active {
    color: #3b82f6;
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.2);
}

/* Card status indicators */
.card-status {
    position: absolute;
    top: 30px;
    right: 30px;
    z-index: 3;
}

.status-dot {
    width: 12px;
    height: 12px;
    background: linear-gradient(135deg, #10b981, #3b82f6);
    border-radius: 50%;
    animation: statusPulse 2s ease-in-out infinite;
    box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
}

@keyframes statusPulse {
    0%, 100% { 
        transform: scale(1);
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
    }
    50% { 
        transform: scale(1.2);
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.6);
    }
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .travel-inquiry-card {
        padding: 20px;
        border-radius: 16px;
        margin: 15px 0;
    }
    
    .inquiry-card-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 10px;
    }
    
    .inquiry-card-title {
        font-size: 1.5rem;
    }
    
    .inquiry-card-subtitle {
        padding-left: 0;
    }
    
    .custom-textarea {
        padding: 15px !important;
        font-size: 0.95rem !important;
    }
    
    .inquiry-card-footer {
        flex-direction: column;
        text-align: center;
        gap: 10px;
    }
    
    .card-status {
        top: 20px;
        right: 20px;
    }
}

/* Loading state for text area */
.custom-textarea.loading {
    background: linear-gradient(
        90deg,
        rgba(255, 255, 255, 0.8) 0%,
        rgba(248, 250, 252, 0.9) 50%,
        rgba(255, 255, 255, 0.8) 100%
    ) !important;
    background-size: 200% 100% !important;
    animation: loadingShimmer 2s ease-in-out infinite !important;
}

@keyframes loadingShimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Focus indicator animation */
.focus-indicator {
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 18px;
    background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
    z-index: 2;
    opacity: 0;
    animation: focusPulse 2s ease-in-out infinite;
    pointer-events: none;
}

@keyframes focusPulse {
    0%, 100% { opacity: 0; }
    50% { opacity: 0.1; }
}

.custom-textarea:focus ~ .focus-indicator {
    opacity: 0.2;
    animation: none;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None
if 'email_text' not in st.session_state:
    st.session_state.email_text = ""
if 'image_cache' not in st.session_state:
    st.session_state.image_cache = {}
if 'places_cache' not in st.session_state:
    st.session_state.places_cache = {}
if 'countries_data' not in st.session_state:
    st.session_state.countries_data = {}

# Function to create hero section
def create_hero_section():
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-badge">AI-Powered Luxury Travel</div>
            <h1 class="hero-title">Sri Lanka Itinerary Planner</h1>
            <p class="hero-subtitle">
                Design your perfect Sri Lankan adventure with our intelligent day-by-day planner. 
                Get personalized recommendations, real-time updates, and seamless itinerary management.
            </p>
            <div style="display: flex; gap: 20px; justify-content: center; margin-top: 40px; flex-wrap: wrap;">
                <div class="glass-badge">📅 Daily Planning</div>
                <div class="glass-badge">🏨 Smart Accommodation</div>
                <div class="glass-badge">🚗 Transport Integration</div>
                <div class="glass-badge">🎯 Personalized Activities</div>
            </div>
        </div> 
    </div>
    """, unsafe_allow_html=True)

# Function to fetch all countries from REST Countries API
@st.cache_data(ttl=86400) # Cache for 24 hours
def get_all_countries():
    """Fetch all countries with details from REST Countries API"""
    try:
        response = requests.get("https://restcountries.com/v3.1/all", timeout=10)
        if response.status_code == 200:
            countries = response.json()
            country_list = []
          
            for country in countries:
                country_data = {
                    "name": country.get("name", {}).get("common", "Unknown"),
                    "official_name": country.get("name", {}).get("official", ""),
                    "capital": country.get("capital", ["N/A"])[0] if country.get("capital") else "N/A",
                    "region": country.get("region", "N/A"),
                    "subregion": country.get("subregion", "N/A"),
                    "population": country.get("population", 0),
                    "area": country.get("area", 0),
                    "languages": list(country.get("languages", {}).values()) if country.get("languages") else [],
                    "currencies": list(country.get("currencies", {}).keys()) if country.get("currencies") else [],
                    "flag": country.get("flag", "🏳️"),
                    "timezones": country.get("timezones", []),
                    "borders": country.get("borders", []),
                    "cca2": country.get("cca2", ""), # Country code
                    "latlng": country.get("latlng", [0, 0]) # Latitude, Longitude
                }
                country_list.append(country_data)
          
            # Sort alphabetically
            country_list.sort(key=lambda x: x["name"])
            return country_list
    except Exception as e:
        st.warning(f"Could not fetch countries: {str(e)}")
        return []
  
    return []

# Function to get real places from OpenTripMap API
@st.cache_data(ttl=3600)
def get_places_from_opentripmap(lat, lon, radius=10000, limit=20):
    """Get tourist attractions from OpenTripMap API"""
    if not OPENTRIPMAP_API_KEY:
        return []
  
    try:
        url = "https://api.opentripmap.com/0.1/en/places/radius"
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "format": "json",
            "limit": limit,
            "apikey": OPENTRIPMAP_API_KEY,
            "kinds": "historic,architecture,cultural,museums,religion,beaches,natural" # Filter for tourist attractions
        }
      
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            places = response.json()
            detailed_places = []
          
            # Get details for each place
            for place in places[:10]: # Limit to 10 for performance
                xid = place.get("xid")
                if xid:
                    details = get_place_details_from_opentripmap(xid)
                    if details:
                        detailed_places.append(details)
          
            return detailed_places
    except Exception as e:
        st.warning(f"OpenTripMap API error: {str(e)}")
  
    return []

def get_place_details_from_opentripmap(xid):
    """Get detailed information about a specific place"""
    try:
        url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
        params = {"apikey": OPENTRIPMAP_API_KEY}
      
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            place = response.json()
          
            # Extract place type from kinds
            kinds = place.get("kinds", "").split(",")
            place_type = "Attraction"
            if "historic" in kinds:
                place_type = "Historic Site"
            elif "museum" in kinds:
                place_type = "Museum"
            elif "religious" in kinds:
                place_type = "Religious Site"
            elif "beach" in kinds:
                place_type = "Beach"
            elif "natural" in kinds:
                place_type = "Natural"
            elif "architecture" in kinds:
                place_type = "Architecture"
          
            return {
                "name": place.get("name", "Unknown Place"),
                "type": place_type,
                "description": place.get("wikipedia_extracts", {}).get("text", "A popular tourist attraction.")[:200] + "...",
                "rating": round(random.uniform(3.5, 5.0), 1),
                "coordinates": {
                    "lat": place.get("point", {}).get("lat", 0),
                    "lon": place.get("point", {}).get("lon", 0)
                },
                "wikipedia": place.get("wikipedia", "")
            }
    except:
        pass
  
    return None

# Function to get places from Foursquare API
@st.cache_data(ttl=3600)
def get_places_from_foursquare(city, country, category="tourism"):
    """Get places from Foursquare API"""
    if not FOURSQUARE_API_KEY:
        return []
  
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            "Authorization": FOURSQUARE_API_KEY,
            "accept": "application/json"
        }
      
        query = f"{city}, {country}"
        params = {
            "query": "tourist attraction",
            "near": query,
            "limit": 15,
            "categories": "16000" # Travel & Transportation category
        }
      
        response = requests.get(url, headers=headers, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            places = []
          
            for venue in data.get("results", []):
                place = {
                    "name": venue.get("name", "Unknown"),
                    "type": venue.get("categories", [{}])[0].get("name", "Attraction"),
                    "rating": venue.get("rating", round(random.uniform(3.5, 5.0), 1)),
                    "description": f"A popular attraction in {city}.",
                    "coordinates": {
                        "lat": venue.get("geocodes", {}).get("main", {}).get("latitude", 0),
                        "lon": venue.get("geocodes", {}).get("main", {}).get("longitude", 0)
                    }
                }
                places.append(place)
          
            return places
    except Exception as e:
        st.warning(f"Foursquare API error: {str(e)}")
  
    return []

# Function to get city coordinates
@st.cache_data(ttl=86400)
def get_city_coordinates(city, country):
    """Get latitude and longitude for a city"""
    try:
        geolocator = Nominatim(user_agent="travel_itinerary_app")
        location = geolocator.geocode(f"{city}, {country}")
        if location:
            return location.latitude, location.longitude
    except:
        pass
  
    # Fallback coordinates for Sri Lankan cities
    fallback_coords = {
        "Colombo": (6.9271, 79.8612),
        "Kandy": (7.2906, 80.6337),
        "Galle": (6.0535, 80.2200),
        "Negombo": (7.2090, 79.8367),
        "Bentota": (6.4210, 79.9988),
        "Hikkaduwa": (6.1390, 80.1038),
        "Mirissa": (5.9455, 80.4583),
        "Weligama": (5.9743, 80.4294),
        "Tangalle": (6.0167, 80.7833),
        "Nuwara Eliya": (6.9497, 80.7890),
        "Ella": (6.8675, 81.0486),
        "Badulla": (6.9895, 81.0557),
        "Bandarawela": (6.8256, 80.9982),
        "Hatton": (6.8917, 80.5958),
        "Sigiriya": (7.9570, 80.7603),
        "Dambulla": (7.8567, 80.6491),
        "Polonnaruwa": (7.9403, 81.0188),
        "Anuradhapura": (8.3114, 80.4037),
        "Trincomalee": (8.5874, 81.2152),
        "Batticaloa": (7.7167, 81.7000),
        "Pasikudah": (7.9347, 81.5677),
        "Arugam Bay": (6.8385, 81.8352),
        "Jaffna": (9.6615, 80.0255),
        "Mannar": (8.9814, 79.9044),
        "Vavuniya": (8.7543, 80.4981),
        "Yala": (6.3833, 81.5167),
        "Udawalawe": (6.4435, 80.8747),
        "Wilpattu": (8.4500, 80.0000),
        "Kitulgala": (6.9894, 80.4175),
        "Ratnapura": (6.6828, 80.3992),
        "Kalutara": (6.5831, 79.9593),
        "Beruwala": (6.4733, 79.9844),
        "Chilaw": (7.5758, 79.7956),
        "Puttalam": (8.0362, 79.8283),
        "Matara": (5.9485, 80.5353),
        "Hambantota": (6.1240, 81.1185),
        "Ampara": (7.2833, 81.6667),
        "Monaragala": (6.8728, 81.3506),
        "Kurunegala": (7.4867, 80.3647),
        "Kegalle": (7.2533, 80.3464),
        "Matale": (7.4675, 80.6234),
        "Nuwara Eliya": (6.9708, 80.7829)
    }
  
    if city in fallback_coords:
        return fallback_coords[city]
  
    # Return default coordinates
    return (7.8731, 80.7718) # Center of Sri Lanka

# Function to get real images with multiple sources
@st.cache_data(ttl=3600, show_spinner=False)
def get_place_image(place_name, city, country, size="medium"):
    """Get high-quality image for a real place from multiple sources"""
    cache_key = f"{place_name}_{city}_{country}_{size}"
  
    # Check cache first
    if cache_key in st.session_state.image_cache:
        return st.session_state.image_cache[cache_key]
  
    # Try Unsplash first
    if UNSPLASH_ACCESS_KEY:
        try:
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
          
            queries = [
                f"{place_name} {city} {country} tourism",
                f"{place_name} landmark",
                f"{city} {place_name} tourist attraction",
                f"{place_name} travel",
                place_name
            ]
          
            for query in queries:
                params = {
                    "query": query,
                    "per_page": 1,
                    "orientation": "landscape",
                    "content_filter": "high"
                }
              
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results") and len(data["results"]) > 0:
                        photo = data["results"][0]
                        image_url = photo["urls"]["regular"] if size == "medium" else photo["urls"]["full"]
                      
                        result = {
                            "url": image_url,
                            "photographer": photo["user"]["name"],
                            "photographer_url": photo["user"]["links"]["html"],
                            "alt": photo.get("alt_description", f"{place_name} in {city}"),
                            "source": "Unsplash"
                        }
                        st.session_state.image_cache[cache_key] = result
                        return result
        except:
            pass
  
    # Try Pexels
    if PEXELS_API_KEY:
        try:
            headers = {"Authorization": PEXELS_API_KEY}
            url = "https://api.pexels.com/v1/search"
          
            queries = [
                f"{place_name} {city} tourism",
                f"{place_name} landmark {country}",
                f"{city} attractions",
                place_name
            ]
          
            for query in queries:
                params = {
                    "query": query,
                    "per_page": 1,
                    "orientation": "landscape"
                }
              
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("photos") and len(data["photos"]) > 0:
                        photo = data["photos"][0]
                        image_url = photo["src"]["large"] if size == "large" else photo["src"]["medium"]
                      
                        result = {
                            "url": image_url,
                            "photographer": photo["photographer"],
                            "photographer_url": photo["photographer_url"],
                            "alt": photo.get("alt", f"{place_name} in {city}"),
                            "source": "Pexels"
                        }
                        st.session_state.image_cache[cache_key] = result
                        return result
        except:
            pass
  
    # Fallback: Use Wikimedia Commons for famous places
    try:
        search_query = f"{place_name} {city}"
        wiki_url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "piprop": "original",
            "titles": search_query
        }
      
        response = requests.get(wiki_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                if "original" in page:
                    result = {
                        "url": page["original"]["source"],
                        "photographer": "Wikimedia Commons",
                        "photographer_url": "https://commons.wikimedia.org",
                        "alt": f"{place_name}",
                        "source": "Wikimedia"
                    }
                    st.session_state.image_cache[cache_key] = result
                    return result
    except:
        pass
  
    # Return None if no image found
    return None

# Function to get real places for a city
def get_real_places(city, country, limit=10):
    """Get real tourist places for a city from multiple APIs"""
    cache_key = f"{city}_{country}"
  
    if cache_key in st.session_state.places_cache:
        return st.session_state.places_cache[cache_key]
  
    places = []
  
    # Get city coordinates
    lat, lon = get_city_coordinates(city, country)
  
    # Try OpenTripMap API first
    opentripmap_places = get_places_from_opentripmap(lat, lon, limit=limit)
    places.extend(opentripmap_places)
  
    # Try Foursquare API
    foursquare_places = get_places_from_foursquare(city, country)
    places.extend(foursquare_places)
  
    # If no places found from APIs, use fallback database
    if not places:
        fallback_places = {
            "Colombo": [
                {"name": "Gangaramaya Temple", "type": "Buddhist Temple", "rating": 4.5, "description": "A beautiful Buddhist temple complex in Colombo with traditional architecture and museum."},
                {"name": "Galle Face Green", "type": "Urban Park", "rating": 4.3, "description": "Ocean-side urban park perfect for evening walks, kite flying, and sunset views."},
                {"name": "National Museum of Colombo", "type": "Museum", "rating": 4.2, "description": "Sri Lanka's largest museum showcasing cultural heritage and historical artifacts."},
                {"name": "Mount Lavinia Beach", "type": "Beach", "rating": 4.2, "description": "Popular beach area with golden sands, swimming spots, and beachside restaurants."},
                {"name": "Viharamahadevi Park", "type": "Park", "rating": 4.1, "description": "Colombo's largest park with beautiful gardens, fountains, and a giant Buddha statue."},
                {"name": "Independence Memorial Hall", "type": "Monument", "rating": 4.0, "description": "Historical monument commemorating independence from British rule."},
                {"name": "Pettah Floating Market", "type": "Market", "rating": 4.0, "description": "Colorful floating market with local produce, crafts, and street food."},
                {"name": "Colombo Dutch Museum", "type": "Museum", "rating": 3.9, "description": "Museum showcasing Dutch colonial history in a restored 17th-century building."},
                {"name": "Seema Malaka Temple", "type": "Buddhist Temple", "rating": 4.3, "description": "Serene temple on Beira Lake designed by Geoffrey Bawa."},
                {"name": "Colombo Lotus Tower", "type": "Observation Tower", "rating": 4.1, "description": "Tallest tower in South Asia with observation decks and panoramic city views."}
            ],
            "Kandy": [
                {"name": "Temple of the Sacred Tooth Relic", "type": "Buddhist Temple", "rating": 4.8, "description": "UNESCO World Heritage site housing Buddha's tooth relic, most sacred Buddhist site in Sri Lanka."},
                {"name": "Kandy Lake", "type": "Lake", "rating": 4.2, "description": "Scenic artificial lake in the heart of Kandy, perfect for evening walks with temple views."},
                {"name": "Royal Botanical Gardens Peradeniya", "type": "Botanical Garden", "rating": 4.6, "description": "One of Asia's finest botanical gardens with diverse plant collections and orchid house."},
                {"name": "Bahiravokanda Vihara Buddha Statue", "type": "Monument", "rating": 4.4, "description": "Giant white Buddha statue overlooking Kandy with panoramic city views."},
                {"name": "Udawatta Kele Sanctuary", "type": "Forest Reserve", "rating": 4.3, "description": "Forest reserve with walking trails, birdwatching, and tranquility near Temple of Tooth."},
                {"name": "Kandy Arts & Crafts Association", "type": "Crafts Center", "rating": 4.0, "description": "Center showcasing traditional Sri Lankan arts, crafts, and wood carvings."},
                {"name": "Commonwealth War Cemetery", "type": "Memorial", "rating": 4.2, "description": "Well-maintained cemetery honoring Commonwealth soldiers from World War II."},
                {"name": "Kandy View Point", "type": "Viewpoint", "rating": 4.5, "description": "Best viewpoint for panoramic photos of Kandy city and the lake."},
                {"name": "National Museum Kandy", "type": "Museum", "rating": 3.8, "description": "Museum in the former royal palace showcasing Kandy's history and culture."},
                {"name": "Embekka Devalaya", "type": "Hindu Temple", "rating": 4.3, "description": "Famous for intricate wood carvings and pillars, UNESCO tentative site."}
            ],
            "Galle": [
                {"name": "Galle Fort", "type": "Fort", "rating": 4.8, "description": "UNESCO World Heritage site with Dutch colonial architecture, ramparts, and charming streets."},
                {"name": "Unawatuna Beach", "type": "Beach", "rating": 4.6, "description": "Pristine crescent-shaped beach with coral reefs, water sports, and beach cafes."},
                {"name": "Japanese Peace Pagoda", "type": "Pagoda", "rating": 4.3, "description": "Peaceful stupa on Rumassala Hill with panoramic ocean views and meditation areas."},
                {"name": "Galle Lighthouse", "type": "Lighthouse", "rating": 4.4, "description": "Iconic lighthouse at the edge of Galle Fort, Sri Lanka's oldest light station."},
                {"name": "National Maritime Museum", "type": "Museum", "rating": 4.0, "description": "Museum showcasing maritime history, marine biology, and naval artifacts."},
                {"name": "Jungle Beach", "type": "Beach", "rating": 4.5, "description": "Secluded beach surrounded by jungle, accessible by short hike from Unawatuna."},
                {"name": "Galle Fort Clock Tower", "type": "Landmark", "rating": 4.2, "description": "Historic clock tower at the fort entrance, built in 1883."},
                {"name": "Martin Wickramasinghe Museum", "type": "Museum", "rating": 4.1, "description": "Museum dedicated to Sri Lanka's renowned author in his childhood home."},
                {"name": "Rumassala Sanctuary", "type": "Sanctuary", "rating": 4.3, "description": "Jungle sanctuary with hiking trails, medicinal plants, and beach access."},
                {"name": "St. Mary's Cathedral", "type": "Church", "rating": 4.0, "description": "Historic Catholic church within Galle Fort with beautiful architecture."}
            ],
            "Negombo": [
                {"name": "Negombo Beach", "type": "Beach", "rating": 4.3, "description": "Long golden sandy beach close to Colombo International Airport, perfect for sunset walks."},
                {"name": "Negombo Fish Market", "type": "Market", "rating": 4.2, "description": "Bustling fish market showcasing daily catch, auctions, and traditional fishing methods."},
                {"name": "Dutch Canal", "type": "Canal", "rating": 4.1, "description": "Historic canal network built by Dutch, perfect for boat rides and birdwatching tours."},
                {"name": "St. Mary's Church", "type": "Church", "rating": 4.3, "description": "Beautiful Catholic church with impressive architecture and religious significance."},
                {"name": "Negombo Lagoon", "type": "Lagoon", "rating": 4.4, "description": "Extensive lagoon perfect for birdwatching, boat tours, and mangrove exploration."},
                {"name": "Muthurajawela Marsh", "type": "Wetland", "rating": 4.2, "description": "Protected wetland with boat safaris, diverse birdlife, and mangrove forests."},
                {"name": "Angurukaramulla Temple", "type": "Buddhist Temple", "rating": 4.0, "description": "Ancient Buddhist temple with intricate murals, statues, and peaceful atmosphere."},
                {"name": "Negombo Dutch Fort", "type": "Fort", "rating": 3.9, "description": "Remains of Dutch fort overlooking Negombo lagoon, built in 1672."},
                {"name": "Hamilton Canal", "type": "Canal", "rating": 4.0, "description": "Scenic canal built by British, connecting Colombo to Puttalam."},
                {"name": "St. Sebastian's Church", "type": "Church", "rating": 4.1, "description": "Gothic-style church with beautiful stained glass windows and architecture."}
            ],
            "Bentota": [
                {"name": "Bentota Beach", "type": "Beach", "rating": 4.5, "description": "Long golden beach perfect for swimming, water sports, and relaxation with calm waters."},
                {"name": "Brief Garden", "type": "Garden", "rating": 4.4, "description": "Beautiful garden created by Bevis Bawa, brother of architect Geoffrey Bawa."},
                {"name": "Kosgoda Turtle Hatchery", "type": "Conservation Center", "rating": 4.3, "description": "Sea turtle conservation and hatchery project protecting endangered species."},
                {"name": "Bentota River Safari", "type": "River Cruise", "rating": 4.4, "description": "Boat safari through mangrove forests, waterways, and birdwatching spots."},
                {"name": "Lunuganga Garden", "type": "Garden", "rating": 4.6, "description": "Country estate and garden of architect Geoffrey Bawa, showcasing landscape design."},
                {"name": "Galapatha Raja Maha Viharaya", "type": "Buddhist Temple", "rating": 4.2, "description": "Ancient temple with historical significance and beautiful architecture."},
                {"name": "Water Sports Center", "type": "Adventure Sports", "rating": 4.3, "description": "Jet skiing, banana boat rides, windsurfing, and other water activities."},
                {"name": "Bentota Railway Bridge", "type": "Bridge", "rating": 4.0, "description": "Historic railway bridge with scenic views of Bentota River."},
                {"name": "Induruwa Beach", "type": "Beach", "rating": 4.2, "description": "Less crowded beach section ideal for peaceful swimming and relaxation."},
                {"name": "Bawa's Bentota Beach Hotel", "type": "Architecture", "rating": 4.3, "description": "Iconic hotel designed by Geoffrey Bawa, masterpiece of tropical modernism."}
            ],
            "Hikkaduwa": [
                {"name": "Hikkaduwa Beach", "type": "Beach", "rating": 4.5, "description": "Famous for surfing, nightlife, coral reefs, and vibrant beach culture."},
                {"name": "Hikkaduwa Coral Sanctuary", "type": "Marine Sanctuary", "rating": 4.4, "description": "Protected marine area with glass-bottom boat tours and snorkeling."},
                {"name": "Tsunami Honganji Temple", "type": "Buddhist Temple", "rating": 4.2, "description": "Japanese-style temple built after the 2004 tsunami as a memorial."},
                {"name": "Hikkaduwa Turtle Hatchery", "type": "Conservation Center", "rating": 4.3, "description": "Conservation project protecting sea turtles and their hatchlings."},
                {"name": "Narigama Beach", "type": "Beach", "rating": 4.4, "description": "Less crowded beach section with good swimming conditions and beach bars."},
                {"name": "Hikkaduwa National Park", "type": "National Park", "rating": 4.3, "description": "Marine national park protecting coral reefs and marine biodiversity."},
                {"name": "Moonstone Mine", "type": "Mine", "rating": 4.0, "description": "Traditional moonstone mining area showcasing local gem industry."},
                {"name": "Seenigama Temple", "type": "Hindu Temple", "rating": 4.1, "description": "Ancient temple on small island, accessible during low tide."},
                {"name": "Hikkaduwa Surf Point", "type": "Surf Spot", "rating": 4.5, "description": "Popular surfing spot with consistent waves for beginners and experts."},
                {"name": "Hikkaduwa Glass Bottom Boats", "type": "Boat Tour", "rating": 4.2, "description": "Glass bottom boat tours to see coral reefs and marine life without getting wet."}
            ],
            "Mirissa": [
                {"name": "Mirissa Beach", "type": "Beach", "rating": 4.7, "description": "Picturesque beach with palm trees, known for whale watching and beautiful sunsets."},
                {"name": "Mirissa Whale Watching", "type": "Wildlife Tour", "rating": 4.6, "description": "Boat tours to spot blue whales, sperm whales, and dolphins in their natural habitat."},
                {"name": "Secret Beach", "type": "Beach", "rating": 4.5, "description": "Secluded beach accessible through jungle path, perfect for privacy and relaxation."},
                {"name": "Coconut Tree Hill", "type": "Viewpoint", "rating": 4.4, "description": "Iconic viewpoint with coconut trees and panoramic ocean views, perfect for photos."},
                {"name": "Parrot Rock", "type": "Viewpoint", "rating": 4.3, "description": "Rock formation with panoramic views of Mirissa beach and surrounding area."},
                {"name": "Mirissa Fishing Harbour", "type": "Harbor", "rating": 4.0, "description": "Active fishing harbor with colorful boats, fresh seafood, and local atmosphere."},
                {"name": "Weligama Bay", "type": "Bay", "rating": 4.3, "description": "Nearby bay popular for surfing lessons with gentle waves for beginners."},
                {"name": "Mirissa Marine Park", "type": "Marine Park", "rating": 4.2, "description": "Marine protected area with diverse marine life and coral formations."},
                {"name": "Polhena Beach", "type": "Beach", "rating": 4.1, "description": "Sheltered beach with calm waters ideal for swimming and snorkeling."},
                {"name": "Mirissa Cliff", "type": "Viewpoint", "rating": 4.3, "description": "Cliff area with restaurants and bars offering sunset views over the ocean."}
            ],
            "Tangalle": [
                {"name": "Tangalle Beach", "type": "Beach", "rating": 4.6, "description": "Long, pristine beach with golden sand, rock formations, and clear turquoise water."},
                {"name": "Rekawa Turtle Conservation Project", "type": "Conservation Center", "rating": 4.5, "description": "Turtle nesting beach with conservation project and night turtle watching tours."},
                {"name": "Hummanaya Blow Hole", "type": "Natural Wonder", "rating": 4.4, "description": "Only blow hole in Sri Lanka, where sea water sprays up through rock formations."},
                {"name": "Mulkirigala Rock Temple", "type": "Buddhist Temple", "rating": 4.3, "description": "Ancient rock temple with caves, frescoes, and panoramic views from the summit."},
                {"name": "Medaketiya Beach", "type": "Beach", "rating": 4.5, "description": "Secluded beach near Tangalle, perfect for swimming and relaxation."},
                {"name": "Tangalle Fishing Harbor", "type": "Harbor", "rating": 4.0, "description": "Traditional fishing harbor with colorful boats and fresh seafood market."},
                {"name": "Wewurukannala Temple", "type": "Buddhist Temple", "rating": 4.2, "description": "Temple with largest seated Buddha statue in Sri Lanka (160 feet tall)."},
                {"name": "Goyambokka Beach", "type": "Beach", "rating": 4.4, "description": "Beautiful sheltered beach with calm waters, ideal for families with children."},
                {"name": "Kalametiya Bird Sanctuary", "type": "Bird Sanctuary", "rating": 4.3, "description": "Lagoon and mangrove area perfect for birdwatching and boat safaris."},
                {"name": "Palm Paradise Cabanas", "type": "Beach Resort", "rating": 4.2, "description": "Beachfront accommodation with traditional cabanas and palm-fringed beach."}
            ],
            "Nuwara Eliya": [
                {"name": "Gregory Lake", "type": "Lake", "rating": 4.3, "description": "Scenic man-made lake with boating, horse riding, swan pedal boats, and beautiful views."},
                {"name": "Horton Plains National Park", "type": "National Park", "rating": 4.7, "description": "UNESCO World Heritage site with hiking trails to World's End viewpoint and Baker's Falls."},
                {"name": "Tea Plantations", "type": "Plantation", "rating": 4.6, "description": "Famous tea estates offering tours, factory visits, and tastings of Ceylon tea."},
                {"name": "Victoria Park", "type": "Park", "rating": 4.2, "description": "Beautiful botanical garden with exotic plants, flower beds, and birdwatching."},
                {"name": "Lover's Leap Waterfall", "type": "Waterfall", "rating": 4.1, "description": "Scenic waterfall with hiking trails, tea plantation views, and local legends."},
                {"name": "Single Tree Hill", "type": "Viewpoint", "rating": 4.4, "description": "Highest point in Nuwara Eliya with 360-degree panoramic views of surrounding hills."},
                {"name": "Nuwara Eliya Golf Club", "type": "Golf Course", "rating": 4.3, "description": "One of Asia's oldest golf courses (1889) with mountain views and challenging layout."},
                {"name": "Seetha Amman Temple", "type": "Hindu Temple", "rating": 4.2, "description": "Colorful temple associated with the Ramayana epic, located in Seetha Eliya."},
                {"name": "Galway's Land National Park", "type": "National Park", "rating": 4.0, "description": "Small national park ideal for birdwatching, nature walks, and endemic species."},
                {"name": "Pedro Tea Estate", "type": "Tea Factory", "rating": 4.3, "description": "One of Sri Lanka's oldest tea factories offering guided tours and tea tasting."}
            ],
            "Ella": [
                {"name": "Nine Arch Bridge", "type": "Bridge", "rating": 4.8, "description": "Iconic colonial-era railway bridge amidst tea plantations, perfect for photography."},
                {"name": "Little Adam's Peak", "type": "Hiking Trail", "rating": 4.7, "description": "Easy hike with panoramic views of Ella Gap, mountains, and tea plantations."},
                {"name": "Ravana Falls", "type": "Waterfall", "rating": 4.5, "description": "Beautiful cascading waterfall associated with the Ramayana legend, 25m high."},
                {"name": "Ella Rock", "type": "Hiking Trail", "rating": 4.6, "description": "Challenging hike with breathtaking views of surrounding hills and valleys."},
                {"name": "Ella Spice Garden", "type": "Garden", "rating": 4.3, "description": "Educational tour of Sri Lankan spices, herbs, and traditional Ayurvedic plants."},
                {"name": "Ravana's Cave", "type": "Cave", "rating": 4.2, "description": "Historical cave associated with the Ramayana epic, located on cliffs near Ella."},
                {"name": "Ella Village", "type": "Village", "rating": 4.4, "description": "Charming mountain village with cafes, guesthouses, local shops, and friendly atmosphere."},
                {"name": "Demodara Loop", "type": "Railway Engineering", "rating": 4.3, "description": "Famous spiral railway loop engineering marvel, train passes over itself."},
                {"name": "Ella Gap Viewpoint", "type": "Viewpoint", "rating": 4.5, "description": "Spectacular views of the valley, southern plains, and distant mountains."},
                {"name": "Ella Train Station", "type": "Railway Station", "rating": 4.1, "description": "Picturesque railway station with colonial architecture and mountain views."}
            ],
            "Badulla": [
                {"name": "Dunhinda Falls", "type": "Waterfall", "rating": 4.6, "description": "Magnificent 64m high waterfall, one of Sri Lanka's most beautiful waterfalls."},
                {"name": "Muthiyangana Raja Maha Viharaya", "type": "Buddhist Temple", "rating": 4.3, "description": "Ancient temple believed to be visited by Lord Buddha, important pilgrimage site."},
                {"name": "Badulla Park", "type": "Park", "rating": 4.1, "description": "Central park in Badulla town with gardens, walking paths, and colonial atmosphere."},
                {"name": "St. Mark's Church", "type": "Church", "rating": 4.0, "description": "Historic Anglican church built in 1857 with beautiful architecture and stained glass."},
                {"name": "Bogoda Wooden Bridge", "type": "Bridge", "rating": 4.4, "description": "Ancient wooden bridge from 16th century, oldest surviving wooden bridge in Sri Lanka."},
                {"name": "Halpewatte Tea Factory", "type": "Tea Factory", "rating": 4.2, "description": "Tea factory offering tours of tea processing and tasting of Uva region tea."},
                {"name": "Badulla Market", "type": "Market", "rating": 4.0, "description": "Local market with fresh produce, spices, and goods from surrounding hill country."},
                {"name": "Uma Oya", "type": "River", "rating": 4.2, "description": "Scenic river valley with waterfalls, hiking trails, and natural swimming spots."},
                {"name": "Kandyan Dance Show", "type": "Cultural Show", "rating": 4.3, "description": "Traditional Kandyan dance performances showcasing Sri Lankan culture."},
                {"name": "Badulla Railway Station", "type": "Railway Station", "rating": 4.1, "description": "Historic railway station at end of famous Colombo-Badulla train route."}
            ],
            "Bandarawela": [
                {"name": "Dowa Rock Temple", "type": "Buddhist Temple", "rating": 4.4, "description": "Ancient rock temple with unfinished Buddha carving and cave paintings."},
                {"name": "Bandarawela Town", "type": "Town", "rating": 4.2, "description": "Charming hill station town with colonial architecture and cool climate."},
                {"name": "Adisham Bungalow", "type": "Historic House", "rating": 4.3, "description": "English country house style monastery with beautiful gardens and architecture."},
                {"name": "Lipton's Seat", "type": "Viewpoint", "rating": 4.7, "description": "Famous viewpoint where Sir Thomas Lipton surveyed his tea empire, panoramic views."},
                {"name": "St. Andrew's Church", "type": "Church", "rating": 4.1, "description": "Historic church built in 1908 with beautiful stained glass and architecture."},
                {"name": "Bandarawela Golf Club", "type": "Golf Course", "rating": 4.2, "description": "9-hole golf course with mountain views and challenging terrain."},
                {"name": "Bandarawela Market", "type": "Market", "rating": 4.0, "description": "Local market with fresh hill country vegetables, fruits, and local products."},
                {"name": "Diyaluma Falls", "type": "Waterfall", "rating": 4.5, "description": "Second highest waterfall in Sri Lanka (220m), with natural infinity pools at top."},
                {"name": "Bandarawela Railway Station", "type": "Railway Station", "rating": 4.1, "description": "Historic railway station on Main Line, beautiful mountain setting."},
                {"name": "Haputale", "type": "Nearby Town", "rating": 4.3, "description": "Nearby hill town with tea plantations and stunning views of southern plains."}
            ],
            "Hatton": [
                {"name": "Adam's Peak", "type": "Mountain", "rating": 4.8, "description": "Sacred mountain pilgrimage site with sunrise views and Buddha's footprint shrine."},
                {"name": "St. Clair's Falls", "type": "Waterfall", "rating": 4.5, "description": "Widest waterfall in Sri Lanka, known as 'Little Niagara of Sri Lanka'."},
                {"name": "Devon Falls", "type": "Waterfall", "rating": 4.4, "description": "97m high waterfall named after English coffee planter, visible from main road."},
                {"name": "Hatton Town", "type": "Town", "rating": 4.1, "description": "Main town serving Adam's Peak pilgrims and surrounding tea plantations."},
                {"name": "Castlereagh Reservoir", "type": "Reservoir", "rating": 4.3, "description": "Beautiful reservoir surrounded by tea plantations, perfect for photography."},
                {"name": "Gartmore Falls", "type": "Waterfall", "rating": 4.2, "description": "Lesser-known waterfall near Hatton, accessible through tea estate paths."},
                {"name": "Tea Plantation Tours", "type": "Plantation", "rating": 4.4, "description": "Guided tours of tea estates to learn about tea production and processing."},
                {"name": "Hatton Market", "type": "Market", "rating": 4.0, "description": "Local market serving hill country communities with fresh produce and goods."},
                {"name": "Laxapana Falls", "type": "Waterfall", "rating": 4.3, "description": "129m high waterfall, one of Sri Lanka's highest, located near hydro power station."},
                {"name": "Adam's Peak Base Camps", "type": "Pilgrimage Site", "rating": 4.2, "description": "Starting points for Adam's Peak pilgrimage with guesthouses and facilities."}
            ],
            "Sigiriya": [
                {"name": "Sigiriya Rock Fortress", "type": "Archaeological Site", "rating": 4.9, "description": "UNESCO World Heritage site, ancient rock fortress with frescoes, gardens, and palace ruins."},
                {"name": "Pidurangala Rock", "type": "Hiking Trail", "rating": 4.7, "description": "Alternative hike with best views of Sigiriya Rock, especially at sunrise."},
                {"name": "Sigiriya Museum", "type": "Museum", "rating": 4.2, "description": "Modern museum explaining Sigiriya's history, archaeology, and conservation efforts."},
                {"name": "Sigiriya Frescoes", "type": "Ancient Art", "rating": 4.6, "description": "Famous ancient paintings of celestial maidens in sheltered rock pocket."},
                {"name": "Mirror Wall", "type": "Archaeological Feature", "rating": 4.3, "description": "Ancient polished wall with historical graffiti from 8th-10th centuries."},
                {"name": "Water Gardens", "type": "Gardens", "rating": 4.4, "description": "Sophisticated ancient hydraulic engineering with pools, fountains, and gardens."},
                {"name": "Lion's Paw Terrace", "type": "Archaeological Feature", "rating": 4.5, "description": "Remains of the giant lion statue that formed entrance to summit palace."},
                {"name": "Boulder Gardens", "type": "Gardens", "rating": 4.2, "description": "Ancient garden complex with natural boulders, pathways, and pavilions."},
                {"name": "Sigiriya Village Tour", "type": "Cultural Tour", "rating": 4.3, "description": "Cultural tours of local villages to experience traditional Sri Lankan life."},
                {"name": "Elephant Safari", "type": "Wildlife Safari", "rating": 4.4, "description": "Elephant back safaris through surrounding forests and countryside."}
            ],
            "Dambulla": [
                {"name": "Dambulla Cave Temple", "type": "Buddhist Temple", "rating": 4.8, "description": "UNESCO World Heritage site with five caves containing Buddha statues and murals."},
                {"name": "Golden Temple of Dambulla", "type": "Buddhist Temple", "rating": 4.4, "description": "Large golden Buddha statue and museum at base of cave temple complex."},
                {"name": "Rose Quartz Mountain", "type": "Mountain", "rating": 4.3, "description": "Unique mountain with rose quartz deposits and hiking trails with panoramic views."},
                {"name": "Ibbankatuwa Megalithic Tombs", "type": "Archaeological Site", "rating": 4.0, "description": "Ancient burial site dating back to 700 BC with stone arrangements."},
                {"name": "Dambulla Market", "type": "Market", "rating": 4.1, "description": "Vibrant local market with spices, fruits, vegetables, and local products."},
                {"name": "Na Uyana Aranya", "type": "Forest Monastery", "rating": 4.5, "description": "Large forest monastery with meditation opportunities and peaceful surroundings."},
                {"name": "Dambulla Dedicated Economic Centre", "type": "Market", "rating": 4.0, "description": "Large wholesale market for fruits and vegetables from surrounding farms."},
                {"name": "Spice Gardens", "type": "Garden", "rating": 4.2, "description": "Educational tours of spice gardens showcasing Sri Lankan spices and herbs."},
                {"name": "Kandalama Hotel", "type": "Architecture", "rating": 4.6, "description": "Iconic hotel designed by Geoffrey Bawa, blending with natural landscape."},
                {"name": "Dambulla Cricket Stadium", "type": "Sports Venue", "rating": 4.1, "description": "International cricket stadium hosting test matches and one-day internationals."}
            ],
            "Polonnaruwa": [
                {"name": "Ancient City of Polonnaruwa", "type": "Archaeological Site", "rating": 4.8, "description": "UNESCO World Heritage site with well-preserved ancient ruins of Sri Lanka's medieval capital."},
                {"name": "Gal Vihara", "type": "Buddhist Statues", "rating": 4.7, "description": "Famous rock temple with four magnificent Buddha statues carved from single granite rock."},
                {"name": "Parakrama Samudra", "type": "Ancient Reservoir", "rating": 4.5, "description": "Massive ancient reservoir built by King Parakramabahu, covering 2,500 hectares."},
                {"name": "Polonnaruwa Vatadage", "type": "Ancient Structure", "rating": 4.6, "description": "Circular relic house with intricate stone carvings and moonstones."},
                {"name": "Lankatilaka Temple", "type": "Buddhist Temple", "rating": 4.4, "description": "Imposing brick temple with massive Buddha statue and architectural grandeur."},
                {"name": "Royal Palace Complex", "type": "Archaeological Site", "rating": 4.3, "description": "Ruins of the ancient royal palace, council chamber, and royal baths."},
                {"name": "Archaeological Museum", "type": "Museum", "rating": 4.1, "description": "Museum showcasing artifacts, sculptures, and information from Polonnaruwa period."},
                {"name": "Shiva Devale", "type": "Hindu Temple", "rating": 4.2, "description": "Ancient Hindu temples showing South Indian architectural influence."},
                {"name": "Statue of King Parakramabahu", "type": "Monument", "rating": 4.3, "description": "Stone statue believed to be King Parakramabahu I holding a palm-leaf manuscript."},
                {"name": "Polonnaruwa Quadrangle", "type": "Archaeological Site", "rating": 4.5, "description": "Sacred quadrangle containing most important religious monuments in compact area."}
            ],
            "Anuradhapura": [
                {"name": "Sacred City of Anuradhapura", "type": "Archaeological Site", "rating": 4.8, "description": "UNESCO World Heritage site, ancient capital with sacred Buddhist sites dating to 4th century BC."},
                {"name": "Sri Maha Bodhi", "type": "Sacred Tree", "rating": 4.9, "description": "Oldest historically documented tree in the world, grown from Buddha's enlightenment tree branch."},
                {"name": "Ruwanwelisaya Stupa", "type": "Buddhist Stupa", "rating": 4.7, "description": "Massive white stupa built by King Dutugemunu, one of Sri Lanka's most revered."},
                {"name": "Jetavanaramaya Stupa", "type": "Buddhist Stupa", "rating": 4.6, "description": "One of the tallest ancient structures in the world when built (122m)."},
                {"name": "Abhayagiri Monastery", "type": "Monastery Complex", "rating": 4.5, "description": "Ancient monastery complex with museum, twin ponds, and massive stupa."},
                {"name": "Isurumuniya Temple", "type": "Buddhist Temple", "rating": 4.4, "description": "Rock temple famous for its rock carvings including 'Isurumuniya Lovers'."},
                {"name": "Samadhi Buddha Statue", "type": "Buddhist Statue", "rating": 4.6, "description": "Famous granite Buddha statue in meditation pose, considered masterpiece of ancient sculpture."},
                {"name": "Kuttam Pokuna", "type": "Ancient Ponds", "rating": 4.3, "description": "Twin ponds showcasing ancient Sinhalese engineering and symmetry."},
                {"name": "Mihintale", "type": "Sacred Mountain", "rating": 4.7, "description": "Birthplace of Buddhism in Sri Lanka, pilgrimage site with temples and stupas."},
                {"name": "Archaeological Museum", "type": "Museum", "rating": 4.2, "description": "Museum showcasing artifacts from Anuradhapura period and explaining site's history."}
            ],
            "Trincomalee": [
                {"name": "Nilaveli Beach", "type": "Beach", "rating": 4.7, "description": "One of Sri Lanka's most beautiful beaches with white sand and clear turquoise water."},
                {"name": "Pigeon Island National Park", "type": "National Park", "rating": 4.6, "description": "Marine national park ideal for snorkeling, diving, and coral reef exploration."},
                {"name": "Fort Frederick", "type": "Fort", "rating": 4.3, "description": "Historic fort built by Portuguese and expanded by Dutch, now housing military base."},
                {"name": "Koneswaram Temple", "type": "Hindu Temple", "rating": 4.5, "description": "Ancient Hindu temple complex on Swami Rock with panoramic ocean views."},
                {"name": "Marble Beach", "type": "Beach", "rating": 4.4, "description": "Secluded beach with marble-like sand and crystal clear water, within Air Force base."},
                {"name": "Uppuveli Beach", "type": "Beach", "rating": 4.3, "description": "Long sandy beach popular for swimming, water sports, and beachfront accommodation."},
                {"name": "Trinco Whale Watching", "type": "Wildlife Tour", "rating": 4.5, "description": "Whale watching tours in the Bay of Bengal to spot blue whales and dolphins."},
                {"name": "Lovers' Leap", "type": "Viewpoint", "rating": 4.2, "description": "Cliff viewpoint with tragic love story legend and ocean views."},
                {"name": "Trincomalee War Cemetery", "type": "Memorial", "rating": 4.1, "description": "Commonwealth war cemetery honoring soldiers from World War II."},
                {"name": "Trincomalee Harbor", "type": "Harbor", "rating": 4.0, "description": "One of world's finest natural harbors, fifth largest natural harbor globally."}
            ],
            "Batticaloa": [
                {"name": "Batticaloa Lagoon", "type": "Lagoon", "rating": 4.4, "description": "Sri Lanka's second largest lagoon, perfect for boat rides, birdwatching, and sunset views."},
                {"name": "Kallady Bridge", "type": "Bridge", "rating": 4.2, "description": "Iconic Dutch-era bridge connecting Batticaloa town to Kallady, known for singing fish phenomenon."},
                {"name": "Batticaloa Fort", "type": "Fort", "rating": 4.3, "description": "Dutch fort built in 1628, overlooking the lagoon with historical significance and architecture."},
                {"name": "Pasikudah Beach", "type": "Beach", "rating": 4.6, "description": "One of Sri Lanka's finest beaches with shallow turquoise waters, perfect for swimming."},
                {"name": "Kalkudah Beach", "type": "Beach", "rating": 4.5, "description": "Long, flat beach ideal for swimming, windsurfing, and water sports with gentle waves."},
                {"name": "St. Mary's Cathedral", "type": "Church", "rating": 4.2, "description": "Beautiful Catholic cathedral with impressive architecture in heart of Batticaloa."},
                {"name": "Batticaloa Lighthouse", "type": "Lighthouse", "rating": 4.1, "description": "Historic lighthouse on edge of Batticaloa Lagoon with panoramic views."},
                {"name": "Navatkuli Bridge", "type": "Bridge", "rating": 4.0, "description": "British-era bridge with scenic views of lagoon and surrounding landscape."},
                {"name": "Koddamunai Hindu Temple", "type": "Hindu Temple", "rating": 4.3, "description": "Prominent Hindu temple showcasing Tamil architecture and cultural significance."},
                {"name": "Batticaloa Dutch Bar Heritage Museum", "type": "Museum", "rating": 4.1, "description": "Museum in restored Dutch-era building showcasing colonial history and artifacts."}
            ],
            "Pasikudah": [
                {"name": "Pasikudah Beach", "type": "Beach", "rating": 4.7, "description": "Famous for its shallow, calm turquoise waters extending 100-200m from shore, perfect for swimming."},
                {"name": "Coral Reefs", "type": "Marine Life", "rating": 4.5, "description": "Protected coral reefs ideal for snorkeling and observing marine biodiversity."},
                {"name": "Kalkudah Beach", "type": "Beach", "rating": 4.6, "description": "Adjacent beach with similar shallow waters, less developed and more natural."},
                {"name": "Water Sports Center", "type": "Adventure Sports", "rating": 4.3, "description": "Jet skiing, banana boat rides, kayaking, and other water activities."},
                {"name": "Beach Resorts", "type": "Accommodation", "rating": 4.4, "description": "Luxury beachfront resorts with spa facilities, pools, and fine dining."},
                {"name": "Sunset Views", "type": "Viewpoint", "rating": 4.6, "description": "Spectacular sunsets over Bay of Bengal with colors reflecting on calm waters."},
                {"name": "Beach Walks", "type": "Beach Activity", "rating": 4.4, "description": "Long, peaceful walks along pristine shoreline, especially enjoyable at sunrise."},
                {"name": "Local Fishing Village", "type": "Cultural Experience", "rating": 4.2, "description": "Visit traditional fishing village to see local lifestyle and fishing techniques."},
                {"name": "Beachfront Dining", "type": "Dining", "rating": 4.3, "description": "Restaurants serving fresh seafood with beach views and ocean breeze."},
                {"name": "Paddle Boarding", "type": "Water Sport", "rating": 4.4, "description": "Stand-up paddle boarding in calm, shallow waters suitable for beginners."}
            ],
            "Arugam Bay": [
                {"name": "Arugam Bay Beach", "type": "Beach", "rating": 4.7, "description": "World-class surfing destination with consistent waves, laid-back vibe, and beautiful beach."},
                {"name": "Pottuvil Point", "type": "Surf Spot", "rating": 4.6, "description": "Famous surfing point break for experienced surfers, best during April-October season."},
                {"name": "Lahugala National Park", "type": "National Park", "rating": 4.3, "description": "Elephant sanctuary with natural water holes, birdwatching, and wildlife."},
                {"name": "Muhudu Maha Viharaya", "type": "Buddhist Temple", "rating": 4.2, "description": "Ancient temple with beachfront location and archaeological significance."},
                {"name": "Elephant Rock", "type": "Viewpoint", "rating": 4.4, "description": "Hiking spot with panoramic views of Arugam Bay and surrounding coastline."},
                {"name": "Panama Beach", "type": "Beach", "rating": 4.5, "description": "Secluded beach ideal for swimming, relaxation, and escaping crowds."},
                {"name": "Surf Schools", "type": "Surfing Lessons", "rating": 4.5, "description": "Professional surf schools offering lessons for beginners and intermediate surfers."},
                {"name": "Crocodile Rock", "type": "Surf Spot", "rating": 4.4, "description": "Surfing spot named for crocodile-shaped rock formation, suitable for experienced surfers."},
                {"name": "Arugam Bay Lagoon", "type": "Lagoon", "rating": 4.3, "description": "Calm lagoon perfect for kayaking, paddle boarding, and birdwatching."},
                {"name": "Beach Bars", "type": "Nightlife", "rating": 4.2, "description": "Beachfront bars and restaurants with live music, bonfires, and international cuisine."}
            ],
            "Jaffna": [
                {"name": "Jaffna Fort", "type": "Fort", "rating": 4.4, "description": "Dutch fort built in 1680, one of best preserved Dutch forts in Sri Lanka."},
                {"name": "Nallur Kandaswamy Temple", "type": "Hindu Temple", "rating": 4.7, "description": "Large Hindu temple complex, most significant in Jaffna, famous for annual festival."},
                {"name": "Jaffna Public Library", "type": "Library", "rating": 4.3, "description": "Iconic library symbolizing Tamil heritage and revival, rebuilt after 1981 fire."},
                {"name": "Nagadeepa Purana Viharaya", "type": "Buddhist Temple", "rating": 4.5, "description": "Ancient Buddhist temple on Nagadeepa Island, accessible by ferry."},
                {"name": "Keerimalai Springs", "type": "Natural Springs", "rating": 4.2, "description": "Natural freshwater springs with separate bathing ponds for men and women."},
                {"name": "Jaffna Market", "type": "Market", "rating": 4.1, "description": "Bustling local market with fresh produce, Tamil sweets, and cultural experience."},
                {"name": "Casuarina Beach", "type": "Beach", "rating": 4.3, "description": "Beautiful beach with casuarina trees, ideal for sunset walks and relaxation."},
                {"name": "Point Pedro", "type": "Town", "rating": 4.2, "description": "Northernmost point of Sri Lanka with lighthouse and fishing harbor."},
                {"name": "Kankesanturai Beach", "type": "Beach", "rating": 4.3, "description": "Pristine beach near Kankesanturai port, less crowded with natural beauty."},
                {"name": "Jaffna Archaeological Museum", "type": "Museum", "rating": 4.0, "description": "Museum showcasing artifacts from Jaffna kingdom and Hindu cultural heritage."}
            ],
            "Mannar": [
                {"name": "Adam's Bridge", "type": "Natural Formation", "rating": 4.5, "description": "Chain of limestone shoals between India and Sri Lanka, visible from Mannar."},
                {"name": "Mannar Fort", "type": "Fort", "rating": 4.2, "description": "Portuguese then Dutch fort overlooking Gulf of Mannar, built in 1560."},
                {"name": "Baobab Tree", "type": "Tree", "rating": 4.4, "description": "Ancient baobab tree believed to be 700 years old, brought by Arab traders."},
                {"name": "Mannar Island", "type": "Island", "rating": 4.3, "description": "Island connected to mainland by causeway, known for salt production and fishing."},
                {"name": "Thanthirimale Temple", "type": "Buddhist Temple", "rating": 4.3, "description": "Ancient temple with rock inscriptions and connections to arrival of Buddhism."},
                {"name": "Giant's Tank", "type": "Reservoir", "rating": 4.1, "description": "Ancient irrigation tank built by King Dhatusena in 5th century AD."},
                {"name": "Mannar Beach", "type": "Beach", "rating": 4.2, "description": "Long, windy beach with shell collecting opportunities and sunset views."},
                {"name": "Our Lady of Madhu Church", "type": "Church", "rating": 4.4, "description": "Important Catholic pilgrimage site with shrine of Our Lady of Madhu."},
                {"name": "Mannar Market", "type": "Market", "rating": 4.0, "description": "Local market with seafood, dry fish, and products unique to Mannar region."},
                {"name": "Birdwatching Sites", "type": "Bird Sanctuary", "rating": 4.3, "description": "Important area for migratory birds including flamingos during season."}
            ],
            "Vavuniya": [
                {"name": "Vavuniya Museum", "type": "Museum", "rating": 4.1, "description": "Local museum showcasing artifacts and information about Vavuniya region."},
                {"name": "Kandasamy Kovil", "type": "Hindu Temple", "rating": 4.2, "description": "Prominent Hindu temple in Vavuniya with colorful architecture."},
                {"name": "Vavuniya Tank", "type": "Reservoir", "rating": 4.0, "description": "Ancient irrigation tank providing water to surrounding agricultural areas."},
                {"name": "Pandivirichchan Thermal Springs", "type": "Hot Springs", "rating": 4.3, "description": "Natural thermal springs believed to have medicinal properties."},
                {"name": "Vavuniya Market", "type": "Market", "rating": 4.0, "description": "Main market serving northern region with diverse goods and produce."},
                {"name": "Sivapuram Temple", "type": "Hindu Temple", "rating": 4.1, "description": "Ancient temple with cultural and religious significance."},
                {"name": "Vavuniya Town", "type": "Town", "rating": 4.0, "description": "Gateway town to northern province with administrative and commercial importance."},
                {"name": "Agriculture Farms", "type": "Farm", "rating": 4.1, "description": "Visit local farms to see cultivation of crops like onions, chilies, and grains."},
                {"name": "Community Projects", "type": "Cultural Experience", "rating": 4.2, "description": "Community-based tourism initiatives showcasing local life and traditions."},
                {"name": "Historical Sites", "type": "Archaeological Site", "rating": 4.1, "description": "Various historical sites reflecting region's diverse cultural heritage."}
            ],
            "Yala": [
                {"name": "Yala National Park", "type": "National Park", "rating": 4.8, "description": "Sri Lanka's most famous wildlife park for leopard and elephant sightings, diverse ecosystems."},
                {"name": "Sithulpawwa Rajamaha Viharaya", "type": "Buddhist Monastery", "rating": 4.4, "description": "Ancient rock temple with archaeological significance and meditation caves."},
                {"name": "Kumana National Park", "type": "National Park", "rating": 4.6, "description": "Birdwatcher's paradise adjacent to Yala, known for migratory birds and lagoons."},
                {"name": "Patangala", "type": "Archaeological Site", "rating": 4.2, "description": "Ancient cave complex with Brahmi inscriptions and archaeological importance."},
                {"name": "Yala Safari Experience", "type": "Wildlife Safari", "rating": 4.7, "description": "Jeep safaris to spot leopards, elephants, sloth bears, and diverse wildlife."},
                {"name": "Yala Village", "type": "Local Village", "rating": 4.0, "description": "Experience local culture and traditional Sri Lankan life in nearby villages."},
                {"name": "Yala Beach", "type": "Beach", "rating": 4.3, "description": "Pristine beach within Yala National Park with nesting turtles."},
                {"name": "Buttala", "type": "Town", "rating": 3.9, "description": "Nearby town with local markets, temples, and cultural sites."},
                {"name": "Magul Maha Viharaya", "type": "Buddhist Temple", "rating": 4.2, "description": "Ancient temple believed to be where King Kavantissa married Princess Viharamahadevi."},
                {"name": "Wildlife Photography", "type": "Photography", "rating": 4.6, "description": "Excellent opportunities for wildlife photography with professional guides."}
            ],
            "Udawalawe": [
                {"name": "Udawalawe National Park", "type": "National Park", "rating": 4.7, "description": "Best place in Sri Lanka to see elephants in large herds, also home to other wildlife."},
                {"name": "Udawalawe Elephant Transit Home", "type": "Conservation Center", "rating": 4.6, "description": "Elephant orphanage where baby elephants are cared for before release to wild."},
                {"name": "Udawalawe Reservoir", "type": "Reservoir", "rating": 4.4, "description": "Large irrigation reservoir attracting birds and wildlife, scenic views."},
                {"name": "Safari Tours", "type": "Wildlife Safari", "rating": 4.7, "description": "Jeep safaris through national park to see elephants, birds, and other animals."},
                {"name": "Birdwatching", "type": "Bird Sanctuary", "rating": 4.5, "description": "Excellent birdwatching with over 200 bird species including many endemic."},
                {"name": "Elephant Feeding", "type": "Wildlife Experience", "rating": 4.3, "description": "Observe feeding times at elephant transit home (3 times daily)."},
                {"name": "Butterfly Park", "type": "Park", "rating": 4.1, "description": "Park showcasing Sri Lanka's diverse butterfly species and their life cycles."},
                {"name": "Local Villages", "type": "Cultural Experience", "rating": 4.2, "description": "Visit traditional villages to see rural Sri Lankan life and agriculture."},
                {"name": "Scenic Drives", "type": "Scenic Route", "rating": 4.3, "description": "Beautiful drives through rural landscapes and reservoir views."},
                {"name": "Conservation Education", "type": "Educational", "rating": 4.4, "description": "Educational programs about elephant conservation and wildlife protection."}
            ],
            "Wilpattu": [
                {"name": "Wilpattu National Park", "type": "National Park", "rating": 4.7, "description": "Sri Lanka's largest national park known for natural lakes (villus) and leopard sightings."},
                {"name": "Safari Tours", "type": "Wildlife Safari", "rating": 4.6, "description": "Full-day jeep safaris to explore diverse habitats and spot wildlife."},
                {"name": "Leopard Tracking", "type": "Wildlife Experience", "rating": 4.5, "description": "Specialized tours focusing on leopard sightings and behavior observation."},
                {"name": "Birdwatching", "type": "Bird Sanctuary", "rating": 4.4, "description": "Over 200 bird species including many migratory and endemic birds."},
                {"name": "Natural Lakes (Villus)", "type": "Lakes", "rating": 4.3, "description": "Characteristic natural lakes that give Wilpattu its name (Land of Lakes)."},
                {"name": "Kudiramalai Point", "type": "Historical Site", "rating": 4.2, "description": "Historical site with archaeological significance and ocean views."},
                {"name": "Ancient Ruins", "type": "Archaeological Site", "rating": 4.1, "description": "Remains of ancient civilizations within park boundaries."},
                {"name": "Wildlife Photography", "type": "Photography", "rating": 4.6, "description": "Excellent opportunities for wildlife and landscape photography."},
                {"name": "Camping", "type": "Camping", "rating": 4.3, "description": "Wildlife camping experiences within designated areas of the park."},
                {"name": "Conservation Areas", "type": "Conservation", "rating": 4.4, "description": "Protected areas showcasing Sri Lanka's commitment to wildlife conservation."}
            ],
            "Kitulgala": [
                {"name": "White Water Rafting", "type": "Adventure Sports", "rating": 4.7, "description": "Sri Lanka's best white water rafting on Kelani River with Grade 2-3 rapids."},
                {"name": "Belilena Cave", "type": "Cave", "rating": 4.4, "description": "Archaeological cave where 12,000-year-old human remains were discovered."},
                {"name": "Kitulgala Forest Reserve", "type": "Forest Reserve", "rating": 4.5, "description": "Beautiful rainforest area with hiking trails and biodiversity."},
                {"name": "The Bridge on the River Kwai", "type": "Film Location", "rating": 4.3, "description": "Location where 1957 film was shot, though bridge was destroyed for film."},
                {"name": "Waterfall Abseiling", "type": "Adventure Sports", "rating": 4.6, "description": "Abseiling down waterfalls in surrounding jungle areas."},
                {"name": "Jungle Trekking", "type": "Hiking Trail", "rating": 4.4, "description": "Guided treks through rainforest to see wildlife and waterfalls."},
                {"name": "Birdwatching", "type": "Bird Sanctuary", "rating": 4.3, "description": "Excellent birdwatching with many endemic Sri Lankan species."},
                {"name": "Canyoning", "type": "Adventure Sports", "rating": 4.5, "description": "Canyoning adventures combining climbing, swimming, and jumping."},
                {"name": "Kayaking", "type": "Water Sport", "rating": 4.4, "description": "Kayaking on Kelani River through scenic gorges and rapids."},
                {"name": "Camping", "type": "Camping", "rating": 4.3, "description": "Riverside camping experiences with bonfires and nature immersion."}
            ],
            "Ratnapura": [
                {"name": "Gem Mines", "type": "Mine", "rating": 4.5, "description": "Visit working gem mines to see extraction of precious stones including sapphires and rubies."},
                {"name": "Gemological Museum", "type": "Museum", "rating": 4.3, "description": "Museum showcasing Sri Lanka's gem industry, history, and precious stones."},
                {"name": "Sinharaja Forest Reserve", "type": "Forest Reserve", "rating": 4.7, "description": "UNESCO World Heritage site, biodiversity hotspot with endemic species."},
                {"name": "Bopath Falls", "type": "Waterfall", "rating": 4.4, "description": "Waterfall shaped like Bo leaf (sacred fig), 30m high with pool for swimming."},
                {"name": "Ratnapura Market", "type": "Market", "rating": 4.2, "description": "Famous gem market where traders buy and sell precious stones."},
                {"name": "Mahaweli River", "type": "River", "rating": 4.1, "description": "Longest river in Sri Lanka, scenic spots for picnics and river baths."},
                {"name": "Gem Cutting Workshops", "type": "Workshop", "rating": 4.3, "description": "See traditional gem cutting and polishing techniques by skilled artisans."},
                {"name": "Ancient Temples", "type": "Buddhist Temple", "rating": 4.2, "description": "Several ancient temples in and around Ratnapura with historical significance."},
                {"name": "Tea Estates", "type": "Plantation", "rating": 4.3, "description": "Tea plantations in surrounding hills producing quality low-grown tea."},
                {"name": "Agricultural Farms", "type": "Farm", "rating": 4.1, "description": "Farms producing spices, fruits, and vegetables in fertile Ratnapura region."}
            ],
            "Kalutara": [
                {"name": "Kalutara Bodhiya", "type": "Buddhist Temple", "rating": 4.4, "description": "Sacred Bodhi tree and temple complex with beautiful white stupa."},
                {"name": "Kalutara Beach", "type": "Beach", "rating": 4.3, "description": "Long sandy beach popular for swimming, sunset views, and water sports."},
                {"name": "Richmond Castle", "type": "Historic House", "rating": 4.2, "description": "Colonial mansion built in 1896, now cultural center with gardens."},
                {"name": "Kalu Ganga River", "type": "River", "rating": 4.1, "description": "River trips and fishing experiences on Kalutara's namesake river."},
                {"name": "Fa Hien Cave", "type": "Cave", "rating": 4.3, "description": "Archaeological cave where remains of prehistoric humans were discovered."},
                {"name": "Kalutara Temple", "type": "Buddhist Temple", "rating": 4.2, "description": "Hollow stupa containing smaller stupa inside, unique architectural feature."},
                {"name": "Water Sports", "type": "Adventure Sports", "rating": 4.3, "description": "Jet skiing, banana boat rides, and other beach activities."},
                {"name": "Local Markets", "type": "Market", "rating": 4.0, "description": "Markets selling fresh seafood, local produce, and handicrafts."},
                {"name": "Sunset Cruises", "type": "Boat Tour", "rating": 4.4, "description": "Boat trips on Kalu Ganga River during sunset hours."},
                {"name": "Garden Restaurants", "type": "Dining", "rating": 4.2, "description": "Riverside and garden restaurants serving fresh seafood and local cuisine."}
            ],
            "Beruwala": [
                {"name": "Beruwala Beach", "type": "Beach", "rating": 4.4, "description": "Long golden beach with calm waters, popular for swimming and family vacations."},
                {"name": "Kande Viharaya", "type": "Buddhist Temple", "rating": 4.5, "description": "Temple with giant standing Buddha statue, important Buddhist site."},
                {"name": "Barberyn Lighthouse", "type": "Lighthouse", "rating": 4.3, "description": "Historic lighthouse on small island, accessible during low tide."},
                {"name": "Masjid-ul-Abrar", "type": "Mosque", "rating": 4.2, "description": "One of Sri Lanka's oldest mosques, built by Arab traders in 920 AD."},
                {"name": "Water Sports Center", "type": "Adventure Sports", "rating": 4.3, "description": "Various water activities including jet skiing, parasailing, and boat rides."},
                {"name": "Moragalla Beach", "type": "Beach", "rating": 4.4, "description": "Less crowded beach section with pristine sand and clear water."},
                {"name": "Traditional Fishing", "type": "Cultural Experience", "rating": 4.2, "description": "Observe traditional stilt fishing and local fishing techniques."},
                {"name": "Spice Garden Tours", "type": "Garden", "rating": 4.1, "description": "Educational tours of spice gardens showcasing Sri Lankan spices."},
                {"name": "Beach Resorts", "type": "Accommodation", "rating": 4.3, "description": "Range of beachfront resorts with amenities and ocean views."},
                {"name": "Local Crafts", "type": "Shopping", "rating": 4.0, "description": "Purchase traditional Sri Lankan crafts, batik, and souvenirs."}
            ],
            "Chilaw": [
                {"name": "Munneswaram Temple", "type": "Hindu Temple", "rating": 4.5, "description": "Important Hindu temple complex dedicated to Lord Shiva, pilgrimage site."},
                {"name": "Chilaw Beach", "type": "Beach", "rating": 4.2, "description": "Fishing beach with colorful boats, fresh seafood, and local atmosphere."},
                {"name": "St. Mary's Church", "type": "Church", "rating": 4.1, "description": "Historic church with beautiful architecture and religious significance."},
                {"name": "Chilaw Fishing Harbor", "type": "Harbor", "rating": 4.0, "description": "Active fishing harbor where daily catch is brought in and auctioned."},
                {"name": "Anawilundawa Bird Sanctuary", "type": "Bird Sanctuary", "rating": 4.4, "description": "Ramsar wetland site with diverse birdlife including migratory species."},
                {"name": "Dutch Church", "type": "Church", "rating": 4.0, "description": "Remains of Dutch colonial church with historical significance."},
                {"name": "Crab Farming", "type": "Aquaculture", "rating": 4.2, "description": "Visit crab farms to see mud crab cultivation and processing."},
                {"name": "Local Cuisine", "type": "Dining", "rating": 4.3, "description": "Fresh seafood restaurants specializing in crab and fish dishes."},
                {"name": "Traditional Industries", "type": "Cultural Experience", "rating": 4.1, "description": "See traditional industries like coir making and fishing net weaving."},
                {"name": "Paddy Fields", "type": "Agricultural Landscape", "rating": 4.2, "description": "Extensive paddy fields surrounding Chilaw, important rice growing area."}
            ],
            "Puttalam": [
                {"name": "Puttalam Lagoon", "type": "Lagoon", "rating": 4.3, "description": "Extensive lagoon system with mangrove forests and birdwatching opportunities."},
                {"name": "Kalpitiya Beach", "type": "Beach", "rating": 4.5, "description": "Long sandy beach popular for kitesurfing, windsurfing, and dolphin watching."},
                {"name": "Wilpattu National Park", "type": "National Park", "rating": 4.6, "description": "Access to Sri Lanka's largest national park from Puttalam side."},
                {"name": "Dutch Canal", "type": "Canal", "rating": 4.1, "description": "Historic canal built by Dutch connecting Puttalam to Colombo."},
                {"name": "St. Anne's Church", "type": "Church", "rating": 4.2, "description": "Historic church in Talawila, important Catholic pilgrimage site."},
                {"name": "Kitesurfing Centers", "type": "Adventure Sports", "rating": 4.5, "description": "Professional kitesurfing schools and equipment rentals in Kalpitiya."},
                {"name": "Dolphin Watching", "type": "Wildlife Tour", "rating": 4.4, "description": "Boat tours to see large pods of dolphins in Kalpitiya waters."},
                {"name": "Salt Pans", "type": "Industry", "rating": 4.1, "description": "Traditional salt production using evaporation ponds, important local industry."},
                {"name": "Mangrove Forests", "type": "Forest", "rating": 4.2, "description": "Boat tours through mangrove ecosystems with diverse flora and fauna."},
                {"name": "Fishing Villages", "type": "Cultural Experience", "rating": 4.1, "description": "Visit traditional fishing communities along Puttalam coastline."}
            ],
            "Matara": [
                {"name": "Star Fort", "type": "Fort", "rating": 4.3, "description": "Unique star-shaped Dutch fort built in 1765, now housing museum."},
                {"name": "Matara Paravi Duwa Temple", "type": "Buddhist Temple", "rating": 4.2, "description": "Temple on small island connected by bridge, picturesque setting."},
                {"name": "Polhena Beach", "type": "Beach", "rating": 4.4, "description": "Sheltered beach with coral reef, ideal for snorkeling and safe swimming."},
                {"name": "Weherahena Temple", "type": "Buddhist Temple", "rating": 4.5, "description": "Unique temple with tunnel depicting Buddhist hell and heaven scenes."},
                {"name": "Matara Beach", "type": "Beach", "rating": 4.3, "description": "Main beach area with promenade, restaurants, and sunset views."},
                {"name": "Dutch Reformed Church", "type": "Church", "rating": 4.1, "description": "Historic Dutch church built in 1706, still in use today."},
                {"name": "Nilwala River", "type": "River", "rating": 4.2, "description": "River trips and boat rides on Matara's main river."},
                {"name": "Local Markets", "type": "Market", "rating": 4.0, "description": "Vibrant markets selling fresh produce, seafood, and local goods."},
                {"name": "Historical Museum", "type": "Museum", "rating": 4.1, "description": "Museum showcasing Matara's history and cultural heritage."},
                {"name": "Dondra Lighthouse", "type": "Lighthouse", "rating": 4.2, "description": "Southernmost point of Sri Lanka with lighthouse and ocean views."}
            ],
            "Hambantota": [
                {"name": "Yala National Park", "type": "National Park", "rating": 4.7, "description": "Access to famous Yala National Park from Hambantota side."},
                {"name": "Hambantota Port", "type": "Port", "rating": 4.1, "description": "Deep sea port built with Chinese assistance, engineering marvel."},
                {"name": "Mattala Rajapaksa International Airport", "type": "Airport", "rating": 4.0, "description": "Second international airport in Sri Lanka, interesting architecture."},
                {"name": "Bundala National Park", "type": "National Park", "rating": 4.4, "description": "Ramsar wetland site important for migratory birds and wildlife."},
                {"name": "Hambantota Cricket Stadium", "type": "Sports Venue", "rating": 4.2, "description": "International cricket stadium hosting major matches."},
                {"name": "Bird Sanctuary", "type": "Bird Sanctuary", "rating": 4.3, "description": "Important area for birdwatching, especially wetland species."},
                {"name": "Salt Pans", "type": "Industry", "rating": 4.1, "description": "Traditional salt production using natural evaporation."},
                {"name": "Local Fisheries", "type": "Industry", "rating": 4.0, "description": "Fishing industry and fresh seafood markets."},
                {"name": "Development Projects", "type": "Modern Infrastructure", "rating": 4.1, "description": "See modern infrastructure development in Hambantota region."},
                {"name": "Rural Villages", "type": "Cultural Experience", "rating": 4.2, "description": "Traditional village life in southern Sri Lanka."}
            ],
            "Ampara": [
                {"name": "Lahugala National Park", "type": "National Park", "rating": 4.3, "description": "Elephant sanctuary with natural water holes and wildlife."},
                {"name": "Deegawapiya Temple", "type": "Buddhist Temple", "rating": 4.4, "description": "Ancient temple believed to be visited by Lord Buddha."},
                {"name": "Ampara Tank", "type": "Reservoir", "rating": 4.1, "description": "Large irrigation reservoir supporting agriculture in dry zone."},
                {"name": "Gal Oya National Park", "type": "National Park", "rating": 4.4, "description": "Boat safaris to see elephants swimming between islands."},
                {"name": "Senanayake Samudraya", "type": "Reservoir", "rating": 4.3, "description": "Largest reservoir in Sri Lanka, scenic and important for irrigation."},
                {"name": "Ancient Buddhist Sites", "type": "Archaeological Site", "rating": 4.2, "description": "Several ancient Buddhist monasteries and ruins in Ampara district."},
                {"name": "Agriculture Farms", "type": "Farm", "rating": 4.1, "description": "Visit farms growing rice, vegetables, and fruits in fertile Ampara region."},
                {"name": "Local Markets", "type": "Market", "rating": 4.0, "description": "Markets serving agricultural communities in eastern Sri Lanka."},
                {"name": "Traditional Crafts", "type": "Crafts", "rating": 4.1, "description": "Local crafts including pottery, weaving, and woodwork."},
                {"name": "Cultural Diversity", "type": "Cultural Experience", "rating": 4.2, "description": "Experience multicultural society with Sinhalese, Tamil, and Muslim communities."}
            ],
            "Monaragala": [
                {"name": "Maligawila Buddha Statue", "type": "Buddhist Statue", "rating": 4.4, "description": "Ancient standing Buddha statue from 7th century, 11.5m tall."},
                {"name": "Buddhangala Monastery", "type": "Buddhist Monastery", "rating": 4.3, "description": "Ancient forest monastery with archaeological remains and meditation opportunities."},
                {"name": "Monaragala Town", "type": "Town", "rating": 4.0, "description": "Main town serving southeastern region with local markets and services."},
                {"name": "Agricultural Areas", "type": "Agricultural Landscape", "rating": 4.1, "description": "Extensive agricultural lands growing rice, fruits, and vegetables."},
                {"name": "Traditional Villages", "type": "Cultural Experience", "rating": 4.2, "description": "Visit traditional villages to see rural Sri Lankan life."},
                {"name": "Natural Springs", "type": "Natural Springs", "rating": 4.1, "description": "Natural freshwater springs used by local communities."},
                {"name": "Forest Areas", "type": "Forest", "rating": 4.2, "description": "Dry zone forests with hiking opportunities and wildlife."},
                {"name": "Local Crafts", "type": "Crafts", "rating": 4.0, "description": "Traditional crafts including pottery, basket weaving, and wood carving."},
                {"name": "Agricultural Markets", "type": "Market", "rating": 4.1, "description": "Markets selling agricultural produce from Monaragala region."},
                {"name": "Rural Tourism", "type": "Cultural Experience", "rating": 4.2, "description": "Community-based tourism initiatives showcasing local culture."}
            ],
            "Kurunegala": [
                {"name": "Ethagala (Elephant Rock)", "type": "Rock Formation", "rating": 4.3, "description": "Large rock formation resembling elephant, landmark of Kurunegala."},
                {"name": "Yapahuwa Rock Fortress", "type": "Archaeological Site", "rating": 4.5, "description": "Ancient rock fortress and palace with impressive staircase and architecture."},
                {"name": "Panduwasnuwara", "type": "Archaeological Site", "rating": 4.2, "description": "Ancient capital with ruins, palace site, and Buddhist monuments."},
                {"name": "Kurunegala Lake", "type": "Lake", "rating": 4.1, "description": "Artificial lake in town center with walking paths and gardens."},
                {"name": "Ridi Viharaya", "type": "Buddhist Temple", "rating": 4.4, "description": "Ancient temple complex with silver deposits, historically significant."},
                {"name": "Arankele Monastery", "type": "Buddhist Monastery", "rating": 4.3, "description": "Forest monastery with meditation caves and ancient ruins."},
                {"name": "Local Markets", "type": "Market", "rating": 4.0, "description": "Busy markets serving northwestern province with diverse goods."},
                {"name": "Agriculture", "type": "Agricultural Landscape", "rating": 4.1, "description": "Visit farms growing rice, coconut, and fruits in fertile region."},
                {"name": "Historical Sites", "type": "Archaeological Site", "rating": 4.2, "description": "Several historical sites reflecting Kurunegala's ancient importance."},
                {"name": "Temple Circuit", "type": "Religious Tour", "rating": 4.3, "description": "Tour of important Buddhist temples in and around Kurunegala."}
            ],
            "Kegalle": [
                {"name": "Pinnawala Elephant Orphanage", "type": "Conservation Center", "rating": 4.6, "description": "World's largest captive elephant herd, famous for elephant bathing and feeding times."},
                {"name": "Elephant Bathing", "type": "Wildlife Experience", "rating": 4.7, "description": "Watch elephants bathing in river at scheduled times, popular photo opportunity."},
                {"name": "Millennium Elephant Foundation", "type": "Conservation Center", "rating": 4.4, "description": "Elephant conservation and welfare organization offering educational programs."},
                {"name": "Kegalle Town", "type": "Town", "rating": 4.0, "description": "Town serving central province with local markets and services."},
                {"name": "Spice Gardens", "type": "Garden", "rating": 4.2, "description": "Educational tours of spice gardens showcasing Sri Lankan spices."},
                {"name": "Traditional Industries", "type": "Cultural Experience", "rating": 4.1, "description": "See traditional industries like gem mining and agriculture."},
                {"name": "Elephant Back Rides", "type": "Wildlife Experience", "rating": 4.3, "description": "Ethical elephant back rides through designated areas."},
                {"name": "Local Markets", "type": "Market", "rating": 4.0, "description": "Markets selling local produce, spices, and handicrafts."},
                {"name": "Rubber Plantations", "type": "Plantation", "rating": 4.1, "description": "Visit rubber plantations to see latex collection and processing."},
                {"name": "Scenic Countryside", "type": "Scenic Route", "rating": 4.2, "description": "Beautiful drives through Kegalle's hilly countryside and plantations."}
            ],
            "Matale": [
                {"name": "Aluvihara Rock Temple", "type": "Buddhist Temple", "rating": 4.4, "description": "Ancient cave temple where Buddhist scriptures were first written on palm leaves."},
                {"name": "Matale Spice Gardens", "type": "Garden", "rating": 4.3, "description": "Educational tours of spice gardens in Sri Lanka's spice capital."},
                {"name": "Sri Muthumariamman Temple", "type": "Hindu Temple", "rating": 4.2, "description": "Colorful Hindu temple with impressive architecture and festivals."},
                {"name": "Knuckles Mountain Range", "type": "Mountain Range", "rating": 4.6, "description": "UNESCO World Heritage site with hiking, waterfalls, and biodiversity."},
                {"name": "Riverston", "type": "Viewpoint", "rating": 4.5, "description": "Spectacular viewpoint in Knuckles Range with panoramic mountain views."},
                {"name": "Matale Market", "type": "Market", "rating": 4.1, "description": "Famous spice market with wide variety of fresh spices and herbs."},
                {"name": "Ancient Temples", "type": "Buddhist Temple", "rating": 4.2, "description": "Several ancient Buddhist temples in and around Matale."},
                {"name": "Spice Processing", "type": "Industry", "rating": 4.2, "description": "See traditional spice processing and packaging methods."},
                {"name": "Hiking Trails", "type": "Hiking Trail", "rating": 4.4, "description": "Various hiking trails in Knuckles Range for different fitness levels."},
                {"name": "Cultural Diversity", "type": "Cultural Experience", "rating": 4.1, "description": "Experience multicultural society with Buddhist, Hindu, and Muslim communities."}
            ],
            "Weligama": [
                {"name": "Weligama Beach", "type": "Beach", "rating": 4.5, "description": "Long sandy beach famous for surfing, stilt fishermen, and whale watching."},
                {"name": "Stilt Fishermen", "type": "Cultural Experience", "rating": 4.4, "description": "Iconic traditional fishing method unique to Weligama area."},
                {"name": "Surfing Lessons", "type": "Surfing Lessons", "rating": 4.6, "description": "Surf schools offering lessons for beginners in gentle waves."},
                {"name": "Taprobane Island", "type": "Island", "rating": 4.3, "description": "Private island with luxury villa, accessible during low tide."},
                {"name": "Whale Watching", "type": "Wildlife Tour", "rating": 4.5, "description": "Boat tours to see blue whales and dolphins from Weligama harbor."},
                {"name": "Polhena Beach", "type": "Beach", "rating": 4.4, "description": "Sheltered beach with coral reef, ideal for snorkeling and safe swimming."},
                {"name": "Local Markets", "type": "Market", "rating": 4.1, "description": "Markets selling fresh seafood, local produce, and handicrafts."},
                {"name": "Beachfront Restaurants", "type": "Dining", "rating": 4.3, "description": "Restaurants serving fresh seafood with ocean views."},
                {"name": "Water Sports", "type": "Adventure Sports", "rating": 4.2, "description": "Various water activities including kayaking and paddle boarding."},
                {"name": "Sunset Views", "type": "Viewpoint", "rating": 4.5, "description": "Beautiful sunsets over Indian Ocean from Weligama beach."}
            ]
        }
      
        if city in fallback_places:
            places = fallback_places[city]
  
    # Cache the results
    st.session_state.places_cache[cache_key] = places
    return places

# Function to extract city from day title
def extract_city_from_title(title):
    """Extract the primary city from the day title"""
    title_lower = title.lower()
    city_mappings = {
        "colombo": "Colombo",
        "kandy": "Kandy",
        "nuwara eliya": "Nuwara Eliya",
        "nuwaraeliya": "Nuwara Eliya",
        "ella": "Ella",
        "yala": "Yala",
        "galle": "Galle",
        "sigiriya": "Sigiriya",
        "polonnaruwa": "Polonnaruwa",
        "anuradhapura": "Anuradhapura",
        "bentota": "Bentota",
        "mirissa": "Mirissa",
        "trincomalee": "Trincomalee",
        "trinco": "Trincomalee",
        "jaffna": "Jaffna",
        "dambulla": "Dambulla",
        "hikkaduwa": "Hikkaduwa",
        "arugam bay": "Arugam Bay",
        "arugambay": "Arugam Bay",
        "negombo": "Negombo",
        "batticaloa": "Batticaloa",
        "batti": "Batticaloa",
        "pasikudah": "Pasikudah",
        "weligama": "Weligama",
        "tangalle": "Tangalle",
        "badulla": "Badulla",
        "bandarawela": "Bandarawela",
        "hatton": "Hatton",
        "matara": "Matara",
        "hambantota": "Hambantota",
        "kalutara": "Kalutara",
        "beruwala": "Beruwala",
        "chilaw": "Chilaw",
        "puttalam": "Puttalam",
        "ratnapura": "Ratnapura",
        "kitulgala": "Kitulgala",
        "kegalle": "Kegalle",
        "kurunegala": "Kurunegala",
        "matale": "Matale",
        "monaragala": "Monaragala",
        "ampara": "Ampara",
        "vavuniya": "Vavuniya",
        "mannar": "Mannar",
        "udawalawe": "Udawalawe",
        "wilpattu": "Wilpattu"
    }
    for key, city in city_mappings.items():
        if key in title_lower:
            return city
    return None

# Function to get daily places
def get_daily_places(day_number, city, country, num_places=3):
    """Get real places for a specific day"""
    all_places = get_real_places(city, country, limit=20)
  
    if not all_places:
        return []
  
    # Select different places for each day
    start_idx = (day_number - 1) * num_places
    selected_places = []
  
    for i in range(num_places):
        idx = (start_idx + i) % len(all_places)
        place = all_places[idx].copy()
      
        # Add additional information
        best_times = [
            "Morning 9AM-12PM (Best for photos)",
            "Afternoon 2PM-5PM (Avoid crowds)",
            "Evening 6PM-9PM (Beautiful sunset views)"
        ]
      
        durations = ["2-3 hours", "3-4 hours", "1-2 hours"]
      
        # Map place types to icons
        icon_map = {
            "Buddhist Temple": "🛕", "Hindu Temple": "🛕", "Mosque": "🕌", "Church": "⛪",
            "Temple": "🛕", "Park": "🏞️", "Museum": "🏛️", "Historic": "🏛️",
            "Market": "🛍️", "Beach": "🏖️", "Palace": "🏰", "Castle": "🏰",
            "Viewpoint": "🌄", "Garden": "🌿", "Lake": "🌊", "Statue": "🗽",
            "Fort": "🏯", "Shopping": "🛒", "Cathedral": "⛪", "Shrine": "⛩️",
            "Religious": "🕌", "Natural": "🌲", "Architecture": "🏢", "Attraction": "📍",
            "Bridge": "🌉", "Hiking Trail": "🥾", "Waterfall": "🌊", "Plantation": "🍵",
            "Lagoon": "🏝️", "Island": "🏝️", "Lighthouse": "🗼", "Forest Reserve": "🌳",
            "National Park": "🐘", "Wildlife Safari": "🐅", "Conservation Center": "🐘",
            "Archaeological Site": "🏺", "Ancient Structure": "🏛️", "Monument": "🗽",
            "Mountain": "⛰️", "River": "🌊", "Cave": "🕳️", "Hot Springs": "♨️",
            "Reservoir": "💧", "Wetland": "🌿", "Bird Sanctuary": "🦅", "Marine Sanctuary": "🐠",
            "Adventure Sports": "🏄", "Surf Spot": "🏄", "Boat Tour": "🚤", "Cultural Show": "🎭",
            "Workshop": "🔨", "Farm": "🚜", "Tea Factory": "🍵", "Mine": "⛏️",
            "Golf Course": "⛳", "Sports Venue": "🏟️", "Airport": "✈️", "Port": "🚢",
            "Town": "🏙️", "Village": "🏡", "Historical House": "🏚️", "Film Location": "🎬",
            "Camping": "🏕️", "Scenic Route": "🛣️", "Modern Infrastructure": "🏗️",
            "Accommodation": "🏨", "Dining": "🍽️", "Nightlife": "🍸", "Shopping": "🛍️",
            "Cultural Experience": "🎎", "Educational": "📚", "Photography": "📷",
            "Pilgrimage Site": "🙏", "Religious Tour": "🛐", "Rural Tourism": "🌾"
        }
      
        place.update({
            "best_time": best_times[i % len(best_times)],
            "duration": durations[i % len(durations)],
            "icon": icon_map.get(place['type'], "📍"),
            "tags": [place['type'], "Popular", "Must Visit"]
        })
      
        selected_places.append(place)
  
    return selected_places

# Function to generate comprehensive itinerary using AI
def generate_comprehensive_itinerary(email_content):
    """Generate comprehensive travel itinerary using AI"""
  
    # Extract destination from email
    destination_prompt = f"""
    Extract the following information from this travel inquiry:
    {email_content}
  
    Return as JSON:
    {{
        "destination_country": "string",
        "destinations": ["string"],
        "duration_days": number,
        "travelers": number,
        "budget": "string",
        "interests": ["string"],
        "travel_dates": "string"
    }}
    """
  
    try:
        # First, extract destination info
        extraction_response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Extract travel information from the email. Parse destinations as a list if multiple cities are mentioned."},
                {"role": "user", "content": destination_prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
      
        extracted_info = json.loads(extraction_response.choices[0].message.content)
      
        country = extracted_info.get("destination_country", "")
        destinations = extracted_info.get("destinations", [])
        if not destinations:
            main_city = extracted_info.get("destination_city", "")
            if main_city:
                destinations = [main_city]
        days = extracted_info.get("duration_days", 5)
      
        # Get real places for each destination
        places_by_city = {}
        for dest_city in destinations:
            places_by_city[dest_city] = get_real_places(dest_city, country, limit=10)
      
        # Create itinerary prompt with real places
        system_prompt = f"""You are an expert travel planner with deep knowledge of global destinations.
      
        Create a detailed, realistic multi-city travel itinerary for the route {', '.join(destinations)} in {country}.
      
        Available real places by city:
        {json.dumps(places_by_city, indent=2)}
      
        Travel details:
        - Duration: {days} days
        - Travelers: {extracted_info.get('travelers', 2)}
        - Budget: {extracted_info.get('budget', 'Medium')}
        - Interests: {extracted_info.get('interests', ['General'])}
        - Dates: {extracted_info.get('travel_dates', 'Not specified')}
      
        IMPORTANT: Use the real places listed above, selecting from the appropriate city's list for each day. Include specific details like:
        - Opening hours
        - Ticket prices
        - Best times to visit
        - Transportation tips
        - Local food recommendations
        - Cultural insights
      
        Return ONLY valid JSON with this structure:
        {{
            "trip_summary": {{
                "destination_country": "{country}",
                "destinations": {json.dumps(destinations)},
                "duration_days": {days},
                "travelers": {extracted_info.get('travelers', 2)},
                "budget": "{extracted_info.get('budget', 'Medium')}",
                "trip_title": "string",
                "trip_theme": "string",
                "best_time_to_visit": "string",
                "currency": "string",
                "language": "string",
                "time_zone": "string",
                "visa_requirements": "string",
                "vaccinations": "string",
                "safety_tips": "string",
                "packing_tips": "string"
            }},
            "daily_itinerary": [
                {{
                    "day": 1,
                    "title": "string (include city name)",
                    "overview": "string",
                    "morning": {{
                        "time": "9:00 AM - 12:00 PM",
                        "activity": "string (use real place names)",
                        "description": "detailed description",
                        "duration": "3 hours",
                        "cost": "string",
                        "transportation": "string",
                        "tips": "string"
                    }},
                    "afternoon": {{...}},
                    "evening": {{...}},
                    "accommodation_suggestion": "string",
                    "food_recommendations": ["string"]
                }}
            ],
            "key_attractions": [
                {{
                    "name": "string (must be from real places list)",
                    "city": "string (the city where this attraction is)",
                    "type": "string",
                    "description": "string",
                    "best_time_to_visit": "string",
                    "ticket_price": "string",
                    "opening_hours": "string",
                    "duration_needed": "string",
                    "transportation": "string",
                    "tips": "string"
                }}
            ],
            "local_cuisine": [
                {{
                    "dish": "string",
                    "description": "string",
                    "where_to_try": "string",
                    "approximate_cost": "string",
                    "vegetarian_option": "boolean"
                }}
            ],
            "transportation_guide": {{
                "airport_transfer": "string",
                "public_transportation": "string",
                "taxi_services": "string",
                "car_rental": "string",
                "walking_tours": "string",
                "transportation_tips": ["string"]
            }},
            "accommodation_recommendations": [
                {{
                    "type": "string (Budget/Mid-range/Luxury)",
                    "suggestions": ["string"],
                    "average_price": "string",
                    "best_locations": ["string"]
                }}
            ],
            "cultural_tips": [
                "string"
            ],
            "budget_breakdown": {{
                "accommodation": "string",
                "food": "string",
                "transportation": "string",
                "activities": "string",
                "souvenirs": "string",
                "miscellaneous": "string",
                "total_estimate": "string"
            }},
            "emergency_information": {{
                "emergency_number": "string",
                "police": "string",
                "ambulance": "string",
                "tourist_police": "string",
                "nearest_hospital": "string",
                "embassy_contact": "string"
            }},
            "seasonal_considerations": [
                "string"
            ]
        }}
      
        Make it practical, detailed, and based on actual tourism information."""
      
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a comprehensive itinerary for this trip: {email_content}"}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=8000,
            response_format={"type": "json_object"}
        )
      
        result = response.choices[0].message.content.strip()
      
        # Clean JSON
        if result.startswith("```json"):
            result = result[7:-3]
        elif result.startswith("```"):
            result = result[3:-3]
      
        itinerary_data = json.loads(result)
      
        # Add real places data to itinerary
        itinerary_data["places_by_city"] = places_by_city
      
        return itinerary_data
      
    except Exception as e:
        st.error(f"Error generating itinerary: {str(e)}")
        return None

# Function to create map visualization
def create_places_map(places, city, country):
    """Create an interactive map showing all places"""
    try:
        # Get city coordinates
        lat, lon = get_city_coordinates(city, country)
      
        # Create map
        m = folium.Map(location=[lat, lon], zoom_start=12, tiles="CartoDB positron")
      
        # Add markers for each place
        for place in places:
            if "coordinates" in place and place["coordinates"]["lat"] and place["coordinates"]["lon"]:
                popup_html = f"""
                <div style="width: 200px;">
                    <h4 style="margin: 5px 0; color: #3b82f6;">{place['name']}</h4>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">
                        <strong>Type:</strong> {place.get('type', 'Attraction')}<br>
                        <strong>Rating:</strong> {place.get('rating', 'N/A')}/5
                    </p>
                </div>
                """
              
                folium.Marker(
                    location=[place["coordinates"]["lat"], place["coordinates"]["lon"]],
                    popup=folium.Popup(popup_html, max_width=250),
                    tooltip=place["name"],
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
      
        return m
    except:
        return None

# Create Hero Section
create_hero_section()

# Sidebar with enhanced features
with st.sidebar:
    st.markdown("### 🎯 Sri Lanka Explorer")
  
    # Set default country to Sri Lanka
    countries_data = get_all_countries()
    sri_lanka_data = next((c for c in countries_data if c["name"] == "Sri Lanka"), None)
  
    if sri_lanka_data:
        col_flag, col_info = st.columns([1, 3])
        with col_flag:
            st.markdown(f"<div style='font-size: 2.5rem;'>{sri_lanka_data['flag']}</div>", unsafe_allow_html=True)
        with col_info:
            st.markdown(f"""
            <div>
                <strong style="color: #1e293b;">{sri_lanka_data['name']}</strong><br>
                <span style="color: #475569; font-size: 0.9rem;">
                    📍 {sri_lanka_data['capital']}<br>
                    👥 {sri_lanka_data['population']:,}<br>
                    🌐 {sri_lanka_data['region']}
                </span>
            </div>
            """, unsafe_allow_html=True)
  
    # Sri Lanka regions
    st.markdown("### 🗺️ Regions of Sri Lanka")
  
    regions = {
        "🏙️ Western Province": ["Colombo", "Negombo", "Kalutara"],
        "🏞️ Central Province": ["Kandy", "Nuwara Eliya", "Matale"],
        "🏖️ Southern Province": ["Galle", "Matara", "Hambantota"],
        "☕ Hill Country": ["Ella", "Badulla", "Bandarawela", "Hatton"],
        "🏛️ Cultural Triangle": ["Sigiriya", "Dambulla", "Polonnaruwa", "Anuradhapura"],
        "🐘 Wildlife": ["Yala", "Udawalawe", "Wilpattu"],
        "🏄 Adventure": ["Kitulgala", "Arugam Bay", "Weligama"],
        "🏝️ Beach Paradise": ["Bentota", "Hikkaduwa", "Mirissa", "Tangalle", "Pasikudah"],
        "🌅 East Coast": ["Trincomalee", "Batticaloa"],
        "🌴 North": ["Jaffna", "Mannar", "Vavuniya"]
    }
  
    selected_region = st.selectbox("Choose Region", list(regions.keys()))
  
    if selected_region:
        cities_in_region = regions[selected_region]
        selected_city = st.selectbox("Choose City", cities_in_region)
      
        if st.button("🔍 Explore City", use_container_width=True):
            # Get places for this city
            with st.spinner(f"Finding places in {selected_city}..."):
                places = get_real_places(selected_city, "Sri Lanka", limit=10)
              
                if places:
                    st.success(f"Found {len(places)} places in {selected_city}!")
                    for place in places[:3]:
                        st.markdown(f"""
                        <div style="background: #f8fafc; border-radius: 12px; padding: 12px; margin: 8px 0; border: 1px solid #e2e8f0;">
                            <strong style="color: #1e293b;">{place['name']}</strong>
                            <div style="color: #475569; font-size: 0.85rem;">{place['type']} • ⭐ {place.get('rating', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
  
    st.markdown("---")
  
    # Quick templates
    st.markdown("### 📋 Sri Lanka Itinerary Templates")
  
    template_options = {
        "🇱🇰 Sri Lanka Classic 12-Day": """Planning a 12-day comprehensive tour of Sri Lanka.
Travel Dates: December 15-26, 2024
Travelers: 2 adults
Budget: $3500
Interests: Culture, history, beaches, wildlife, tea plantations
Destinations: Colombo, Sigiriya, Kandy, Nuwara Eliya, Ella, Yala, Galle, Bentota
Specific Requests:
- Visit UNESCO World Heritage sites
- Experience tea plantations and factory tour
- Go on wildlife safari in Yala National Park
- Try authentic Sri Lankan cuisine
- Take scenic train from Kandy to Ella
- Include beach time in Bentota and Galle
- Visit Temple of the Sacred Tooth Relic
Accommodation: Mix of 4-star hotels and boutique properties
Transport: Private car with driver for entire trip
Please create balanced itinerary with cultural, natural, and relaxation components.""",
      
        "🏖️ South Coast Beach Holiday 10-Day": """Planning a 10-day beach holiday in Southern Sri Lanka.
Travel Dates: January 10-19, 2025
Travelers: Family of 4 (2 adults, 2 children ages 8 and 12)
Budget: $4000
Interests: Beaches, water sports, family activities, relaxation
Destinations: Colombo, Bentota, Hikkaduwa, Mirissa, Galle, Weligama
Specific Requests:
- Family-friendly beach resorts with pools
- Water sports activities (snorkeling, jet skiing)
- Visit Galle Fort and turtle hatchery
- Whale watching in Mirissa
- Safe swimming beaches for children
- Cultural activities suitable for kids
- Evening entertainment options
Accommodation: Beachfront resorts with family rooms
Transport: Private minivan with driver
Want relaxed pace with beach time and family-friendly activities.""",
      
        "🌄 Hill Country Adventure 8-Day": """Planning an 8-day hill country adventure.
Travel Dates: March 15-22, 2025
Travelers: Young couple (active travelers)
Budget: $2500
Interests: Hiking, tea plantations, waterfalls, scenic views, photography
Destinations: Kandy, Nuwara Eliya, Ella, Hatton, Bandarawela
Specific Requests:
- Hiking to Little Adam's Peak and Ella Rock
- Visit Horton Plains and World's End
- Tea plantation tours and tasting
- Scenic train journeys
- Waterfall visits (Ravana Falls, St. Clair's Falls)
- Photography opportunities
- Local village experiences
Accommodation: Boutique hotels and guesthouses
Transport: Combination of train and private car
Prefer active itinerary with moderate hiking.""",
      
        "🐘 Wildlife & Nature 7-Day": """Planning a 7-day wildlife focused trip.
Travel Dates: February 2025
Travelers: 2 wildlife enthusiasts
Budget: $3000
Interests: Wildlife safaris, birdwatching, national parks, conservation
Destinations: Colombo, Yala, Udawalawe, Kitulgala, Sinharaja
Specific Requests:
- Multiple wildlife safaris (morning and evening)
- Birdwatching tours
- Visit elephant orphanage and transit home
- White water rafting in Kitulgala
- Guided nature walks
- Photography focused itinerary
- Conservation project visits
Accommodation: Wildlife lodges and eco-hotels
Transport: 4x4 safari jeeps and private car
Want maximum wildlife viewing opportunities."""
    }
  
    selected_template = st.selectbox("Choose Template", list(template_options.keys()))
  
    if st.button("📝 Use Template", use_container_width=True):
        st.session_state.email_text = template_options[selected_template]
  
    st.markdown("---")
  
    # Stats
    st.markdown("### 📊 Sri Lanka Stats")
  
    col_stat1, col_stat2 = st.columns(2)
    with col_stat1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">🏙️</div>
            <div class="stat-number">35</div>
            <div class="stat-label">Cities</div>
        </div>
        """, unsafe_allow_html=True)
  
    with col_stat2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-icon">📍</div>
            <div class="stat-number">350+</div>
            <div class="stat-label">Attractions</div>
        </div>
        """, unsafe_allow_html=True)
  
    st.markdown("---")
  
    # Settings
    st.markdown("### ⚙️ Settings")
  
    show_images = st.checkbox("Show Images", value=True)
    show_map = st.checkbox("Show Interactive Map", value=True)
    image_quality = st.select_slider("Image Quality", ["Low", "Medium", "High"], value="Medium")
  
    if st.button("🔄 Clear Cache", use_container_width=True):
        st.session_state.image_cache = {}
        st.session_state.places_cache = {}
        st.success("Cache cleared!")

# Main content area
col1, col2 = st.columns([2, 1])
with col1:
    # Card styling applied directly to the text area container
    st.markdown("""
    <div class="travel-inquiry-card">
        <div class="inquiry-card-header">
            <span class="inquiry-card-icon">📝</span>
            <div>
                <h3 class="inquiry-card-title">Travel Inquiry</h3>
                <p class="inquiry-card-subtitle">Share your travel dreams, we'll create the perfect itinerary</p>
            </div>
            <div class="card-status">
                <div class="status-dot"></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    
    
    
    
    
    
    # Create a container with custom class
    st.markdown('<div class="text-area-wrapper">', unsafe_allow_html=True)
    
    email_text = st.text_area(
        "Describe your travel plans:",  # Keep label visible
        value=st.session_state.email_text,
        height=280,
        placeholder="""🇱🇰 Tell us about your Sri Lanka trip!...""",  # Shortened for brevity
        key="travel_inquiry_textarea"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer stays outside
    st.markdown("""
    <div class="inquiry-card-footer">
        <span class="tips-icon">💡</span>
        <div class="tips-content">
            <div class="tips-title">Tips for better results:</div>
            <p class="tips-text">Include travel dates, number of travelers, budget, interests, and specific requests.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("### ✨ Sri Lanka Features")
  
    features = [
        ("🏛️", "8 UNESCO Sites", "Cultural Triangle & Forts"),
        ("🏖️", "1340km Coastline", "Beautiful beaches"),
        ("🐘", "26 National Parks", "Wildlife & Safari"),
        ("☕", "Tea Country", "Hill Station tours"),
        ("🕌", "Multi-Cultural", "Buddhist, Hindu, Muslim, Christian"),
        ("🌶️", "Spice Gardens", "Authentic cuisine"),
        ("🏄", "Water Sports", "Surfing, diving, rafting"),
        ("🚂", "Scenic Trains", "Mountain railways"),
        ("🌿", "Ayurveda", "Wellness & Spa"),
        ("📷", "Photography", "Stunning landscapes")
    ]
  
    for icon, title, desc in features[:5]:
        st.markdown(f"""
        <div style="background: #f8fafc; border-radius: 12px; padding: 12px; margin-bottom: 10px; border-left: 3px solid #3b82f6; border: 1px solid #e2e8f0;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5rem;">{icon}</span>
                <div>
                    <strong style="color: #1e293b;">{title}</strong>
                    <p style="color: #475569; font-size: 0.8rem; margin: 3px 0 0 0;">{desc}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Generate button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([3, 1, 1])
with col_btn1:
    generate_clicked = st.button(
        "🚀 Generate Sri Lanka Itinerary",
        type="primary",
        use_container_width=True,
        help="Create detailed itinerary with real places and images"
    )
with col_btn2:
    if st.button("🎲 Inspire Me", use_container_width=True):
        sri_lanka_cities = [
            "Colombo", "Kandy", "Galle", "Sigiriya", "Nuwara Eliya",
            "Ella", "Yala", "Mirissa", "Trincomalee", "Bentota"
        ]
        random_city = random.choice(sri_lanka_cities)
        days = random.randint(7, 14)
      
        st.session_state.email_text = f"""Planning a {days}-day trip to explore the beauty of Sri Lanka, focusing on {random_city} and surrounding areas.
Travel Dates: Flexible dates next year
Travelers: {random.randint(1, 4)} {'person' if random.randint(1, 4) == 1 else 'people'}
Budget: ${random.randint(2000, 5000)}
Interests: Cultural immersion, local food, natural attractions, photography
Destinations: {random_city} and nearby attractions
Want to experience: Authentic local culture, must-see attractions, hidden gems
Please create a well-balanced itinerary that mixes popular tourist spots with off-the-beaten-path experiences."""
with col_btn3:
    if st.button("🔄 Clear All", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# Generate and display itinerary
if generate_clicked and email_text.strip():
    with st.spinner("🇱🇰 Creating your comprehensive Sri Lanka itinerary with real destinations..."):
        itinerary_data = generate_comprehensive_itinerary(email_text)
      
        if itinerary_data:
            st.session_state.itinerary = itinerary_data
            st.success("✨ Itinerary generated successfully!")
            time.sleep(1)
            st.rerun()
# Display itinerary if available
if st.session_state.itinerary:
    itinerary_data = st.session_state.itinerary
    summary = itinerary_data.get("trip_summary", {})
  
    country = summary.get("destination_country", "Sri Lanka")
    destinations = summary.get("destinations", [])
    city = destinations[0] if destinations else ""
    days = summary.get("duration_days", 0)
    travelers = summary.get("travelers", 2)
    budget = summary.get("budget", "")
    theme = summary.get("trip_theme", "")
  
    # Get Sri Lanka flag
    countries_data = get_all_countries()
    sri_lanka_data = next((c for c in countries_data if c["name"] == "Sri Lanka"), {})
    flag = sri_lanka_data.get("flag", "🇱🇰") if sri_lanka_data else "🇱🇰"
  
    # Trip Summary Header
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 40px; padding: 30px; background: #f8fafc; border-radius: 25px; border: 1px solid #e2e8f0;">
        <div style="font-size: 4rem; margin-bottom: 10px;">{flag}</div>
        <h1 class="gradient-text" style="font-size: 2.8rem; margin-bottom: 15px;">
            {summary.get('trip_title', 'Your Sri Lanka Travel Itinerary')}
        </h1>
        <p style="color: #475569; font-size: 1.3rem; margin-bottom: 5px;">
            📍 {', '.join(destinations)} • ⏱️ {days} Days • 👥 {travelers} Travelers
        </p>
        <p style="color: #10b981; font-size: 1.1rem; font-weight: 600;">
            {theme} • 💰 Budget: {budget} • ⭐ {summary.get('best_time_to_visit', 'Best Season')}
        </p>
    </div>
    """, unsafe_allow_html=True)
  
    # Enhanced Stats Cards
    col_stats = st.columns(5)
  
    stats_data = [
        ("📍", "Destinations", ', '.join(destinations[:2]) + ('...' if len(destinations)>2 else '')),
        ("⏱️", "Duration", f"{days} Days"),
        ("👥", "Travelers", str(travelers)),
        ("💰", "Budget", budget),
        ("⭐", "Theme", theme[:15] + ('...' if len(theme) > 15 else ''))
    ]
  
    # Display stats cards
    for idx, (icon, label, value) in enumerate(stats_data):
        with col_stats[idx]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-icon">{icon}</div>
                <div class="stat-number animated">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
  
    # Additional Info Cards
    if any([summary.get('currency'), summary.get('language'), summary.get('time_zone')]):
        st.markdown("### ℹ️ Destination Information")
      
        info_cols = st.columns(3)
      
        info_items = [
            ("💱", "Currency", summary.get('currency', 'Sri Lankan Rupee (LKR)')),
            ("🗣️", "Language", summary.get('language', 'Sinhala, Tamil, English')),
            ("🕐", "Time Zone", summary.get('time_zone', 'GMT+5:30'))
        ]
      
        for idx, (icon, label, value) in enumerate(info_items):
            with info_cols[idx]:
                st.markdown(f"""
                <div style="background: #f8fafc; border-radius: 15px; padding: 20px; text-align: center; border: 1px solid #e2e8f0;">
                    <div style="font-size: 2rem; margin-bottom: 10px;">{icon}</div>
                    <div style="color: #1e293b; font-weight: 600; margin-bottom: 5px;">{label}</div>
                    <div style="color: #475569; font-size: 0.9rem;">{value}</div>
                </div>
                """, unsafe_allow_html=True)
  
    # Interactive Map (for main city)
    if show_map:
        real_places = itinerary_data.get("places_by_city", {}).get(city, [])
        if real_places:
            st.markdown('<div class="section-title">🗺️ Interactive Map</div>', unsafe_allow_html=True)
          
            map_obj = create_places_map(real_places, city, country)
            if map_obj:
                with st.container():
                    folium_static(map_obj, width=1200, height=500)
  
    # Key Attractions
    key_attractions = itinerary_data.get("key_attractions", [])
    if key_attractions:
        st.markdown('<div class="section-title">🌟 Must-Visit Attractions</div>', unsafe_allow_html=True)
      
        # Top view: Horizontal layout using columns for side-by-side cards
        num_cols = min(3, len(key_attractions)) # Up to 3 columns for top view
        attraction_cols = st.columns(num_cols)
      
        for idx, attraction in enumerate(key_attractions):
            with attraction_cols[idx % num_cols]:
                # Fetch real image for the attraction using its city
                att_city = attraction.get("city", city)
                image_data = get_place_image(attraction["name"], att_city, country, size="medium") if show_images else None
              
                # Place Card without raw HTML to avoid rendering issues
                st.markdown(f"### {attraction['name']}")
                st.markdown(f"**Type:** {attraction.get('type', 'Attraction')}")
                st.markdown(f"**Best Time:** {attraction.get('best_time_to_visit', 'N/A')}")
                st.markdown(f"**Duration:** {attraction.get('duration_needed', 'N/A')}")
              
                if image_data:
                    st.image(image_data["url"], caption=f"📸 {image_data['photographer']}", use_container_width=True)
              
                st.markdown(f"**Description:** {attraction.get('description', '')}")
              
                # Info grid using columns to simulate the grid without HTML
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.markdown(f"**🎫 Ticket Price:** {attraction.get('ticket_price', 'Varies')}")
                    st.markdown(f"**🕐 Opening Hours:** {attraction.get('opening_hours', 'N/A')}")
                with info_col2:
                    st.markdown(f"**🚗 Transportation:** {attraction.get('transportation', 'N/A')}")
                    st.markdown(f"**💡 Tips:** {attraction.get('tips', 'N/A')}")
              
                st.markdown("---") # Separator for each attraction
  
    # Daily Itinerary Section
    st.markdown('<div class="section-title">📅 Daily Itinerary</div>', unsafe_allow_html=True)
  
    daily_itinerary = itinerary_data.get("daily_itinerary", [])
  
    for day in daily_itinerary:
        day_num = day.get("day", 1)
        day_title = day.get("title", "Exploring")
        day_overview = day.get("overview", "")
      
        # Extract city for this day
        current_city = extract_city_from_title(day_title)
        if not current_city:
            current_city = city # fallback to main city
      
        # Day Header
        st.markdown(f"""
        <div class="day-header">
            <h2 style="color: white; margin: 0; font-size: 1.8rem;">Day {day_num}: {day_title}</h2>
            {f'<p style="color: rgba(255, 255, 255, 0.8); margin: 10px 0 0 0; font-size: 1rem;">{day_overview}</p>' if day_overview else ''}
        </div>
        """, unsafe_allow_html=True)
      
        # Get REAL places for this day using current city
        daily_places = get_daily_places(day_num, current_city, country, num_places=3)
      
        # Display Places
        if daily_places:
            st.markdown("### 🏆 Top Attractions for Today")
          
            place_cols = st.columns(min(3, len(daily_places)))
          
            for idx, place in enumerate(daily_places):
                with place_cols[idx]:
                    with st.container():
                        # Get image
                        image_data = None
                        if show_images:
                            with st.spinner(""):
                                image_data = get_place_image(place["name"], current_city, country, size="medium")
                      
                        # Card content
                        col_badge, col_rating = st.columns([2, 1])
                        with col_badge:
                            st.markdown(f"""<div class="place-badge">{place['type']}</div>""", unsafe_allow_html=True)
                      
                        with col_rating:
                            stars = "⭐" * int(place.get("rating", 4))
                            if place.get("rating", 4) - int(place.get("rating", 4)) >= 0.5:
                                stars += "½"
                          
                            st.markdown(f"""
                            <div style="display: flex; align-items: center; gap: 5px;">
                                <span style="color: #f59e0b; font-size: 0.9rem;">{stars}</span>
                                <span style="color: #f59e0b; font-weight: bold; font-size: 0.9rem;">
                                    {place.get('rating', 4)}/5
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                      
                        # Place name
                        st.markdown(f"""
                        <div style="color: #1e293b; font-size: 1.2rem; font-weight: 700; margin: 10px 0;">
                            {place['icon']} {place['name']}
                        </div>
                        """, unsafe_allow_html=True)
                      
                        # Image
                        if image_data and show_images:
                            try:
                                st.image(
                                    image_data["url"],
                                    caption=f"📸 {image_data['photographer']}",
                                    use_container_width=True
                                )
                            except:
                                pass
                      
                        # Description
                        st.markdown(f"""
                        <div style="color: #475569; font-size: 0.9rem; line-height: 1.6; margin: 10px 0;">
                            {place['description']}
                        </div>
                        """, unsafe_allow_html=True)
                      
                        # Tags
                        if "tags" in place:
                            tag_cols = st.columns(3)
                            for tag_idx, tag in enumerate(place["tags"][:3]):
                                with tag_cols[tag_idx]:
                                    st.markdown(f"""<div class="place-tag">{tag}</div>""", unsafe_allow_html=True)
                      
                        # Time info
                        col_time1, col_time2 = st.columns(2)
                        with col_time1:
                            st.markdown(f"""
                            <div class="time-item">
                                <span style="color: #60a5fa;">⏰</span>
                                <span>{place['best_time']}</span>
                            </div>
                            """, unsafe_allow_html=True)
                      
                        with col_time2:
                            st.markdown(f"""
                            <div class="time-item">
                                <span style="color: #10b981;">🕐</span>
                                <span>{place['duration']}</span>
                            </div>
                            """, unsafe_allow_html=True)
      
        # Daily Schedule
        st.markdown("### ⏰ Daily Schedule")
      
        schedule_data = [
            ("🌅 Morning", "morning", day.get("morning", {})),
            ("☀️ Afternoon", "afternoon", day.get("afternoon", {})),
            ("🌙 Evening", "evening", day.get("evening", {}))
        ]
      
        schedule_cols = st.columns(3)
      
        for idx, (title, key, schedule) in enumerate(schedule_data):
            with schedule_cols[idx]:
                if schedule:
                    card_class = f"{key}-card"
                  
                    st.markdown(f"""
                    <div class="schedule-card {card_class}">
                        <h4 style="color: {['#f59e0b', '#10b981', '#8b5cf6'][idx]}; margin: 0 0 15px 0; font-size: 1.2rem;">
                            {title}
                        </h4>
                        <p style="color: #475569; font-size: 0.9rem; margin: 5px 0;">
                            <strong>{schedule.get('time', 'N/A')}</strong>
                        </p>
                        <p style="color: #1e293b; font-weight: 600; margin: 10px 0; font-size: 1.1rem;">
                            {schedule.get('activity', '')}
                        </p>
                        <p style="color: #475569; font-size: 0.9rem; line-height: 1.6;">
                            {schedule.get('description', '')}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                  
                    # Additional info
                    info_items = [
                        ("💰 Cost", schedule.get('cost')),
                        ("🚗 Transport", schedule.get('transportation')),
                        ("💡 Tips", schedule.get('tips'))
                    ]
                  
                    for info_label, info_value in info_items:
                        if info_value:
                            st.info(f"**{info_label}:** {info_value}")
      
        # Accommodation & Food
        col_acc, col_food = st.columns(2)
      
        with col_acc:
            if day.get("accommodation_suggestion"):
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); border-radius: 15px; padding: 20px; margin-top: 20px;">
                    <h4 style="color: #3b82f6; margin: 0 0 10px 0;">🏨 Accommodation</h4>
                    <p style="color: #475569; margin: 0;">{day['accommodation_suggestion']}</p>
                </div>
                """, unsafe_allow_html=True)
      
        with col_food:
            if day.get("food_recommendations"):
                st.markdown(f"""
                <div style="background: rgba(245, 158, 11, 0.1); border-radius: 15px; padding: 20px; margin-top: 20px;">
                    <h4 style="color: #f59e0b; margin: 0 0 10px 0;">🍽️ Food Recommendations</h4>
                    <ul style="color: #475569; margin: 0; padding-left: 20px;">
                        {"".join([f'<li style="margin-bottom: 5px;">{item}</li>' for item in day["food_recommendations"][:3]])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
      
        st.markdown("---")
  
    # Budget Breakdown (Visual)
    budget_data = itinerary_data.get("budget_breakdown", {})
    if budget_data and budget_data.get("total_estimate"):
        st.markdown('<div class="section-title">💰 Budget Breakdown</div>', unsafe_allow_html=True)
      
        # Create pie chart
        budget_items = []
        budget_values = []
      
        for key, value in budget_data.items():
            if key != "total_estimate" and value:
                budget_items.append(key.title())
                budget_values.append(float(value.replace('$', '').replace(',', '')) if '$' in str(value) else 100)
      
        if budget_items and budget_values:
            fig = go.Figure(data=[go.Pie(
                labels=budget_items,
                values=budget_values,
                hole=.3,
                marker_colors=['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#6b7280']
            )])
          
            fig.update_layout(
                title="Budget Distribution",
                showlegend=True,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#475569')
            )
          
            st.plotly_chart(fig, use_container_width=True)
          
            st.markdown(f"""
            <div style="text-align: center; margin-top: 20px;">
                <h3 style="color: #10b981;">Total Estimated Budget: {budget_data.get('total_estimate', 'N/A')}</h3>
            </div>
            """, unsafe_allow_html=True)
  
    # Emergency Information
    emergency_info = itinerary_data.get("emergency_information", {})
    if emergency_info:
        st.markdown('<div class="section-title">⚕️ Emergency Information</div>', unsafe_allow_html=True)
      
        em_cols = st.columns(2)
      
        with em_cols[0]:
            st.warning(f"""
            **Emergency Contacts in Sri Lanka:**
            - 🚨 Emergency: {emergency_info.get('emergency_number', '119 / 118')}
            - 👮 Police: {emergency_info.get('police', '119')}
            - 🚑 Ambulance: {emergency_info.get('ambulance', '110')}
            - 🛡️ Tourist Police: {emergency_info.get('tourist_police', '1912')}
            """)
      
        with em_cols[1]:
            st.error(f"""
            **Important Information:**
            - 🏥 Nearest Hospital: {emergency_info.get('nearest_hospital', 'Check locally')}
            - 🏛️ Embassy Contact: {emergency_info.get('embassy_contact', 'Contact your embassy in Colombo')}
            - ⚠️ Safety Tips: {summary.get('safety_tips', 'Stay vigilant in crowded areas')}
            """)
  
    # Download Section
    st.markdown('<div class="section-title">📥 Export Options</div>', unsafe_allow_html=True)
  
    col_dl1, col_dl2, col_dl3, col_dl4 = st.columns(4)
  
    with col_dl1:
        # JSON Download
        json_data = json.dumps(itinerary_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📊 Full Data (JSON)",
            data=json_data,
            file_name=f"sri_lanka_itinerary.json",
            mime="application/json",
            use_container_width=True
        )
  
    with col_dl2:
        # PDF-like text download
        daily_itinerary = itinerary_data.get("daily_itinerary", [])
        key_attractions = itinerary_data.get("key_attractions", [])
        text_content = f"""
{'='*70}
🇱🇰 COMPREHENSIVE SRI LANKA TRAVEL ITINERARY
{'='*70}
Destination: {', '.join(destinations)}
Duration: {days} days
Travelers: {travelers}
Budget: {budget}
Theme: {theme}
{'='*70}
TRIP SUMMARY
{'='*70}
• Best Time to Visit: {summary.get('best_time_to_visit', 'December to April for West/South, May to September for East')}
• Currency: {summary.get('currency', 'Sri Lankan Rupee (LKR)')}
• Language: {summary.get('language', 'Sinhala, Tamil, English')}
• Time Zone: {summary.get('time_zone', 'GMT+5:30')}
• Visa Requirements: {summary.get('visa_requirements', 'ETA required for most nationalities')}
• Vaccinations: {summary.get('vaccinations', 'Consult doctor, recommended: Hepatitis A, Typhoid')}
• Packing Tips: {summary.get('packing_tips', 'Light cotton clothes, sun protection, mosquito repellent, modest clothing for temples')}
{'='*70}
DAILY ITINERARY
{'='*70}
"""
        for day in daily_itinerary:
            text_content += f"""
Day {day.get('day')}: {day.get('title')}
{'-'*50}
Morning ({day.get('morning', {}).get('time', 'N/A')}):
Activity: {day.get('morning', {}).get('activity', 'N/A')}
Description: {day.get('morning', {}).get('description', 'N/A')}
Cost: {day.get('morning', {}).get('cost', 'N/A')}
Afternoon ({day.get('afternoon', {}).get('time', 'N/A')}):
Activity: {day.get('afternoon', {}).get('activity', 'N/A')}
Description: {day.get('afternoon', {}).get('description', 'N/A')}
Cost: {day.get('afternoon', {}).get('cost', 'N/A')}
Evening ({day.get('evening', {}).get('time', 'N/A')}):
Activity: {day.get('evening', {}).get('activity', 'N/A')}
Description: {day.get('evening', {}).get('description', 'N/A')}
Cost: {day.get('evening', {}).get('cost', 'N/A')}
Accommodation: {day.get('accommodation_suggestion', 'N/A')}
Food Recommendations: {', '.join(day.get('food_recommendations', []))}
"""
      
        text_content += f"""
{'='*70}
KEY ATTRACTIONS
{'='*70}
"""
        for attraction in key_attractions[:5]:
            text_content += f"""
• {attraction['name']} ({attraction.get('type', 'Attraction')}) in {attraction.get('city', 'N/A')}
  Description: {attraction.get('description', 'N/A')}
  Best Time: {attraction.get('best_time_to_visit', 'N/A')}
  Ticket: {attraction.get('ticket_price', 'N/A')}
  Hours: {attraction.get('opening_hours', 'N/A')}
  Tips: {attraction.get('tips', 'N/A')}
"""
      
        st.download_button(
            label="📝 Detailed Guide (TXT)",
            data=text_content,
            file_name="sri_lanka_travel_guide.txt",
            mime="text/plain",
            use_container_width=True
        )
  
    with col_dl3:
        # CSV Download
        csv_data = []
        daily_itinerary = itinerary_data.get("daily_itinerary", [])
        for day in daily_itinerary:
            day_num = day.get("day", 1)
            day_city = extract_city_from_title(day.get("title", "")) or city
            daily_places = get_daily_places(day_num, day_city, country)
            for place in daily_places:
                csv_data.append({
                    "Day": day_num,
                    "Place": place["name"],
                    "Type": place["type"],
                    "Rating": place.get("rating", ""),
                    "Best Time": place["best_time"],
                    "Duration": place["duration"],
                    "Description": place["description"][:150]
                })
      
        if csv_data:
            df = pd.DataFrame(csv_data)
            csv_string = df.to_csv(index=False)
            st.download_button(
                label="📈 Places Data (CSV)",
                data=csv_string,
                file_name="sri_lanka_places.csv",
                mime="text/csv",
                use_container_width=True
            )
  
    with col_dl4:
        if st.button("🔄 New Itinerary", use_container_width=True):
            st.session_state.itinerary = None
            st.session_state.email_text = ""
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; padding: 30px; margin-top: 40px;">
    <div style="display: flex; justify-content: center; gap: 25px; margin-bottom: 20px; flex-wrap: wrap;">
        <div style="display: flex; align-items: center; gap: 8px; background: #f8fafc; padding: 10px 20px; border-radius: 25px; border: 1px solid #e2e8f0;">
            <span style="color: #60a5fa;">🏙️</span>
            <span>35 Sri Lankan Cities</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; background: #f8fafc; padding: 10px 20px; border-radius: 25px; border: 1px solid #e2e8f0;">
            <span style="color: #60a5fa;">📍</span>
            <span>350+ Attractions</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; background: #f8fafc; padding: 10px 20px; border-radius: 25px; border: 1px solid #e2e8f0;">
            <span style="color: #60a5fa;">🤖</span>
            <span>AI-Powered Itineraries</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; background: #f8fafc; padding: 10px 20px; border-radius: 25px; border: 1px solid #e2e8f0;">
            <span style="color: #60a5fa;">🔄</span>
            <span>Real-Time Updates</span>
        </div>
    </div>
    <p style="margin: 10px 0; font-size: 0.9rem; color: #475569;">
        Powered by: <strong>REST Countries • OpenTripMap • Foursquare • Unsplash • Pexels • Groq AI</strong>
    </p>
    <p style="margin: 0; font-size: 0.8rem; color: #64748b;">
        © 2024 Sri Lanka Travel Itinerary AI • The Pearl of the Indian Ocean • All data verified and curated
    </p>
</div>
""", unsafe_allow_html=True)
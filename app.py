#!/usr/bin/env python3
"""
Render Deployment Entry Point for Graph-Reasoned USL System
"""

import os
import sys
import streamlit as st

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the complete system
from complete_usl_system import main

if __name__ == "__main__":
    # Set Streamlit configuration for deployment
    st.set_page_config(
        page_title="USL Medical Translator - 99.2% Accuracy",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Run the main application
    main()
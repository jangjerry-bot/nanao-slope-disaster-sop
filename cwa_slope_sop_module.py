import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
from pathlib import Path
import urllib3

# 忽略政府憑證偶發之 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 0. 延續邊坡口卡系統 style.py 之動畫與手機端放大 CSS
# ==========================================
def inject_custom_style_and_banner():
    """
    注入專為手機端優化的放大字體、高對比毛玻璃卡片，以及開頭動態雷達橫幅 (style.py 風格)
    """
    st.markdown("""
    <style>
        /* 全域字體與手機端觸控優化 */
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", Roboto, sans-serif;
            font-size: 18px !important;
        }
        .block-container {
            padding-top: 2rem !important; /* 增加頂部安全距離，避免被頁面頂端裁切 */
            padding-bottom: 3rem !important;
            max-width: 960px !important;
        }

        /* 下拉選單 (Selectbox) 與輸入框字體全面放大，方便現場單手操作 */
        div[data-baseweb="select"] > div {
            min-height: 52px !important;
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            background-color: #1e293b !important;
            border: 2px solid #38bdf8 !important;
            border-radius: 12px !important;
            color: #ffffff !important;
        }
        label[data-testid="stWidgetLabel"] p {
            font-size: 1.1rem !important;
            font-weight: 700 !important;
            color: #cbd5e1 !important;
        }

        /* 動態視覺橫幅動畫 (Keyframes) */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes radarPulse {
            0% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.8); transform: scale(0.95); }
            70% { box-shadow: 0 0 0 14px rgba(245, 158, 11, 0); transform: scale(1.05); }
            100% { box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); transform: scale(0.95); }
        }
        @keyframes slideDownFade {
            0% { opacity: 0; transform: translateY(-18px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes scanLine {
            0% { transform: translateX(-100%);

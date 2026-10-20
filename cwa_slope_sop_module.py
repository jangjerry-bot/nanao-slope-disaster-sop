import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
from pathlib import Path
import urllib3

# 忽略政府憑證偶發之 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 0. 動態雷達視覺橫幅與手機端高可視性 CSS
# ==========================================
def inject_custom_style_and_banner():
    st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Microsoft JhengHei", Roboto, sans-serif;
            font-size: 18px !important;
        }
        .block-container {
            padding-top: 2rem !important; 
            padding-bottom: 3rem !important;
            max-width: 980px !important;
        }

        /* 下拉選單與輸入框字體全面放大，支援手機單手操作 */
        div[data-baseweb="select"] > div {
            min-height: 52px !important;
            font-size: 1.12rem !important;
            font-weight: 700 !important;
            background-color: #1e293b !important;
            border: 2px solid #38bdf8 !important;
            border-radius: 12px !important;
            color: #ffffff !important;
        }
        label[data-testid="stWidgetLabel"] p {
            font-size: 1.08rem !important;
            font-weight: 700 !important;
            color: #cbd5e1 !important;
        }

        /* 動態視覺橫幅動畫 */
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        @keyframes radarPulse {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.85); transform: scale(0.95); }
            70% { box-shadow: 0 0 0 14px rgba(16, 185, 129, 0); transform: scale(1.05); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); transform: scale(0.95); }
        }
        @keyframes slideDownFade {
            0% { opacity: 0; transform: translateY(-18px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes scanLine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .hero-banner {
            position: relative;
            overflow: hidden;
            background: linear-gradient(-45deg, #0f172a, #1e3a8a, #0f766e, #1e293b);
            background-size: 300% 300%;
            animation: gradientBG 10s ease infinite;
            border-radius: 18px;
            padding: 28px 22px 22px 22px; 
            border: 1px solid rgba(56, 189, 248, 0.4);
            box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.6);
            margin-top: 15px; 
            margin-bottom: 14px;
        }
        .hero-banner::after {
            content: "";
            position: absolute;
            top: 0; left: 0; width: 100%; height: 3px;
            background: linear-gradient(90deg, transparent, #38bdf8, #f59e0b, transparent);
            animation: scanLine 3.5s linear infinite;
        }
        .radar-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid #10b981;
            color: #6ee7b7;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .radar-dot {
            width: 10px;
            height: 10px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            animation: radarPulse 1.8s infinite;
        }
        .hero-title {
            font-size: 1.65rem !important;
            font-weight: 900 !important;
            color: #ffffff !important;
            line-height: 1.3 !important;
            margin: 0 0 10px 0 !important;
            letter-spacing: 0.5px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }
        .hero-subtitle {
            font-size: 0.95rem !important;
            color: #e2e8f0 !important;
            line-height: 1.45 !important;
            font-weight: 600;
            background: rgba(15, 23, 42, 0.6);
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 4px solid #38bdf8;
        }

        /* 手機端重點放大卡片 */
        .mobile-card {
            background: #1e293b;
            border-radius: 16px;
            padding: 18px;
            margin-bottom: 14px;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 6px 16px rgba(0,0,0,0.35);
        }
        .card-safe { border-left: 8px solid #10b981; }
        .card-warn { border-left: 8px solid #f59e0b; }
        .card-danger { border-left: 8px solid #ef4444; background: linear-gradient(145deg, #1e293b, #311018); }

        .big-number {
            font-size: 2.1rem;
            font-weight: 900;
            line-height: 1.1;
            color: #ffffff;
        }
        .sop-action-box {
            background: rgba(15, 23, 42, 0.88);
            border-radius: 12px;
            padding: 12px 14px;
            margin-top: 10px;
            font-size: 1.08rem;
            font-weight: 700;
            line-height: 1.5;
            color: #fef08a;
            border: 1px solid rgba(250, 204, 21, 0.35);
        }
        .sop-mgmt-box {
            background: rgba(6, 78, 59, 0.45);
            border-radius: 12px;
            padding: 10px 14px;
            margin-top: 8px;
            font-size: 1.02rem;
            font-weight: 700;
            color: #6ee7b7;
            border: 1px solid rgba(16, 185, 129, 0.35);
        }
        .link-btn {
            display: inline-block;
            background: #0284c7;
            color: #ffffff !important;
            font-weight: 800;
            font-size: 0.92rem;
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none !important;
            text-align: center;
            border: 1px solid #38bdf8;
        }
        .link-btn-sec {
            display: inline-block;
            background: #334155;
            color: #e2e8f0 !important;
            font-weight: 700;
            font-size: 0.92rem;
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none !important;
            text-align: center;
            border: 1px solid #64748b;
        }
    </style>

    <div class="hero-banner">
        <div class="radar-badge">
            <span class="radar-dot"></span> 中央氣象署 Open Data API 即時連線 × 115年最新邊坡檢查機制
        </div>
        <div class="hero-title">蘇花廊道災變暨邊坡巡查自動化決策系統</div>
        <div class="hero-subtitle">
            法規依據：路養護字第1155009531號函(115年5月修訂)｜雨量分析邏輯：採用【區域測站群組最大值包絡法】
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# 1. 核心常數、API 金鑰與蘇花五大防區群組定義
# ==========================================
try:
    DEFAULT_CWA_API_KEY = st.secrets.get("CWA_API_KEY", "CWA-E9410456-F2F6-489C-BD69-8C45B13EBEFD")
except Exception:
    DEFAULT_CWA_API_KEY = "CWA-E9410456-F2F6-489C-BD69-8C45B13EBEFD"

REGIONAL_GROUPS = {
    "蘇澳地區": ["蘇澳", "馬賽", "永樂", "白米", "南方澳", "北方澳"],
    "東澳地區": ["東澳", "東澳嶺", "粉鳥林", "西帽山"],
    "南澳地區": ["南澳", "朝陽", "碧候", "金洋", "古魯", "鹿皮"],
    "武塔觀音漢本區": ["武塔", "觀音", "澳花", "漢本", "大濁水"],
    "和平崇德地區": ["和平", "和中", "和仁", "崇德", "太魯閣", "清水", "富世", "布洛灣"]
}

SEISMIC_RANK = {"0級": 0, "1級": 1, "2級": 2, "3級": 3, "4級": 4, "5弱": 5, "5強": 6, "6弱": 7, "6強": 8, "7級": 9}
RANK_TO_SEISMIC = {v: k for k, v in SEISMIC_RANK.items()}

# 完整涵蓋近 10 年 (2016 ~ 2026) 蘇花廊道重大地震、颱風、豪雨事件庫
DEFAULT_DISASTER_HISTORY = [
    {"date": "2026-09-20", "type": "地震", "name": "0920 南澳外海地震 (M5.6)", "max_seismic": "4級", "max_rain_3h": 0.0, "max_rain_48h": 10.0, "region": "南澳地區", "collapse_m3": 0, "note": "震度達4級，觸發優先關注邊坡(A、B級RHRS中高風險)立即特別巡查"},
    {"date": "2026-05-12", "type": "豪雨", "name": "0512 梅雨滯留鋒面劇烈豪雨", "max_seismic": "0級", "max_rain_3h": 130.0, "max_rain_48h": 365.0, "region": "東澳地區", "collapse_m3": 0, "note": "115年汛期首波達標豪雨，東澳嶺3hr與48hr雙雙突破門檻，A級邊坡14日特檢"},
    {"date": "2025-11-18", "type": "豪雨", "name": "1118 東北季風共伴超大豪雨", "max_seismic": "0級", "max_rain_3h": 142.0, "max_rain_48h": 460.0, "region": "東澳地區", "collapse_m3": 1200, "note": "典型秋冬地形鎖水效應，啟動A級邊坡14日內特檢與降低雨量門檻"},
    {"date": "2025-08-13", "type": "颱風", "name": "楊柳颱風外圍環流強降雨", "max_seismic": "0級", "max_rain_3h": 135.0, "max_rain_48h": 390.0, "region": "南澳地區", "collapse_m3": 0, "note": "短延時強降雨突破120mm/3hr，揭露強降雨訊息並於2日內特巡"},
    {"date": "2024-10-31", "type": "颱風", "name": "康芮颱風東部超大豪雨", "max_seismic": "0級", "max_rain_3h": 160.0, "max_rain_48h": 680.0, "region": "和平崇德地區", "collapse_m3": 8500, "note": "海警解除後全線特巡，坍方逾5,000m³路段強制升級比照A級列管"},
    {"date": "2024-07-24", "type": "颱風", "name": "凱米颱風強降雨致災", "max_seismic": "0級", "max_rain_3h": 185.0, "max_rain_48h": 820.0, "region": "和平崇德地區", "collapse_m3": 25000, "note": "0403震後首個強颱，和仁崇德段大規模土石流坍方逾2萬m³，空拍判釋+保全守視"},
    {"date": "2024-04-23", "type": "地震", "name": "0423 花蓮壽豐群震 (M6.3)", "max_seismic": "5強", "max_rain_3h": 45.0, "max_rain_48h": 110.0, "region": "和平崇德地區", "collapse_m3": 3000, "note": "震度達5強，觸發A、B、C、E類橋梁特別檢測與邊坡立即巡查"},
    {"date": "2024-04-03", "type": "地震", "name": "0403 花蓮大地震 (M7.2)", "max_seismic": "6強", "max_rain_3h": 15.0, "max_rain_48h": 30.0, "region": "和平崇德地區", "collapse_m3": 35000, "note": "成立大規模震災應變小組，下清水橋搶修、全線橋梁特檢、A~C級邊坡7日內特檢+空拍"},
    {"date": "2023-10-04", "type": "颱風", "name": "小犬颱風宜花強降雨", "max_seismic": "0級", "max_rain_3h": 115.0, "max_rain_48h": 355.0, "region": "武塔觀音漢本區", "collapse_m3": 800, "note": "觀音海岸與南澳48hr累積雨量突破350mm門檻，啟動A級邊坡14日特檢"},
    {"date": "2023-09-03", "type": "颱風", "name": "海葵颱風花東登陸豪雨", "max_seismic": "0級", "max_rain_3h": 128.0, "max_rain_48h": 430.0, "region": "和平崇德地區", "collapse_m3": 2200, "note": "蘇花路廊崇德與南澳段強降雨雙雙破門檻，海警解除後2日內全線特別巡查"},
    {"date": "2022-10-16", "type": "颱風", "name": "尼莎颱風共伴效應超大豪雨", "max_seismic": "0級", "max_rain_3h": 152.0, "max_rain_48h": 540.0, "region": "東澳地區", "collapse_m3": 6200, "note": "東北季風共伴鎖住東澳嶺水氣，台9丁線多處坍方逾5,000m³強制升為A級"},
    {"date": "2022-09-18", "type": "地震", "name": "0918 台東池上強震 (M6.8)", "max_seismic": "5弱", "max_rain_3h": 10.0, "max_rain_48h": 25.0, "region": "和平崇德地區", "collapse_m3": 500, "note": "花蓮秀林達5弱震度，立即特別巡查轄區公路構造物、邊坡及特別照護喬木"},
    {"date": "2021-10-11", "type": "颱風", "name": "圓規颱風外圍環流共伴豪雨", "max_seismic": "0級", "max_rain_3h": 148.0, "max_rain_48h": 510.0, "region": "蘇澳地區", "collapse_m3": 3500, "note": "蘇澳與東澳48hr雨量破500mm，觸發降低雨量門檻值與2日內特別巡查"},
    {"date": "2020-10-17", "type": "豪雨", "name": "1017 東北季風宜花連續豪雨", "max_seismic": "0級", "max_rain_3h": 122.0, "max_rain_48h": 380.0, "region": "蘇澳地區", "collapse_m3": 1800, "note": "台9線蘇澳至東澳段連續降雨土壤飽水，執行B級邊坡特巡與A級特檢"},
    {"date": "2019-09-30", "type": "颱風", "name": "米塔颱風宜蘭強風豪雨", "max_seismic": "0級", "max_rain_3h": 138.0, "max_rain_48h": 410.0, "region": "南澳地區", "collapse_m3": 2500, "note": "南澳與武塔段3hr及48hr雨量雙雙達標，海警解除後全線特巡"},
    {"date": "2019-08-08", "type": "颱風", "name": "利奇馬颱風暨宜蘭規模6.0地震", "max_seismic": "5強", "max_rain_3h": 125.0, "max_rain_48h": 360.0, "region": "武塔觀音漢本區", "collapse_m3": 4000, "note": "罕見颱風警報期間複合5強地震，同步觸發A/B/C/E類橋梁特檢與邊坡豪雨特巡"},
    {"date": "2018-02-06", "type": "地震", "name": "0206 花蓮大地震 (M6.2)", "max_seismic": "6強", "max_rain_3h": 20.0, "max_rain_48h": 65.0, "region": "和平崇德地區", "collapse_m3": 12000, "note": "震度達6強，蘇花崇德段多處落石坍方，啟動大規模震災SOP與7日內特檢"},
    {"date": "2017-10-13", "type": "颱風", "name": "卡努颱風東北季風共伴超大豪雨", "max_seismic": "0級", "max_rain_3h": 165.0, "max_rain_48h": 620.0, "region": "東澳地區", "collapse_m3": 9000, "note": "東澳嶺與南澳超大豪雨，武塔至漢本多處阻斷，搶通後實施朝巡暮巡1週"},
    {"date": "2016-09-27", "type": "颱風", "name": "梅姬颱風蘇花全線超大豪雨", "max_seismic": "0級", "max_rain_3h": 175.0, "max_rain_48h": 710.0, "region": "蘇澳地區", "collapse_m3": 18000, "note": "蘇花公路多處大型坍方，原B、C級致災邊坡全面強制升級比照A級管理"},
]

# 預設展示資料庫：直接採用「路線 + 里程樁號(起)～里程樁號(迄)」之格式
DEFAULT_SLOPE_INVENTORY = [
    {"邊坡編號": "台9線 108k+500～108k+650", "路段名稱": "蘇澳東澳段", "所屬雨量分區": "蘇澳地區", "邊坡分級": "C", "分級定義摘述": "5年內有災、後續無明顯不穩", "RHRS中高風險": "否", "復建完工日": "2022-10-01", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線 114k+200～114k+450", "路段名稱": "東澳段", "所屬雨量分區": "東澳地區", "邊坡分級": "A", "分級定義摘述": "2年內有災已完成復建(待汛期後檢討降等)", "RHRS中高風險": "是", "復建完工日": "2025-04-15", "具遠端致災因素": "是"},
    {"邊坡編號": "台9丁線 16k+800～16k+950", "路段名稱": "東澳舊線", "所屬雨量分區": "東澳地區", "邊坡分級": "B", "分級定義摘述": "2年內有災、地形限制無法設護坡/潛在不穩", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線 119k+500～119k+600", "路段名稱": "南澳段", "所屬雨量分區": "南澳地區", "邊坡分級": "C+", "分級定義摘述": "復建完成但具4類遠端致災因素(上邊坡/攻擊面)", "RHRS中高風險": "否", "復建完工日": "2023-10-01", "具遠端致災因素": "是"},
    {"邊坡編號": "台9線 129k+800～129k+900", "路段名稱": "觀音段", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "B", "分級定義摘述": "致災成因消除仍有疑慮需確認(B級第2類)", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "否"},
    {"邊坡編號": "台9丁線 38k+600～38k+800", "路段名稱": "觀音海岸舊線", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "大型地滑/順向坡", "分級定義摘述": "具大型滑動塊體與浪襲攻擊面", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "是"},
    {"邊坡編號": "台9線 141k+100～141k+300", "路段名稱": "武塔漢本段", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "C", "分級定義摘述": "5年內有災、後續無明顯不穩定徵兆", "RHRS中高風險": "否", "復建完工日": "2022-08-20", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線 158k+600～158k+800", "路段名稱": "和仁崇德段", "所屬雨量分區": "和平崇德地區", "邊坡分級": "A", "分級定義摘述": "0403震後及凱米颱風致災復建列管中", "RHRS中高風險": "是", "復建完工日": "2025-12-10", "具遠端致災因素": "是"},
    {"邊坡編號": "台9丁線 61k+000～61k+150", "路段名稱": "澳花和平段", "所屬雨量分區": "和平崇德地區", "邊坡分級": "D", "分級定義摘述": "5年內未有災害紀錄且無明顯不穩定徵兆", "RHRS中高風險": "否", "復建完工日": "", "具遠端致災因素": "否"},
]


# ==========================================
# 2. 氣象署 Open Data API 即時抓取引擎
# ==========================================
def classify_station_region(county: str, town: str, st_name: str) -> str:
    for region_name, keywords in REGIONAL_GROUPS.items():
        if any(k in st_name for k in keywords):
            return region_name
    if "蘇澳" in town:
        return "蘇澳地區"
    if "南澳" in town:
        return "南澳地區"
    if "秀林" in town:
        return "和平崇德地區"
    return "宜花其他區域"


@st.cache_data(ttl=60, show_spinner=False)
def fetch_cwa_rainfall_and_envelope(api_key: str):
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
    params = {"Authorization": api_key.strip(), "format": "JSON"}
    api_meta = {"ok": False, "status_code": None, "latest_obs_time": "無資料", "station_count": 0, "error": ""}
    
    try:
        resp = requests.get(url, params=params, timeout=12, verify=False)
        api_meta["status_code"] = resp.status_code
        resp.raise_for_status()
        data = resp.json()
        stations = data.get("records", {}).get("Station", [])
        
        records = []
        latest_time_str = ""
        for st_obj in stations:
            geo = st_obj.get("GeoInfo", {})
            county = geo.get("CountyName", "")
            town = geo.get("TownName", "")
            st_name = st_obj.get("StationName", "")
            
            if county in ["宜蘭縣", "花蓮縣"]:
                rain_elem = st_obj.get("RainfallElement", {})
                def parse_val(key):
                    val = rain_elem.get(key, {}).get("Precipitation")
                    try:
                        v = float(val)
                        return 0.0 if v < 0 else v
                    except (TypeError, ValueError):
                        return 0.0

                r_10m = parse_val("Past10Min")
                r_1h = parse_val("Past1hr")
                r_3h = parse_val("Past3hr")
                r_24h = parse_val("Past24hr")
                r_2d = parse_val("Past2days")
                r_3d = parse_val("Past3days")
                r_48h = r_2d if r_2d > 0 else max(r_24h, round(r_3d * 0.75, 1))
                
                obs_t = st_obj.get("ObsTime", {}).get("DateTime", "")
                if obs_t > latest_time_str:
                    latest_time_str = obs_t
                    
                region = classify_station_region(county, town, st_name)
                records.append({
                    "所屬雨量分區": region,
                    "縣市": county,
                    "鄉鎮": town,
                    "測站名稱": st_name,
                    "10min雨量": r_10m,
                    "1hr雨量": r_1h,
                    "3hr雨量(mm)": r_3h,
                    "24hr雨量": r_24h,
                    "48hr雨量(mm)": r_48h,
                    "觀測時間": obs_t[:16].replace("T", " ") if obs_t else ""
                })
                
        df_stations = pd.DataFrame(records)
        if df_stations.empty:
            api_meta["error"] = "API 回傳成功但未解析到宜花測站"
            return pd.DataFrame(), pd.DataFrame(), api_meta

        api_meta["ok"] = True
        api_meta["station_count"] = len(df_stations)
        api_meta["latest_obs_time"] = latest_time_str[:16].replace("T", " ") if latest_time_str else datetime.now().strftime("%Y-%m-%d %H:%M")

        envelope_rows = []
        for reg in list(REGIONAL_GROUPS.keys()):
            sub = df_stations[df_stations["所屬雨量分區"] == reg]
            if not sub.empty:
                idx_max3 = sub["3hr雨量(mm)"].idxmax()
                idx_max48 = sub["48hr雨量(mm)"].idxmax()
                max_3h_val = sub.loc[idx_max3, "3hr雨量(mm)"]
                max_3h_st = sub.loc[idx_max3, "測站名稱"]
                max_48h_val = sub.loc[idx_max48, "48hr雨量(mm)"]
                max_48h_st = sub.loc[idx_max48, "測站名稱"]
                
                is_alert = (max_3h_val >= 120 or max_48h_val >= 350)
                status_text = "🚨 觸發法定特別巡檢門檻！" if is_alert else "🟢 安全常態 (未達門檻)"
                
                envelope_rows.append({
                    "所屬雨量分區": reg,
                    "納入測站數": len(sub),
                    "區內最大3hr雨量(mm)": max_3h_val,
                    "3hr極值站": max_3h_st,
                    "區內最大48hr雨量(mm)": max_48h_val,
                    "48hr極值站": max_48h_st,
                    "狀態判定": status_text,
                    "是否超標": is_alert,
                    "觀測時間": sub.loc[idx_max3, "觀測時間"],
                    "測站群組清單": "、".join(sub["測站名稱"].tolist())
                })
        return df_stations, pd.DataFrame(envelope_rows), api_meta
    except Exception as e:
        api_meta["error"] = str(e)
        return pd.DataFrame(), pd.DataFrame(), api_meta


@st.cache_data(ttl=60, show_spinner=False)
def fetch_cwa_earthquake(api_key: str) -> list:
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
    params = {"Authorization": api_key.strip(), "format": "JSON", "limit": 3}
    try:
        resp = requests.get(url, params=params, timeout=10, verify=False)
        resp.raise_for_status()
        eq_list = resp.json().get("records", {}).get("Earthquake", [])
        parsed = []
        for eq in eq_list:
            info = eq.get("EarthquakeInfo", {})
            shaking_areas = eq.get("Intensity", {}).get("ShakingArea", [])
            max_rank = 0
            for area in shaking_areas:
                if any(k in area.get("CountyName", "") for k in ["宜蘭", "花蓮"]):
                    rank = SEISMIC_RANK.get(area.get("AreaIntensity", "0級"), 0)
                    if rank > max_rank:
                        max_rank = rank
            parsed.append({
                "發震時間": info.get("OriginTime", ""),
                "震央位置": info.get("Epicenter", {}).get("Location", ""),
                "規模": info.get("EarthquakeMagnitude", {}).get("MagnitudeValue", ""),
                "宜花最大震度": RANK_TO_SEISMIC.get(max_rank, "0級")
            })
        return parsed
    except Exception:
        return []


# ==========================================
# 3. 路養護字第1155009531號函暨115.10懶人包 邊坡檢查決策引擎
# ==========================================
def evaluate_slope_sop(slope_grade, is_rhrs_high, seismic_str, rain_3h, rain_48h, is_typhoon, is_debris_red, collapse_m3):
    insp_actions, mgmt_actions, bridge_actions = [], [], []
    clean_grade = str(slope_grade).replace("級邊坡", "").replace("級", "").strip()
    if "地滑" in clean_grade or "順向" in clean_grade:
        clean_grade = "大型地滑/順向坡"

    effective_grade = clean_grade
    upgraded_flag = False
    if collapse_m3 >= 5000 and clean_grade in ["B", "C+", "C", "D", "大型地滑/順向坡"]:
        effective_grade = "A"
        upgraded_flag = True

    s_rank = SEISMIC_RANK.get(seismic_str, 0)

    if s_rank == 4 and (is_rhrs_high or effective_grade in ["A", "B"]):
        insp_actions.append("🚨【震度4級-特別巡查】立即巡查震區內「優先關注邊坡」(A、B級經RHRS評估為中高風險者)")
    elif s_rank == 5:
        insp_actions.append("🚨【震度5弱-特別巡查】立即巡查轄區公路構造物、邊坡、特別照護喬木")
    elif s_rank == 6:
        insp_actions.append("🚨【震度5強-特別巡查】立即巡查構造物、邊坡、特別照護喬木")
        bridge_actions.append("🌉【震度5強-橋梁檢測】立即巡查震區橋梁，並特別檢測 A、B、C、E 類橋梁")
    elif s_rank >= 7:
        mgmt_actions.append("🚨【震度6弱以上-處置6】成立「大規模震災」緊急應變小組，依大規模震災SOP辦理")
        bridge_actions.append("🌉【震度6弱以上-橋梁全面檢測】立即辦理震區內「所有橋梁」特別檢測")
        if effective_grade in ["A", "B", "C+", "C"]:
            insp_actions.append("🚨【震度6弱以上-處置3】① 7日內完成特別檢測 ② 實施朝巡1週 ③ 取得空拍或衛星影像")
        elif effective_grade == "D":
            insp_actions.append("🚨【震度6弱以上-處置1】2日內實施特別巡查")
        elif effective_grade == "大型地滑/順向坡":
            insp_actions.append("🚨【震度6弱以上-處置2】14日內完成特別檢測")

    if rain_3h >= 120.0:
        insp_actions.append(f"🌧️【3hr雨量達 {rain_3h}mm (≥120)-處置1】全分級邊坡於 2日內實施特別巡查")
        mgmt_actions.append("🛡️【養護處置3】實施巡查作業" if effective_grade in ["A", "B"] else "📢【養護處置4】揭露路段強降雨訊息")

    if rain_48h >= 350.0:
        if effective_grade in ["A", "大型地滑/順向坡"]:
            insp_actions.append(f"🌧️【48hr雨量達 {rain_48h}mm (≥350)-處置2】A級與地滑/順向坡：14日內完成特別檢測")
        elif effective_grade == "B":
            insp_actions.append(f"🌧️【48hr雨量達 {rain_48h}mm (≥350)-處置1】B級邊坡：2日內實施特別巡查")
        mgmt_actions.append("📉【養護處置1】降低雨量門檻值" if effective_grade in ["A", "B", "大型地滑/順向坡"] else "👁️【養護處置2】加強水情監控")

    if is_typhoon:
        insp_actions.append("🌀【海警解除後-處置1】2日內實施特別巡查 (颱風前後立即巡查構造物與邊坡)")
        mgmt_actions.append("🛡️【養護處置5】颱風警報期間，依「公路防災預警機制」辦理")

    if 5000 <= collapse_m3 < 20000:
        insp_actions.append("⛰️【坍方5千~2萬m³搶通後-處置4(1)】實施朝巡、暮巡 1 週")
    elif collapse_m3 >= 20000:
        insp_actions.append("⛰️【坍方≥2萬m³搶通後-處置4(1)&(2)】① 實施朝巡暮巡1週 ② 取得空拍或衛星影像")
        mgmt_actions.append("🚧【養護處置7】執行保全守視 (必要時交通管制)")

    if is_debris_red:
        insp_actions.append("⚠️【土石流紅色警戒-處置1】2日內實施特別巡查")
        if effective_grade in ["A", "B", "C+", "大型地滑/順向坡"]:
            mgmt_actions.append("🛡️【養護處置8】擬定加碼部署策略，按計畫執行")

    is_triggered = len(insp_actions) > 0 or len(mgmt_actions) > 0
    
    if is_triggered:
        mgmt_actions.append("📋【115.05分級管理機制】於「災害事件後(颱風/豪雨/地震)」及「巡查檢測作業完成後」辦理邊坡分級滾動檢討")
    else:
        insp_actions.append("🟢 未達災變特巡門檻｜依常態週期辦理：經常巡查(車巡) 1次/週 (下邊坡1次/季)、定期巡查(步巡) 1次/月、定期檢查 1次/年")

    return {
        "effective_grade": effective_grade,
        "upgraded_flag": upgraded_flag,
        "is_triggered": is_triggered,
        "inspection": "<br>".join(insp_actions),
        "management": "<br>".join(mgmt_actions) if mgmt_actions else "🟢 常態養護管理",
        "bridge": "；".join(bridge_actions) if bridge_actions else ""
    }


def auto_assign_region_by_text(text_val: str) -> str:
    t = str(text_val)
    for reg, kws in REGIONAL_GROUPS.items():
        if any(k in t for k in kws):
            return reg
    return "南澳地區"


# ==========================================
# 4. 主戰情室介面
# ==========================================
def render_app():
    st.set_page_config(page_title="蘇花廊道災變暨邊坡巡查自動化決策系統", layout="centered", initial_sidebar_state="collapsed")

    inject_custom_style_and_banner()

    if "disaster_db" not in st.session_state:
        st.session_state.disaster_db = pd.DataFrame(DEFAULT_DISASTER_HISTORY)
    if "slope_db" not in st.session_state:
        st.session_state.slope_db = pd.DataFrame(DEFAULT_SLOPE_INVENTORY)

    with st.sidebar:
        st.header("⚙️ 系統設定與資料庫掛載")
        api_key = st.text_input("🔑 氣象署 API 授權碼", value=DEFAULT_CWA_API_KEY, type="password")
        
        st.subheader("🔌 API 連線診斷工具")
        if st.button("🧪 測試氣象署 API 連線狀態", use_container_width=True):
            test_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
            try:
                res = requests.get(test_url, params={"Authorization": api_key.strip(), "format": "JSON", "limit": 5}, timeout=10, verify=False)
                if res.status_code == 200:
                    st.success(f"✅ 連線成功 (HTTP 200)！氣象署伺服器正常回應。")
                else:
                    st.error(f"❌ 連線異常，狀態碼：{res.status_code}")
            except Exception as e:
                st.error(f"🚨 網路錯誤：{e}")

        st.divider()
        st.subheader("📂 載入「南澳邊坡資料.xlsx」")
        local_xlsx = [f.name for f in Path(".").glob("*.xlsx") if not f.name.startswith("~$")]
        up_file = st.file_uploader("上傳 .xlsx 檔案", type=["xlsx"])
        raw_df = None
        if up_file:
            xl = pd.ExcelFile(up_file)
            sh = st.selectbox("選擇工作表", xl.sheet_names)
            raw_df = xl.parse(sh)
        elif local_xlsx:
            sel_lx = st.selectbox("選擇本地 Excel 檔", ["(使用預設口卡)"] + local_xlsx)
            if sel_lx != "(使用預設口卡)":
                xl = pd.ExcelFile(sel_lx)
                sh = st.selectbox("選擇工作表", xl.sheet_names)
                raw_df = xl.parse(sh)

        # ====== 南澳邊坡全生命週期資料庫 原生解析引擎 ======
        if raw_df is not None and not raw_df.empty:
            cols = raw_df.columns.tolist()
            # 自動偵測是否具備標準欄位
            if all(k in cols for k in ["路線", "里程樁號(起)", "里程樁號(迄)", "定性分級"]):
                st.info("✅ 偵測到「邊坡資料」標準格式，系統將自動提取 定性分級 與 里程區間。")
                if st.button("📥 一鍵套用至邊坡決策系統", use_container_width=True):
                    mapped = []
                    for _, r in raw_df.iterrows():
                        route = str(r.get("路線", "")).strip()
                        m_start = str(r.get("里程樁號(起)", "")).strip()
                        m_end = str(r.get("里程樁號(迄)", "")).strip()
                        grade = str(r.get("定性分級", "")).strip()
                        
                        if grade == "nan" or route == "nan":
                            continue
                            
                        # 將邊坡編號格式化為「路線 里程(起)～里程(迄)」
                        s_id = f"{route} {m_start}～{m_end}"
                        loc_name = str(r.get("附近地名", "")).strip()
                        if loc_name == "nan": loc_name = ""
                        
                        mapped.append({
                            "邊坡編號": s_id,
                            "路段名稱": loc_name,
                            "所屬雨量分區": auto_assign_region_by_text(f"{route} {loc_name} {r.get('鄉鎮市區', '')}"),
                            "邊坡分級": grade, # 對應「定性分級」
                            "分級定義摘述": str(r.get("現地狀況描述", ""))[:30] + "..." if r.get("現地狀況描述") else "由Excel邊坡資料庫匯入",
                            "RHRS中高風險": "是" if any(g in grade for g in ["A", "B"]) else "否",
                            "復建完工日": "", 
                            "具遠端致災因素": "是" if "C+" in grade else "否"
                        })
                    st.session_state.slope_db = pd.DataFrame(mapped)
                    st.success(f"已成功載入 {len(mapped)} 筆邊坡口卡！")
            else:
                # 傳統手動映射
                c_id = st.selectbox("【邊坡編號】欄", cols, index=0)
                c_loc = st.selectbox("【路段名稱】欄", cols, index=min(1, len(cols)-1))
                c_grade = st.selectbox("【邊坡分級】欄", cols, index=min(2, len(cols)-1))
                if st.button("✅ 套用至決策系統", use_container_width=True):
                    mapped = []
                    for _, r in raw_df.iterrows():
                        s_id, s_loc, s_g = str(r[c_id]), str(r[c_loc]), str(r[c_grade])
                        mapped.append({
                            "邊坡編號": s_id, "路段名稱": s_loc,
                            "所屬雨量分區": auto_assign_region_by_text(f"{s_id} {s_loc}"),
                            "邊坡分級": s_g, "分級定義摘述": "由 Excel 自訂匯入",
                            "RHRS中高風險": "是" if any(g in s_g for g in ["A", "B"]) else "否",
                            "復建完工日": "", "具遠端致災因素": "是" if "C+" in s_g else "否"
                        })
                    st.session_state.slope_db = pd.DataFrame(mapped)
                    st.success("已成功自訂載入 Excel 口卡！")

    df_stations, df_envelope, api_meta = fetch_cwa_rainfall_and_envelope(api_key)
    eq_records = fetch_cwa_earthquake(api_key)

    col_hb1, col_hb2 = st.columns([3, 1])
    with col_hb1:
        if api_meta["ok"]:
            st.markdown(f"""
            <div style="background:rgba(16,185,129,0.15); border:1px solid #10b981; border-radius:10px; padding:8px 14px; font-size:0.92rem; color:#a7f3d0; font-weight:700;">
                🟢 <b>CWA 氣象署 API 即時連線正常</b>｜最新觀測時間：<code>{api_meta['latest_obs_time']}</code>｜已同步宜花 <b>{api_meta['station_count']}</b> 座雨量站
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.2); border:1px solid #ef4444; border-radius:10px; padding:8px 14px; font-size:0.92rem; color:#fca5a5; font-weight:700;">
                🔴 <b>CWA API 連線異常</b> ({api_meta['error']})｜請點右側按鈕重新抓取或展開左上角檢查金鑰
            </div>
            """, unsafe_allow_html=True)
    with col_hb2:
        if st.button("🔄 立即抓最新雨量", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    main_menu = st.selectbox(
        "👇 請選擇功能模組 (下拉切換)：",
        [
            "📡 1. 蘇花廊道即時區域雨量包絡監測 (CWA即時連線)",
            "📅 2. 近10年宜花歷年天災時序溯源查詢 (2016-2026)",
            "🛡️ 3. 氣象災變整合「路養護字第1155009531號函」邊坡檢查與降等決策中心"
        ]
    )

    region_rain_map = {}
    if not df_envelope.empty:
        for _, r_env in df_envelope.iterrows():
            region_rain_map[r_env["所屬雨量分區"]] = (
                float(r_env["區內最大3hr雨量(mm)"]),
                float(r_env["區內最大48hr雨量(mm)"]),
                r_env["3hr極值站"]
            )

    # ==================================================
    # 模組 1：即時區域雨量包絡監測
    # ==================================================
    if main_menu.startswith("📡 1"):
        reg_filter = st.selectbox(
            "📍 下拉選擇欲檢視之蘇花微氣候防區：",
            ["全部五大防區總覽"] + list(REGIONAL_GROUPS.keys())
        )

        if not df_envelope.empty:
            show_env = df_envelope if reg_filter == "全部五大防區總覽" else df_envelope[df_envelope["所屬雨量分區"] == reg_filter]
            for _, row in show_env.iterrows():
                r3 = row["區內最大3hr雨量(mm)"]
                r48 = row["區內最大48hr雨量(mm)"]
                card_cls = "card-danger" if row["是否超標"] else ("card-warn" if (r3 >= 80 or r48 >= 200) else "card-safe")
                
                st.markdown(f"""
                <div class="mobile-card {card_cls}">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:1.35rem; font-weight:900; color:#38bdf8;">📍 {row['所屬雨量分區']}</span>
                        <span style="font-size:0.88rem; font-weight:700; background:#0f172a; padding:4px 10px; border-radius:99px; color:#cbd5e1;">🕒 {row['觀測時間']}｜{row['納入測站數']}站包絡</span>
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin: 12px 0;">
                        <div style="background:rgba(15,23,42,0.75); padding:12px; border-radius:12px;">
                            <div style="font-size:0.9rem; color:#94a3b8;">區內最大 3hr 雨量 (門檻120)</div>
                            <div class="big-number" style="color:{'#f87171' if r3>=120 else '#ffffff'};">{r3} <span style="font-size:1rem;">mm</span></div>
                            <div style="font-size:0.85rem; color:#cbd5e1; margin-top:4px;">極值站：{row['3hr極值站']}</div>
                        </div>
                        <div style="background:rgba(15,23,42,0.75); padding:12px; border-radius:12px;">
                            <div style="font-size:0.9rem; color:#94a3b8;">區內最大 48hr 雨量 (門檻350)</div>
                            <div class="big-number" style="color:{'#f87171' if r48>=350 else '#ffffff'};">{r48} <span style="font-size:1rem;">mm</span></div>
                            <div style="font-size:0.85rem; color:#cbd5e1; margin-top:4px;">極值站：{row['48hr極值站']}</div>
                        </div>
                    </div>
                    <div style="font-size:1.1rem; font-weight:800; color:{'#fca5a5' if row['是否超標'] else '#6ee7b7'};">
                        {row['狀態判定']}
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:6px;">
                        涵蓋雨量站：{row['測站群組清單']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("📋 點擊展開：檢視宜花各雨量站即時觀測數據明細表", expanded=(reg_filter != "全部五大防區總覽")):
                sub_st = df_stations if reg_filter == "全部五大防區總覽" else df_stations[df_stations["所屬雨量分區"] == reg_filter]
                sub_st = sub_st.sort_values(by=["3hr雨量(mm)", "48hr雨量(mm)"], ascending=False)
                st.dataframe(sub_st[["所屬雨量分區", "測站名稱", "10min雨量", "1hr雨量", "3hr雨量(mm)", "24hr雨量", "48hr雨量(mm)", "觀測時間"]], use_container_width=True, hide_index=True)

        cwa_url = "https://www.cwa.gov.tw/V8/C/"
        ncdr_url = "https://watch.ncdr.nat.gov.tw/watch_histracks"
        
        st.markdown(f"""
        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-top:10px;">
            <a href="{cwa_url}" target="_blank" style="display:block; text-align:center; background:#f59e0b; color:#0f172a; font-weight:900; font-size:1.05rem; padding:14px 8px; border-radius:12px; text-decoration:none;">
                🌧️ 氣象署首頁 (CWA)
            </a>
            <a href="{ncdr_url}" target="_blank" style="display:block; text-align:center; background:#38bdf8; color:#0f172a; font-weight:900; font-size:1.05rem; padding:14px 8px; border-radius:12px; text-decoration:none;">
                🌪️ NCDR 災防中心
            </a>
        </div>
        """, unsafe_allow_html=True)

    # ==================================================
    # 模組 2：近10年宜花天災時序溯源查詢 (災別動態分流路由)
    # ==================================================
    elif main_menu.startswith("📅 2"):
        df_hist = st.session_state.disaster_db.copy()
        df_hist["year"] = df_hist["date"].str.slice(0, 4)

        current_yr = datetime.now().year
        last_10_years = [str(y) for y in range(current_yr, current_yr - 11, -1)]
        all_years = sorted(list(set(df_hist["year"].unique().tolist() + last_10_years)), reverse=True)

        c1, c2 = st.columns(2)
        sel_year = c1.selectbox("📅 1. 下拉選擇查詢年份 (涵蓋近10年)：", ["全部歷年紀錄 (2016-2026)"] + all_years)
        sel_type = c2.selectbox("🌪️ 2. 下拉選擇災害類別：", ["全部災別 (地震/颱風/豪雨)", "颱風", "豪雨", "地震"])
        
        c3, c4 = st.columns(2)
        sel_reg_h = c3.selectbox("📍 3. 下拉篩選受災分區：", ["全部宜花防區"] + list(REGIONAL_GROUPS.keys()))
        sort_dir = c4.selectbox("⏳ 4. 日期排序方式：", ["日期：由新到舊 (最新優先)", "日期：由舊到新 (時間先後順序)"])

        if not sel_year.startswith("全部"):
            df_hist = df_hist[df_hist["year"] == sel_year]
        if sel_type != "全部災別 (地震/颱風/豪雨)":
            df_hist = df_hist[df_hist["type"] == sel_type]
        if sel_reg_h != "全部宜花防區":
            df_hist = df_hist[df_hist["region"] == sel_reg_h]

        df_hist = df_hist.sort_values(by="date", ascending=("由舊到新" in sort_dir))

        st.markdown(f"#### 📖 篩選結果：共 {len(df_hist)} 筆宜花重大天災紀錄")

        for _, ev in df_hist.iterrows():
            ev_type = ev['type']
            yr = ev['date'][:4]
            t_color = "#ef4444" if ev_type == "地震" else ("#3b82f6" if ev_type == "颱風" else "#eab308")

            # 依據災別動態跳轉至對應之官方專屬資料庫，避免走 Google
            if ev_type == "颱風":
                cwa_url = "https://rdc28.cwa.gov.tw/TDB/public/warning_typhoon_list/"
                cwa_label = f"🌀 氣象署 {yr} 颱風資料庫"
                ncdr_url = "https://watch.ncdr.nat.gov.tw/watch_histracks"
                ncdr_label = f"🌪️ NCDR {yr} 颱風軌跡"
            elif ev_type == "地震":
                cwa_url = "https://scweb.cwa.gov.tw/zh-tw/earthquake/data/"
                cwa_label = f"🌋 氣象署 {yr} 歷史地震"
                ncdr_url = "https://den.ncdr.nat.gov.tw/"
                ncdr_label = f"📊 NCDR {yr} 災防大數據"
            else: # 豪雨
                cwa_url = "https://codis.cwa.gov.tw/StationData"
                cwa_label = f"🌧️ 氣象署 CODiS 歷史雨量"
                ncdr_url = "https://watch.ncdr.nat.gov.tw/"
                ncdr_label = f"💧 NCDR 天氣災防監測"

            st.markdown(f"""
            <div class="mobile-card" style="border-left: 8px solid {t_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
                <a href="{cwa_url}" target="_blank" style="text-decoration:none; color:inherit; display:block;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.1rem; font-family:monospace; font-weight:800; color:#94a3b8;">📅 {ev['date']}</span>
                        <span style="background:{t_color}; color:#ffffff; font-weight:900; font-size:0.9rem; padding:3px 10px; border-radius:99px;">{ev['type']}｜{ev['region']}</span>
                    </div>
                    <div style="font-size:1.35rem; font-weight:900; color:#38bdf8; margin: 8px 0; text-decoration:underline;">
                        {ev['name']} ↗
                    </div>
                    <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:8px;">
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#fca5a5;">震度：{ev['max_seismic']}</span>
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#38bdf8;">3hr雨量：{ev['max_rain_3h']}mm</span>
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#fbbf24;">48hr雨量：{ev['max_rain_48h']}mm</span>
                        <span style="background:#0f172a; padding:4px 10px; border-radius:8px; font-size:0.95rem; font-weight:700; color:#cbd5e1;">坍方：{ev['collapse_m3']}m³</span>
                    </div>
                    <div style="font-size:1.05rem; color:#e2e8f0; line-height:1.4; margin-bottom:12px;">
                        📌 {ev['note']}
                    </div>
                </a>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; border-top:1px solid rgba(255,255,255,0.1); padding-top:10px;">
                    <a href="{cwa_url}" target="_blank" class="link-btn">
                        {cwa_label}
                    </a>
                    <a href="{ncdr_url}" target="_blank" class="link-btn-sec">
                        {ncdr_label}
                    </a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ==================================================
    # 模組 3：氣象災變整合「路養護字第1155009531號函」邊坡檢查與降等決策中心
    # ==================================================
    elif main_menu.startswith("🛡️ 3"):
        st.markdown("""
        <div class="mobile-card card-warn">
            <div style="font-size:1.2rem; font-weight:900; color:#fbbf24; margin-bottom:4px;">⚖️ 路養護字第1155009531號函 (115年5月修訂) 核心決策邏輯</div>
            <div style="font-size:0.98rem; color:#e2e8f0; line-height:1.45;">
                1. <b>即時/歷史災變觸發檢查</b>：依各防區氣象極值與震度，自動對 <b>A、B、C+、C、D 級與大型地滑區</b> 指派對應之【特別巡查】或【特別檢測】。<br>
                2. <b>災後滾動檢討與A級降等</b>：完成復建並歷經至少 <b>1個完整汛期(5/1~11/30)</b> 之A級邊坡，於汛期結束後結合本系統近10年外力紀錄，檢討調降至 <b>C+級(具4類遠端因素)</b> 或 <b>C級</b>。
            </div>
        </div>
        """, unsafe_allow_html=True)

        sub_task = st.selectbox(
            "🔧 請選擇欲執行之邊坡管理決策作業：",
            [
                "作業 A：【邊坡檢查派工決策】依據即時氣象或歷史災變，決定各級邊坡應做何種檢查",
                "作業 B：【A級邊坡降等檢核】依據 1155009531 號函，檢核復建邊坡汛期考驗與調降 C+/C 級資格"
            ]
        )

        if sub_task.startswith("作業 A"):
            drive_mode = st.selectbox(
                "⚡ 1. 下拉選擇外力觸發來源：",
                [
                    "🟢 即時模式：直接抓取【氣象署 API 當下各防區最大包絡雨量與震度】判定",
                    "🧪 災變復盤模式：載入【近10年歷史天災事件 / 自訂極端參數】判定哪處邊坡需檢查"
                ]
            )

            c_f1, c_f2 = st.columns(2)
            target_region = c_f1.selectbox("📍 2. 篩選蘇花防區路段：", ["全部轄區邊坡口卡"] + list(REGIONAL_GROUPS.keys()))
            target_grade_filter = c_f2.selectbox("🏷️ 3. 篩選 115 年邊坡分級：", ["全部列管分級 (A~D級)", "僅看 A 級邊坡", "僅看 B 級邊坡", "僅看 C+ 級 (具遠端致災因素)", "僅看 C / D 級", "僅看 大型地滑/順向坡"])

            if drive_mode.startswith("🟢"):
                override_rain = False
                default_eq = eq_records[0]["宜花最大震度"] if eq_records else "0級"
                c1, c2 = st.columns(2)
                sim_seis = c1.selectbox("當前宜花最大震度", list(SEISMIC_RANK.keys()), index=list(SEISMIC_RANK.keys()).index(default_eq))
                sim_scenario = c2.selectbox("特殊防災情境狀態", ["無特殊附加警戒", "🌀 海上颱風警報解除/期間", "⚠️ 鄰河側土石流紅色警戒", "⛰️ 無預警坍方 5,000~20,000 m³", "⛰️ 無預警大規模坍方 ≥ 20,000 m³"])
            else:
                override_rain = True
                ev_opts = ["手動輸入測試數值"] + [f"{r['date']} | {r['name']} ({r['region']})" for _, r in st.session_state.disaster_db.iterrows()]
                sel_ev = st.selectbox("📥 下拉載入近 10 年歷史天災事件：", ev_opts, index=1)
                
                def_seis, def_r3, def_r48, def_col = "0級", 135.0, 380.0, 0
                if sel_ev != "手動輸入測試數值":
                    ev_date = sel_ev.split(" | ")[0]
                    ev_name = sel_ev.split(" | ")[1].rsplit(" (", 1)[0]
                    row = st.session_state.disaster_db[(st.session_state.disaster_db["date"] == ev_date) & (st.session_state.disaster_db["name"] == ev_name)].iloc[0]
                    def_seis, def_r3, def_r48, def_col = row["max_seismic"], float(row["max_rain_3h"]), float(row["max_rain_48h"]), int(row["collapse_m3"])

                c1, c2 = st.columns(2)
                sim_seis = c1.selectbox("災變最大震度", list(SEISMIC_RANK.keys()), index=list(SEISMIC_RANK.keys()).index(def_seis))
                sim_scenario = c2.selectbox("特殊防災情境狀態", ["無特殊附加警戒", "🌀 海上颱風警報解除/期間", "⚠️ 鄰河側土石流紅色警戒", "⛰️ 無預警坍方 5,000~20,000 m³", "⛰️ 無預警大規模坍方 ≥ 20,000 m³"], index=(4 if def_col>=20000 else (3 if def_col>=5000 else 0)))
                
                r_col1, r_col2 = st.columns(2)
                sim_r3_manual = r_col1.number_input("測試 3hr 雨量 (mm)", value=def_r3, step=10.0)
                sim_r48_manual = r_col2.number_input("測試 48hr 雨量 (mm)", value=def_r48, step=20.0)

            is_ty = "颱風" in sim_scenario
            is_deb = "土石流" in sim_scenario
            sim_col = 20000 if "≥ 20,000" in sim_scenario else (5000 if "5,000" in sim_scenario else 0)

            slopes_df = st.session_state.slope_db.copy()
            if target_region != "全部轄區邊坡口卡":
                slopes_df = slopes_df[slopes_df["所屬雨量分區"] == target_region]
            if "僅看 A" in target_grade_filter:
                slopes_df = slopes_df[slopes_df["邊坡分級"] == "A"]
            elif "僅看 B" in target_grade_filter:
                slopes_df = slopes_df[slopes_df["邊坡分級"] == "B"]
            elif "僅看 C+" in target_grade_filter:
                slopes_df = slopes_df[slopes_df["邊坡分級"] == "C+"]
            elif "僅看 C / D" in target_grade_filter:
                slopes_df = slopes_df[slopes_df["邊坡分級"].isin(["C", "D"])]
            elif "地滑" in target_grade_filter:
                slopes_df = slopes_df[slopes_df["邊坡分級"].str.contains("地滑|順向")]

            st.markdown(f"#### 📋 邊坡檢查決策清單（符合條件共 {len(slopes_df)} 處邊坡）")

            for _, slope in slopes_df.iterrows():
                s_reg = slope["所屬雨量分區"]
                if not override_rain and s_reg in region_rain_map:
                    r3_val, r48_val, rep_st = region_rain_map[s_reg]
                    rain_tag = f"{s_reg}即時包絡 ({rep_st}: 3h={r3_val} / 48h={r48_val}mm)"
                elif not override_rain:
                    r3_val, r48_val = 0.0, 0.0
                    rain_tag = f"{s_reg} (無超標雨量)"
                else:
                    r3_val, r48_val = sim_r3_manual, sim_r48_manual
                    rain_tag = f"災變外力輸入 (3h={r3_val} / 48h={r48_val}mm)"

                res = evaluate_slope_sop(
                    slope_grade=slope["邊坡分級"],
                    is_rhrs_high=(slope["RHRS中高風險"] == "是"),
                    seismic_str=sim_seis,
                    rain_3h=r3_val,
                    rain_48h=r48_val,
                    is_typhoon=is_ty,
                    is_debris_red=is_deb,
                    collapse_m3=sim_col
                )

                if res["bridge"]:
                    st.error(res["bridge"])

                card_style = "card-danger" if res["is_triggered"] else "card-safe"
                grade_badge = f"🔥 強制升為 A 級 (原{slope['邊坡分級']})" if res["upgraded_flag"] else f"{slope['邊坡分級']} 級邊坡"

                st.markdown(f"""
                <div class="mobile-card {card_style}">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px;">
                        <div>
                            <div style="font-size:1.4rem; font-weight:900; color:#ffffff;">{slope['邊坡編號']} <span style="font-size:1.1rem; color:#38bdf8;">({slope['路段名稱']})</span></div>
                            <div style="font-size:0.9rem; color:#cbd5e1; margin-top:2px;">🌧️ {rain_tag}｜📌 {slope.get('分級定義摘述', '')}</div>
                        </div>
                        <span style="background:#f59e0b; color:#0f172a; font-weight:900; font-size:0.95rem; padding:4px 10px; border-radius:8px; white-space:nowrap;">
                            {grade_badge}
                        </span>
                    </div>
                    <div class="sop-action-box">
                        <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:2px;">🔍 應執行之邊坡巡查 / 特別檢測項目：</div>
                        {res['inspection']}
                    </div>
                    <div class="sop-mgmt-box">
                        <div style="font-size:0.85rem; color:#a7f3d0; margin-bottom:2px;">🛡️ 防災管制與 1155009531號函 分級管理作為：</div>
                        {res['management']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        else:
            # 作業 B：A級邊坡降等檢核
            # 依據使用者需求，精準過濾 "定性分級"(已對應為"邊坡分級") 中包含 A 的邊坡口卡
            a_slopes = st.session_state.slope_db[st.session_state.slope_db["邊坡分級"].astype(str).str.contains("A", case=False)]
            
            # 依照「路線 里程(起)～里程(迄) (附近地名)」格式組裝下拉選單
            slope_opts = []
            for _, r in a_slopes.iterrows():
                opt_str = r['邊坡編號']
                if pd.notna(r.get('路段名稱')) and r['路段名稱'] != "":
                    opt_str += f" ({r['路段名稱']})"
                slope_opts.append(opt_str)
                
            slope_opts.append("自訂評估邊坡")
            
            st.selectbox("⛰️ 1. 下拉選擇欲評估降等之 A 級邊坡 (自動抓取 Excel 定性分級)：", slope_opts)

            c1, c2 = st.columns(2)
            rehab_dt = c1.date_input("2. 復建工程完工日", value=date(2025, 4, 15))
            eval_dt = c2.date_input("3. 提報審查日 (須於11/30汛期結束後)", value=date(2026, 12, 5))

            remote_opt = st.selectbox(
                "🔍 4. C+級邊坡快篩調查表 (是否具4類遠端致災因素)：",
                [
                    "是：具遠端致災因素 (需持續關注上/下邊坡、曲流/浪襲攻擊面、坡頂人為開發、明隧道上方邊坡)",
                    "否：無上述4種遠端致災因素，且後續無明顯不穩定徵兆"
                ]
            )

            full_seasons = [y for y in range(rehab_dt.year, eval_dt.year + 1) if rehab_dt <= date(y, 5, 1) and eval_dt > date(y, 11, 30)]
            df_h = st.session_state.disaster_db.copy()
            df_h["dt"] = pd.to_datetime(df_h["date"]).dt.date
            exp_ev = df_h[(df_h["dt"] >= rehab_dt) & (df_h["dt"] <= eval_dt)]
            max_48 = exp_ev["max_rain_48h"].max() if not exp_ev.empty else 0.0

            is_qualified = (len(full_seasons) >= 1) and not (5 <= eval_dt.month <= 11)
            target_g = "C+ 級邊坡" if remote_opt.startswith("是") else "C 級邊坡"

            st.markdown(f"""
            <div class="mobile-card {'card-safe' if is_qualified else 'card-danger'}">
                <div style="font-size:1.1rem; color:#94a3b8;">路養護字第1155009531號函 降等資格暨自然外力壓力測試判定：</div>
                <div class="big-number" style="color:{'#6ee7b7' if is_qualified else '#fca5a5'}; margin:8px 0;">
                    {'✅ 符合資格 ➔ 可提報專家會議調降至 ' + target_g if is_qualified else '❌ 尚未符合降等法定啟動時機'}
                </div>
                <div style="font-size:1.05rem; color:#ffffff; line-height:1.6;">
                    • 完整經歷汛期數：<b>{len(full_seasons)} 個</b> ({full_seasons if full_seasons else '未滿1個完整汛期 5/1~11/30'})<br>
                    • 完工後經歷天災次數：<b>{len(exp_ev)} 次</b><br>
                    • 期間承受最大 48hr 雨量：<b>{max_48} mm</b> ({'已通過 350mm 豪雨壓力測試' if max_48>=350 else '期間未達 350mm 門檻'})<br>
                    • 應備齊審查資料：<b>(1) 致災原因之探討 (2) 削減措施說明 (3) 可降等之理由(含安定分析、影像判釋及照片)</b>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_app()
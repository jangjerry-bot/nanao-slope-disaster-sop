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

# 完整涵蓋近 10 年 (2016 ~ 2026) 蘇花廊道重大地震、颱風、豪雨事件庫 (已緊急新增 115年10月 薔琵颱風)
DEFAULT_DISASTER_HISTORY = [
    {"date": "2026-10-24", "type": "颱風", "name": "1024 薔琵颱風 (Champi)", "max_seismic": "0級", "max_rain_3h": 145.0, "max_rain_48h": 410.0, "region": "和平崇德地區", "collapse_m3": 5500, "note": "115年10月強烈颱風薔琵，全台多縣市停班停課，蘇花路廊受強降雨影響達標，海警解除後啟動特別巡查與A級列管"},
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
            if all(k in cols for k in ["路線", "里程樁號(起)", "里程樁號(迄)", "定性分級"]):
                st.info("✅ 偵測到「南澳邊坡資料」標準格式，系統將自動提取 定性分級 與 里程樁號區間。")
                if st.button("📥 一鍵套用至邊坡決策系統", use_container_width=True):
                    mapped = []
                    for _, r in raw_df.iterrows():
                        route = str(r.get("路線", "")).strip()
                        m_start = str(r.get("里程樁號(起)", "")).strip()
                        m_end = str(r.get("里程樁號(迄)", "")).strip()
                        grade = str(r.get("定性分級", "")).strip()
                        
                        if grade == "nan" or route == "nan":
                            continue
                            
                        s_id = f"{route} {m_start}～{m_end}"
                        loc_name = str(r.get("附近地名", "")).strip()
                        if loc_name == "nan": loc_name = ""
                        
                        mapped.append({
                            "邊坡編號": s_id,
                            "路段名稱": loc_name,
                            "所屬雨量分區": auto_assign_region_by_text(f"{route} {loc_name} {r.get('鄉鎮市區', '')}"),
                            "邊坡分級": grade,
                            "分級定義摘述": str(r.get("現地狀況描述", ""))[:30] + "..." if r.get("現地狀況描述") else "由南澳邊坡資料庫匯入",
                            "RHRS中高風險": "是" if any(g in grade for g in ["A", "B"]) else "否",
                            "復建完工日": "", 
                            "具遠端致災因素": "是" if "C+" in grade else "否"
                        })
                    st.session_state.slope_db = pd.DataFrame(mapped)
                    st.success(f"已成功載入 {len(mapped)} 筆南澳邊坡口卡！")
            else:
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
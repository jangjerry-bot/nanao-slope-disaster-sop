import streamlit as st
import pandas as pd
import requests
from datetime import datetime, date
from pathlib import Path
import urllib3

# 忽略政府憑證偶發之 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 1. 核心常數、預設 API 金鑰與區域群組定義
# ==========================================
# 將原本寫死的 DEFAULT_CWA_API_KEY 改為以下動態讀取機制：
try:
    DEFAULT_CWA_API_KEY = st.secrets.get("CWA_API_KEY", "CWA-E9410456-F2F6-489C-BD69-8C45B13EBEFD")
except Exception:
    DEFAULT_CWA_API_KEY = "CWA-E9410456-F2F6-489C-BD69-8C45B13EBEFD"

# 蘇花廊道(宜花區)五大微氣候分區與測站關鍵字映射表
REGIONAL_GROUPS = {
    "蘇澳地區": ["蘇澳", "馬賽", "永樂", "白米", "南方澳", "北方澳"],
    "東澳地區": ["東澳", "東澳嶺", "粉鳥林", "西帽山"],
    "南澳地區": ["南澳", "朝陽", "碧候", "金洋", "古魯", "鹿皮"],
    "武塔觀音漢本區": ["武塔", "觀音", "澳花", "漢本", "大濁水"],
    "和平崇德地區": ["和平", "和中", "和仁", "崇德", "太魯閣", "清水", "富世", "布洛灣"]
}

SEISMIC_RANK = {"0級": 0, "1級": 1, "2級": 2, "3級": 3, "4級": 4, "5弱": 5, "5強": 6, "6弱": 7, "6強": 8, "7級": 9}
RANK_TO_SEISMIC = {v: k for k, v in SEISMIC_RANK.items()}

DEFAULT_DISASTER_HISTORY = [
    {"date": "2026-09-20", "type": "地震", "name": "0920 南澳外海地震 (M5.6)", "max_seismic": "4級", "max_rain_3h": 0.0, "max_rain_48h": 10.0, "region": "南澳地區", "collapse_m3": 0, "note": "震度達4級，觸發優先關注邊坡(RHRS中高風險)立即巡查"},
    {"date": "2026-05-12", "type": "豪雨", "name": "0512 梅雨滯留鋒面劇烈豪雨", "max_seismic": "0級", "max_rain_3h": 130.0, "max_rain_48h": 365.0, "region": "東澳地區", "collapse_m3": 0, "note": "115年汛期首波達標豪雨，東澳嶺3hr與48hr雙雙突破門檻"},
    {"date": "2025-11-18", "type": "豪雨", "name": "東北季風共伴效應超大豪雨", "max_seismic": "0級", "max_rain_3h": 142.0, "max_rain_48h": 460.0, "region": "東澳地區", "collapse_m3": 1200, "note": "典型秋冬地形鎖水效應，啟動A級邊坡14日內特檢與降低雨量門檻"},
    {"date": "2025-08-13", "type": "颱風", "name": "楊柳颱風外圍環流強降雨", "max_seismic": "0級", "max_rain_3h": 135.0, "max_rain_48h": 390.0, "region": "南澳地區", "collapse_m3": 0, "note": "短延時強降雨突破120mm/3hr，揭露強降雨訊息並於2日內特巡"},
    {"date": "2024-10-31", "type": "颱風", "name": "康芮颱風東部超大豪雨", "max_seismic": "0級", "max_rain_3h": 160.0, "max_rain_48h": 680.0, "region": "和平崇德地區", "collapse_m3": 8500, "note": "海警解除後全線特巡，坍方逾5,000m³路段強制升級比照A級"},
    {"date": "2024-07-24", "type": "颱風", "name": "凱米颱風強降雨致災", "max_seismic": "0級", "max_rain_3h": 185.0, "max_rain_48h": 820.0, "region": "和平崇德地區", "collapse_m3": 25000, "note": "0403震後首個強颱，坍方逾20,000m³，啟動空拍判釋與保全守視"},
    {"date": "2024-04-23", "type": "地震", "name": "0423 花蓮壽豐群震 (M6.3)", "max_seismic": "5強", "max_rain_3h": 45.0, "max_rain_48h": 110.0, "region": "和平崇德地區", "collapse_m3": 3000, "note": "震度達5強，觸發A、B、C、E類橋梁特別檢測與邊坡立即巡查"},
    {"date": "2024-04-03", "type": "地震", "name": "0403 花蓮大地震 (M7.2)", "max_seismic": "6強", "max_rain_3h": 15.0, "max_rain_48h": 30.0, "region": "和平崇德地區", "collapse_m3": 35000, "note": "成立大規模震災緊急應變小組，全線橋梁特檢、A~C級邊坡7日內特檢+朝巡1週+空拍"},
]

DEFAULT_SLOPE_INVENTORY = [
    {"邊坡編號": "台9線-108K+500", "路段名稱": "蘇澳東澳段", "所屬雨量分區": "蘇澳地區", "邊坡分級": "C", "RHRS中高風險": "否", "復建完工日": "2022-10-01", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線-114K+200", "路段名稱": "東澳段", "所屬雨量分區": "東澳地區", "邊坡分級": "A", "RHRS中高風險": "是", "復建完工日": "2025-04-15", "具遠端致災因素": "是"},
    {"邊坡編號": "台9丁線-16K+800", "路段名稱": "東澳舊線", "所屬雨量分區": "東澳地區", "邊坡分級": "B", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "否"},
    {"邊坡編號": "台9線-119K+500", "路段名稱": "南澳段", "所屬雨量分區": "南澳地區", "邊坡分級": "C+", "RHRS中高風險": "否", "復建完工日": "2023-10-01", "具遠端致災因素": "是"},
    {"邊坡編號": "台9線-129K+800", "路段名稱": "觀音段", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "B", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "否"},
    {"邊坡編號": "台9丁線-38K+600", "路段名稱": "觀音海岸舊線", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "大型地滑/順向坡", "RHRS中高風險": "是", "復建完工日": "", "具遠端致災因素": "是"},
    {"邊坡編號": "台9線-141K+100", "路段名稱": "武塔漢本段", "所屬雨量分區": "武塔觀音漢本區", "邊坡分級": "C", "RHRS中高風險": "否", "復建完工日": "2022-08-20", "具遠端致災因素": "否"},
    {"邊坡編號": "台9丁線-61K+000", "路段名稱": "澳花和平段", "所屬雨量分區": "和平崇德地區", "邊坡分級": "D", "RHRS中高風險": "否", "復建完工日": "", "具遠端致災因素": "否"},
]


# ==========================================
# 2. 區域分類與氣象署 API 串接引擎
# ==========================================
def classify_station_region(county: str, town: str, st_name: str) -> str:
    """根據測站名稱與鄉鎮市區，自動歸類至蘇花五大微氣候防區"""
    for region_name, keywords in REGIONAL_GROUPS.items():
        if any(k in st_name for k in keywords):
            return region_name
    # 若站名無直接命中，依鄉鎮歸類
    if "蘇澳" in town:
        return "蘇澳地區"
    if "南澳" in town:
        return "南澳地區"
    if "秀林" in town:
        return "和平崇德地區"
    if county == "宜蘭縣":
        return "宜蘭其他區域"
    if county == "花蓮縣":
        return "花蓮其他區域"
    return "其他區域"


@st.cache_data(ttl=600, show_spinner=False)
def fetch_cwa_rainfall_and_envelope(api_key: str):
    """
    串接氣象署 O-A0002-001 自動雨量站 API
    同時回傳：(1) 各測站明細表 df_stations, (2) 區域極值包絡統計表 df_envelope
    """
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0002-001"
    params = {"Authorization": api_key.strip(), "format": "JSON"}
    try:
        resp = requests.get(url, params=params, timeout=12, verify=False)
        resp.raise_for_status()
        data = resp.json()
        stations = data.get("records", {}).get("Station", [])
        
        records = []
        for st_obj in stations:
            geo = st_obj.get("GeoInfo", {})
            county = geo.get("CountyName", "")
            town = geo.get("TownName", "")
            st_name = st_obj.get("StationName", "")
            st_id = st_obj.get("StationId", "")
            
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
                
                # 優先使用氣象署原生 Past2days (48hr)，若無則以 max(24hr, 3days*0.75) 保守包絡
                r_48h = r_2d if r_2d > 0 else max(r_24h, round(r_3d * 0.75, 1))
                region = classify_station_region(county, town, st_name)
                
                records.append({
                    "所屬雨量分區": region,
                    "縣市": county,
                    "鄉鎮": town,
                    "站碼": st_id,
                    "測站名稱": st_name,
                    "10min雨量": r_10m,
                    "1hr雨量(mm)": r_1h,
                    "3hr雨量(mm)": r_3h,
                    "24hr雨量(mm)": r_24h,
                    "48hr雨量(mm)": r_48h,
                    "72hr雨量(mm)": r_3d,
                    "觀測時間": st_obj.get("ObsTime", {}).get("DateTime", "")
                })
                
        df_stations = pd.DataFrame(records)
        if df_stations.empty:
            return pd.DataFrame(), pd.DataFrame()

        # 計算各分區「群組極值包絡 (Regional Max Envelope)」
        envelope_rows = []
        target_regions = list(REGIONAL_GROUPS.keys()) + ["宜蘭其他區域", "花蓮其他區域"]
        for reg in target_regions:
            sub = df_stations[df_stations["所屬雨量分區"] == reg]
            if not sub.empty:
                idx_max3 = sub["3hr雨量(mm)"].idxmax()
                idx_max48 = sub["48hr雨量(mm)"].idxmax()
                max_3h_val = sub.loc[idx_max3, "3hr雨量(mm)"]
                max_3h_st = sub.loc[idx_max3, "測站名稱"]
                max_48h_val = sub.loc[idx_max48, "48hr雨量(mm)"]
                max_48h_st = sub.loc[idx_max48, "測站名稱"]
                
                status_list = []
                if max_3h_val >= 120:
                    status_list.append("🚨 3hr≥120mm 達標")
                if max_48h_val >= 350:
                    status_list.append("🚨 48hr≥350mm 達標")
                
                envelope_rows.append({
                    "所屬雨量分區": reg,
                    "納入分析測站數": len(sub),
                    "區內最大3hr雨量(mm)": max_3h_val,
                    "3hr極值代表站": max_3h_st,
                    "區內最大48hr雨量(mm)": max_48h_val,
                    "48hr極值代表站": max_48h_st,
                    "分區門檻觸發狀態": " / ".join(status_list) if status_list else "🟢 未達門檻",
                    "納入測站清單": "、".join(sub["測站名稱"].tolist())
                })
        df_envelope = pd.DataFrame(envelope_rows)
        return df_stations, df_envelope
    except Exception as e:
        st.error(f"CWA 雨量 API 拉取失敗：{e}")
        return pd.DataFrame(), pd.DataFrame()


@st.cache_data(ttl=600, show_spinner=False)
def fetch_cwa_earthquake(api_key: str) -> list:
    url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001"
    params = {"Authorization": api_key.strip(), "format": "JSON", "limit": 5}
    try:
        resp = requests.get(url, params=params, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        eq_list = data.get("records", {}).get("Earthquake", [])
        parsed = []
        for eq in eq_list:
            info = eq.get("EarthquakeInfo", {})
            shaking_areas = eq.get("Intensity", {}).get("ShakingArea", [])
            max_rank = 0
            detail_areas = []
            for area in shaking_areas:
                c_name = area.get("CountyName", "")
                if any(k in c_name for k in ["宜蘭", "花蓮"]):
                    intensity_str = area.get("AreaIntensity", "0級")
                    rank = SEISMIC_RANK.get(intensity_str, 0)
                    if rank > max_rank:
                        max_rank = rank
                    detail_areas.append(f"{c_name}({intensity_str})")
            parsed.append({
                "發震時間": info.get("OriginTime", ""),
                "震央位置": info.get("Epicenter", {}).get("Location", ""),
                "規模": info.get("EarthquakeMagnitude", {}).get("MagnitudeValue", ""),
                "宜花最大震度": RANK_TO_SEISMIC.get(max_rank, "0級"),
                "宜花各區震度": ", ".join(set(detail_areas)) if detail_areas else "未達顯著震度"
            })
        return parsed
    except Exception:
        return []


# ==========================================
# 3. 115年10月版養護手冊 SOP 律定決策演算法
# ==========================================
def evaluate_slope_sop(
    slope_grade: str,
    is_rhrs_high: bool,
    seismic_str: str,
    rain_3h: float,
    rain_48h: float,
    is_typhoon: bool,
    is_debris_red: bool,
    collapse_m3: float
) -> dict:
    insp_actions = []
    mgmt_actions = []
    bridge_actions = []
    
    # 整理分級字串 (兼容 Excel 可能出現的 "A級" -> "A")
    clean_grade = str(slope_grade).replace("級邊坡", "").replace("級", "").strip()
    if "地滑" in clean_grade or "順向" in clean_grade:
        clean_grade = "大型地滑/順向坡"

    effective_grade = clean_grade
    upgraded_flag = False
    if collapse_m3 >= 5000 and clean_grade in ["B", "C+", "C", "D", "大型地滑/順向坡"]:
        effective_grade = "A"
        upgraded_flag = True

    s_rank = SEISMIC_RANK.get(seismic_str, 0)

    # 震災邏輯 (附錄3 & 附錄2情境四)
    if s_rank == 4:
        if is_rhrs_high or effective_grade in ["A", "B"]:
            insp_actions.append("【震度4級】立即巡查震區內「優先關注邊坡」(RHRS中高風險)")
    elif s_rank == 5:
        insp_actions.append("【震度5弱】立即特別巡查公路構造物、邊坡、特別照護喬木")
    elif s_rank == 6:
        insp_actions.append("【震度5強】立即特別巡查公路構造物、邊坡、特別照護喬木")
        bridge_actions.append("【震度5強】立即巡查震區內橋梁，並特別檢測 A、B、C、E 類橋梁")
    elif s_rank >= 7:
        mgmt_actions.append("🚨【震度6弱以上-處置6】成立「大規模震災」緊急應變小組，依標準作業程序辦理")
        bridge_actions.append("🚨【震度6弱以上】立即辦理震區內「所有橋梁」特別檢測")
        if effective_grade in ["A", "B", "C+", "C"]:
            insp_actions.append("【震度6弱以上-處置3】(1) 7日內完成特別檢測 (2) 實施朝巡1週 (3) 取得空拍或衛星影像")
        elif effective_grade == "D":
            insp_actions.append("【震度6弱以上-處置1】2日內實施特別巡查")
        elif effective_grade == "大型地滑/順向坡":
            insp_actions.append("【震度6弱以上-處置2】14日內完成特別檢測")

    # 情境一：3小時累積雨量 >= 120mm
    if rain_3h >= 120.0:
        insp_actions.append(f"【情境一：分區3hr雨量達 {rain_3h}mm (≥120mm)-處置1】2日內實施特別巡查")
        if effective_grade in ["A", "B"]:
            mgmt_actions.append("【情境一養護-處置3】實施巡查作業")
        else:
            mgmt_actions.append("【情境一養護-處置4】揭露路段強降雨訊息")

    # 情境二：48小時累積雨量 >= 350mm
    if rain_48h >= 350.0:
        if effective_grade in ["A", "大型地滑/順向坡"]:
            insp_actions.append(f"【情境二：分區48hr雨量達 {rain_48h}mm (≥350mm)-處置2】14日內完成特別檢測")
        elif effective_grade == "B":
            insp_actions.append(f"【情境二：分區48hr雨量達 {rain_48h}mm (≥350mm)-處置1】2日內實施特別巡查")
        
        if effective_grade in ["A", "B", "大型地滑/順向坡"]:
            mgmt_actions.append("【情境二養護-處置1】降低雨量門檻值")
        else:
            mgmt_actions.append("【情境二養護-處置2】加強水情監控")

    # 情境三：海上颱風警報
    if is_typhoon:
        insp_actions.append("【情境三：海警解除後-處置1】2日內實施特別巡查")
        mgmt_actions.append("【情境三養護-處置5】颱風警報期間，依「公路防災預警機制」辦理")

    # 情境五：無預警大規模坍方搶通後
    if 5000 <= collapse_m3 < 20000:
        insp_actions.append("【情境五：坍方 5,000~20,000m³ 搶通後-處置4(1)】實施朝巡、暮巡 1 週")
    elif collapse_m3 >= 20000:
        insp_actions.append("【情境五：坍方 ≥20,000m³ 搶通後-處置4(1)&(2)】(1) 朝巡、暮巡 1 週 (2) 取得空拍或衛星影像")
        mgmt_actions.append("【情境五養護-處置7】執行保全守視（必要時交通管制）")

    # 情境六：土石流紅色警戒
    if is_debris_red:
        insp_actions.append("【情境六：土石流紅色警戒-處置1】2日內實施特別巡查")
        if effective_grade in ["A", "B", "C+", "大型地滑/順向坡"]:
            mgmt_actions.append("【情境六養護-處置8】擬定加碼部署策略，按計畫執行")

    if not insp_actions and not mgmt_actions:
        insp_actions.append("🟢 常態週期：車巡 1次/週 (下邊坡1次/季)、步巡 1次/月、定期檢查 1次/年")

    return {
        "effective_grade": effective_grade,
        "upgraded_flag": upgraded_flag,
        "inspection": "；".join(insp_actions),
        "management": "；".join(mgmt_actions) if mgmt_actions else "常態養護管理",
        "bridge": "；".join(bridge_actions) if bridge_actions else "無特殊橋梁震災指令"
    }


def auto_assign_region_by_text(text_val: str) -> str:
    """根據 Excel 中的路段名稱或里程文字，自動推論所屬雨量分區"""
    t = str(text_val)
    for reg, kws in REGIONAL_GROUPS.items():
        if any(k in t for k in kws):
            return reg
    return "南澳地區" # 預設歸入南澳工務段核心區


# ==========================================
# 4. Streamlit 介面主架構
# ==========================================
def render_app():
    st.set_page_config(page_title="蘇花廊道區域雨量包絡與邊坡SOP決策系統", layout="wide")

    if "disaster_db" not in st.session_state:
        st.session_state.disaster_db = pd.DataFrame(DEFAULT_DISASTER_HISTORY)
    if "slope_db" not in st.session_state:
        st.session_state.slope_db = pd.DataFrame(DEFAULT_SLOPE_INVENTORY)

    # 側邊欄：API 設定與 .xlsx 邊坡全生命週期資料庫掛載
    with st.sidebar:
        st.header("⚙️ 資料管線與 Excel 掛載設定")
        api_key = st.text_input("🔑 氣象署 API 授權碼", value=DEFAULT_CWA_API_KEY, type="password")
        if st.button("🔄 立即強制刷新氣象署 API 數據"):
            st.cache_data.clear()
            st.rerun()

        st.divider()
        st.subheader("📂 掛載「南澳邊坡全生命週期資料庫 (.xlsx)」")
        
        # 自動掃描同目錄下是否有 .xlsx 檔案
        local_xlsx_files = [f.name for f in Path(".").glob("*.xlsx") if not f.name.startswith("~$")]
        uploaded_xlsx = st.file_uploader("上傳邊坡資料庫 Excel 檔 (.xlsx)", type=["xlsx"])
        
        raw_excel_df = None
        if uploaded_xlsx is not None:
            xl = pd.ExcelFile(uploaded_xlsx)
            sheet = st.selectbox("選擇工作表 (Sheet)", xl.sheet_names)
            raw_excel_df = xl.parse(sheet)
            st.success(f"已載入上傳檔案：{uploaded_xlsx.name} ({len(raw_excel_df)} 筆)")
        elif local_xlsx_files:
            sel_local = st.selectbox("或選擇 SOP 資料夾內既有 Excel 檔", ["(使用系統預設範例口卡)"] + local_xlsx_files)
            if sel_local != "(使用系統預設範例口卡)":
                xl = pd.ExcelFile(sel_local)
                sheet = st.selectbox("選擇工作表 (Sheet)", xl.sheet_names)
                raw_excel_df = xl.parse(sheet)
                st.success(f"已直接讀取本地檔案：{sel_local} ({len(raw_excel_df)} 筆)")

        # 動態欄位映射器 (Schema Mapper)：不論您的 Excel 欄位叫什麼名字，都能直接對應
        if raw_excel_df is not None and not raw_excel_df.empty:
            with st.expander("🔗 Excel 欄位智慧對應設定", expanded=True):
                cols = raw_excel_df.columns.tolist()
                c_id = st.selectbox("對應【邊坡編號/樁號】欄位", cols, index=0)
                c_loc = st.selectbox("對應【路段/地名描述】欄位 (用於自動歸類雨量分區)", cols, index=min(1, len(cols)-1))
                c_grade = st.selectbox("對應【邊坡分級(A/B/C+/C/D)】欄位", cols, index=min(2, len(cols)-1))
                c_rhrs = st.selectbox("對應【RHRS中高風險/優先關注】欄位 (選填)", ["(無對應欄位，預設A/B級為是)"] + cols)
                
                if st.button("✅ 套用 Excel 資料至決策引擎"):
                    mapped_rows = []
                    for _, r in raw_excel_df.iterrows():
                        s_id = str(r[c_id])
                        s_loc = str(r[c_loc])
                        s_grade = str(r[c_grade])
                        s_reg = auto_assign_region_by_text(f"{s_id} {s_loc}")
                        is_rhrs = "是" if (c_rhrs == "(無對應欄位，預設A/B級為是)" and any(g in s_grade for g in ["A", "B"])) else str(r.get(c_rhrs, "否"))
                        mapped_rows.append({
                            "邊坡編號": s_id,
                            "路段名稱": s_loc,
                            "所屬雨量分區": s_reg,
                            "邊坡分級": s_grade,
                            "RHRS中高風險": "是" if any(k in is_rhrs for k in ["是", "True", "高", "中", "1"]) else "否",
                            "復建完工日": "",
                            "具遠端致災因素": "是" if "C+" in s_grade else "否"
                        })
                    st.session_state.slope_db = pd.DataFrame(mapped_rows)
                    st.toast("已成功將 Excel 邊坡資料庫同步至派工決策引擎！")

    # 主畫面標題與氣象署快速查核列
    st.markdown("## 🛡️ 蘇花廊道（宜花地區）區域雨量包絡暨邊坡巡查自動化決策系統")
    st.caption("法規依據：115年10月版《養護手冊-路基及邊坡巡查-懶人包》｜雨量分析邏輯：採用【區域測站群組最大值包絡法】(例如：東澳地區自動納入東澳、東澳嶺等所有鄰近測站取極值)")

    # 預先拉取氣象署即時資料
    df_stations, df_envelope = fetch_cwa_rainfall_and_envelope(api_key)
    eq_records = fetch_cwa_earthquake(api_key)

    # 頂部即時水情看板 (Metrics)
    if not df_envelope.empty:
        st.markdown("##### 📊 蘇花五大微氣候防區即時雨量極值包絡看板 (每 10 分鐘同步中央氣象署 API)")
        core_env = df_envelope[df_envelope["所屬雨量分區"].isin(REGIONAL_GROUPS.keys())]
        cols_m = st.columns(len(core_env))
        for idx, (_, row_e) in enumerate(core_env.iterrows()):
            with cols_m[idx]:
                r3 = row_e["區內最大3hr雨量(mm)"]
                r48 = row_e["區內最大48hr雨量(mm)"]
                st_3 = row_e["3hr極值代表站"]
                alert_flag = (r3 >= 120 or r48 >= 350)
                st.metric(
                    label=f"📍 {row_e['所屬雨量分區']} ({row_e['納入分析測站數']}站)",
                    value=f"3hr: {r3} mm",
                    delta=f"48hr: {r48} mm (極值站:{st_3})",
                    delta_color="inverse" if alert_flag else "normal"
                )

    tab1, tab2, tab3, tab4 = st.tabs([
        "📡 1. 區域雨量群組包絡明細 (CWA即時連線)",
        "⚙️ 2. 轄區邊坡口卡 × 區域雨量自動派工引擎",
        "📅 3. 宜花歷年天災時序查詢 (依日期先後順序)",
        "📉 4. 115年修訂：A級邊坡降等與汛期壓力測試"
    ])

    # --------------------------------------------------
    # Tab 1: 區域雨量群組包絡與測站明細
    # --------------------------------------------------
    with tab1:
        st.subheader("📡 宜蘭/花蓮各分區雨量站群組極值包絡表")
        st.markdown("""
        **為什麼採用群組包絡？** 當法定指標雨量站未明定時，系統自動將各分區（如**東澳地區**包含東澳、東澳嶺；**南澳地區**包含南澳、碧候、古魯；**武塔觀音漢本區**包含觀音海岸、武塔、澳花等）所有測站納入，並以**該區最高雨量**作為觸發門檻（$3\text{hr} \ge 120\text{mm}$ 或 $48\text{hr} \ge 350\text{mm}$）之判定依據。
        * 🔗 [點此開啟：中央氣象署即時雨量觀測網頁核對](https://www.cwa.gov.tw/V8/C/P/Rainfall/Rainfall_QZJ.html)
        """)
        
        if not df_envelope.empty:
            st.dataframe(df_envelope, use_container_width=True, hide_index=True)
            
            st.markdown("##### 🔍 檢視單一分區底下所有納入分析之氣象署雨量站明細")
            sel_reg_view = st.selectbox("選擇欲展開檢視之雨量分區：", ["顯示宜花全部測站"] + df_envelope["所屬雨量分區"].tolist())
            sub_st = df_stations if sel_reg_view == "顯示宜花全部測站" else df_stations[df_stations["所屬雨量分區"] == sel_reg_view]
            st.dataframe(sub_st.sort_values(by=["3hr雨量(mm)", "48hr雨量(mm)"], ascending=False), use_container_width=True, hide_index=True)
        else:
            st.warning("目前無法取得氣象署雨量站明細，請檢查網路連線或 API 授權碼。")

        if eq_records:
            st.markdown("##### 🌋 氣象署最新顯著有感地震報告 (`E-A0015-001`)")
            st.dataframe(pd.DataFrame(eq_records), use_container_width=True, hide_index=True)

    # --------------------------------------------------
    # Tab 2: 轄區邊坡口卡 × 區域雨量自動派工引擎
    # --------------------------------------------------
    with tab2:
        st.subheader("⚙️ 轄區邊坡口卡批次派工決策引擎 (自動讀取各邊坡所屬分區之最大雨量)")
        
        mode_choice = st.radio(
            "選擇外力參數驅動模式：",
            ["🟢 模式 A：直接以【氣象署 API 即時分區包絡雨量】自動派工", "🧪 模式 B：載入【歷年天災事件 / 手動模擬壓力測試】派工"],
            horizontal=True
        )

        # 建立各分區雨量查找字典 {region: (rain_3h, rain_48h, rep_station)}
        region_rain_map = {}
        if not df_envelope.empty:
            for _, r_env in df_envelope.iterrows():
                region_rain_map[r_env["所屬雨量分區"]] = (
                    float(r_env["區內最大3hr雨量(mm)"]),
                    float(r_env["區內最大48hr雨量(mm)"]),
                    r_env["3hr極值代表站"]
                )

        if "模式 A" in mode_choice:
            c1, c2, c3, c4 = st.columns(4)
            default_eq = eq_records[0]["宜花最大震度"] if eq_records else "0級"
            sim_seis = c1.selectbox("當前宜花最大震度", list(SEISMIC_RANK.keys()), index=list(SEISMIC_RANK.keys()).index(default_eq))
            sim_col = c2.number_input("無預警坍方規模 (m³)", value=0, step=1000)
            sim_ty = c3.checkbox("海上颱風警報解除/期間", value=False)
            sim_deb = c4.checkbox("鄰河側土石流紅色警戒", value=False)
            override_rain = False
        else:
            override_rain = True
            event_options = ["手動自訂模擬參數"] + [f"{r['date']} | {r['name']} ({r['region']})" for _, r in st.session_state.disaster_db.iterrows()]
            sel_ev = st.selectbox("📥 選擇歷史天災事件帶入參數：", event_options)
            
            def_seis, def_r3, def_r48, def_ty, def_col = "0級", 135.0, 380.0, False, 0
            if sel_ev != "手動自訂模擬參數":
                ev_date = sel_ev.split(" | ")[0]
                ev_name = sel_ev.split(" | ")[1].split(" (")[0]
                row = st.session_state.disaster_db[(st.session_state.disaster_db["date"] == ev_date) & (st.session_state.disaster_db["name"] == ev_name)].iloc[0]
                def_seis, def_r3, def_r48 = row["max_seismic"], float(row["max_rain_3h"]), float(row["max_rain_48h"])
                def_ty, def_col = (row["type"] == "颱風"), int(row["collapse_m3"])

            p1, p2, p3, p4, p5, p6 = st.columns(6)
            sim_seis = p1.selectbox("模擬最大震度", list(SEISMIC_RANK.keys()), index=list(SEISMIC_RANK.keys()).index(def_seis))
            sim_r3_manual = p2.number_input("模擬 3hr 雨量 (mm)", value=def_r3, step=10.0)
            sim_r48_manual = p3.number_input("模擬 48hr 雨量 (mm)", value=def_r48, step=20.0)
            sim_col = p4.number_input("無預警坍方量 (m³)", value=def_col, step=1000)
            sim_ty = p5.checkbox("海上颱風警報", value=def_ty)
            sim_deb = p6.checkbox("土石流紅色警戒", value=False)

        # 批次掃描每一處邊坡口卡
        dispatch_rows = []
        bridge_alert = "無特殊橋梁震災指令"
        for _, slope in st.session_state.slope_db.iterrows():
            s_reg = slope["所屬雨量分區"]
            if not override_rain and s_reg in region_rain_map:
                r3_val, r48_val, rep_st = region_rain_map[s_reg]
                rain_src_str = f"{s_reg}極值 ({rep_st}: 3h={r3_val}/48h={r48_val}mm)"
            elif not override_rain:
                r3_val, r48_val = 0.0, 0.0
                rain_src_str = f"{s_reg} (無即時超標測站)"
            else:
                r3_val, r48_val = sim_r3_manual, sim_r48_manual
                rain_src_str = f"模擬測試值 (3h={r3_val}/48h={r48_val}mm)"

            res = evaluate_slope_sop(
                slope_grade=slope["邊坡分級"],
                is_rhrs_high=(slope["RHRS中高風險"] == "是"),
                seismic_str=sim_seis,
                rain_3h=r3_val,
                rain_48h=r48_val,
                is_typhoon=sim_ty,
                is_debris_red=sim_deb,
                collapse_m3=sim_col
            )
            bridge_alert = res["bridge"]
            dispatch_rows.append({
                "邊坡編號": slope["邊坡編號"],
                "路段名稱": slope["路段名稱"],
                "所屬雨量分區与極值來源": rain_src_str,
                "原分級": slope["邊坡分級"],
                "處置適用分級": "🔥 強制比照 A 級" if res["upgraded_flag"] else res["effective_grade"],
                "RHRS優先關注": slope["RHRS中高風險"],
                "法定巡查與特別檢測派工指令 (附錄1~3)": res["inspection"],
                "防災管制與養護管理機制 (附錄2)": res["management"]
            })

        if bridge_alert != "無特殊橋梁震災指令":
            st.error(f"🌉 **震災橋梁專案檢測指令 (附錄3)**：{bridge_alert}")

        df_dispatch = pd.DataFrame(dispatch_rows)
        st.dataframe(df_dispatch, use_container_width=True, hide_index=True)

        csv_bytes = df_dispatch.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 匯出分區邊坡特別巡查/特別檢測派工單 (CSV)",
            data=csv_bytes,
            file_name=f"南澳段邊坡防災派工單_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

    # --------------------------------------------------
    # Tab 3: 宜花歷年天災時序查詢
    # --------------------------------------------------
    with tab3:
        st.subheader("📅 宜蘭/花蓮歷年天災事件簿 (依日期先後順序查詢)")
        c_f1, c_f2, c_f3, c_f4 = st.columns(4)
        df_hist = st.session_state.disaster_db.copy()
        df_hist["year"] = df_hist["date"].str.slice(0, 4)

        with c_f1:
            sel_y = st.selectbox("篩選年份", ["全部年份"] + sorted(df_hist["year"].unique().tolist(), reverse=True))
        with c_f2:
            sel_t = st.multiselect("災害類別", ["地震", "颱風", "豪雨"], default=["地震", "颱風", "豪雨"])
        with c_f3:
            sort_dir = st.radio("日期先後排序", ["由新到舊 (最新優先)", "由舊到新 (時間軸先後順序)"], horizontal=True)
        with c_f4:
            kw_s = st.text_input("搜尋分區/事件關鍵字", placeholder="例：東澳、南澳、凱米...")

        if sel_y != "全部年份":
            df_hist = df_hist[df_hist["year"] == sel_y]
        if sel_t:
            df_hist = df_hist[df_hist["type"].isin(sel_t)]
        if kw_s:
            df_hist = df_hist[df_hist["name"].str.contains(kw_s, case=False) | df_hist["region"].str.contains(kw_s, case=False) | df_hist["note"].str.contains(kw_s, case=False)]

        df_hist = df_hist.sort_values(by="date", ascending=(sort_dir == "由舊到新 (時間軸先後順序)")).drop(columns=["year"])
        st.dataframe(df_hist, use_container_width=True, hide_index=True)

        # 快速把當日氣象署 API 抓到的極值一鍵寫入歷史事件簿
        with st.expander("➕ 將今日氣象署分區極值或新天災事件寫入歷史資料庫"):
            with st.form("new_ev_form"):
                f1, f2, f3, f4 = st.columns(4)
                in_date = f1.date_input("發生日期", value=date.today())
                in_type = f2.selectbox("災害類別", ["豪雨", "颱風", "地震"])
                in_reg = f3.selectbox("主要受災雨量分區", list(REGIONAL_GROUPS.keys()))
                in_name = f4.text_input("事件名稱", placeholder="例：1016 東澳嶺共伴豪雨")
                
                def_r3_now, def_r48_now, _ = region_rain_map.get(in_reg, (0.0, 0.0, ""))
                f5, f6, f7, f8 = st.columns(4)
                in_seis = f5.selectbox("最大震度", list(SEISMIC_RANK.keys()))
                in_r3 = f6.number_input("分區最大 3hr 雨量 (mm)", value=def_r3_now)
                in_r48 = f7.number_input("分區最大 48hr 雨量 (mm)", value=def_r48_now)
                in_col = f8.number_input("坍方規模 (m³)", value=0, step=500)
                in_note = st.text_input("災情與處置備註")
                
                if st.form_submit_button("💾 寫入歷史天災時序表"):
                    new_r = {
                        "date": in_date.strftime("%Y-%m-%d"), "type": in_type, "name": in_name or f"{in_reg}{in_type}事件",
                        "max_seismic": in_seis, "max_rain_3h": in_r3, "max_rain_48h": in_r48,
                        "region": in_reg, "collapse_m3": in_col, "note": in_note
                    }
                    st.session_state.disaster_db = pd.concat([st.session_state.disaster_db, pd.DataFrame([new_r])], ignore_index=True)
                    st.success("已成功新增至歷年天災時序資料庫！")
                    st.rerun()

    # --------------------------------------------------
    # Tab 4: 115年5月修訂 A級邊坡降等檢核
    # --------------------------------------------------
    with tab4:
        st.subheader("📉 115年修訂：A級邊坡降等資格暨「汛期自然外力壓力測試」檢核")
        st.caption("依據：115年5月19日路養護字第1155009531號函 (須歷經至少1個完整汛期 5/1~11/30，並於汛期結束後由分局召開專家會議研商降至 C+ 或 C 級)")
        
        d1, d2, d3 = st.columns(3)
        rehab_dt = d1.date_input("1. 復建工程完工日期", value=date(2025, 4, 15))
        eval_dt = d2.date_input("2. 提報審查日期 (須於11/30汛期結束後)", value=date(2026, 12, 5))
        remote_chk = d3.selectbox("3. C+級邊坡快篩調查表 (4類遠端致災因素)", ["具遠端致災因素 (上/下邊坡、曲流/浪襲、坡頂開發、明隧道上方)", "無遠端致災因素且無明顯不穩定徵兆"])

        full_seasons = [y for y in range(rehab_dt.year, eval_dt.year + 1) if rehab_dt <= date(y, 5, 1) and eval_dt > date(y, 11, 30)]
        df_h = st.session_state.disaster_db.copy()
        df_h["dt"] = pd.to_datetime(df_h["date"]).dt.date
        exp_ev = df_h[(df_h["dt"] >= rehab_dt) & (df_h["dt"] <= eval_dt)]

        m1, m2, m3 = st.columns(3)
        m1.metric("完整經歷汛期數", f"{len(full_seasons)} 個", f"通過年份: {full_seasons}" if full_seasons else "未滿1個完整汛期")
        m2.metric("期間經歷宜花天災次數", f"{len(exp_ev)} 次")
        max_48 = exp_ev["max_rain_48h"].max() if not exp_ev.empty else 0.0
        m3.metric("期間承受最大 48hr 雨量", f"{max_48} mm")

        if len(full_seasons) >= 1 and not (5 <= eval_dt.month <= 11):
            tgt = "C+ 級" if "具遠端" in remote_chk else "C 級"
            st.success(f"✅ **符合提報降等審查資格**：已歷經 {full_seasons} 完整汛期，期間承受最大 48hr 雨量達 {max_48}mm。請檢具致災原因探討、削減措施說明及安定分析/影像佐證，提請東區養護工程分局召會調降為 **{tgt}**。")
        else:
            st.error("❌ **尚未符合法定啟動時機**：必須完整跨越至少 1 個汛期（5/1～11/30），且申請日須於年度汛期結束後（12月1日起）。")

if __name__ == "__main__":
    render_app()
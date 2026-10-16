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

        /* 下拉選單 (Selectbox) 與輸入框字體全面放大 */
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

        /* 動態視覺橫幅動畫 (修正上邊距與 padding，防止字被卡住) */
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
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .hero-banner {
            position: relative;
            overflow: hidden;
            background: linear-gradient(-45deg, #0f172a, #1e3a8a, #0f766e, #1e293b);
            background-size: 300% 300%;
            animation: gradientBG 10s ease infinite, slideDownFade 0.7s ease-out;
            border-radius: 18px;
            padding: 28px 22px 22px 22px; /* 增加上方 padding 至 28px，徹底解決卡字問題 */
            border: 1px solid rgba(56, 189, 248, 0.35);
            box-shadow: 0 12px 28px -6px rgba(0, 0, 0, 0.6);
            margin-top: 15px;  /* 增加與頂部的距離 */
            margin-bottom: 18px;
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
            background: rgba(15, 23, 42, 0.75);
            border: 1px solid #f59e0b;
            color: #fbbf24;
            padding: 4px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 800;
            margin-bottom: 10px;
        }
        .radar-dot {
            width: 10px;
            height: 10px;
            background-color: #f59e0b;
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
            background: rgba(15, 23, 42, 0.55);
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 4px solid #38bdf8;
        }
    </style>
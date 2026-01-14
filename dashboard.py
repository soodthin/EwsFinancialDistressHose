import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF
from datetime import datetime
import io

# -----------------------------------------
# 1. CONFIG
# -----------------------------------------
st.set_page_config(
    page_title="Financial Distress EWS Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------
# CUSTOM CSS
# -----------------------------------------
st.markdown("""
<style>
/* ========== FADE-IN ANIMATION ========== */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Apply fade-in to main sections */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    animation: fadeInUp 0.5s ease-out forwards;
}

/* Staggered animation for multiple sections */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:nth-child(1) { animation-delay: 0.1s; }
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:nth-child(2) { animation-delay: 0.2s; }
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:nth-child(3) { animation-delay: 0.3s; }

/* ========== SECTION TITLE ========== */
.section-title {
    background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 50%, #3182ce 100%);
    color: white !important;
    padding: 0.85rem 1.5rem;
    border-radius: 10px;
    margin-bottom: 1.25rem;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.3px;
    box-shadow: 0 4px 15px rgba(30, 58, 95, 0.3);
    text-shadow: 0 1px 2px rgba(0,0,0,0.1);
}

/* ========== CARD CONTAINERS WITH HOVER ========== */
[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(128,128,128,0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 30px rgba(128,128,128,0.15);
    transform: translateY(-2px);
}

/* ========== METRIC CARDS ========== */
[data-testid="stMetric"] {
    padding: 1rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    background: rgba(128,128,128,0.08);
    border: 1px solid rgba(128,128,128,0.15);
}

[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 12px rgba(128,128,128,0.2);
    transform: scale(1.02);
    background: rgba(128,128,128,0.12);
}

[data-testid="stMetric"] label {
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-weight: 700 !important;
    font-size: 1.5rem !important;
}

/* ========== CHARTS STYLING ========== */
[data-testid="stPlotlyChart"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(128,128,128,0.1);
    transition: all 0.3s ease;
}

[data-testid="stPlotlyChart"]:hover {
    box-shadow: 0 6px 20px rgba(128,128,128,0.15);
}

/* ========== SIDEBAR IMPROVEMENTS ========== */
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding-top: 0.5rem !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {
    font-weight: 700 !important;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #3182ce;
    margin-bottom: 0.75rem !important;
    margin-top: 0 !important;
}

[data-testid="stSidebar"] .stSelectbox,
[data-testid="stSidebar"] .stSlider {
    padding: 0.5rem;
    border-radius: 10px;
    margin-bottom: 0.5rem;
}

/* ========== TABS STYLING ========== */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    padding: 0.5rem;
    border-radius: 12px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.6rem 1.25rem;
    font-weight: 600;
    transition: all 0.2s ease;
}

/* ========== ALERT BOXES ========== */
.stAlert {
    border-radius: 10px;
    border-left-width: 4px;
    font-weight: 500;
}

/* ========== DATAFRAME ========== */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(128,128,128,0.1);
}

/* ========== BUTTONS ========== */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
}

/* ========== EXPANDER ========== */
[data-testid="stExpander"] {
    border-radius: 12px;
    overflow: hidden;
}

[data-testid="stExpander"] summary {
    font-weight: 600;
    padding: 1rem;
}

/* ========== TYPOGRAPHY & SPACING ========== */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 2.5rem;
    max-width: 1400px;
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -0.5px;
}

p, span, label {
    line-height: 1.6;
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}

/* ========== DIVIDER STYLING ========== */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(128,128,128,0.5), transparent);
    margin: 1.5rem 0;
}

/* ========== RISK INDICATOR ========== */
.risk-safe {
    background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%);
    color: white;
    padding: 2rem 1.5rem;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(46, 204, 113, 0.35);
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.risk-watchlist {
    background: linear-gradient(135deg, #F1C40F 0%, #F39C12 100%);
    color: white;
    padding: 2rem 1.5rem;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(241, 196, 15, 0.35);
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.risk-distress {
    background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%);
    color: white;
    padding: 2rem 1.5rem;
    border-radius: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(231, 76, 60, 0.35);
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}

.risk-safe h2, .risk-watchlist h2, .risk-distress h2 {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    font-weight: 800;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.risk-safe p, .risk-watchlist p, .risk-distress p {
    font-size: 1rem;
    opacity: 0.95;
    margin: 0;
}

/* ========== FILE UPLOADER ========== */
[data-testid="stFileUploader"] {
    border: 2px dashed #3182ce;
    border-radius: 12px;
    padding: 1rem;
    background: rgba(49, 130, 206, 0.03);
}

[data-testid="stFileUploader"]:hover {
    border-color: #2c5282;
    background: rgba(49, 130, 206, 0.06);
}

/* Uploaded file info */
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] {
    font-weight: 500;
}

/* Year selector height match */
[data-testid="stSelectbox"] > div {
    min-height: 54px;
}

[data-testid="stSelectbox"] > div > div {
    min-height: 54px;
    display: flex;
    align-items: center;
}

/* ========== FINANCIAL OVERVIEW CARDS ========== */
.finance-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1.2rem;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    margin-bottom: 0.5rem;
}

.finance-card-blue {
    background: linear-gradient(135deg, #3182ce 0%, #2c5282 100%);
}

.finance-card-green {
    background: linear-gradient(135deg, #38a169 0%, #276749 100%);
}

.finance-card-orange {
    background: linear-gradient(135deg, #dd6b20 0%, #c05621 100%);
}

.finance-card-purple {
    background: linear-gradient(135deg, #805ad5 0%, #6b46c1 100%);
}

.finance-card h3 {
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 0.3rem;
    opacity: 0.9;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.finance-card h2 {
    font-size: 1.5rem;
    font-weight: 800;
    margin: 0;
}

/* ========== RATIO CARDS ========== */
.ratio-card {
    background: rgba(128,128,128,0.08);
    border: 1px solid rgba(128,128,128,0.15);
    padding: 1rem;
    border-radius: 12px;
    text-align: center;
    transition: all 0.3s ease;
}

.ratio-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(128,128,128,0.15);
}

.ratio-good { border-left: 4px solid #2ECC71; }
.ratio-warning { border-left: 4px solid #F1C40F; }
.ratio-danger { border-left: 4px solid #E74C3C; }

/* ========== SUMMARY BOX ========== */
.summary-box {
    background: linear-gradient(135deg, #1e3a5f 0%, #2c5282 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 15px;
    margin: 1rem 0;
}

.summary-box h3 {
    font-size: 1.1rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid rgba(255,255,255,0.2);
    padding-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------
# 2. MAPPING DICTIONARIES
# -----------------------------------------

# Mapping for CF-Export format (FCC codes) - Based on CF-Export-07-01-2026 (6) (1).xlsx
# NOTE: CF-Export files have Scaling=Thousands, values need to be multiplied by 1000
FCC_MAPPING = {
    # Balance Sheet
    'Total Assets': ['ATOT', 'Total Assets'],
    'Total Current Assets': ['STCA', 'Total Current Assets'],
    'Total Current Liabilities': ['SCLT', 'Total Current Liabilities'],
    'Total Liabilities': ['STLB', 'Total Liabilities'],
    'Total Fixed Assets - Net': ['STNCA', 'Total Fixed Assets - Net'],
    'PPE Net': ['SPPE', 'Property, Plant & Equipment - Net - Total'],
    'Intangible Assets Net': ['SINN', 'Intangible Assets - Total - Net'],
    'Shareholders Equity': ['QTEP', "Shareholders' Equity - Attributable to Parent ShHold - Total",
                           "Shareholders' Equity - Attributable to Parent Shareholders - Total"],
    'Total Equity': ['STLE', "Total Shareholders' Equity - including Minority Interest & Hybrid Debt"],
    'Retained Earnings': ['SRED', 'Retained Earnings - Total'],
    # Income Statement
    'Revenue': ['STLR', 'Revenue from Business Activities - Total'],
    'Net Income after Tax': ['SIAT', 'Net Income after Tax'],
    'Income before Taxes': ['SIBT', 'Income before Taxes'],
    'EBIT': ['SEBIT', 'Earnings before Interest & Taxes (EBIT)'],
    # Interest Expense - Net of (Interest Income) = SNII
    'Interest Expense': ['SNII', 'Interest Expense - Net of (Interest Income)']
}

# Mapping for Vietnamese BCTC format - Based on TLG financial statement format
# NOTE: Vietnamese BCTC files typically use "Nghìn đồng" (thousands) as unit
VN_MAPPING = {
    # Balance Sheet (Cân đối kế toán)
    'Total Assets': ['TỔNG TÀI SẢN', 'TỔNG CỘNG TÀI SẢN', 'Tổng cộng tài sản', 'Tổng tài sản'],
    'Total Current Assets': ['A. TÀI SẢN NGẮN HẠN', 'TÀI SẢN NGẮN HẠN', 'A. Tài sản ngắn hạn', 'Tài sản ngắn hạn'],
    'Total Current Liabilities': ['I. Nợ ngắn hạn', 'Nợ ngắn hạn', 'NỢ NGẮN HẠN'],
    'Total Liabilities': ['C. NỢ PHẢI TRẢ', 'NỢ PHẢI TRẢ', 'C. Nợ phải trả', 'Nợ phải trả', 'Tổng nợ phải trả'],
    'Total Fixed Assets - Net': ['II. Tài sản cố định', 'Tài sản cố định', 'TÀI SẢN CỐ ĐỊNH'],
    'Shareholders Equity': ['D. VỐN CHỦ SỞ HỮU', 'VỐN CHỦ SỞ HỮU', 'D. Vốn chủ sở hữu', 'Vốn chủ sở hữu', 'I. Vốn chủ sở hữu'],
    'Retained Earnings': ['Lợi nhuận sau thuế chưa phân phối', '11. Lợi nhuận sau thuế chưa phân phối', 'LNST chưa phân phối'],
    # Fixed Assets components for calculation: TSCĐ = TSCĐ hữu hình + TSCĐ thuê tài chính + TSCĐ vô hình
    'Tangible Fixed Assets Net': ['1. Tài sản cố định hữu hình', 'Tài sản cố định hữu hình', 'TSCĐ hữu hình'],
    'Leased Fixed Assets Net': ['2. Tài sản cố định thuê tài chính', 'Tài sản cố định thuê tài chính', 'TSCĐ thuê tài chính'],
    'Intangible Fixed Assets Net': ['3. Tài sản cố định vô hình', 'Tài sản cố định vô hình', 'TSCĐ vô hình'],
    # Income Statement (Báo cáo thu nhập)
    'Revenue': ['1. Doanh thu bán hàng và cung cấp dịch vụ', 'Doanh thu bán hàng và cung cấp dịch vụ', 'Doanh thu thuần', 'Doanh thu'],
    'Net Income after Tax': ['18. Lợi nhuận sau thuế', 'Lợi nhuận sau thuế', '20. Lợi nhuận sau thuế của công ty mẹ', 'LNST'],
    'Income before Taxes': ['15. Tổng lợi nhuận kế toán trước thuế', 'Tổng lợi nhuận kế toán trước thuế', 'Lợi nhuận trước thuế'],
    'EBIT': ['11. Lợi nhuận thuần từ hoạt động kinh doanh', 'Lợi nhuận thuần từ hoạt động kinh doanh', 'Lợi nhuận từ HĐKD'],
    'Interest Expense': ['- Trong đó: Chi phí lãi vay', 'Chi phí lãi vay', 'Lãi vay'],
    # Components for Net Interest Expense calculation: Chi phí lãi vay (ròng) = Chi phí tài chính - Doanh thu tài chính
    'Financial Expenses': ['7. Chi phí tài chính', 'Chi phí tài chính', '6. Chi phí tài chính'],
    'Financial Revenue': ['4. Doanh thu hoạt động tài chính', 'Doanh thu hoạt động tài chính', 'Doanh thu tài chính', '3. Doanh thu hoạt động tài chính']
}

# Vietnamese sheet name mapping
VN_SHEET_NAMES = {
    'balance_sheet': ['Cân đối kế toán', 'CĐKT', 'Balance Sheet', 'Bảng cân đối kế toán'],
    'income_statement': ['Báo cáo thu nhập', 'BCKQKD', 'Kết quả kinh doanh', 'Income Statement', 'Báo cáo kết quả kinh doanh']
}

# Required fields for analysis
REQUIRED_FIELDS = [
    'Total Assets',
    'Total Current Assets',
    'Total Current Liabilities',
    'Total Liabilities',
    'Shareholders Equity',
    'Net Income after Tax',
    'Revenue'
]

OPTIONAL_FIELDS = [
    'Total Fixed Assets - Net',
    'Retained Earnings',
    'EBIT',
    'Income before Taxes',
    'Interest Expense'
]

# -----------------------------------------
# 3. DATA READING FUNCTIONS
# -----------------------------------------

def detect_file_format(df, sheet_name=None):
    """Detect if file is CF-Export format or Vietnamese BCTC format"""
    # Check for FCC codes
    if 'FCC Code' in df.columns or df.iloc[:, 0].astype(str).str.match(r'^[A-Z]{4}$').any():
        return 'cf_export'

    # Check for Vietnamese keywords
    vn_keywords = ['TÀI SẢN', 'NỢ PHẢI TRẢ', 'VỐN CHỦ SỞ HỮU', 'Doanh thu', 'Lợi nhuận']
    text_content = ' '.join(df.iloc[:30, 0].astype(str).tolist())
    if any(kw in text_content for kw in vn_keywords):
        return 'vietnamese'

    return 'unknown'

def find_data_start_row(df):
    """Find the row where actual data starts"""
    for idx, row in df.iterrows():
        # Look for year columns (e.g., 2020, 2021, 2022 or dates)
        row_str = ' '.join([str(x) for x in row.values])
        if any(str(year) in row_str for year in range(2010, 2030)):
            return idx
    return 0

def extract_years_from_columns(df, start_row):
    """Extract year columns from dataframe"""
    years = []
    year_cols = {}

    header_row = df.iloc[start_row] if start_row < len(df) else df.columns

    for idx, val in enumerate(header_row):
        val_str = str(val)
        # Try to extract year
        for year in range(2010, 2030):
            if str(year) in val_str:
                years.append(year)
                year_cols[year] = idx
                break
        # Check for date format
        if '-12-31' in val_str or '-12-30' in val_str:
            try:
                year = int(val_str[:4])
                if 2010 <= year <= 2030:
                    years.append(year)
                    year_cols[year] = idx
            except:
                pass

    return sorted(set(years)), year_cols

def read_cf_export_file(file, sheet_name):
    """Read CF-Export format Excel file"""
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)

    # Find header row (usually row 14 or 15)
    header_row = None
    for idx in range(min(20, len(df))):
        row_vals = df.iloc[idx].astype(str).tolist()
        if 'FCC Code' in row_vals or 'Field Name' in row_vals:
            header_row = idx
            break

    if header_row is None:
        header_row = find_data_start_row(df)

    # Set headers
    df.columns = df.iloc[header_row]
    df = df.iloc[header_row + 1:].reset_index(drop=True)

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    return df

def read_vietnamese_bctc(file, sheet_name):
    """Read Vietnamese BCTC format Excel file"""
    df = pd.read_excel(file, sheet_name=sheet_name, header=None)

    # Find data start
    data_start = 0
    for idx in range(min(10, len(df))):
        row_str = ' '.join([str(x) for x in df.iloc[idx].values if pd.notna(x)])
        if any(str(year) in row_str for year in range(2015, 2030)):
            data_start = idx
            break

    return df, data_start

def extract_field_value(df, field_name, mapping, year_col, file_format):
    """Extract a specific field value from dataframe"""
    search_terms = mapping.get(field_name, [field_name])

    for term in search_terms:
        # Search in first column (field names)
        for idx, row in df.iterrows():
            cell_val = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ''

            if term.lower() in cell_val.lower() or cell_val.lower() in term.lower():
                # Found the field, get value from year column
                if isinstance(year_col, int) and year_col < len(row):
                    val = row.iloc[year_col]
                    if pd.notna(val):
                        try:
                            return float(val)
                        except:
                            pass
    return None

def extract_cf_export_info(df):
    """Extract company name and scaling factor from CF-Export file header"""
    company_name = "Unknown Company"
    scaling_factor = 1000  # Default for CF-Export is Thousands

    for idx in range(min(15, len(df))):
        for col_idx in range(min(5, len(df.columns))):
            cell_val = str(df.iloc[idx, col_idx]) if pd.notna(df.iloc[idx, col_idx]) else ''

            # Find Company Name row
            if 'Company Name' in cell_val:
                # Company name is in the next column
                if col_idx + 1 < len(df.columns):
                    name_val = df.iloc[idx, col_idx + 1]
                    if pd.notna(name_val):
                        company_name = str(name_val).strip()

            # Find Scaling row
            if 'Scaling' in cell_val:
                if col_idx + 1 < len(df.columns):
                    scale_val = str(df.iloc[idx, col_idx + 1]).lower() if pd.notna(df.iloc[idx, col_idx + 1]) else ''
                    if 'thousand' in scale_val:
                        scaling_factor = 1000
                    elif 'million' in scale_val:
                        scaling_factor = 1000000
                    elif 'billion' in scale_val:
                        scaling_factor = 1000000000
                    else:
                        scaling_factor = 1

    return company_name, scaling_factor

def extract_cf_export_data(df, field_name, mapping, year_col):
    """Extract data from CF-Export format using FCC codes"""
    search_terms = mapping.get(field_name, [field_name])

    for idx in range(len(df)):
        fcc_code = str(df.iloc[idx, 0]) if pd.notna(df.iloc[idx, 0]) else ''
        field_desc = str(df.iloc[idx, 1]) if len(df.columns) > 1 and pd.notna(df.iloc[idx, 1]) else ''

        # Check if FCC code matches or field description matches
        for term in search_terms:
            if fcc_code == term or term.lower() in field_desc.lower():
                # Found the field, get value from year column
                if year_col < len(df.columns):
                    val = df.iloc[idx, year_col]
                    if pd.notna(val):
                        try:
                            return float(val)
                        except:
                            pass
                break
    return None

def extract_vn_field_value(df, field_name, mapping, year_col):
    """Extract data from Vietnamese BCTC format using field name matching"""
    search_terms = mapping.get(field_name, [field_name])

    for idx in range(len(df)):
        cell_val = str(df.iloc[idx, 0]) if pd.notna(df.iloc[idx, 0]) else ''
        cell_val_clean = cell_val.strip()

        # Check if any search term matches
        for term in search_terms:
            # Exact match or contains match
            if term == cell_val_clean or term.lower() == cell_val_clean.lower():
                # Exact match found
                if year_col < len(df.columns):
                    val = df.iloc[idx, year_col]
                    if pd.notna(val):
                        try:
                            return float(val)
                        except:
                            pass
                break
            elif term.lower() in cell_val_clean.lower():
                # Partial match - be more careful to avoid false positives
                # Check if it's a close enough match
                if len(term) > 10 or cell_val_clean.startswith(term) or cell_val_clean.endswith(term):
                    if year_col < len(df.columns):
                        val = df.iloc[idx, year_col]
                        if pd.notna(val):
                            try:
                                return float(val)
                            except:
                                pass
                    break

    return None

def process_uploaded_file(uploaded_file):
    """Process uploaded Excel file and extract financial data"""
    results = {
        'success': False,
        'data': {},
        'years': [],
        'missing_fields': [],
        'company_info': {
            'name': 'Unknown Company',
            'file_name': uploaded_file.name if hasattr(uploaded_file, 'name') else 'Unknown'
        },
        'errors': []
    }

    try:
        # Read Excel file
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names

        # Detect CF-Export format by checking for typical sheets
        is_cf_export = any(s.lower() in ['balance sheet', 'income statement', 'financial summary']
                          for s in sheet_names)

        if is_cf_export:
            # CF-Export format processing
            # Read Balance Sheet
            df_bs = None
            df_is = None
            scaling_factor = 1000

            for sheet in sheet_names:
                if 'balance' in sheet.lower():
                    df_bs = pd.read_excel(uploaded_file, sheet_name=sheet, header=None)
                elif 'income' in sheet.lower():
                    df_is = pd.read_excel(uploaded_file, sheet_name=sheet, header=None)

            if df_bs is None:
                df_bs = pd.read_excel(uploaded_file, sheet_name=sheet_names[0], header=None)

            # Extract company info and scaling
            company_name, scaling_factor = extract_cf_export_info(df_bs)
            results['company_info']['name'] = company_name

            # Find years row (row with "Statement Data" or year values like 2014, 2015...)
            year_row = None
            year_cols = {}

            for idx in range(min(20, len(df_bs))):
                row_vals = [str(df_bs.iloc[idx, c]) for c in range(len(df_bs.columns))]
                # Check for Statement Data row or FCC header row
                if 'Statement Data' in row_vals or 'FCC' in row_vals:
                    year_row = idx
                    # Next row or same row should have years
                    for col_idx in range(2, len(df_bs.columns)):
                        val = df_bs.iloc[idx, col_idx]
                        if pd.notna(val):
                            try:
                                year = int(float(val))
                                if 2010 <= year <= 2030:
                                    year_cols[year] = col_idx
                            except:
                                pass
                    break

            results['years'] = sorted(year_cols.keys())

            # Extract data for each year
            for year in results['years']:
                year_data = {}
                year_col = year_cols[year]

                # Extract from Balance Sheet
                if df_bs is not None:
                    for field in ['Total Assets', 'Total Current Assets', 'Total Current Liabilities',
                                 'Total Liabilities', 'Total Fixed Assets - Net', 'Shareholders Equity',
                                 'Retained Earnings']:
                        val = extract_cf_export_data(df_bs, field, FCC_MAPPING, year_col)
                        if val is not None:
                            year_data[field] = val * scaling_factor

                    # If Total Fixed Assets - Net not found, calculate from PPE + Intangibles
                    if 'Total Fixed Assets - Net' not in year_data or year_data.get('Total Fixed Assets - Net') is None:
                        ppe = extract_cf_export_data(df_bs, 'PPE Net', FCC_MAPPING, year_col)
                        intangibles = extract_cf_export_data(df_bs, 'Intangible Assets Net', FCC_MAPPING, year_col)

                        fixed_assets_total = 0
                        if ppe is not None:
                            fixed_assets_total += ppe
                        if intangibles is not None:
                            fixed_assets_total += intangibles

                        if fixed_assets_total > 0:
                            year_data['Total Fixed Assets - Net'] = fixed_assets_total * scaling_factor

                # Extract from Income Statement
                if df_is is not None:
                    for field in ['Revenue', 'Net Income after Tax', 'Income before Taxes',
                                 'EBIT', 'Interest Expense']:
                        val = extract_cf_export_data(df_is, field, FCC_MAPPING, year_col)
                        if val is not None:
                            year_data[field] = val * scaling_factor
                elif df_bs is not None:
                    # Try to get from Balance Sheet file if Income Statement not found
                    for field in ['Revenue', 'Net Income after Tax', 'Income before Taxes',
                                 'EBIT', 'Interest Expense']:
                        val = extract_cf_export_data(df_bs, field, FCC_MAPPING, year_col)
                        if val is not None:
                            year_data[field] = val * scaling_factor

                # EBIT: Use extracted value if available
                # Only calculate from formula if EBIT was not extracted
                if not year_data.get('EBIT'):
                    income_before_taxes = year_data.get('Income before Taxes', 0)
                    interest_expense = year_data.get('Interest Expense', 0)
                    if income_before_taxes and interest_expense:
                        year_data['EBIT'] = income_before_taxes + interest_expense

                results['data'][year] = year_data

        else:
            # Vietnamese BCTC format processing
            # Find Balance Sheet and Income Statement sheets
            df_bs = None
            df_is = None
            scaling_factor = 1000  # Default: "Nghìn đồng" (thousands)

            for sheet in sheet_names:
                sheet_lower = sheet.lower()
                # Check for Balance Sheet
                if any(vn_name.lower() in sheet_lower or sheet_lower in vn_name.lower()
                       for vn_name in VN_SHEET_NAMES['balance_sheet']):
                    df_bs = pd.read_excel(uploaded_file, sheet_name=sheet, header=None)
                # Check for Income Statement
                elif any(vn_name.lower() in sheet_lower or sheet_lower in vn_name.lower()
                         for vn_name in VN_SHEET_NAMES['income_statement']):
                    df_is = pd.read_excel(uploaded_file, sheet_name=sheet, header=None)

            # If no specific sheets found, use first sheet
            if df_bs is None:
                df_bs = pd.read_excel(uploaded_file, sheet_name=sheet_names[0], header=None)

            # Extract company name from header (usually in first rows)
            for idx in range(min(10, len(df_bs))):
                for col_idx in range(min(5, len(df_bs.columns))):
                    cell_val = str(df_bs.iloc[idx, col_idx]) if pd.notna(df_bs.iloc[idx, col_idx]) else ''
                    if 'CÔNG TY' in cell_val.upper() or 'COMPANY' in cell_val.upper():
                        # Extract company name
                        company_name = cell_val.split('\n')[0].strip()
                        if '-' in company_name:
                            company_name = company_name.split('-')[0].strip()
                        results['company_info']['name'] = company_name
                        break
                    # Also check for unit/scaling
                    if 'nghìn đồng' in cell_val.lower() or 'nghin dong' in cell_val.lower():
                        scaling_factor = 1000
                    elif 'triệu đồng' in cell_val.lower() or 'trieu dong' in cell_val.lower():
                        scaling_factor = 1000000
                    elif 'tỷ đồng' in cell_val.lower() or 'ty dong' in cell_val.lower():
                        scaling_factor = 1000000000

            # Find year row and extract years
            # Only use first occurrence of each year (avoid percentage columns)
            years = []
            year_cols = {}

            for idx in range(min(10, len(df_bs))):
                row_vals = df_bs.iloc[idx].tolist()
                for col_idx, val in enumerate(row_vals):
                    if pd.notna(val):
                        try:
                            year_val = int(float(val))
                            if 2010 <= year_val <= 2030:
                                # Only add if this year hasn't been found yet
                                # This ensures we get the FIRST occurrence (actual data columns)
                                if year_val not in year_cols:
                                    years.append(year_val)
                                    year_cols[year_val] = col_idx
                        except (ValueError, TypeError):
                            pass

            years = sorted(set(years))
            results['years'] = years

            # Extract data for each year from Balance Sheet
            for year in years:
                year_data = {}
                year_col = year_cols.get(year, None)
                if year_col is None:
                    continue

                # Extract from Balance Sheet
                if df_bs is not None:
                    for field in ['Total Assets', 'Total Current Assets', 'Total Current Liabilities',
                                 'Total Liabilities', 'Total Fixed Assets - Net', 'Shareholders Equity',
                                 'Retained Earnings']:
                        val = extract_vn_field_value(df_bs, field, VN_MAPPING, year_col)
                        if val is not None:
                            year_data[field] = val * scaling_factor

                    # If Total Fixed Assets - Net not found, calculate from components
                    # Formula: TSCĐ = TSCĐ hữu hình + TSCĐ thuê tài chính + TSCĐ vô hình
                    if 'Total Fixed Assets - Net' not in year_data or year_data.get('Total Fixed Assets - Net') is None:
                        tangible = extract_vn_field_value(df_bs, 'Tangible Fixed Assets Net', VN_MAPPING, year_col)
                        leased = extract_vn_field_value(df_bs, 'Leased Fixed Assets Net', VN_MAPPING, year_col)
                        intangible = extract_vn_field_value(df_bs, 'Intangible Fixed Assets Net', VN_MAPPING, year_col)

                        # Sum up components (treat None as 0)
                        fixed_assets_total = 0
                        if tangible is not None:
                            fixed_assets_total += tangible
                        if leased is not None:
                            fixed_assets_total += leased
                        if intangible is not None:
                            fixed_assets_total += intangible

                        if fixed_assets_total > 0:
                            year_data['Total Fixed Assets - Net'] = fixed_assets_total * scaling_factor

                # Extract from Income Statement
                if df_is is not None:
                    for field in ['Revenue', 'Net Income after Tax', 'Income before Taxes',
                                 'EBIT', 'Interest Expense', 'Financial Expenses', 'Financial Revenue']:
                        val = extract_vn_field_value(df_is, field, VN_MAPPING, year_col)
                        if val is not None:
                            year_data[field] = val * scaling_factor
                else:
                    # Try extracting from Balance Sheet file (some files have all data in one sheet)
                    for field in ['Revenue', 'Net Income after Tax', 'Income before Taxes',
                                 'EBIT', 'Interest Expense', 'Financial Expenses', 'Financial Revenue']:
                        if field not in year_data:
                            val = extract_vn_field_value(df_bs, field, VN_MAPPING, year_col)
                            if val is not None:
                                year_data[field] = val * scaling_factor

                # Interest Expense: Use extracted "Chi phí lãi vay" directly
                # Only calculate from Financial Expenses - Financial Revenue if not available
                if not year_data.get('Interest Expense'):
                    financial_expenses = year_data.get('Financial Expenses', 0)
                    financial_revenue = year_data.get('Financial Revenue', 0)
                    if financial_expenses:
                        year_data['Interest Expense'] = financial_expenses - (financial_revenue or 0)

                # EBIT: Use extracted "Lợi nhuận thuần từ HĐKD" directly
                # Only calculate from formula if EBIT was not extracted
                if not year_data.get('EBIT'):
                    income_before_taxes = year_data.get('Income before Taxes', 0)
                    interest_expense = year_data.get('Interest Expense', 0)
                    if income_before_taxes and interest_expense:
                        year_data['EBIT'] = income_before_taxes + interest_expense

                results['data'][year] = year_data

        # Check for missing required fields
        if results['years']:
            latest_year = max(results['years'])
            latest_data = results['data'].get(latest_year, {})
            for field in REQUIRED_FIELDS:
                if field not in latest_data or latest_data[field] is None:
                    results['missing_fields'].append(field)

        results['success'] = len(results['missing_fields']) < len(REQUIRED_FIELDS) / 2

    except Exception as e:
        results['errors'].append(str(e))
        results['success'] = False

    return results

# -----------------------------------------
# 4. FINANCIAL RATIO CALCULATIONS
# -----------------------------------------

def calculate_financial_ratios(data):
    """Calculate financial ratios from extracted data"""
    ratios = {}

    # Get values with defaults
    total_assets = data.get('Total Assets', 0)
    current_assets = data.get('Total Current Assets', 0)
    current_liabilities = data.get('Total Current Liabilities', 0)
    total_liabilities = data.get('Total Liabilities', 0)
    fixed_assets = data.get('Total Fixed Assets - Net', 0)
    equity = data.get('Shareholders Equity', 0)
    retained_earnings = data.get('Retained Earnings', 0)
    net_income = data.get('Net Income after Tax', 0)
    ebit = data.get('EBIT', 0)
    revenue = data.get('Revenue', 0)
    interest_expense = data.get('Interest Expense', 0)

    # Avoid division by zero
    if total_assets > 0:
        ratios['ROA'] = net_income / total_assets
        ratios['LEV'] = total_liabilities / total_assets
        ratios['FAR'] = fixed_assets / total_assets if fixed_assets else 0
        ratios['SIZE'] = np.log(total_assets)
        ratios['Retained_Earnings_to_Assets'] = retained_earnings / total_assets if retained_earnings else 0
        ratios['Working_Capital_to_Assets'] = (current_assets - current_liabilities) / total_assets
        ratios['Equity_to_Assets'] = equity / total_assets if equity else 0

    if current_liabilities > 0:
        ratios['CUR'] = current_assets / current_liabilities
    else:
        ratios['CUR'] = 0

    if revenue > 0:
        ratios['Net_Profit_Margin'] = net_income / revenue
        ratios['EBIT_Margin'] = ebit / revenue if ebit else 0

    if total_liabilities > 0:
        ratios['Equity_to_Debt'] = equity / total_liabilities if equity else 0

    if interest_expense and interest_expense > 0:
        ratios['EBIT_to_Interest'] = ebit / interest_expense if ebit else 0
        ratios['Interest_Coverage'] = ebit / interest_expense if ebit else 0
    else:
        ratios['EBIT_to_Interest'] = None
        ratios['Interest_Coverage'] = None

    return ratios

# -----------------------------------------
# 5. FINANCIAL DISTRESS MODELS
# -----------------------------------------

def calculate_altman_z_score(data, ratios):
    """
    Calculate Altman Z''-Score for non-manufacturing/emerging market firms
    Z'' = 6.56*X1 + 3.26*X2 + 6.72*X3 + 1.05*X4
    """
    total_assets = data.get('Total Assets', 0)
    current_assets = data.get('Total Current Assets', 0)
    current_liabilities = data.get('Total Current Liabilities', 0)
    retained_earnings = data.get('Retained Earnings', 0)
    ebit = data.get('EBIT', 0)
    equity = data.get('Shareholders Equity', 0)
    total_liabilities = data.get('Total Liabilities', 0)

    if total_assets <= 0:
        return None, "N/A"

    # X1 = Working Capital / Total Assets
    X1 = (current_assets - current_liabilities) / total_assets

    # X2 = Retained Earnings / Total Assets
    X2 = retained_earnings / total_assets if retained_earnings else 0

    # X3 = EBIT / Total Assets
    X3 = ebit / total_assets if ebit else ratios.get('ROA', 0)

    # X4 = Book Value of Equity / Total Liabilities
    X4 = equity / total_liabilities if total_liabilities > 0 and equity else 0

    # Z'' Score
    z_score = 6.56 * X1 + 3.26 * X2 + 6.72 * X3 + 1.05 * X4

    # Interpretation
    if z_score > 2.6:
        zone = "Safe Zone"
    elif z_score > 1.1:
        zone = "Grey Zone"
    else:
        zone = "Distress Zone"

    return z_score, zone

def calculate_s_score(data, ratios):
    """
    Calculate S-Score for emerging markets
    Based on profitability, leverage, and liquidity
    """
    roa = ratios.get('ROA', 0)
    leverage = ratios.get('LEV', 0)
    current_ratio = ratios.get('CUR', 0)

    # S-Score formula (simplified)
    # Higher is better
    s_score = 2.5 * roa - 0.5 * leverage + 0.3 * min(current_ratio, 3)

    # Interpretation
    if s_score > 0.8:
        zone = "Safe"
    elif s_score > 0.4:
        zone = "Watch"
    else:
        zone = "Distress"

    return s_score, zone

def calculate_ews_signals(data, ratios):
    """Calculate Early Warning System signals"""
    signals = {
        'signal_ebit': 0,
        'signal_z': 0,
        'signal_s': 0,
        'n_signals': 0,
        'ews_level': 'Safe',
        'drivers': []
    }

    # Signal 1: EBIT < Interest Expense
    ebit = data.get('EBIT', 0)
    interest = data.get('Interest Expense', 0)
    if interest and interest > 0 and ebit:
        if ebit < interest:
            signals['signal_ebit'] = 1
            signals['drivers'].append("EBIT lower than Interest Expense - Weak interest coverage")

    # Signal 2: Z-Score
    z_score, z_zone = calculate_altman_z_score(data, ratios)
    if z_score is not None and z_zone == "Distress Zone":
        signals['signal_z'] = 1
        signals['drivers'].append(f"Altman Z-Score = {z_score:.2f} - Financial distress zone")

    # Signal 3: S-Score
    s_score, s_zone = calculate_s_score(data, ratios)
    if s_zone == "Distress":
        signals['signal_s'] = 1
        signals['drivers'].append(f"S-Score = {s_score:.2f} - High risk")

    # Additional warning signals
    # Low Current Ratio
    if ratios.get('CUR', 0) < 1:
        signals['drivers'].append(f"Current Ratio = {ratios.get('CUR', 0):.2f} < 1 - Liquidity risk")

    # High Leverage
    if ratios.get('LEV', 0) > 0.7:
        signals['drivers'].append(f"Leverage = {ratios.get('LEV', 0):.2%} > 70% - High debt risk")

    # Negative ROA
    if ratios.get('ROA', 0) < 0:
        signals['drivers'].append(f"ROA = {ratios.get('ROA', 0):.2%} < 0 - Operating loss")

    # Count signals
    signals['n_signals'] = signals['signal_ebit'] + signals['signal_z'] + signals['signal_s']

    # Determine EWS Level
    if signals['n_signals'] == 0:
        signals['ews_level'] = 'Safe'
    elif signals['n_signals'] == 1:
        signals['ews_level'] = 'Watchlist'
    else:
        signals['ews_level'] = 'Distress'

    return signals

def generate_recommendations(signals, ratios, data):
    """Generate management recommendations based on analysis"""
    recommendations = []

    ews_level = signals.get('ews_level', 'Safe')

    if ews_level == 'Safe':
        recommendations.append("Financial condition is stable. Continue maintaining current indicators.")
        recommendations.append("Investment opportunities may be considered, subject to further strategic evaluation.")

    elif ews_level == 'Watchlist':
        recommendations.append("Close monitoring of financial indicators in subsequent periods is required.")

        if signals.get('signal_ebit') == 1:
            recommendations.append("Improve operating profit margin to enhance interest coverage.")

        if ratios.get('CUR', 0) < 1.2:
            recommendations.append("Strengthen working capital management to ensure liquidity.")

        if ratios.get('LEV', 0) > 0.6:
            recommendations.append("Consider debt restructuring or increasing equity capital.")

    else:  # Distress
        recommendations.append("WARNING: The company shows strong signs of financial distress.")
        recommendations.append("Urgent action is required:")

        if signals.get('signal_ebit') == 1:
            recommendations.append("- Renegotiate debt terms with creditors.")
            recommendations.append("- Cut unnecessary operating expenses.")

        if signals.get('signal_z') == 1:
            recommendations.append("- Consider selling non-performing assets.")
            recommendations.append("- Seek additional capital from shareholders.")

        if ratios.get('CUR', 0) < 0.8:
            recommendations.append("- Prioritize settlement of maturing short-term debts.")

        recommendations.append("- Engage restructuring consultants if necessary.")

    return recommendations

# -----------------------------------------
# 6. VISUALIZATION FUNCTIONS
# -----------------------------------------

def create_gauge_chart(value, title, min_val, max_val, thresholds):
    """Create a gauge chart for displaying metrics"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, thresholds[0]], 'color': "#E74C3C"},
                {'range': [thresholds[0], thresholds[1]], 'color': "#F1C40F"},
                {'range': [thresholds[1], max_val], 'color': "#2ECC71"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig

def create_ratio_comparison_chart(ratios, year):
    """
    Compare company ratios with pre-computed market medians (reference only).
    Market medians are calculated from the research sample by year.
    """

    ratio_names = ['ROA', 'CUR', 'LEV', 'FAR','WC_Assets']

    # ===== PRE-COMPUTED MARKET MEDIANS (FROM RESEARCH SAMPLE) =====
    market_median_by_year = {
      2014: {'ROA': 0.052769, 'CUR': 1.510826, 'LEV': 0.502633, 'FAR': 0.360363, 'WC_Assets': 0.187950},
        2015: {'ROA': 0.052414, 'CUR': 1.606347, 'LEV': 0.504608, 'FAR': 0.337595, 'WC_Assets': 0.210579},
        2016: {'ROA': 0.054283, 'CUR': 1.641246, 'LEV': 0.500153, 'FAR': 0.360917, 'WC_Assets': 0.211378},
        2017: {'ROA': 0.059779, 'CUR': 1.589761, 'LEV': 0.493173, 'FAR': 0.374649, 'WC_Assets': 0.202941},
        2018: {'ROA': 0.059748, 'CUR': 1.604579, 'LEV': 0.476176, 'FAR': 0.358879, 'WC_Assets': 0.200405},
        2019: {'ROA': 0.050066, 'CUR': 1.563973, 'LEV': 0.474889, 'FAR': 0.367471, 'WC_Assets': 0.214203},
        2020: {'ROA': 0.046377, 'CUR': 1.557456, 'LEV': 0.467699, 'FAR': 0.371910, 'WC_Assets': 0.185982},
        2021: {'ROA': 0.050660, 'CUR': 1.653436, 'LEV': 0.464749, 'FAR': 0.333126, 'WC_Assets': 0.216935},
        2022: {'ROA': 0.045701, 'CUR': 1.677991, 'LEV': 0.454609, 'FAR': 0.324720, 'WC_Assets': 0.226708},
        2023: {'ROA': 0.033380, 'CUR': 1.671736, 'LEV': 0.452314, 'FAR': 0.323718, 'WC_Assets': 0.220284},
        2024: {'ROA': 0.038895, 'CUR': 1.677622, 'LEV': 0.455929, 'FAR': 0.317569, 'WC_Assets': 0.228293},
        2025: {'ROA': 0.030631, 'CUR': 1.446915, 'LEV': 0.432996, 'FAR': 0.309996, 'WC_Assets': 0.232440},
    }

    median_ref = market_median_by_year.get(year, {})

    # Nếu năm không có median (fallback an toàn)
    if median_ref is None:
        median_ref = {r: None for r in ratio_names}

    values = [ratios.get(r, None) for r in ratio_names]
    median_values = [median_ref.get(r, None) for r in ratio_names]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name='Company Value',
        x=ratio_names,
        y=values,
        marker_color='#3182ce'
    ))

    fig.add_trace(go.Bar(
        name=f'Market Median ({year})',
        x=ratio_names,
        y=median_values,
        marker_color='rgba(128,128,128,0.5)'
    ))

    fig.update_layout(
        barmode='group',
        title=f'Financial Ratios vs Market Median ({year})',
        yaxis_title='Value',
        height=350,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Values"
    )

    return fig

# -----------------------------------------
# 7. MAIN APPLICATION
# -----------------------------------------

def main():
    st.title("Financial Distress Early Warning System (EWS)")
    st.caption("Early Warning System for Financial Distress | Upload Financial Statements for Analysis")

    # Sidebar
    st.sidebar.header("Data Input Method")
    input_mode = st.sidebar.radio(
        "Select data source:",
        ["Upload Financial Statements", "Sample Data (CSV)"]
    )

    if input_mode == "Upload Financial Statements":
        render_upload_mode()
    else:
        render_csv_mode()

def generate_sample_csv():
    """Generate sample CSV template for users to download"""
    sample_data = {
        'Field Name': [
            'Total Assets',
            'Current Assets',
            'Current Liabilities',
            'Total Liabilities',
            'Fixed Assets',
            'Shareholders Equity',
            'Retained Earnings',
            'Net Income after Tax',
            'EBIT',
            'Income before Taxes',
            'Revenue',
            'Interest Expense'
        ],
        'Field Code': [
            'Total Assets',
            'Total Current Assets',
            'Total Current Liabilities',
            'Total Liabilities',
            'Total Fixed Assets - Net',
            'Shareholders Equity',
            'Retained Earnings',
            'Net Income after Tax',
            'EBIT',
            'Income before Taxes',
            'Revenue',
            'Interest Expense'
        ],
        '2022': [
            1000000000000,
            400000000000,
            250000000000,
            600000000000,
            350000000000,
            400000000000,
            150000000000,
            80000000000,
            120000000000,
            100000000000,
            800000000000,
            30000000000
        ],
        '2023': [
            1200000000000,
            500000000000,
            300000000000,
            700000000000,
            400000000000,
            500000000000,
            200000000000,
            100000000000,
            150000000000,
            130000000000,
            1000000000000,
            35000000000
        ]
    }
    return pd.DataFrame(sample_data)

def render_sample_csv_section():
    """Render the sample CSV download section"""
    st.markdown("---")
    st.markdown('<p class="section-title">Sample CSV</p>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("**Download sample CSV file to view the required data format**")
        st.caption("Sample file contains the financial indicators required for EWS analysis")

        sample_df = generate_sample_csv()

        # Preview the sample data
        with st.expander("Preview sample data", expanded=False):
            st.dataframe(sample_df, use_container_width=True, hide_index=True)

            st.markdown("""
            **Field Descriptions:**
            - **Total Assets**: Total value of company assets
            - **Current Assets**: Assets convertible to cash within 1 year
            - **Current Liabilities**: Obligations due within 1 year
            - **EBIT**: Earnings Before Interest and Taxes
            - **Interest Expense**: Total interest payable during the period
            """)

        # Download button
        csv_buffer = io.StringIO()
        sample_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue()

        col_download, col_info = st.columns([1, 2])
        with col_download:
            st.download_button(
                label="Download Sample CSV",
                data=csv_data,
                file_name="sample_financial_data.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col_info:
            st.info("Unit: VND | Format: UTF-8")

def render_upload_section():
    """Render the file upload section"""
    # =========================================
    # PART 1: UPLOAD FILE
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">1. Upload File</p>', unsafe_allow_html=True)

    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Select Financial Statement File (Excel)",
            type=['xlsx', 'xls'],
            help="Supports CF-Export format or Vietnamese BCTC format"
        )

        if uploaded_file is not None:
            with st.spinner("Reading and processing data..."):
                results = process_uploaded_file(uploaded_file)

            if results['success']:
                # Display company info
                col_info1, col_info2, col_year = st.columns([2, 2, 1])

                with col_info1:
                    company_name = results['company_info'].get('name', 'Unknown')
                    st.markdown(f"**Company:** {company_name}")

                with col_info2:
                    sorted_years = sorted(results['years'])
                    if len(sorted_years) > 1:
                        years_str = f"{sorted_years[0]} - {sorted_years[-1]}"
                    else:
                        years_str = str(sorted_years[0])
                    st.markdown(f"**Reporting Period:** {years_str} ({len(results['years'])} years)")

                with col_year:
                    if results['years']:
                        selected_year = st.selectbox(
                            "Analysis Year:",
                            options=sorted(results['years'], reverse=True),
                            label_visibility="collapsed"
                        )

                # Status message
                if results['missing_fields']:
                    st.warning(f"Insufficient data for analysis. Missing: {', '.join(results['missing_fields'][:3])}")
                else:
                    st.success("Data loaded successfully!")

                # Process if year selected
                if results['years']:
                    year_data = results['data'].get(selected_year, {})

                    if year_data:
                        # Store in session state
                        st.session_state['year_data'] = year_data
                        st.session_state['all_data'] = results['data']
                        st.session_state['selected_year'] = selected_year
                        st.session_state['num_years'] = len(results['years'])
                        st.session_state['company_info'] = results['company_info']

                        # Continue with analysis
                        render_analysis(year_data, results['data'], selected_year)
                    else:
                        st.error("No data available for the selected year.")
            else:
                st.error("Unable to read data from file. Please check the format.")
                if results['errors']:
                    for err in results['errors']:
                        st.error(err)
                if results['missing_fields']:
                    st.warning(f"Insufficient data for analysis. Missing: {', '.join(results['missing_fields'])}")
        else:
            st.info("Please upload an Excel file containing Financial Statements to begin analysis.")

            # Show supported formats
            with st.expander("Supported File Formats"):
                st.markdown("""
                **1. CF-Export Format (Capital IQ/Refinitiv):**
                - File contains sheets: Balance Sheet, Income Statement, Cash Flow
                - First column contains FCC Code or English field names

                **2. Vietnamese BCTC Format:**
                - File contains sheets: Balance Sheet, Income Statement
                - Field names in Vietnamese

                **Required Fields:**
                - Total Assets
                - Total Current Assets
                - Total Current Liabilities
                - Total Liabilities
                - Shareholders' Equity
                - Net Income after Tax
                - Revenue
                """)

def render_upload_mode():
    """Render the upload mode - only upload section"""
    render_upload_section()

def render_analysis(year_data, all_data, selected_year):
    """Render the analysis dashboard for uploaded BCTC"""

    # ===== Market median by year (pre-computed, reference only) =====
    market_median_by_year = {
        2014: {'ROA': 0.052769, 'CUR': 1.510826, 'LEV': 0.502633, 'FAR': 0.360363, 'WC_Assets': 0.187950},
        2015: {'ROA': 0.052414, 'CUR': 1.606347, 'LEV': 0.504608, 'FAR': 0.337595, 'WC_Assets': 0.210579},
        2016: {'ROA': 0.054283, 'CUR': 1.641246, 'LEV': 0.500153, 'FAR': 0.360917, 'WC_Assets': 0.211378},
        2017: {'ROA': 0.059779, 'CUR': 1.589761, 'LEV': 0.493173, 'FAR': 0.374649, 'WC_Assets': 0.202941},
        2018: {'ROA': 0.059748, 'CUR': 1.604579, 'LEV': 0.476176, 'FAR': 0.358879, 'WC_Assets': 0.200405},
        2019: {'ROA': 0.050066, 'CUR': 1.563973, 'LEV': 0.474889, 'FAR': 0.367471, 'WC_Assets': 0.214203},
        2020: {'ROA': 0.046377, 'CUR': 1.557456, 'LEV': 0.467699, 'FAR': 0.371910, 'WC_Assets': 0.185982},
        2021: {'ROA': 0.050660, 'CUR': 1.653436, 'LEV': 0.464749, 'FAR': 0.333126, 'WC_Assets': 0.216935},
        2022: {'ROA': 0.045701, 'CUR': 1.677991, 'LEV': 0.454609, 'FAR': 0.324720, 'WC_Assets': 0.226708},
        2023: {'ROA': 0.033380, 'CUR': 1.671736, 'LEV': 0.452314, 'FAR': 0.323718, 'WC_Assets': 0.220284},
        2024: {'ROA': 0.038895, 'CUR': 1.677622, 'LEV': 0.455929, 'FAR': 0.317569, 'WC_Assets': 0.228293},
        2025: {'ROA': 0.030631, 'CUR': 1.446915, 'LEV': 0.432996, 'FAR': 0.309996, 'WC_Assets': 0.232440},
    }

    median_ref = market_median_by_year.get(selected_year, {})


    # Get number of years
    num_years = len(all_data)

    # Calculate ratios and signals
    ratios = calculate_financial_ratios(year_data)
    signals = calculate_ews_signals(year_data, ratios)
    z_score, z_zone = calculate_altman_z_score(year_data, ratios)
    s_score, s_zone = calculate_s_score(year_data, ratios)
    recommendations = generate_recommendations(signals, ratios, year_data)

    # Calculate priority flag
    priority_flag = 1 if signals['n_signals'] >= 2 or signals['ews_level'] == 'Distress' else 0

    # Calculate risk trend and YoY changes
    risk_trend = "Stable"
    ebit_yoy = None
    signal_delta = 0

    if num_years > 1:
        years_sorted = sorted(all_data.keys())
        current_idx = years_sorted.index(selected_year) if selected_year in years_sorted else -1

        if current_idx > 0:
            prev_year = years_sorted[current_idx - 1]
            prev_data = all_data[prev_year]
            prev_ratios = calculate_financial_ratios(prev_data)
            prev_signals = calculate_ews_signals(prev_data, prev_ratios)

            # Calculate signal delta
            signal_delta = signals['n_signals'] - prev_signals['n_signals']

            # Determine risk trend
            if signals['n_signals'] > prev_signals['n_signals']:
                risk_trend = "Worsening"
            elif signals['n_signals'] < prev_signals['n_signals']:
                risk_trend = "Improving"
            else:
                risk_trend = "Stable"

            # Calculate EBIT YoY change
            curr_ebit = year_data.get('EBIT', 0)
            prev_ebit = prev_data.get('EBIT', 0)
            if prev_ebit and prev_ebit != 0:
                ebit_yoy = ((curr_ebit - prev_ebit) / abs(prev_ebit)) * 100

    # Get company name from session state
    company_name = st.session_state.get('company_info', {}).get('name', 'Company')

    # =========================================
    # PART 2: COMPANY OVERVIEW
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">2. Company Overview</p>', unsafe_allow_html=True)

    with st.container(border=True):
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"**{company_name} – {selected_year}**")
            m1, m2 = st.columns(2)
            m1.metric("EWS Level", signals['ews_level'])
            m2.metric("Risk Trend", risk_trend)

            m3, m4 = st.columns(2)
            m3.metric("Priority Flag", priority_flag)
            m4.metric("Signals", signals['n_signals'])

        with col_right:
            st.markdown("**Year-over-Year Changes**")
            if num_years > 1:
                c1, c2 = st.columns(2)
                c1.metric(
                    "EBIT Change (%)",
                    f"{ebit_yoy:.1f}%" if ebit_yoy is not None else "N/A"
                )
                c2.metric(
                    "Signal Change",
                    int(signal_delta)
                )
            else:
                st.info("Upload multiple years to see YoY changes")

        st.markdown("---")

        # Display 4 key financial metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Assets",
                f"{year_data.get('Total Assets', 0)/1e9:,.1f} B"
            )

        with col2:
            st.metric(
                "Net Revenue",
                f"{year_data.get('Revenue', 0)/1e9:,.1f} B"
            )

        with col3:
            st.metric(
                "Net Income",
                f"{year_data.get('Net Income after Tax', 0)/1e9:,.1f} B"
            )

        with col4:
            st.metric(
                "Total Liabilities",
                f"{year_data.get('Total Liabilities', 0)/1e9:,.1f} B"
            )

        st.caption("Please verify that the data has been read correctly before proceeding with the analysis.")

    # =========================================
    # PART 3: Financial Distress Signal Assessment
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">3. Financial Distress Signal Assessment</p>', unsafe_allow_html=True)

    with st.container(border=True):
        col_left, col_right = st.columns([2, 3])

        with col_left:
            ews_level = signals['ews_level']
            n_signals = signals['n_signals']

            if ews_level == 'Safe':
                st.markdown(f"""
                <div class="risk-safe">
                    <h2>SAFE</h2>
                    <p>Warning Signals: {n_signals}/3</p>
                </div>
                """, unsafe_allow_html=True)
            elif ews_level == 'Watchlist':
                st.markdown(f"""
                <div class="risk-watchlist">
                    <h2>WATCHLIST</h2>
                    <p>Warning Signals: {n_signals}/3</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="risk-distress">
                    <h2>DISTRESS</h2>
                    <p>Warning Signals: {n_signals}/3</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Priority Flag
            if priority_flag == 1:
                st.error(f"**Priority Flag:** Immediate attention required!")
            else:
                st.success(f"**Priority Flag:** No urgent action needed")

        with col_right:
            # Gauge charts side by side
            gauge_col1, gauge_col2 = st.columns(2)

            with gauge_col1:
                if z_score is not None:
                    fig_z = create_gauge_chart(
                        z_score,
                        f"Altman Z''-Score",
                        -2, 5, [1.1, 2.6]
                    )
                    fig_z.update_layout(height=220)
                    st.plotly_chart(fig_z, use_container_width=True)
                    zone_color = "#2ECC71" if z_zone == "Safe Zone" else ("#F1C40F" if z_zone == "Grey Zone" else "#E74C3C")
                    st.markdown(f'<p style="text-align:center; color:{zone_color}; font-weight:600;">{z_zone}</p>', unsafe_allow_html=True)
                else:
                    st.info("Insufficient data for Z-Score calculation")

            with gauge_col2:
                fig_s = create_gauge_chart(
                    s_score,
                    f"S-Score",
                    -1, 2, [0.4, 0.8]
                )
                fig_s.update_layout(height=220)
                st.plotly_chart(fig_s, use_container_width=True)
                zone_color = "#2ECC71" if s_zone == "Safe" else ("#F1C40F" if s_zone == "Watch" else "#E74C3C")
                st.markdown(f'<p style="text-align:center; color:{zone_color}; font-weight:600;">{s_zone}</p>', unsafe_allow_html=True)

    # =========================================
    # PART 4: DETAILED ANALYSIS
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">4. Detailed Analysis</p>', unsafe_allow_html=True)

    with st.container(border=True):
        # Two tabs: Financial Ratios and EBIT vs Interest (scatter if >1 year, bar if 1 year)
        tab1, tab2 = st.tabs(["Financial Ratios", "EBIT vs Interest"])

        with tab1:
            col_chart, col_table = st.columns([3, 2])

            with col_chart:
                fig_compare = create_ratio_comparison_chart(ratios, selected_year)
                fig_compare.update_layout(height=380)
                st.plotly_chart(fig_compare, use_container_width=True)

            with col_table:
                st.markdown("**Ratio Details:**")
                ratio_data = []

                roa = ratios.get('ROA', None)
                roa_med = median_ref.get('ROA', None)
                ratio_data.append({
                    'Ratio': 'ROA',
                    'Value': f"{roa*100:.2f}%" if roa is not None else "N/A",
                    'Market Median': f"{roa_med*100:.2f}%" if roa_med is not None else "N/A",
                    'Relative Position': "Above median" if roa >= roa_med else "Below median"
                })

                cur = ratios.get('CUR', None)
                cur_med = median_ref.get('CUR', None)
                ratio_data.append({
                    'Ratio': 'Current Ratio',
                    'Value': f"{cur:.2f}" if cur is not None else "N/A",
                    'Market Median': f"{cur_med:.2f}" if cur_med is not None else "N/A",
                    'Relative Position': "Above median" if cur >= cur_med else "Below median"
                })

                lev = ratios.get('LEV', None)
                lev_med = median_ref.get('LEV', None)
                ratio_data.append({
                    'Ratio': 'Leverage',
                    'Value': f"{lev*100:.1f}%" if lev is not None else "N/A",
                    'Market Median': f"{lev_med*100:.1f}%" if lev_med is not None else "N/A",
                    'Relative Position': "Lower than median" if lev <= lev_med else "Higher than median"
                })

                far = ratios.get('FAR', None)
                far_med = median_ref.get('FAR', None)
                ratio_data.append({
                    'Ratio': 'Fixed Asset Ratio (FAR)',
                    'Value': f"{far*100:.1f}%" if far is not None else "N/A",
                    'Market Median': f"{far_med*100:.1f}%" if far_med is not None else "N/A",
                    'Relative Position': "Lower than median" if far <= far_med else "Higher than median"
                })

                wc = ratios.get('Working_Capital_to_Assets', None)
                wc_med = median_ref.get('WC_Assets', None)

                if wc is not None:
                    ratio_data.append({
                        'Ratio': 'WC / Assets',
                        'Value': f"{wc*100:.1f}%" if wc is not None else "N/A",
                        'Market Median': f"{wc_med*100:.1f}%" if wc_med is not None else "N/A",
                        'Relative Position': (
                            "Above median" if wc_med is not None and wc >= wc_med
                            else "Below median"
                        )
                    })

                df_ratios = pd.DataFrame(ratio_data)
                st.dataframe(df_ratios, use_container_width=True, hide_index=True)
                st.caption(
                    "Market median values are pre-computed from the research sample and used for "
                    "relative interpretation only. They do not affect the signal-based early warning classification."
                )

        with tab2:
            # EBIT vs Interest Expense Analysis
            ebit = year_data.get('EBIT', 0)
            interest = year_data.get('Interest Expense', 0)

            # Check if company has net financial income (negative interest expense)
            has_net_financial_income = interest < 0

            if num_years > 1:
                # Multiple years: show bar chart for trend
                col_chart, col_info = st.columns([3, 2])

                with col_chart:
                    # Prepare data for bar chart
                    chart_data = []
                    for year in sorted(all_data.keys()):
                        data = all_data[year]
                        chart_data.append({
                            'Year': str(year),
                            'EBIT': data.get('EBIT', 0) / 1e9,
                            'Interest Expense': abs(data.get('Interest Expense', 0)) / 1e9,
                            'Type': 'Net Financial Income' if data.get('Interest Expense', 0) < 0 else 'Interest Expense'
                        })

                    df_chart = pd.DataFrame(chart_data)

                    fig_bar = go.Figure()
                    fig_bar.add_trace(go.Bar(
                        name='EBIT',
                        x=df_chart['Year'],
                        y=df_chart['EBIT'],
                        marker_color='#3182ce',
                        text=[f"{v:,.1f}" for v in df_chart['EBIT']],
                        textposition='auto'
                    ))
                    fig_bar.add_trace(go.Bar(
                        name='Interest Expense' if not has_net_financial_income else 'Net Financial Income',
                        x=df_chart['Year'],
                        y=df_chart['Interest Expense'],
                        marker_color='#E74C3C' if not has_net_financial_income else '#2ECC71',
                        text=[f"{v:,.1f}" for v in df_chart['Interest Expense']],
                        textposition='auto'
                    ))
                    fig_bar.update_layout(
                        title='EBIT vs Interest Expense Over Time (Billion VND)',
                        barmode='group',
                        yaxis_title='Value (Billion VND)',
                        height=400,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                with col_info:
                    st.markdown("**Interest Coverage Analysis:**")

                    if has_net_financial_income:
                        st.success("Net Financial Income")
                        st.markdown(f"**Financial Revenue > Financial Expenses**")
                        st.markdown(f"Net Financial Income: **{abs(interest)/1e9:,.1f} B**")
                        st.markdown("The company earns more from financial activities than it pays in interest.")
                    else:
                        coverage = ebit / interest if interest > 0 else 0
                        st.metric("Interest Coverage Ratio", f"{coverage:.2f}x")

                        if interest > 0 and ebit < interest:
                            st.error("Earnings before Interest & Taxes (EBIT) < Interest Expense")
                            st.markdown("The firm **cannot cover** interest payments from operating earnings.")
                        elif coverage > 0 and coverage < 2:
                            st.warning("Coverage < 2x")
                            st.markdown("Interest coverage is **moderate**, requires monitoring.")
                        elif coverage >= 2:
                            st.success(f"Coverage = {coverage:.1f}x")
                            st.markdown("**Strong** interest coverage.")
            else:
                # Single year: show bar chart
                if ebit:
                    col_ebit_chart, col_ebit_info = st.columns([3, 2])

                    with col_ebit_chart:
                        # Determine label and color based on interest expense sign
                        int_label = 'Net Financial Income' if has_net_financial_income else 'Interest Expense'
                        int_color = '#2ECC71' if has_net_financial_income else '#E74C3C'
                        int_value = abs(interest) / 1e9

                        fig_ebit = go.Figure()
                        fig_ebit.add_trace(go.Bar(
                            x=['EBIT', int_label],
                            y=[ebit/1e9, int_value],
                            marker_color=['#3182ce', int_color],
                            text=[f"{ebit/1e9:,.1f}", f"{int_value:,.1f}"],
                            textposition='auto'
                        ))
                        fig_ebit.update_layout(
                            title='EBIT vs Interest Expense (Billion VND)',
                            yaxis_title='Value (Billion VND)',
                            height=350,
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)"
                        )
                        st.plotly_chart(fig_ebit, use_container_width=True)

                    with col_ebit_info:
                        st.markdown("**Interest Coverage Analysis:**")

                        if has_net_financial_income:
                            st.success("Net Financial Income")
                            st.markdown(f"**Financial Revenue > Financial Expenses**")
                            st.markdown(f"Net Financial Income: **{abs(interest)/1e9:,.1f} B**")
                            st.markdown("The company earns more from financial activities than it pays in interest.")
                        else:
                            coverage = ebit / interest if interest > 0 else 0
                            st.metric("Interest Coverage Ratio", f"{coverage:.2f}x")

                            if interest > 0 and ebit < interest:
                                st.error("Earnings before Interest & Taxes (EBIT) < Interest Expense")
                                st.markdown("The firm **cannot cover** interest payments.")
                            elif coverage > 0 and coverage < 2:
                                st.warning("Coverage < 2x")
                                st.markdown("Interest coverage is **moderate**.")
                            elif coverage >= 2:
                                st.success(f"Coverage = {coverage:.1f}x")
                                st.markdown("**Strong** interest coverage.")
                else:
                    st.info("Insufficient EBIT data for analysis.")

        # Add Recommendation at the end of Detailed Analysis
        st.markdown("---")
        st.markdown("**Recommendation:**")
        if ews_level == 'Safe':
            st.success("The company is operating stably. Continue maintaining current financial indicators and conduct regular monitoring.")
        elif ews_level == 'Watchlist':
            st.warning("The company shows signs of declining profitability and liquidity pressure. Close monitoring of cash flow and short-term debt repayment capacity is recommended.")
        else:
            st.error("The company is experiencing serious financial difficulties. Urgent management attention is required.")

    # =========================================
    # PART 5: TREND ANALYSIS (only if > 1 year)
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">5. Trend Analysis</p>', unsafe_allow_html=True)

    if num_years > 1:
        with st.container(border=True):
            col_chart1, col_chart2 = st.columns(2)

            # Prepare trend data
            trend_data = []
            for year in sorted(all_data.keys()):
                data = all_data[year]
                yr_ratios = calculate_financial_ratios(data)
                yr_signals = calculate_ews_signals(data, yr_ratios)
                trend_data.append({
                    'Year': year,
                    'n_signals': yr_signals['n_signals'],
                    'ews_level': yr_signals['ews_level'],
                    'ROA': yr_ratios.get('ROA', 0),
                    'CUR': yr_ratios.get('CUR', 0),
                    'LEV': yr_ratios.get('LEV', 0),
                    'FAR': yr_ratios.get('FAR', 0)
                })
            df_trend = pd.DataFrame(trend_data)

            with col_chart1:
                st.markdown("**Distress Signals Over Time**")
                fig_trend = px.line(
                    df_trend,
                    x="Year",
                    y="n_signals",
                    markers=True,
                    title="Number of distress signals over time"
                )
                # Add annotation for selected year
                selected_row = df_trend[df_trend['Year'] == selected_year]
                if not selected_row.empty:
                    fig_trend.add_annotation(
                        x=selected_year,
                        y=selected_row['n_signals'].values[0],
                        text=f"EWS: {selected_row['ews_level'].values[0]}",
                        showarrow=True,
                        arrowhead=1
                    )
                st.plotly_chart(fig_trend, use_container_width=True)

            with col_chart2:
                st.markdown("**Financial Ratios**")
                ratio_option = st.selectbox(
                    "Select ratio",
                    ["ROA", "CUR", "LEV", "FAR"],
                    key="upload_ratio_selector",
                    label_visibility="collapsed"
                )
                fig_ratio = px.line(
                    df_trend,
                    x="Year",
                    y=ratio_option,
                    markers=True,
                    title=f"{ratio_option} over time"
                )
                st.plotly_chart(fig_ratio, use_container_width=True)
    else:
        with st.container(border=True):
            st.info("Trend analysis requires multiple years of data. Upload financial statements for multiple years to enable this feature.")

    # =========================================
    # PART 6: MANAGEMENT RECOMMENDATIONS
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">6. Management Recommendations</p>', unsafe_allow_html=True)

    ews_level = signals['ews_level']

    # Summary box - without Z-Score, S-Score on the right
    if ews_level == 'Safe':
        box_style = "background: linear-gradient(135deg, #2ECC71 0%, #27AE60 100%);"
        status_text = "SAFE"
    elif ews_level == 'Watchlist':
        box_style = "background: linear-gradient(135deg, #F1C40F 0%, #F39C12 100%);"
        status_text = "WATCHLIST"
    else:
        box_style = "background: linear-gradient(135deg, #E74C3C 0%, #C0392B 100%);"
        status_text = "DISTRESS"

    st.markdown(f"""
    <div style="{box_style} color: white; padding: 1.5rem; border-radius: 15px; margin-bottom: 1rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <h3 style="margin: 0; font-size: 1.3rem;">Risk Level: {status_text}</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Analysis Year: {selected_year}</p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 0.9rem;">Warning Signals: <strong>{signals['n_signals']}/3</strong></div>
                <div style="font-size: 0.9rem;">Priority Flag: <strong>{'Yes' if priority_flag else 'No'}</strong></div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Recommendations in columns
    st.markdown("**Specific Recommendations:**")

    rec_cols = st.columns(2)
    for i, rec in enumerate(recommendations):
        with rec_cols[i % 2]:
            if rec.startswith("CẢNH BÁO"):
                st.error(rec)
            elif rec.startswith("-"):
                st.markdown(f"  {rec}")
            else:
                st.info(rec)

    # =========================================
    # PART 7: EXECUTIVE SUMMARY
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">7. Executive Summary</p>', unsafe_allow_html=True)

    # Generate executive summary based on EWS level and number of years
    summary = generate_executive_summary(signals, ratios, num_years, all_data, selected_year)

    st.markdown(f"""
    <div style="background: rgba(49, 130, 206, 0.1); border-left: 4px solid #3182ce; padding: 1.2rem; border-radius: 0 10px 10px 0;">
        <p style="margin: 0; line-height: 1.7;">{summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # Raw Data Expander
    st.markdown("---")
    with st.expander("View Raw Data"):
        data_col1, data_col2 = st.columns(2)
        with data_col1:
            st.markdown("**Raw Financial Data:**")
            st.json(year_data)
        with data_col2:
            st.markdown("**Calculated Ratios:**")
            st.dataframe(pd.DataFrame([ratios]).T.rename(columns={0: 'Value'}), use_container_width=True)

def generate_executive_summary(signals, ratios, num_years, all_data, selected_year):
    """
    Generate Executive Summary based on EWS level and number of years
    Answers 3 questions:
    1. Current situation?
    2. Main causes?
    3. What should user do next?
    """
    ews_level = signals['ews_level']
    n_signals = signals['n_signals']

    # Check for worsening trend if multiple years
    worsening_trend = False
    if num_years > 1:
        years_sorted = sorted(all_data.keys())
        if len(years_sorted) >= 2:
            prev_year = years_sorted[-2]
            prev_data = all_data[prev_year]
            prev_ratios = calculate_financial_ratios(prev_data)
            prev_signals = calculate_ews_signals(prev_data, prev_ratios)
            if signals['n_signals'] > prev_signals['n_signals']:
                worsening_trend = True

    # Template selection based on EWS level
    if ews_level == 'Safe':
        if num_years == 1:
            summary = (
                "Based on the uploaded financial statements, the firm is currently classified as <strong>financially stable</strong>. "
                "No major financial distress signals are triggered in the reporting period. "
                "Key profitability and liquidity indicators remain within acceptable ranges. "
                "However, regular monitoring is recommended to ensure that any potential deterioration in operating performance is detected early."
            )
        else:
            summary = (
                "Based on the uploaded financial statements, the firm is currently assessed as <strong>financially stable</strong> based on the early warning signals. "
                "While no immediate financial distress is identified in the most recent year, certain financial indicators show signs of fluctuation over time. "
                "Continued monitoring of profitability and liquidity trends is recommended to prevent potential risk accumulation."
            )

    elif ews_level == 'Watchlist':
        if worsening_trend and num_years > 1:
            # Template 3: Watchlist + Worsening trend
            summary = (
                "The firm is currently classified as <strong>Watchlist</strong> based on the uploaded financial statements. "
                "Although the firm has not entered financial distress, the number of warning signals has increased compared to the previous period. "
                "This suggests a deterioration in financial conditions, and proactive risk management actions are advised, "
                "particularly in areas showing declining performance."
            )
        else:
            # Template 2: Standard Watchlist
            summary = (
                "Based on the uploaded financial statements, the firm is classified under the <strong>Watchlist</strong> category. "
                "One or more early warning signals are triggered, indicating potential weaknesses in profitability or liquidity. "
                "While no immediate financial distress is identified, closer monitoring of key financial indicators is recommended "
                "to prevent further risk escalation."
            )

    else:  # Distress
        # Template 4: Distress
        summary = (
            "The analysis of the uploaded financial statements indicates that the firm exhibits multiple <strong>financial distress</strong> warning signals. "
            "Multiple financial indicators exceed risk thresholds, reflecting pressure on profitability, liquidity, or capital structure. "
            "Immediate attention and corrective actions are recommended to mitigate financial risk and stabilize operations."
        )

    # Add specific drivers if any
    if signals['drivers']:
        main_drivers = signals['drivers'][:2]  # Top 2 drivers
        drivers_text = " The primary concerns include: " + "; ".join(main_drivers) + "."
        summary += drivers_text

    return summary

def generate_ai_summary(data, ratios, signals, z_score, z_zone, s_score, s_zone, year):
    """Generate AI executive summary - kept for CSV mode compatibility"""
    summary_parts = []

    ews_level = signals['ews_level']

    # Opening
    if ews_level == 'Safe':
        summary_parts.append(
            f"In {year}, the company is assessed as FINANCIALLY STABLE according to the early warning system."
        )
    elif ews_level == 'Watchlist':
        summary_parts.append(
            f"In {year}, the company shows FINANCIAL RISK INDICATORS and requires close monitoring."
        )
    else:
        summary_parts.append(
            f"In {year}, the company shows a high level of financial risk based on multiple warning signals.."
        )

    # Z-Score analysis
    if z_score is not None:
        if z_zone == "Safe Zone":
            summary_parts.append(
                f"Altman Z-Score = {z_score:.2f} indicates the company is in the safe zone."
            )
        elif z_zone == "Grey Zone":
            summary_parts.append(
                f"Altman Z-Score = {z_score:.2f} is in the grey zone, monitoring required."
            )
        else:
            summary_parts.append(
                f"Altman Z-Score = {z_score:.2f} is in the distress zone, immediate action needed."
            )

    # Key ratios analysis
    roa = ratios.get('ROA', 0)
    if roa < 0:
        summary_parts.append(f"Negative ROA ({roa*100:.2f}%) indicates the company is operating at a loss.")
    elif roa < 0.03:
        summary_parts.append(f"ROA at a low level ({roa*100:.2f}%), indicating limited profitability.")
    else:
        summary_parts.append(f"ROA of {roa*100:.2f}% demonstrates good profitability.")

    cur = ratios.get('CUR', 0)
    if cur < 1:
        summary_parts.append(f"Current Ratio = {cur:.2f} < 1 indicates high liquidity risk.")
    elif cur < 1.5:
        summary_parts.append(f"Current Ratio = {cur:.2f}, moderate liquidity level.")

    lev = ratios.get('LEV', 0)
    if lev > 0.7:
        summary_parts.append(f"Leverage of {lev*100:.1f}% > 70% indicates high debt level.")

    # Conclusion
    if signals['n_signals'] == 0:
        summary_parts.append(
            "No early warning signals triggered. Recommend maintaining current financial condition."
        )
    else:
        summary_parts.append(
            f"{signals['n_signals']} warning signal(s) triggered. Appropriate risk management measures are required."
        )

    return " ".join(summary_parts)

def render_csv_mode():
    """Render the CSV data mode (original functionality)"""
    @st.cache_data
    def load_data():
        return pd.read_csv("05_ews_application.csv")

    try:
        df = load_data()
        df = df[(df["Year"] >= 2014) & (df["Year"] <= 2024)]

        # Original dashboard code
        st.sidebar.header("Filters")

        code_list = sorted(df["Name"].unique())
        selected_code = st.sidebar.selectbox("Select company name", code_list)

        year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
        selected_year = st.sidebar.slider(
            "Select year",
            min_value=year_min,
            max_value=year_max,
            value=year_max
        )

        df_company = df[df["Name"] == selected_code].sort_values("Year")
        df_year = df_company[df_company["Year"] == selected_year]

        # Continue with original analysis...
        render_csv_analysis(df, df_company, df_year, selected_code, selected_year)

    except FileNotFoundError:
        st.error("Sample data file '05_ews_application.csv' not found.")
        st.info("Please switch to 'Upload Financial Statements' mode for analysis.")

def render_csv_analysis(df, df_company, df_year, selected_code, selected_year):
    """Render analysis for CSV data"""

    # Calculate metrics
    df_company = df_company.sort_values("Year")
    df_company["EBIT_yoy"] = df_company["Earnings before Interest & Taxes (EBIT)"].pct_change() * 100
    df_company["signal_delta"] = df_company["n_signals"].diff()
    latest = df_company[df_company["Year"] == selected_year]

    # Helper function
    def identify_signal_based_driver(row):
        drivers = []
        if row.get("signal_ebit", 0) == 1:
            drivers.append("Weak earnings coverage (EBIT < Interest Expense)")
        if row.get("signal_z", 0) == 1:
            drivers.append("Altman Z''-score distress signal")
        if row.get("signal_s", 0) == 1:
            drivers.append("S-score distress signal")
        if not drivers:
            return "No early-warning signal triggered"
        return "; ".join(drivers)

    # =========================================
    # SECTION 1: COMPANY OVERVIEW
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">1. Company Overview</p>', unsafe_allow_html=True)

    with st.container(border=True):
        if df_year.empty:
            st.warning("No data available for selected year.")
        else:
            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown(f"**{selected_code} – {selected_year}**")
                m1, m2 = st.columns(2)
                m1.metric("EWS Level", df_year["ews_level"].values[0])
                m2.metric("Risk Trend", df_year["risk_trend"].values[0])

                m3, m4 = st.columns(2)
                m3.metric("Priority Flag", int(df_year["priority_flag"].values[0]))
                m4.metric("Signals", int(df_year["n_signals"].values[0]))

            with col_right:
                st.markdown("**Year-over-Year Changes**")
                if not latest.empty:
                    c1, c2 = st.columns(2)
                    ebit_yoy = latest['EBIT_yoy'].values[0]
                    c1.metric(
                        "EBIT Change (%)",
                        f"{ebit_yoy:.1f}%" if not pd.isna(ebit_yoy) else "N/A"
                    )
                    signal_delta = latest["signal_delta"].values[0]
                    c2.metric(
                        "Signal Change",
                        int(signal_delta) if not pd.isna(signal_delta) else 0
                    )

    # =========================================
    # SECTION 2: RISK ASSESSMENT
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">2. Risk Assessment</p>', unsafe_allow_html=True)

    with st.container(border=True):
        col_signals, col_recommendation = st.columns(2)

        with col_signals:
            st.markdown("**Early Warning Signals**")
            if not df_year.empty:
                signal_driver = identify_signal_based_driver(df_year.iloc[0])
                if signal_driver == "No early-warning signal triggered":
                    st.success("No early-warning signal triggered")
                else:
                    for signal in signal_driver.split("; "):
                        st.error(f"{signal}")
            else:
                st.info("No data available.")

        with col_recommendation:
            st.markdown("**Recommendation**")
            if not df_year.empty:
                st.info(df_year["recommendation"].values[0])
            else:
                st.info("No recommendation available.")

    # =========================================
    # SECTION 3: TREND ANALYSIS
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">3. Trend Analysis</p>', unsafe_allow_html=True)

    if not df_company.empty:
        with st.container(border=True):
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown("**Distress Signals Over Time**")
                fig_trend = px.line(
                    df_company,
                    x="Year",
                    y="n_signals",
                    markers=True,
                    title="Number of distress signals over time"
                )

                if not latest.empty:
                    fig_trend.add_annotation(
                        x=latest["Year"].values[0],
                        y=latest["n_signals"].values[0],
                        text=f"EWS: {latest['ews_level'].values[0]}",
                        showarrow=True,
                        arrowhead=1
                    )
                st.plotly_chart(fig_trend, use_container_width=True)

            with col_chart2:
                st.markdown("**Financial Ratios**")
                ratio_option = st.selectbox(
                    "Select ratio",
                    ["ROA", "CUR", "LEV", "FAR", "SIZE"],
                    key="ratio_selector",
                    label_visibility="collapsed"
                )

                fig_ratio = px.line(
                    df_company,
                    x="Year",
                    y=ratio_option,
                    markers=True,
                    title=f"{ratio_option} over time"
                )
                st.plotly_chart(fig_ratio, use_container_width=True)

    # =========================================
    # SECTION 4: DETAILED ANALYSIS
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">4. Detailed Analysis</p>', unsafe_allow_html=True)

    with st.container(border=True):
        tab_ebit, tab_ratios = st.tabs(["EBIT vs Interest Expense", "Financial Ratios Table"])

        with tab_ebit:
            interest_col = "Interest Expense - Net of (Interest Income)"

            if interest_col in df_company.columns:
                df_scatter = df_company.dropna(subset=["Earnings before Interest & Taxes (EBIT)", interest_col])
                df_scatter = df_scatter[
                    (df_scatter["Earnings before Interest & Taxes (EBIT)"] > 0) & (df_scatter[interest_col] > 0)
                ]

                if not df_scatter.empty:
                    fig_scatter = px.scatter(
                        df_scatter,
                        x=interest_col,
                        y="Earnings before Interest & Taxes (EBIT)",
                        color="ews_level",
                        color_discrete_map={
                            'Safe': '#2ECC71',
                            'Watchlist': '#F1C40F',
                            'Distress': '#E74C3C'
                        },
                        title="EBIT vs Interest Expense"
                    )

                    # Add reference lines
                    x_min = df_scatter[interest_col].min() * 0.5
                    x_max = df_scatter[interest_col].max() * 2
                    x_range = [x_min, x_max]

                    # Line 1: EBIT = Interest (Coverage = 1x)
                    fig_scatter.add_trace(go.Scatter(
                        x=x_range,
                        y=x_range,
                        mode='lines',
                        name='Coverage = 1x',
                        line=dict(color='#E74C3C', width=2, dash='dash'),
                        showlegend=True
                    ))

                    # Line 2: EBIT = 2x Interest (Coverage = 2x)
                    fig_scatter.add_trace(go.Scatter(
                        x=x_range,
                        y=[x * 2 for x in x_range],
                        mode='lines',
                        name='Coverage = 2x',
                        line=dict(color='#2ECC71', width=2, dash='dash'),
                        showlegend=True
                    ))

                    fig_scatter.update_xaxes(type="log")
                    fig_scatter.update_yaxes(type="log")
                    fig_scatter.update_layout(height=400)
                    st.plotly_chart(fig_scatter, use_container_width=True)

        with tab_ratios:
            if not df_year.empty:
                r = df_year.iloc[0]
                rows = [
                    {"Ratio": "ROA", "Value": round(r["ROA"], 3), "Role": "Profitability"},
                    {"Ratio": "Leverage", "Value": round(r["LEV"], 2), "Role": "Capital structure"},
                    {"Ratio": "Current Ratio", "Value": round(r["CUR"], 2), "Role": "Liquidity"}
                ]
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # =========================================
    # SECTION 5: PORTFOLIO VIEW
    # =========================================
    st.markdown("---")
    st.markdown('<p class="section-title">5. Portfolio View - EWS Distribution</p>', unsafe_allow_html=True)

    with st.container(border=True):
        col_filter, col_chart = st.columns([1, 4])

        with col_filter:
            ews_year = st.selectbox(
                "Year",
                options=["All years"] + sorted(df["Year"].dropna().unique().tolist())
            )

            if ews_year == "All years":
                df_dist = df.copy()
            else:
                df_dist = df[df["Year"] == ews_year]

            ews_summary = df_dist["ews_level"].value_counts()

            st.markdown("**Summary**")
            if "Safe" in ews_summary:
                st.success(f"Safe: {ews_summary.get('Safe', 0)}")
            if "Watchlist" in ews_summary:
                st.warning(f"Watchlist: {ews_summary.get('Watchlist', 0)}")
            if "Distress" in ews_summary:
                st.error(f"Distress: {ews_summary.get('Distress', 0)}")

        with col_chart:
            ews_count = (
                df_dist
                .groupby(["Year", "ews_level"])
                .size()
                .reset_index(name="count")
            )

            ews_colors = {
                "Safe": "#2ECC71",
                "Watchlist": "#F1C40F",
                "Distress": "#E74C3C"
            }

            fig_ews = px.bar(
                ews_count,
                x="Year",
                y="count",
                color="ews_level",
                color_discrete_map=ews_colors
            )
            fig_ews.update_layout(barmode="stack", height=400)
            st.plotly_chart(fig_ews, use_container_width=True)

    # Raw Data
    st.markdown("---")
    with st.expander("View Raw Data"):
        st.dataframe(df_company, use_container_width=True, hide_index=True)

# -----------------------------------------
# RUN APPLICATION
# -----------------------------------------
if __name__ == "__main__":
    main()

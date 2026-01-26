import streamlit as st
from bs4 import BeautifulSoup
import pandas as pd
import requests

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Dubai Property Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Premium Dark UI (NO white boxes)
# -------------------------------------------------
st.markdown("""
<style>
.hero {
    padding: 2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: white;
    margin-bottom: 2rem;
}

.property-row {
    padding: 1.3rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    background: rgba(77,163,255,0.15);
    color: #7db1ff;
    font-size: 12px;
    font-weight: 600;
}

a {
    color: #4da3ff !important;
    text-decoration: none;
    font-weight: 500;
}

a:hover {
    text-decoration: underline;
}

[data-testid="stMetric"] {
    background: rgba(255,255,255,0.05);
    padding: 16px;
    border-radius: 14px;
}
</style>

<div class="hero">
    <h1>🏙️ Property Intelligence Tool For Fetch Properties</h1>
    <h3>Dubai’s most exceptional off-plan, ready, and leasing opportunities.</h3>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------
# Scraping Function
# -------------------------------------------------
@st.cache_data(show_spinner=True)
def load_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    url = "https://www.propertyfinder.ae/en/search?c=2&fu=0&rp=y&ob=mr"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    cards = soup.find_all("li", {"role": "listitem"})

    prices = [x.find("div", {"data-testid": "property-card-price"}).get_text(strip=True) for x in cards]
    locations = [x.find("div", {"data-testid": "property-card-location"}).get_text(strip=True) for x in cards]
    sqft = [x.find("p", {"data-testid": "property-card-spec-area"}).get_text(strip=True) for x in cards]
    ptype = [x.find("p", {"data-testid": "property-card-type"}).get_text(strip=True) for x in cards]

    links = [
        "https://www.propertyfinder.ae" + x.find("a")["href"]
        for x in soup.find_all("article", {"data-testid": "property-card"})
    ]

    titles = [
        x.find_next("h3").get_text(strip=True)
        for x in soup.find_all("div", {"data-testid": "property-card-price"})
    ]

    return pd.DataFrame({
        "Title": titles,
        "Location": locations,
        "Price": prices,
        "Area": sqft,
        "Type": ptype,
        "Link": links
    })

# -------------------------------------------------
# Load Data
# -------------------------------------------------
df = load_data()

# -------------------------------------------------
# Sidebar Filters
# -------------------------------------------------
st.sidebar.header("🎯 Filters")

property_types = ["All"] + sorted(df["Type"].unique())
locations = ["All"] + sorted(df["Location"].unique())

selected_type = st.sidebar.selectbox("🏷️ Property Type", property_types)
selected_location = st.sidebar.selectbox("📍 Location", locations)

if selected_type != "All":
    df = df[df["Type"] == selected_type]

if selected_location != "All":
    df = df[df["Location"] == selected_location]

# -------------------------------------------------
# KPIs
# -------------------------------------------------
k1, k2, k3 = st.columns(3)
k1.metric("🏠 Listings", len(df))
k2.metric("🏷️ Types", df["Type"].nunique())
k3.metric("📍 Locations", df["Location"].nunique())

st.markdown("---")

# -------------------------------------------------
# Property Listings (NO white cards)
# -------------------------------------------------
for _, row in df.iterrows():
    st.markdown(f"""
    <div class="property-row">
        <span class="badge">{row['Type']}</span>
        <h3 style="margin-top:8px;">{row['Title']}</h3>
        <p>📍 <b>{row['Location']}</b></p>
        <p>📐 {row['Area']} &nbsp;&nbsp; | &nbsp;&nbsp; 💰 <b>{row['Price']}</b></p>
        <a href="{row['Link']}" target="_blank">🔗 View Property</a>
    </div>
    """, unsafe_allow_html=True)

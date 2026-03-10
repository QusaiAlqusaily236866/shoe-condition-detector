import streamlit as st
import numpy as np
from PIL import Image
import requests
import io
import os

st.set_page_config(page_title="Vinted", page_icon="👗", layout="wide")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

VINTED_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 110 38" width="110" height="38">
  <text x="2" y="30" font-family="Georgia,'Times New Roman',serif" font-size="30"
        font-weight="700" font-style="italic" fill="#007782" letter-spacing="-0.5">Vinted</text>
</svg>"""

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #fff; color: #1a1a1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* search input */
.stTextInput input {
    border: 1px solid #d5d5d5 !important;
    border-radius: 999px !important;
    padding: 10px 18px !important;
    font-size: 14px !important;
    background: #f7f7f5 !important;
    color: #1a1a1a !important;
}
.stTextInput input:focus {
    border-color: #007782 !important;
    background: white !important;
    box-shadow: none !important;
}
.stTextInput input::placeholder { color: #9e9e9e !important; }

/* all buttons default teal */
.stButton > button {
    background: #007782 !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    width: 100% !important;
    padding: 11px !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover { background: #005f6a !important; }

/* pill filter chips */
.pill-btn > .stButton > button {
    background: white !important;
    color: #1a1a1a !important;
    border: 1.5px solid #d5d5d5 !important;
    border-radius: 999px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
}
.pill-btn > .stButton > button:hover {
    border-color: #007782 !important;
    color: #007782 !important;
    background: white !important;
}
.pill-btn-active > .stButton > button {
    background: #1a1a1a !important;
    color: white !important;
    border: 1.5px solid #1a1a1a !important;
    border-radius: 999px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
}

/* product card */
.product-card {
    background: white;
    cursor: pointer;
    margin-bottom: 6px;
}
.product-img-wrap { position: relative; overflow: hidden; border-radius: 6px; }
.product-img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; transition: transform 0.3s; }
.product-card:hover .product-img { transform: scale(1.04); }
.heart-btn {
    position: absolute; top: 8px; right: 8px;
    background: white; border-radius: 50%;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; box-shadow: 0 1px 6px rgba(0,0,0,0.18);
    cursor: pointer;
}
.product-info { padding: 6px 2px 10px; }
.product-price { font-size: 15px; font-weight: 700; color: #1a1a1a; }
.product-brand { font-size: 12px; color: #666; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.product-size  { font-size: 11px; color: #9e9e9e; margin-top: 1px; }
.cond-gently { background: #e8f5e9; color: #2e7d32; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 3px; display: inline-block; margin-top: 4px; }
.cond-worn   { background: #fce4ec; color: #c62828; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 3px; display: inline-block; margin-top: 4px; }

/* sell flow */
.ai-box { background: #f0faf9; border: 1.5px solid #007782; border-radius: 8px; padding: 14px 16px; margin-top: 12px; }

div[data-testid="column"] { padding: 3px !important; }
.element-container { margin-bottom: 6px !important; }
</style>
""", unsafe_allow_html=True)

# ── API helpers ───────────────────────────────────────────────────────────────
def api_get_listings(condition=None, search=None):
    try:
        params = {}
        if condition and condition != "All": params["condition"] = condition
        if search: params["search"] = search
        r = requests.get(f"{BACKEND_URL}/listings", params=params, timeout=5)
        return r.json().get("listings", [])
    except:
        return []

def api_create_listing(data):
    try:
        r = requests.post(f"{BACKEND_URL}/listings", json=data, timeout=5)
        return r.json()
    except:
        return None

def api_predict(image_bytes):
    try:
        r = requests.post(f"{BACKEND_URL}/predict",
                          files={"file": ("shoe.jpg", image_bytes, "image/jpeg")},
                          timeout=30)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("page","browse"),("step",1),("ai",None),("listed",False),("cf","All")]:
    if k not in st.session_state:
        st.session_state[k] = v

def go_sell():
    st.session_state.page   = "sell"
    st.session_state.step   = 1
    st.session_state.ai     = None
    st.session_state.listed = False

# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR  — matches screenshot exactly
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='background:white;border-bottom:1px solid #e8e8e8;padding:10px 20px'>", unsafe_allow_html=True)
nav1, nav2, nav3, nav4 = st.columns([0.6, 0.7, 5, 0.8])
with nav1:
    st.markdown(f"<div style='padding:6px 0'>{VINTED_LOGO}</div>", unsafe_allow_html=True)
with nav2:
    # "Catalog ▾" pill — exactly like screenshot
    st.markdown("""
    <div style='padding:7px 0'>
        <span style='font-size:13px;font-weight:500;color:#1a1a1a;
                     border:1.5px solid #d5d5d5;padding:8px 14px;
                     border-radius:999px;cursor:pointer;background:white;
                     display:inline-flex;align-items:center;gap:6px'>
            Catalog <span style='font-size:10px'>▾</span>
        </span>
    </div>""", unsafe_allow_html=True)
with nav3:
    search = st.text_input("s", placeholder="🔍  Search for items",
                           label_visibility="collapsed", key="srch")
with nav4:
    if st.button("Sell now", key="sell_nav"):
        go_sell(); st.rerun()
st.markdown("</div>", unsafe_allow_html=True)

# ── Category pill bar — matches screenshot exactly ────────────────────────────
cats = ["All","Women","Men","Designer","Kids","Home","Electronics","Entertainment","Hobbies & collectibles","Sport"]
cf   = st.session_state.cf

st.markdown("<div style='background:white;padding:10px 20px 0;display:flex;flex-wrap:nowrap;overflow-x:auto;gap:8px;border-bottom:1px solid #f0f0f0'>", unsafe_allow_html=True)
cat_cols = st.columns(len(cats))
for i, cat in enumerate(cats):
    with cat_cols[i]:
        is_active = (cf == cat) or (cat == "All" and cf == "All")
        css_class = "pill-btn-active" if is_active else "pill-btn"
        st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
        if st.button(cat, key=f"cat_{cat}"):
            st.session_state.cf = cat
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BROWSE
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "browse":

    # ── Hero — exactly matches screenshot ─────────────────────────────────
    st.markdown("""
    <div style="position:relative;width:100%;height:440px;overflow:hidden">
        <img src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1600&q=85"
             style="width:100%;height:100%;object-fit:cover;object-position:center 20%;display:block"/>
        <div style="position:absolute;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.04)"></div>
        <!-- White card bottom-left exactly like Vinted -->
        <div style="position:absolute;bottom:40px;left:40px;
                    background:white;border-radius:4px;
                    padding:32px 32px 36px;max-width:280px;
                    box-shadow:0 2px 16px rgba(0,0,0,0.1)">
            <h2 style="font-size:26px;font-weight:700;color:#1a1a1a;
                       line-height:1.25;margin-bottom:24px">
                Ready to declutter your closet?
            </h2>
            <div id="sell-btn-placeholder" style="height:44px"></div>
            <div style="margin-top:12px;text-align:center">
                <a href="#" style="color:#007782;font-size:13px;font-weight:600;text-decoration:none">
                    Learn how it works
                </a>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Sell now button inside hero card (overlaid)
    _, sell_col, _ = st.columns([0.5, 1, 5])
    with sell_col:
        st.markdown("<div style='margin-top:-195px;position:relative;z-index:10'>", unsafe_allow_html=True)
        if st.button("Sell now", key="hero_sell"):
            go_sell(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Product grid ───────────────────────────────────────────────────────
    cf = st.session_state.cf
    condition_filter = None if cf == "All" else cf
    listings = api_get_listings(
        condition=condition_filter,
        search=search if search else None
    )

    st.markdown(f"""
    <div style="padding:4px 20px 12px;display:flex;justify-content:space-between;align-items:center">
        <span style="font-size:13px;color:#9e9e9e">{len(listings)} items</span>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4, gap="small")
    for i, item in enumerate(listings):
        badge_cls = "cond-gently" if item["condition"]=="Gently worn" else "cond-worn"
        badge_lbl = "✅ Gently worn" if item["condition"]=="Gently worn" else "⚠️ Worn out"
        with cols[i % 4]:
            st.markdown(f"""
            <div class="product-card">
                <div class="product-img-wrap">
                    <img class="product-img" src="{item['img']}" />
                    <div class="heart-btn">🤍</div>
                </div>
                <div class="product-info">
                    <div class="product-price">€{item['price']:.0f}</div>
                    <div class="product-brand">{item['brand']} · {item['title']}</div>
                    <div class="product-size">EU {item['size']}</div>
                    <span class="{badge_cls}">{badge_lbl}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SELL PAGE — same as before, kept exactly
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "sell":

    if st.session_state.listed:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;max-width:480px;margin:40px auto;
                    background:white;border-radius:12px;border:1px solid #e8e8e8">
            <div style="font-size:64px;margin-bottom:16px">🎉</div>
            <h2 style="color:#007782;font-size:24px;margin-bottom:10px;font-weight:700">Item listed!</h2>
            <p style="color:#9e9e9e;font-size:14px">Your shoes are now visible to buyers on Vinted.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Continue browsing"):
            st.session_state.page = "browse"
            st.session_state.listed = False
            st.rerun()
    else:
        step = st.session_state.step
        bc, tc = st.columns([0.4, 5])
        with bc:
            if st.button("←"):
                if step == 1: st.session_state.page = "browse"
                else: st.session_state.step -= 1
                st.rerun()
        with tc:
            st.markdown(f"<h2 style='font-size:18px;font-weight:700;padding:8px 0'>List your item · {step}/3</h2>", unsafe_allow_html=True)

        def dot(n, cur):
            s = "background:#007782;color:white" if n<=cur else "background:#e8e8e8;color:#9e9e9e"
            l = "✓" if n<cur else str(n)
            return f"<span style='{s};width:24px;height:24px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700'>{l}</span>"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px">
            {dot(1,step)}<span style="flex:1;height:1px;background:#e8e8e8"></span>
            {dot(2,step)}<span style="flex:1;height:1px;background:#e8e8e8"></span>
            {dot(3,step)}
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:24px">
            <span style="font-size:11px;color:{'#007782' if step==1 else '#9e9e9e'};font-weight:{'600' if step==1 else '400'}">Photos & AI</span>
            <span style="font-size:11px;color:{'#007782' if step==2 else '#9e9e9e'};font-weight:{'600' if step==2 else '400'}">Details</span>
            <span style="font-size:11px;color:{'#007782' if step==3 else '#9e9e9e'};font-weight:{'600' if step==3 else '400'}">Publish</span>
        </div>
        """, unsafe_allow_html=True)

        if step == 1:
            st.markdown("<p style='font-size:14px;font-weight:600;margin-bottom:6px'>📸 Add photos</p>", unsafe_allow_html=True)
            uploaded = st.file_uploader("Upload", type=["jpg","jpeg","png"], label_visibility="collapsed")
            if uploaded:
                img_bytes = uploaded.read()
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, use_container_width=True)
                if st.session_state.ai is None:
                    if st.button("🤖 Auto-detect condition with AI"):
                        with st.spinner("Analysing..."):
                            result = api_predict(img_bytes)
                            if result: st.session_state.ai = result
                            else: st.error("Could not connect to backend.")
                        st.rerun()
                if st.session_state.ai:
                    r    = st.session_state.ai
                    is_g = r["condition"] == "Gently worn"
                    tip  = "Great condition! Mention this in your listing." if is_g else "Be honest about wear — buyers appreciate transparency."
                    st.markdown(f"""
                    <div class="ai-box">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                            <span style="font-size:13px;font-weight:700;color:#007782">🤖 AI Condition Analysis</span>
                            <span style="background:#007782;color:white;font-size:11px;font-weight:700;padding:3px 10px;border-radius:20px">{r['confidence']}%</span>
                        </div>
                        <span style="background:{'#e8f5e9' if is_g else '#fce4ec'};color:{'#2e7d32' if is_g else '#c62828'};font-size:12px;font-weight:700;padding:3px 12px;border-radius:4px">
                            {'✅ Gently worn' if is_g else '⚠️ Worn out'}
                        </span>
                        <div style="background:#d0e8eb;border-radius:4px;height:4px;margin:10px 0">
                            <div style="background:#007782;height:4px;border-radius:4px;width:{r['confidence']}%"></div>
                        </div>
                        <div style="font-size:12px;color:#666;margin-bottom:8px">
                            Gently worn: <b>{r['prob_gently_worn']}%</b> · Worn out: <b>{r['prob_worn_out']}%</b>
                        </div>
                        <div style="background:white;padding:8px 12px;border-radius:6px;font-size:12px;color:#666;border:1px solid #d0e8eb">💡 {tip}</div>
                    </div>
                    <div style='height:10px'></div>
                    """, unsafe_allow_html=True)
                    if st.button("Use this & continue →"):
                        st.session_state.step = 2; st.rerun()

        elif step == 2:
            ai = st.session_state.ai
            default_cond = ai["condition"] if ai else "Gently worn"
            title = st.text_input("Title *", placeholder="e.g. Nike Air Force 1 White Size 42")
            brand = st.text_input("Brand", placeholder="Nike, Adidas, Vans...")
            c1, c2 = st.columns(2)
            with c1: price = st.number_input("Price (€) *", min_value=0.0, step=0.5)
            with c2: size  = st.text_input("Size", placeholder="EU 42")
            idx  = 0 if default_cond == "Gently worn" else 1
            cond = st.selectbox("Condition" + (" (AI suggested ✨)" if ai else ""),
                                ["Gently worn", "worn out"], index=idx)
            if ai:
                st.markdown(f"<p style='font-size:11px;color:#007782;margin-top:-4px'>🤖 {ai['confidence']}% confident</p>", unsafe_allow_html=True)
            desc = st.text_area("Description", placeholder="Any flaws? Box included?", height=80)
            st.session_state._form = {"title":title,"brand":brand,"price":price,"size":size,"condition":cond,"description":desc}
            if st.button("Continue →"):
                if title and price > 0: st.session_state.step = 3; st.rerun()
                else: st.warning("Title and price are required.")

        elif step == 3:
            form = st.session_state.get("_form", {})
            ai   = st.session_state.ai
            is_g = form.get("condition","") == "Gently worn"
            ai_tag = f'<span style="background:#f0faf9;color:#007782;font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;border:1px solid #b2dde0">🤖 AI verified · {ai["confidence"]}%</span>' if ai else ""
            st.markdown(f"""
            <div style="background:#f7f7f7;border-radius:8px;padding:18px;margin-bottom:16px;border:1px solid #e8e8e8">
                <div style="font-size:17px;font-weight:700;margin-bottom:4px">{form.get('title','—')}</div>
                <div style="font-size:13px;color:#777;margin-bottom:12px">{form.get('brand','')}</div>
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                    <span style="font-size:20px;font-weight:800">€{form.get('price',0):.2f}</span>
                    <span style="font-size:12px;color:#9e9e9e;background:#f0f0f0;padding:3px 8px;border-radius:4px">EU {form.get('size','—')}</span>
                    <span style="background:{'#e8f5e9' if is_g else '#fce4ec'};color:{'#2e7d32' if is_g else '#c62828'};font-size:11px;font-weight:700;padding:3px 10px;border-radius:4px">{'Gently worn' if is_g else 'Worn out'}</span>
                    {ai_tag}
                </div>
            </div>
            <p style="font-size:12px;color:#9e9e9e;margin-bottom:16px">AI-verified listings get <b style="color:#007782">2× more views</b> on average.</p>
            """, unsafe_allow_html=True)
            if st.button("🚀 Publish listing"):
                result = api_create_listing({
                    "title": form.get("title",""), "brand": form.get("brand",""),
                    "price": form.get("price",0), "size": form.get("size",""),
                    "condition": form.get("condition",""),
                    "description": form.get("description",""), "seller": "you",
                })
                if result:
                    st.session_state.listed = True
                    st.balloons(); st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="border-top:1px solid #e8e8e8;background:#f7f7f5;padding:28px 40px;margin-top:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:24px;max-width:1000px;margin:0 auto 20px">
        <div>
            {VINTED_LOGO}
            <p style="font-size:12px;color:#aaa;margin-top:6px;max-width:200px;line-height:1.6">
                Buy & sell second-hand fashion.
            </p>
        </div>
        <div><p style="font-size:12px;font-weight:700;color:#444;margin-bottom:8px">Discover</p>
            <p style="font-size:12px;color:#777;margin:3px 0">New arrivals</p>
            <p style="font-size:12px;color:#777;margin:3px 0">Popular brands</p></div>
        <div><p style="font-size:12px;font-weight:700;color:#444;margin-bottom:8px">Help</p>
            <p style="font-size:12px;color:#777;margin:3px 0">Help centre</p>
            <p style="font-size:12px;color:#777;margin:3px 0">Contact us</p></div>
        <div><p style="font-size:12px;font-weight:700;color:#444;margin-bottom:8px">About</p>
            <p style="font-size:12px;color:#777;margin:3px 0">About Vinted</p>
            <p style="font-size:12px;color:#777;margin:3px 0">Careers</p></div>
    </div>
    <div style="border-top:1px solid #e0e0e0;padding-top:14px;text-align:center">
        <p style="font-size:11px;color:#bbb">© 2026 Vinted · Fashion Item Damage Detection · BUAS ADS-AI Block C · Qusai 236866</p>
    </div>
</div>
""", unsafe_allow_html=True)

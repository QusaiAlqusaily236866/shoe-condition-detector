import streamlit as st
import numpy as np
from PIL import Image
import requests
import io
import os

st.set_page_config(page_title="Vinted", page_icon="👗", layout="wide")

# ── Backend URL ───────────────────────────────────────────────────────────────
# When running with Docker Compose, backend is at http://backend:8000
# When running locally, backend is at http://localhost:8000
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #ffffff; color: #1a1a1a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.product-card { background: white; border-radius: 8px; overflow: hidden; cursor: pointer; transition: box-shadow 0.15s; border: 1px solid #e8e8e8; margin-bottom: 10px; }
.product-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.1); }
.product-img { width: 100%; aspect-ratio: 1; object-fit: cover; display: block; }
.product-info { padding: 8px 10px 12px; }
.product-price { font-size: 15px; font-weight: 700; color: #1a1a1a; }
.product-brand { font-size: 12px; color: #555; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.product-size { font-size: 11px; color: #9e9e9e; margin-top: 2px; }
.heart-btn { position: absolute; top: 8px; right: 8px; background: white; border-radius: 50%; width: 30px; height: 30px; display: flex; align-items: center; justify-content: center; font-size: 15px; box-shadow: 0 1px 4px rgba(0,0,0,0.15); }
.cond-gently { background: #e8f5e9; color: #2e7d32; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 3px; display: inline-block; margin-top: 4px; }
.cond-worn { background: #fce4ec; color: #c62828; font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 3px; display: inline-block; margin-top: 4px; }
.ai-box { background: #f0faf9; border: 1.5px solid #007782; border-radius: 8px; padding: 14px 16px; margin-top: 12px; }
.stButton > button { background: #007782 !important; color: white !important; border: none !important; border-radius: 6px !important; font-weight: 600 !important; font-size: 14px !important; width: 100% !important; padding: 10px !important; }
.stButton > button:hover { background: #005f6a !important; }
div[data-testid="column"] { padding: 2px !important; }
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
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")
        return []

def api_create_listing(data):
    try:
        r = requests.post(f"{BACKEND_URL}/listings", json=data, timeout=5)
        return r.json()
    except Exception as e:
        st.error(f"Backend error: {e}")
        return None

def api_predict(image_bytes):
    try:
        r = requests.post(
            f"{BACKEND_URL}/predict",
            files={"file": ("shoe.jpg", image_bytes, "image/jpeg")},
            timeout=30
        )
        if r.status_code == 200:
            return r.json()
        else:
            st.error(f"Prediction failed: {r.text}")
            return None
    except Exception as e:
        st.error(f"Backend error: {e}")
        return None

def api_like(listing_id):
    try:
        r = requests.post(f"{BACKEND_URL}/listings/{listing_id}/like", timeout=5)
        return r.json()
    except:
        return None

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("page","browse"),("step",1),("ai",None),("listed",False),("cf","All")]:
    if k not in st.session_state:
        st.session_state[k] = v

def go_sell():
    st.session_state.page  = "sell"
    st.session_state.step  = 1
    st.session_state.ai    = None
    st.session_state.listed = False

# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────────────────────────────────────
n1, n2, n3, n4, n5 = st.columns([0.7, 0.7, 4, 1.1, 0.7])
with n1:
    st.markdown("<div style='padding:8px 0'><span style='font-family:Georgia,serif;font-size:26px;font-weight:700;font-style:italic;color:#007782'>Vinted</span></div>", unsafe_allow_html=True)
with n2:
    st.markdown("<div style='padding:8px 0'><span style='font-size:13px;color:#1a1a1a;border:1px solid #e0e0e0;padding:8px 14px;border-radius:6px;cursor:pointer'>Articles ▾</span></div>", unsafe_allow_html=True)
with n3:
    search = st.text_input("Search", placeholder="🔍  Find articles", label_visibility="collapsed", key="srch")
with n4:
    st.markdown("<div style='padding:6px 0'><span style='font-size:13px;font-weight:600;color:#007782;border:1.5px solid #007782;padding:8px 14px;border-radius:6px;white-space:nowrap'>Register | Login</span></div>", unsafe_allow_html=True)
with n5:
    if st.button("Sell now", key="sell_nav"):
        go_sell(); st.rerun()

st.markdown("<hr style='margin:0;border:none;border-top:1px solid #e8e8e8'>", unsafe_allow_html=True)

# ── Category bar ──────────────────────────────────────────────────────────────
cats = ["Ladies","Gentlemen","Designer","Children","Home","Electronics","Entertainment","Sport"]
cat_cols = st.columns(len(cats))
for i, cat in enumerate(cats):
    with cat_cols[i]:
        st.button(cat, key=f"cat_{cat}")
st.markdown("<hr style='margin:0;border:none;border-top:1px solid #e8e8e8'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BROWSE PAGE
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "browse":

    # Hero
    st.markdown("""
    <div style="position:relative;width:100%;height:400px;overflow:hidden">
        <img src="https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80"
             style="width:100%;height:100%;object-fit:cover;object-position:center 20%" />
        <div style="position:absolute;top:50%;left:80px;transform:translateY(-50%);
                    background:white;border-radius:12px;padding:32px 36px;max-width:290px;
                    box-shadow:0 4px 24px rgba(0,0,0,0.12)">
            <h2 style="font-size:23px;font-weight:700;color:#1a1a1a;line-height:1.35;margin-bottom:60px">
                Ready to clean out your closet?
            </h2>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, hero_col, _ = st.columns([1, 1.2, 4])
    with hero_col:
        st.markdown("<div style='margin-top:-165px;position:relative;z-index:10'>", unsafe_allow_html=True)
        if st.button("Start selling", key="hero_sell"):
            go_sell(); st.rerun()
        st.markdown("<div style='text-align:center;margin-top:8px'><span style='color:#007782;font-size:13px;font-weight:500'>How it works</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Info bar
    st.markdown("""
    <div style="background:#f9f9f9;border:1px solid #e8e8e8;border-radius:6px;padding:11px 20px;
                font-size:13px;color:#555;display:flex;justify-content:space-between;
                margin:0 24px 16px">
        <span>You will see the shipping costs at checkout.</span>
        <span style="color:#9e9e9e;cursor:pointer">✕</span>
    </div>
    """, unsafe_allow_html=True)

    # Filter chips
    fc1, fc2, fc3, _ = st.columns([0.5, 0.75, 0.65, 5])
    with fc1:
        if st.button("All", key="fc_all"): st.session_state.cf="All"; st.rerun()
    with fc2:
        if st.button("Gently worn", key="fc_g"): st.session_state.cf="Gently worn"; st.rerun()
    with fc3:
        if st.button("Worn out", key="fc_w"): st.session_state.cf="worn out"; st.rerun()

    st.markdown("<div style='font-size:18px;font-weight:700;padding:16px 24px 8px'>White shoes for sale</div>", unsafe_allow_html=True)

    # Fetch from backend
    listings = api_get_listings(
        condition=st.session_state.cf,
        search=search if search else None
    )

    st.markdown(f"<p style='font-size:12px;color:#9e9e9e;padding:0 24px 8px'>{len(listings)} items</p>", unsafe_allow_html=True)

    cols = st.columns(3, gap="small")
    for i, item in enumerate(listings):
        badge_cls = "cond-gently" if item["condition"]=="Gently worn" else "cond-worn"
        badge_lbl = "✅ Gently worn" if item["condition"]=="Gently worn" else "⚠️ Worn out"
        with cols[i % 3]:
            st.markdown(f"""
            <div class="product-card">
                <div style="position:relative">
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
# SELL PAGE
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "sell":

    if st.session_state.listed:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px;max-width:480px;margin:32px auto;
                    background:white;border-radius:12px;border:1px solid #e8e8e8">
            <div style="font-size:56px;margin-bottom:16px">🎉</div>
            <h2 style="color:#007782;font-size:22px;margin-bottom:8px">Item listed!</h2>
            <p style="color:#9e9e9e;font-size:14px">Buyers can now find your shoes on Vinted.</p>
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
            st.markdown(f"<h2 style='font-size:17px;font-weight:700;padding:8px 0'>Add item · {step}/3</h2>", unsafe_allow_html=True)

        def dot(n, cur):
            s = "background:#007782;color:white" if n<=cur else "background:#e0e0e0;color:#9e9e9e"
            l = "✓" if n<cur else str(n)
            return f"<span style='{s};width:22px;height:22px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:11px;font-weight:700'>{l}</span>"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:4px;margin-bottom:6px">
            {dot(1,step)}<span style="flex:1;height:1px;background:#e0e0e0"></span>
            {dot(2,step)}<span style="flex:1;height:1px;background:#e0e0e0"></span>
            {dot(3,step)}
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:20px">
            <span style="font-size:11px;color:{'#007782' if step==1 else '#9e9e9e'}">Photos & AI</span>
            <span style="font-size:11px;color:{'#007782' if step==2 else '#9e9e9e'}">Details</span>
            <span style="font-size:11px;color:{'#007782' if step==3 else '#9e9e9e'}">Publish</span>
        </div>
        """, unsafe_allow_html=True)

        # ── STEP 1: Photo + AI ────────────────────────────────────────────
        if step == 1:
            uploaded = st.file_uploader("Upload shoe photo", type=["jpg","jpeg","png"], label_visibility="collapsed")
            if uploaded:
                img_bytes = uploaded.read()
                img = Image.open(io.BytesIO(img_bytes))
                st.image(img, use_container_width=True)

                if st.session_state.ai is None:
                    if st.button("🤖 Auto-detect condition with AI"):
                        with st.spinner("Sending to AI backend..."):
                            result = api_predict(img_bytes)
                            if result:
                                st.session_state.ai = result
                        st.rerun()

                if st.session_state.ai:
                    r    = st.session_state.ai
                    is_g = r["condition"] == "Gently worn"
                    st.markdown(f"""
                    <div class="ai-box">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
                            <span style="font-size:13px;font-weight:600;color:#007782">🤖 AI Condition Result</span>
                            <span style="background:#007782;color:white;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px">{r['confidence']}%</span>
                        </div>
                        <span style="background:{'#e8f5e9' if is_g else '#fce4ec'};color:{'#2e7d32' if is_g else '#c62828'};font-size:12px;font-weight:700;padding:3px 10px;border-radius:4px">
                            {'✅ Gently worn' if is_g else '⚠️ Worn out'}
                        </span>
                        <div style="background:#d0e8eb;border-radius:3px;height:4px;margin:10px 0">
                            <div style="background:#007782;height:4px;border-radius:3px;width:{r['confidence']}%"></div>
                        </div>
                        <div style="font-size:11px;color:#777">
                            Gently worn: <b>{r['prob_gently_worn']}%</b> · Worn out: <b>{r['prob_worn_out']}%</b>
                        </div>
                    </div>
                    <div style='height:10px'></div>
                    """, unsafe_allow_html=True)
                    if st.button("Next →"):
                        st.session_state.step = 2
                        st.rerun()

        # ── STEP 2: Details ───────────────────────────────────────────────
        elif step == 2:
            ai = st.session_state.ai
            default_cond = ai["condition"] if ai else "Gently worn"
            title = st.text_input("Title *", placeholder="e.g. Nike Air Force 1 White")
            brand = st.text_input("Brand", placeholder="Nike, Adidas, Vans...")
            c1, c2 = st.columns(2)
            with c1: price = st.number_input("Price (€) *", min_value=0.0, step=0.5)
            with c2: size  = st.text_input("Size", placeholder="EU 42")
            idx  = 0 if default_cond == "Gently worn" else 1
            cond = st.selectbox("Condition" + (" (AI suggested ✨)" if ai else ""),
                                ["Gently worn", "worn out"], index=idx)
            desc = st.text_area("Description", placeholder="Any flaws? Box included?", height=80)
            st.session_state._form = {
                "title": title, "brand": brand,
                "price": price, "size": size,
                "condition": cond, "description": desc
            }
            if st.button("Next →"):
                if title and price > 0:
                    st.session_state.step = 3
                    st.rerun()
                else:
                    st.warning("Title and price are required.")

        # ── STEP 3: Review & Publish ──────────────────────────────────────
        elif step == 3:
            form = st.session_state.get("_form", {})
            ai   = st.session_state.ai
            is_g = form.get("condition","") == "Gently worn"
            ai_tag = (f'<span style="background:#f0faf9;color:#007782;font-size:10px;font-weight:700;'
                      f'padding:2px 7px;border-radius:4px;border:1px solid #007782">'
                      f'🤖 AI verified · {ai["confidence"]}%</span>') if ai else ""

            st.markdown(f"""
            <div style="background:white;border-radius:8px;padding:16px;margin-bottom:16px;border:1px solid #e8e8e8">
                <div style="font-size:16px;font-weight:700;margin-bottom:4px">{form.get('title','—')}</div>
                <div style="font-size:12px;color:#9e9e9e;margin-bottom:10px">{form.get('brand','')}</div>
                <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                    <span style="font-size:18px;font-weight:700">€{form.get('price',0):.2f}</span>
                    <span style="font-size:12px;color:#9e9e9e">EU {form.get('size','—')}</span>
                    <span style="background:{'#e8f5e9' if is_g else '#fce4ec'};
                                 color:{'#2e7d32' if is_g else '#c62828'};
                                 font-size:11px;font-weight:700;padding:2px 8px;border-radius:4px">
                        {'Gently worn' if is_g else 'Worn out'}
                    </span>
                    {ai_tag}
                </div>
            </div>
            <p style="font-size:12px;color:#9e9e9e;margin-bottom:16px">
                AI-verified listings get <b style="color:#007782">2× more views</b> on average.
            </p>
            """, unsafe_allow_html=True)

            if st.button("🚀 Publish now"):
                # POST to backend
                result = api_create_listing({
                    "title":       form.get("title",""),
                    "brand":       form.get("brand",""),
                    "price":       form.get("price", 0),
                    "size":        form.get("size",""),
                    "condition":   form.get("condition",""),
                    "description": form.get("description",""),
                    "seller":      "you",
                })
                if result:
                    st.session_state.listed = True
                    st.balloons()
                    st.rerun()

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:28px 16px;margin-top:16px;border-top:1px solid #e8e8e8;background:white">
    <span style="font-family:Georgia,serif;font-size:22px;font-weight:700;font-style:italic;color:#007782">Vinted</span>
    <p style="font-size:11px;color:#9e9e9e;margin-top:6px">Fashion Item Damage Detection · BUAS ADS-AI · Qusai 236866</p>
</div>
""", unsafe_allow_html=True)

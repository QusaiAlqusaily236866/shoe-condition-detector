import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import os

st.set_page_config(page_title="Vinted – Second-hand Shoes", page_icon="👟", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.badge-gently { background: #e8f5e9; color: #2e7d32; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.badge-worn   { background: #fce4ec; color: #c62828; padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; }
.listing-card { background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.07); margin-bottom: 16px; }
.card-img { width: 100%; height: 180px; object-fit: cover; display: block; }
.card-body { padding: 12px 14px; }
.card-title { font-weight: 600; font-size: 14px; color: #222; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 6px; }
.card-seller { font-size: 11px; color: #aaa; margin-top: 6px; }
.ai-box { background: #e6f9fa; border: 1.5px solid #09B1BA; border-radius: 12px; padding: 18px; margin-top: 12px; }
.ai-box h4 { color: #09B1BA; margin: 0 0 10px; font-size: 15px; }
.stButton > button { background: #09B1BA !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 14px !important; width: 100% !important; padding: 10px !important; }
.stButton > button:hover { background: #078a92 !important; }
div[data-testid="column"] { padding: 4px !important; }
</style>
""", unsafe_allow_html=True)

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_PATH  = "best_model.keras"
CLASS_NAMES = ["Gently worn", "worn out"]
IMG_SIZE    = (160, 160)

@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return tf.keras.models.load_model(MODEL_PATH)

def preprocess(img):
    img = img.convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    return np.expand_dims(arr, axis=0)

def predict(model, img):
    arr = preprocess(img)
    prob_worn = float(model.predict(arr, verbose=0)[0][0])
    probs = [1 - prob_worn, prob_worn]
    idx   = int(np.argmax(probs))
    return CLASS_NAMES[idx], probs[idx] * 100, probs

model = load_model()

# ── Session state ─────────────────────────────────────────────────────────────
for k, v in [("page","browse"),("sell_step",1),("ai_result",None),("listed",False),("active_filter","All")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── Listings ──────────────────────────────────────────────────────────────────
listings = [
    {"title":"Nike Air Force 1 White",   "price":"€35","size":"42","condition":"Gently worn","seller":"julia_m", "likes":12,
     "img":"https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=400&q=80"},
    {"title":"Adidas Stan Smith White",  "price":"€28","size":"40","condition":"worn out",   "seller":"thomas_k","likes":7,
     "img":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"},
    {"title":"Vans Old Skool White",     "price":"€22","size":"38","condition":"Gently worn","seller":"sara_v",  "likes":19,
     "img":"https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&q=80"},
    {"title":"Converse Chuck Taylor",    "price":"€18","size":"41","condition":"worn out",   "seller":"mike_r",  "likes":3,
     "img":"https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=400&q=80"},
    {"title":"New Balance 574 White",    "price":"€42","size":"43","condition":"Gently worn","seller":"lena_b",  "likes":24,
     "img":"https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&q=80"},
    {"title":"Puma Suede Classic White", "price":"€30","size":"39","condition":"worn out",   "seller":"alex_f",  "likes":8,
     "img":"https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=400&q=80"},
]

# ─────────────────────────────────────────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────────────────────────────────────────
n1, n2, n3 = st.columns([1, 5, 1])
with n1:
    st.markdown("<div style='padding:14px 0'><span style='font-size:26px;font-weight:800;color:#09B1BA;letter-spacing:-1px'>vinted</span></div>", unsafe_allow_html=True)
with n2:
    search = st.text_input("", placeholder="🔍  Search shoes...", label_visibility="collapsed", key="search_box")
with n3:
    if st.button("＋ Sell now", key="sell_btn"):
        st.session_state.page = "sell"
        st.session_state.sell_step = 1
        st.session_state.ai_result = None
        st.session_state.listed = False
        st.rerun()

st.markdown("<hr style='margin:0 0 0 0;border:none;border-top:1px solid #e8e8e8'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# BROWSE PAGE
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "browse":

    st.markdown("""
    <div style="background:linear-gradient(135deg,#09B1BA,#06979f);padding:40px 32px;text-align:center;color:white">
        <h1 style="font-size:32px;font-weight:800;margin:0 0 8px">Second-hand shoes, first-class style</h1>
        <p style="font-size:16px;opacity:0.9;margin:0">🤖 AI-powered condition detection — list your shoes in seconds</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter buttons
    st.markdown("<div style='padding:12px 0 4px'>", unsafe_allow_html=True)
    fc = st.columns([1,1,1,6])
    for i, f in enumerate(["All","Gently worn","Worn out"]):
        with fc[i]:
            if st.button(f, key=f"f_{f}"):
                st.session_state.active_filter = f
                st.rerun()

    # Filter & search
    af = st.session_state.active_filter
    filtered = [l for l in listings if
                af == "All" or
                l["condition"] == af or
                (af == "Worn out" and l["condition"] == "worn out")]
    if search:
        filtered = [l for l in filtered if search.lower() in l["title"].lower()]

    st.markdown(f"<p style='color:#888;font-size:13px;padding:4px 0'>{len(filtered)} items found</p>", unsafe_allow_html=True)

    # Grid — 3 columns
    cols = st.columns(3)
    for i, shoe in enumerate(filtered):
        badge = ('<span class="badge-gently">✅ Gently worn</span>'
                 if shoe["condition"] == "Gently worn"
                 else '<span class="badge-worn">⚠️ Worn out</span>')
        with cols[i % 3]:
            st.markdown(f"""
            <div class="listing-card">
                <img class="card-img" src="{shoe['img']}" />
                <div class="card-body">
                    <div class="card-title">{shoe['title']}</div>
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
                        <span style="font-weight:700;font-size:16px;color:#09B1BA">{shoe['price']}</span>
                        <span style="font-size:12px;color:#888">EU {shoe['size']}</span>
                    </div>
                    {badge}
                    <div class="card-seller">@{shoe['seller']} · {shoe['likes']} ❤️</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SELL PAGE
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.page == "sell":

    if st.session_state.listed:
        st.markdown("""
        <div style="text-align:center;padding:80px 20px">
            <div style="font-size:64px;margin-bottom:16px">🎉</div>
            <h2 style="color:#09B1BA">Your item is listed!</h2>
            <p style="color:#666">Your shoes are now visible to buyers on Vinted.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("← Back to browsing"):
            st.session_state.page = "browse"
            st.session_state.listed = False
            st.rerun()

    else:
        step = st.session_state.sell_step

        # Header
        hc1, hc2 = st.columns([1,6])
        with hc1:
            if st.button("← Back"):
                if step == 1:
                    st.session_state.page = "browse"
                else:
                    st.session_state.sell_step -= 1
                st.rerun()
        with hc2:
            st.markdown("<h2 style='margin:8px 0;font-size:20px'>List your shoes</h2>", unsafe_allow_html=True)

        # Step indicator
        def pill(n, current):
            if n < current:  return f"<span style='background:#09B1BA;color:white;border-radius:50%;width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700'>✓</span>"
            if n == current: return f"<span style='background:#09B1BA;color:white;border-radius:50%;width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700'>{n}</span>"
            return f"<span style='background:#e0e0e0;color:#aaa;border-radius:50%;width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;font-size:12px'>{n}</span>"

        labels = ["Photo & AI","Details","Publish"]
        pills_html = " <span style='color:#ddd;margin:0 4px'>→</span> ".join(
            f"{pill(i+1,step)} <b style='color:{'#09B1BA' if step==i+1 else '#aaa'};font-size:13px'>{labels[i]}</b>"
            for i in range(3)
        )
        st.markdown(f"<div style='display:flex;align-items:center;gap:6px;padding:8px 0 20px'>{pills_html}</div>", unsafe_allow_html=True)

        # ── STEP 1 ────────────────────────────────────────────────────────
        if step == 1:
            uploaded = st.file_uploader("Upload a photo of your shoes", type=["jpg","jpeg","png"])
            if uploaded:
                img = Image.open(uploaded)
                st.image(img, use_container_width=True, caption="Your photo")

                if st.session_state.ai_result is None:
                    if st.button("✨ Detect condition with AI"):
                        with st.spinner("🔍 AI is inspecting your shoes..."):
                            if model:
                                cond, conf, probs = predict(model, img)
                                st.session_state.ai_result = {"condition":cond,"confidence":conf,"probs":probs}
                            else:
                                st.error("Model not loaded.")
                        st.rerun()

                if st.session_state.ai_result:
                    r = st.session_state.ai_result
                    badge = ('<span class="badge-gently">✅ ' + r["condition"] + '</span>'
                             if r["condition"] == "Gently worn"
                             else '<span class="badge-worn">⚠️ ' + r["condition"] + '</span>')
                    tip = ("Great condition! Highlight this in your listing."
                           if r["condition"] == "Gently worn"
                           else "Be transparent about wear — buyers appreciate honesty.")
                    st.markdown(f"""
                    <div class="ai-box">
                        <h4>🤖 AI Condition Report</h4>
                        <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;flex-wrap:wrap">
                            <span style="font-size:13px;color:#555">Detected:</span>
                            {badge}
                            <span style="margin-left:auto;background:#09B1BA;color:white;border-radius:20px;padding:2px 10px;font-size:12px;font-weight:700">{r['confidence']:.0f}% confident</span>
                        </div>
                        <div style="background:#c8f0f2;border-radius:4px;height:6px;margin:8px 0">
                            <div style="background:#09B1BA;height:6px;border-radius:4px;width:{r['confidence']}%"></div>
                        </div>
                        <div style="font-size:13px;color:#555;margin:6px 0">
                            👟 Gently worn: <b>{r['probs'][0]*100:.1f}%</b> &nbsp;|&nbsp; ⚠️ Worn out: <b>{r['probs'][1]*100:.1f}%</b>
                        </div>
                        <div style="background:white;padding:8px 12px;border-radius:8px;font-size:13px;color:#666;margin-top:8px">
                            💡 <b>Seller tip:</b> {tip}
                        </div>
                    </div>
                    <div style='height:12px'></div>
                    """, unsafe_allow_html=True)
                    if st.button("Use this & continue →"):
                        st.session_state.sell_step = 2
                        st.rerun()

        # ── STEP 2 ────────────────────────────────────────────────────────
        elif step == 2:
            ai = st.session_state.ai_result
            default_cond = ai["condition"] if ai else "Gently worn"
            title = st.text_input("Item title *", placeholder="e.g. Nike Air Force 1 White Size 42")
            c1, c2 = st.columns(2)
            with c1: price = st.number_input("Price (€) *", min_value=0.0, step=0.5)
            with c2: size  = st.text_input("EU Size", placeholder="e.g. 42")
            idx  = 0 if default_cond == "Gently worn" else 1
            cond = st.selectbox("Condition (AI pre-filled ✨)", CLASS_NAMES, index=idx)
            if ai:
                st.markdown(f"<p style='font-size:12px;color:#09B1BA;margin-top:-8px'>🤖 AI suggested: {default_cond}</p>", unsafe_allow_html=True)
            desc = st.text_area("Description", placeholder="Describe your shoes — brand, any flaws, original box?", height=100)
            st.session_state._form = {"title":title,"price":price,"size":size,"cond":cond,"desc":desc}
            if st.button("Continue →"):
                if title and price > 0:
                    st.session_state.sell_step = 3
                    st.rerun()
                else:
                    st.warning("Please fill in title and price.")

        # ── STEP 3 ────────────────────────────────────────────────────────
        elif step == 3:
            form = st.session_state.get("_form", {})
            ai   = st.session_state.ai_result
            ai_html = (f'<div style="margin-top:10px;padding:6px 10px;background:#e6f9fa;border-radius:8px;font-size:12px;color:#09B1BA">🤖 AI-verified condition · {ai["confidence"]:.0f}% confidence</div>'
                       if ai else "")
            st.markdown(f"""
            <div style="background:#f9f9f9;border-radius:12px;padding:16px;margin-bottom:16px">
                <div style="font-weight:700;font-size:15px;margin-bottom:6px">{form.get('title','Your shoes')}</div>
                <div style="font-size:13px;color:#666;display:flex;gap:16px">
                    <span>💰 €{form.get('price',0):.2f}</span>
                    <span>📏 EU {form.get('size','—')}</span>
                    <span style="color:#09B1BA;font-weight:600">✓ {form.get('cond','—')}</span>
                </div>
                {ai_html}
            </div>
            <p style="font-size:13px;color:#888;margin-bottom:20px">
                Listings with AI-verified conditions get <b style="color:#09B1BA">2× more views</b> on average.
            </p>
            """, unsafe_allow_html=True)
            if st.button("🚀 Publish listing"):
                st.session_state.listed = True
                st.balloons()
                st.rerun()

# Footer
st.markdown("""
<div style="text-align:center;font-size:12px;color:#aaa;padding:24px;margin-top:32px;border-top:1px solid #f0f0f0">
    Fashion Item Damage Detection · BUAS ADS-AI Block C · Powered by your CNN 🤖
</div>
""", unsafe_allow_html=True)

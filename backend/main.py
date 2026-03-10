from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import tensorflow as tf
import numpy as np
from PIL import Image
import io, os, uuid, json
from datetime import datetime

app = FastAPI(title="Vinted Shoe Detector API")

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL_PATH  = "best_model.keras"
CLASS_NAMES = ["Gently worn", "worn out"]
IMG_SIZE    = (160, 160)

model = None

@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        model = tf.keras.models.load_model(MODEL_PATH)
        print(f"✅ Model loaded from {MODEL_PATH}")
    else:
        print("⚠️  Model not found — predictions will be unavailable")

# ── In-memory DB (replace with real DB later) ─────────────────────────────────
listings_db: List[dict] = [
    {"id": "1", "title": "Nike Air Force 1 White", "brand": "Nike", "price": 35.0,
     "size": "42", "condition": "Gently worn", "description": "Great condition, worn a few times.",
     "seller": "julia_m", "likes": 12, "created_at": "2026-03-01",
     "img": "https://images.unsplash.com/photo-1600269452121-4f2416e55c28?w=400&q=80"},
    {"id": "2", "title": "Adidas Stan Smith White", "brand": "Adidas", "price": 28.0,
     "size": "40", "condition": "worn out", "description": "Some scuffs on the sole.",
     "seller": "thomas_k", "likes": 7, "created_at": "2026-03-02",
     "img": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"},
    {"id": "3", "title": "Vans Old Skool White", "brand": "Vans", "price": 22.0,
     "size": "38", "condition": "Gently worn", "description": "Barely used.",
     "seller": "sara_v", "likes": 19, "created_at": "2026-03-03",
     "img": "https://images.unsplash.com/photo-1525966222134-fcfa99b8ae77?w=400&q=80"},
    {"id": "4", "title": "Converse Chuck Taylor", "brand": "Converse", "price": 18.0,
     "size": "41", "condition": "worn out", "description": "Visible wear marks.",
     "seller": "mike_r", "likes": 3, "created_at": "2026-03-04",
     "img": "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=400&q=80"},
    {"id": "5", "title": "New Balance 574", "brand": "New Balance", "price": 42.0,
     "size": "43", "condition": "Gently worn", "description": "Like new.",
     "seller": "lena_b", "likes": 24, "created_at": "2026-03-05",
     "img": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=400&q=80"},
    {"id": "6", "title": "Puma Suede Classic", "brand": "Puma", "price": 30.0,
     "size": "39", "condition": "worn out", "description": "Needs cleaning.",
     "seller": "alex_f", "likes": 8, "created_at": "2026-03-06",
     "img": "https://images.unsplash.com/photo-1587563871167-1ee9c731aefb?w=400&q=80"},
]

# ── Schemas ───────────────────────────────────────────────────────────────────
class ListingCreate(BaseModel):
    title: str
    brand: Optional[str] = ""
    price: float
    size: Optional[str] = ""
    condition: str
    description: Optional[str] = ""
    seller: Optional[str] = "anonymous"
    img: Optional[str] = "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"

class PredictionResponse(BaseModel):
    condition: str
    confidence: float
    prob_gently_worn: float
    prob_worn_out: float

# ── ROUTES ────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Vinted Shoe Detector API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

# ── Listings CRUD ─────────────────────────────────────────────────────────────

@app.get("/listings")
def get_listings(condition: Optional[str] = None, search: Optional[str] = None):
    """Get all listings with optional filtering."""
    result = listings_db.copy()
    if condition and condition != "All":
        result = [l for l in result if l["condition"].lower() == condition.lower()]
    if search:
        result = [l for l in result if
                  search.lower() in l["title"].lower() or
                  search.lower() in l["brand"].lower()]
    return {"listings": result, "total": len(result)}

@app.get("/listings/{listing_id}")
def get_listing(listing_id: str):
    """Get a single listing by ID."""
    for l in listings_db:
        if l["id"] == listing_id:
            return l
    raise HTTPException(status_code=404, detail="Listing not found")

@app.post("/listings")
def create_listing(listing: ListingCreate):
    """Create a new listing."""
    new_listing = {
        "id": str(uuid.uuid4()),
        "title": listing.title,
        "brand": listing.brand,
        "price": listing.price,
        "size": listing.size,
        "condition": listing.condition,
        "description": listing.description,
        "seller": listing.seller,
        "img": listing.img,
        "likes": 0,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }
    listings_db.append(new_listing)
    return {"message": "Listing created successfully", "listing": new_listing}

@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: str):
    """Delete a listing."""
    for i, l in enumerate(listings_db):
        if l["id"] == listing_id:
            listings_db.pop(i)
            return {"message": "Listing deleted"}
    raise HTTPException(status_code=404, detail="Listing not found")

@app.post("/listings/{listing_id}/like")
def like_listing(listing_id: str):
    """Like a listing."""
    for l in listings_db:
        if l["id"] == listing_id:
            l["likes"] += 1
            return {"likes": l["likes"]}
    raise HTTPException(status_code=404, detail="Listing not found")

# ── AI Prediction ─────────────────────────────────────────────────────────────

@app.post("/predict", response_model=PredictionResponse)
async def predict_condition(file: UploadFile = File(...)):
    """Predict shoe condition from uploaded image."""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    # Read and preprocess image
    contents = await file.read()
    img = Image.open(io.BytesIO(contents)).convert("RGB").resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) / 255.0
    arr = np.expand_dims(arr, axis=0)

    # Predict
    prob_worn = float(model.predict(arr, verbose=0)[0][0])
    probs = [1 - prob_worn, prob_worn]
    idx   = int(np.argmax(probs))

    return PredictionResponse(
        condition=CLASS_NAMES[idx],
        confidence=round(probs[idx] * 100, 1),
        prob_gently_worn=round(probs[0] * 100, 1),
        prob_worn_out=round(probs[1] * 100, 1),
    )

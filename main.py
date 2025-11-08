import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

app = FastAPI(title="Wellness Chat Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    message: str = Field(..., description="The latest user message")
    history: Optional[List[Message]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    reply: str


def generate_reply(text: str) -> str:
    """Lightweight rule-based wellness assistant.
    This is not medical advice. Encourages safe, general guidance.
    """
    q = text.lower().strip()

    disclaimer = (
        "Note: This is general wellness information and not a medical diagnosis. "
        "Consult a qualified clinician for personalized care or urgent concerns."
    )

    # Tongue health heuristics
    if any(k in q for k in ["tongue", "coating", "ulcer", "sores", "oral", "thrush", "mouth"]):
        return (
            "Tongue health quick read:\n"
            "• Typical: pink, moist, thin white coating.\n"
            "• Thick white/yellow coating: dehydration, oral hygiene issues, or possible fungal overgrowth.\n"
            "• Red/pebbled or very smooth: possible nutrient gaps (B12, iron), irritation, or heat/spice.\n"
            "• Ulcers/sores: consider trauma, stress, vitamin B/iron, or viral causes.\n"
            "Care steps: hydrate, brush tongue gently, avoid irritants, ensure balanced nutrition, and see a dentist/clinician if persistent (>2 weeks), painful, or with fever.\n\n"
            + disclaimer
        )

    # Fitness guidance
    if any(k in q for k in ["workout", "training", "gym", "strength", "cardio", "hypertrophy", "fat loss", "muscle"]):
        return (
            "Smart training plan:\n"
            "• Weekly: 2–3 strength sessions + 150–300 min moderate cardio (or 75–150 min vigorous).\n"
            "• Lifts: focus on compounds (squat, hinge, push, pull), add accessories; 6–12 reps for hypertrophy, 2–3 RIR.\n"
            "• Progression: add small load or reps weekly; deload every 4–8 weeks.\n"
            "• Recovery: sleep 7–9h, protein 1.6–2.2 g/kg/day, manage stress.\n\n"
            + disclaimer
        )

    # Diet & nutrition
    if any(k in q for k in ["diet", "nutrition", "protein", "calorie", "macro", "meal", "keto", "fasting", "fiber"]):
        return (
            "Nutrition basics:\n"
            "• Build plates: 40% veggies, 30% lean protein, 20% smart carbs, 10% healthy fats.\n"
            "• Protein: ~1.6–2.2 g/kg/day; distribute across meals.\n"
            "• Fiber: 25–38 g/day from plants; hydrate well.\n"
            "• Weight goals: modest deficit (250–500 kcal) for fat loss; small surplus for muscle gain.\n"
            "• Adherence beats perfection—choose a pattern you can sustain.\n\n"
            + disclaimer
        )

    # Medical records & tracking
    if any(k in q for k in ["records", "labs", "blood work", "medical history", "medication", "symptom", "log", "trend"]):
        return (
            "Better health record-keeping:\n"
            "• Keep a simple log with dates for symptoms, diagnoses, meds/supplements, allergies, and key vitals (BP, HR, weight).\n"
            "• Track labs as a table (test, value, range, date); add notes and questions for your visit.\n"
            "• Export/share a concise summary (1 page) with your clinician.\n"
            "• Secure storage and backups are important; protect sensitive info.\n\n"
            + disclaimer
        )

    # General wellness
    if any(k in q for k in ["sleep", "stress", "wellness", "energy", "recovery", "habit", "routine", "mindfulness", "hydrate"]):
        return (
            "Core wellness habits:\n"
            "• Sleep: 7–9 hours, consistent schedule, dark/cool room.\n"
            "• Stress: brief daily decompression (walks, breathing, journaling).\n"
            "• Movement: stand and stroll breaks every hour; sunlight in the morning.\n"
            "• Hydration: ~30–35 ml/kg/day; more in heat/exercise.\n\n"
            + disclaimer
        )

    # Safety fallback
    if any(k in q for k in ["chest pain", "shortness of breath", "severe", "emergency", "fainted", "suicidal", "stroke"]):
        return (
            "Your symptoms could be urgent. Please seek immediate in-person medical care or call local emergency services.\n\n"
            + disclaimer
        )

    # Default helpful response
    return (
        "I can help with training plans, macro-friendly meals, tongue health cues, organizing medical records, and daily wellness habits. "
        "Tell me more about your goal or question (e.g., '3-day full-body plan' or 'interpret white tongue coating').\n\n"
        + disclaimer
    )


@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = generate_reply(req.message)
    return ChatResponse(reply=reply)


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        # Try to import database module
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            # Try to list collections to verify connectivity
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]  # Show first 10 collections
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    # Check environment variables
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

"""
ClearLabel — AI Ingredient Education PWA
Backend: Flask + Claude/OpenAI API
"""

import os
import json
import base64
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory

# ── AI client setup ─────────────────────────────────────────────────────────
SECRETS_PATH = Path("/home/node/.openclaw/workspace/automation/secrets.json")
secrets = {}
if SECRETS_PATH.exists():
    with open(SECRETS_PATH) as f:
        secrets = json.load(f)

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY") or secrets.get("anthropic_api_key") or secrets.get("anthropic")
OPENAI_KEY    = os.environ.get("OPENAI_API_KEY")    or secrets.get("openai_api_key")

AI_PROVIDER = "none"
client = None

if ANTHROPIC_KEY:
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    AI_PROVIDER = "anthropic"
    print("✅ Using Claude (Anthropic)")
elif OPENAI_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY)
    AI_PROVIDER = "openai"
    print("✅ Using GPT-4o (OpenAI) — add Anthropic key to switch to Claude")
else:
    print("⚠️  No AI key found — /analyze will return demo data")

# ── OCR setup ────────────────────────────────────────────────────────────────
try:
    import pytesseract
    from PIL import Image
    import io
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ── System prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are ClearLabel, an expert ingredient analyst and consumer advocate.
Your job is to analyze product ingredient lists and explain every ingredient in plain English.

You MUST respond with valid JSON only — no markdown, no explanation outside the JSON.

Respond with this exact structure:
{
  "ingredients": [
    {
      "name": "Ingredient Name",
      "plain_english": "What this actually is in plain English",
      "function": "What it does in this product",
      "safety_rating": "safe|caution|avoid",
      "origin": "natural|synthetic|processed",
      "allergy_flags": ["list", "of", "allergens", "or", "empty"],
      "benefits": "Legitimate benefits or positive effects",
      "concerns": "Known concerns, side effects, or 'None known at normal doses'"
    }
  ],
  "summary": {
    "letter_grade": "A|B|C|D|F",
    "bottom_line": "One plain-English paragraph summarizing this product for a regular person",
    "safe_count": 0,
    "caution_count": 0,
    "avoid_count": 0,
    "worst_offenders": ["ingredient1", "ingredient2"]
  },
  "recommendations": {
    "product_category": "Short name for this product type (e.g. 'moisturizer', 'breakfast cereal', 'protein shake')",
    "alternatives": [
      "Specific, actionable suggestion for a cleaner alternative or brand category — e.g. 'Look for moisturizers with fewer than 5 ingredients and no parabens'",
      "Another concrete tip — e.g. 'Cereal brands like Bob's Red Mill or Nature's Path tend to use fewer artificial additives'",
      "A third option if relevant — skip if only 2 apply"
    ],
    "what_to_look_for": "2-3 sentences: what positive ingredients or label certifications to seek when buying this type of product",
    "red_flags": [
      "Specific ingredient or pattern to avoid for this product category",
      "Another red flag",
      "A third if relevant"
    ]
  }
}

Safety rating guide:
- safe: Generally recognized as safe, well-studied, no significant concerns
- caution: Some concerns exist, may be problematic for sensitive individuals or in high doses
- avoid: Significant evidence of harm, controversial, or banned in some countries

Letter grade guide:
- A: Mostly natural, safe ingredients, clean label
- B: Mostly safe with a few processed ingredients
- C: Mix of safe and concerning ingredients
- D: Multiple concerning ingredients
- F: Dominated by avoid-rated ingredients

For recommendations: be specific and actionable, not generic. Tailor advice to the actual product category you detect from the ingredients.

Be honest, educational, and specific. This helps real people make informed choices."""

USER_PROMPT_TEMPLATE = """Please analyze these product ingredients:

{ingredients}

{profile_note}

Analyze every single ingredient listed. Be thorough and honest."""


def call_ai(ingredient_text: str, profile: dict = None) -> dict:
    """Call Claude or OpenAI and return parsed JSON response."""
    profile_note = ""
    if profile:
        flags = []
        if profile.get("allergens"):
            flags.append(f"User allergens: {', '.join(profile['allergens'])}")
        if profile.get("conditions"):
            flags.append(f"User health notes: {', '.join(profile['conditions'])}")
        if flags:
            profile_note = "PERSONAL PROFILE — flag anything relevant to this user:\n" + "\n".join(flags)

    user_msg = USER_PROMPT_TEMPLATE.format(
        ingredients=ingredient_text,
        profile_note=profile_note
    )

    if AI_PROVIDER == "anthropic":
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}]
        )
        raw = response.content[0].text

    elif AI_PROVIDER == "openai":
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_msg}
            ],
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        raw = response.choices[0].message.content

    else:
        # Demo mode — no API key
        return demo_response(ingredient_text)

    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def demo_response(ingredient_text: str) -> dict:
    """Return a demo response when no API key is configured."""
    ingredients = [i.strip() for i in ingredient_text.replace(",", "\n").split("\n") if i.strip()]
    demo_ingredients = []
    for ing in ingredients[:5]:  # limit demo to 5
        demo_ingredients.append({
            "name": ing,
            "plain_english": f"Demo mode — add an API key to analyze {ing}",
            "function": "Unknown (demo mode)",
            "safety_rating": "caution",
            "origin": "unknown",
            "allergy_flags": [],
            "benefits": "Analysis unavailable in demo mode",
            "concerns": "Add ANTHROPIC_API_KEY or OPENAI_API_KEY to get real analysis"
        })
    return {
        "ingredients": demo_ingredients,
        "summary": {
            "letter_grade": "?",
            "bottom_line": "Demo mode — no API key configured. Add your API key to secrets.json to get real ingredient analysis.",
            "safe_count": 0,
            "caution_count": len(demo_ingredients),
            "avoid_count": 0,
            "worst_offenders": []
        },
        "recommendations": {
            "product_category": "Unknown",
            "alternatives": ["Add an API key to get personalized recommendations"],
            "what_to_look_for": "Demo mode — add your API key to get real shopping guidance.",
            "red_flags": ["Demo mode — add your API key for real red flag detection"]
        },
        "_demo": True
    }


def extract_text_from_image(image_data: bytes) -> str:
    """Use Tesseract OCR to extract text from an image."""
    if not OCR_AVAILABLE:
        raise RuntimeError("OCR not available — install pytesseract and Pillow")
    img = Image.open(io.BytesIO(image_data))
    text = pytesseract.image_to_string(img)
    return text.strip()


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory("static", "manifest.json")


@app.route("/sw.js")
def service_worker():
    return send_from_directory("static", "sw.js", mimetype="application/javascript")


@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        ingredient_text = ""
        profile = {}

        # Handle JSON body (text paste)
        if request.is_json:
            data = request.get_json()
            ingredient_text = data.get("ingredients", "").strip()
            profile = data.get("profile", {})

        # Handle multipart form (file upload)
        elif "file" in request.files:
            f = request.files["file"]
            image_bytes = f.read()
            try:
                ingredient_text = extract_text_from_image(image_bytes)
            except Exception as e:
                return jsonify({"error": f"OCR failed: {str(e)}"}), 400
            profile_raw = request.form.get("profile", "{}")
            try:
                profile = json.loads(profile_raw)
            except Exception:
                profile = {}
        else:
            ingredient_text = request.form.get("ingredients", "").strip()
            profile_raw = request.form.get("profile", "{}")
            try:
                profile = json.loads(profile_raw)
            except Exception:
                profile = {}

        if not ingredient_text:
            return jsonify({"error": "No ingredient text provided"}), 400

        result = call_ai(ingredient_text, profile)
        result["provider"] = AI_PROVIDER
        return jsonify(result)

    except json.JSONDecodeError as e:
        app.logger.error(f"JSON parse error: {e}")
        return jsonify({"error": "AI returned invalid JSON — try again"}), 500
    except Exception as e:
        app.logger.error(f"Analyze error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/health")
def health():
    return jsonify({"status": "ok", "ai_provider": AI_PROVIDER, "ocr": OCR_AVAILABLE})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

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
      "Specific, actionable suggestion for a cleaner alternative or brand category",
      "Another concrete tip",
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

IMPORTANT — Evaluate ingredients IN CONTEXT of the product type:
- An ingredient that is "caution" in a food product may be perfectly safe and expected in a cleaning product
- Preservatives in a baby product deserve more scrutiny than the same preservative in a household cleaner
- A high alcohol content is expected in hand sanitizer but a red flag in a baby lotion
- Always apply appropriate safety standards for the product category provided

IMPORTANT — Be balanced and honest:
- If a product has an excellent ingredient profile, say so clearly and positively. Not every product needs problems invented.
- If worst_offenders is empty because everything is genuinely safe, leave it as an empty array.
- Celebrate clean labels — a Grade A product deserves genuine praise, not forced caveats.
- Only flag real concerns, not theoretical ones at normal usage levels.

For recommendations: be specific and actionable, not generic. Tailor advice to the actual product category.
If the product context was provided by the user, make the recommendations directly relevant to that category and use case.

Be honest, educational, and specific. This helps real people make informed choices."""

USER_PROMPT_TEMPLATE = """Please analyze these product ingredients:

{product_context}{ingredients}

{profile_note}

Analyze every single ingredient listed. Be thorough and honest."""


def build_product_context(product_name: str = "", product_category: str = "", product_description: str = "") -> str:
    """Build a product context block to prepend to the ingredient analysis prompt."""
    if not any([product_name, product_category, product_description]):
        return "Note: No product context was provided — please infer the product type from the ingredients themselves.\n\n"

    lines = ["PRODUCT CONTEXT:"]
    if product_category:
        lines.append(f"- Category: {product_category}")
    if product_name:
        lines.append(f"- Product Name: {product_name}")
    if product_description:
        lines.append(f"- Description: {product_description}")
    lines.append(
        f"\nAnalyze these ingredients in the context of how they would be used in "
        f"{'this ' + product_category.lower() + ' product' if product_category else 'this product'}. "
        f"Apply safety standards appropriate for this category and use case.\n\n"
    )
    return "\n".join(lines) + "\n"


def call_ai(ingredient_text: str, profile: dict = None,
            product_name: str = "", product_category: str = "",
            product_description: str = "") -> dict:
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

    product_context = build_product_context(product_name, product_category, product_description)

    user_msg = USER_PROMPT_TEMPLATE.format(
        product_context=product_context,
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
        ingredient_text  = ""
        profile          = {}
        product_name     = ""
        product_category = ""
        product_description = ""

        # Handle JSON body (text paste)
        if request.is_json:
            data = request.get_json()
            ingredient_text     = data.get("ingredients", "").strip()
            profile             = data.get("profile", {})
            product_name        = data.get("product_name", "").strip()
            product_category    = data.get("product_category", "").strip()
            product_description = data.get("product_description", "").strip()

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
            product_name        = request.form.get("product_name", "").strip()
            product_category    = request.form.get("product_category", "").strip()
            product_description = request.form.get("product_description", "").strip()

        else:
            ingredient_text     = request.form.get("ingredients", "").strip()
            profile_raw         = request.form.get("profile", "{}")
            product_name        = request.form.get("product_name", "").strip()
            product_category    = request.form.get("product_category", "").strip()
            product_description = request.form.get("product_description", "").strip()
            try:
                profile = json.loads(profile_raw)
            except Exception:
                profile = {}

        if not ingredient_text:
            return jsonify({"error": "No ingredient text provided"}), 400

        result = call_ai(
            ingredient_text, profile,
            product_name=product_name,
            product_category=product_category,
            product_description=product_description
        )
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

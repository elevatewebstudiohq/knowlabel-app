"""
KnowLabel — AI Ingredient Education PWA
Backend: Flask + Claude/OpenAI API
"""

import os
import sys
import json
import base64
import logging
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory

# ── AI client setup ─────────────────────────────────────────────────────────
# Try environment variable first (Railway / production), fall back to secrets.json for local dev
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
OPENAI_KEY    = os.environ.get("OPENAI_API_KEY")

if not ANTHROPIC_KEY and not OPENAI_KEY:
    SECRETS_PATH = Path("/home/node/.openclaw/workspace/automation/secrets.json")
    if SECRETS_PATH.exists():
        with open(SECRETS_PATH) as f:
            secrets = json.load(f)
        ANTHROPIC_KEY = secrets.get("anthropic_api_key") or secrets.get("anthropic")
        OPENAI_KEY    = secrets.get("openai_api_key")

if not ANTHROPIC_KEY and not OPENAI_KEY:
    print("❌ ERROR: No AI API key found.")
    print("   Set ANTHROPIC_API_KEY (or OPENAI_API_KEY) as an environment variable,")
    print("   or add it to /home/node/.openclaw/workspace/automation/secrets.json.")
    sys.exit(1)

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
SYSTEM_PROMPT = """You are KnowLabel, an expert ingredient analyst and consumer advocate.
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
      "concerns": "Known concerns, side effects, or 'None known at normal doses'",
      "dosage_assessment": "safe_range|above_rda_below_ul|exceeds_ul|not_specified",
      "dosage_context": "Plain English explanation of the dosage — only include this field when an amount is explicitly stated"
    }
  ],
  "summary": {
    "letter_grade": "A|B|C|D|F",
    "bottom_line": "One plain-English paragraph summarizing this product for a regular person",
    "grade_explanation": "1-2 sentence plain English explanation of WHY the product received that specific grade. Reference the specific concerning ingredients that pulled the grade down and explain the real-world implication (e.g. daily use, hormone disruption, environmental concern). Written for a non-technical user. Do NOT just restate the grade — explain the reasoning behind it.",
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

GRADE EXPLANATION guide (for the grade_explanation field):
- Must be 1-2 sentences, plain English, written for a non-technical user
- For lower grades (C/D/F): name the specific ingredients that pulled the grade down and state the real-world implication (e.g. "daily use risk", "hormone disruption", "environmental concern", "irritation potential")
- For higher grades (A/B): celebrate what makes it clean — name what's good about the formulation
- Do NOT simply restate the grade (e.g. do not write "This product received a B because it has mostly safe ingredients")
- Example C-grade: "This product contains chemical UV filters linked to potential hormone disruption and reef damage. While many base ingredients are safe, the active sunscreen agents lower the overall safety profile — especially for daily use."
- Example A-grade: "All ingredients are naturally sourced with no synthetic additives or concerning chemicals. This product earns an A for its clean, minimal formulation."

DOSAGE ANALYSIS — when ingredient amounts are listed (e.g. Vitamin C 750mg, Sodium 400mg):
1. Compare against established safe limits (RDA, Tolerable Upper Limit from NIH/FDA/EFSA)
2. Set dosage_assessment to one of: safe_range / above_rda_below_ul / exceeds_ul / not_specified
3. Set dosage_context to a plain English explanation, e.g. "750mg Vitamin C is within the safe range. The tolerable upper limit for adults is 2000mg/day."
4. For supplements: note if it is a therapeutic dose vs maintenance dose
5. For food additives: note what percentage of daily recommended intake this represents
6. If no amount is listed for an ingredient, set dosage_assessment to not_specified and omit the dosage_context field entirely
7. Never invent amounts — only analyze what is explicitly stated in the ingredient list

DOSAGE SPECIFICITY RULES:
1. Never default to "none known at normal doses" when more context is available
2. If the product name is provided AND it is a well-known specific product (e.g. "Garden of Life Raw Organic Protein", "Celsius Energy Drink", "Neutrogena Ultra Sheer SPF 50") — use your knowledge of that product's typical serving size and formulation to give specific dosage context. State the serving size you are referencing.
3. If ingredient amounts are explicitly listed — always analyze actual amounts, not hypothetical ones
4. If the product category is provided — apply category-appropriate thresholds (e.g. stricter for baby products, daily skincare vs occasional use)
5. Only use "none known at normal doses" when: the product name is too generic to infer from (e.g. just "protein powder" with no brand), AND no ingredient amounts are listed
6. If the product name is ambiguous (e.g. "Oreos" which has many flavors with different formulations) — acknowledge the ambiguity, state which version you are analyzing, and proceed with the most common/standard formulation
7. Always state what serving size or context you are using for your dosage assessment so the user knows what you are referencing

IMPORTANT — Evaluate ingredients IN CONTEXT of the product type:
- An ingredient that is "caution" in a food product may be perfectly safe and expected in a cleaning product
- Preservatives in a baby product deserve more scrutiny than the same preservative in a household cleaner
- A high alcohol content is expected in hand sanitizer but a red flag in a baby lotion
- Always apply appropriate safety standards for the product category provided

ACCURACY RULES — follow these strictly:
1. Each concern must be sourced from the ingredient itself, not inferred from context. Do not let product category, environmental claims, or nearby ingredients influence what you report about a specific ingredient.
2. Distinguish between separate issues clearly. Examples:
   - Coral TISSUE damage (ingredient disrupts coral biology/reproduction) is NOT the same as reef-safe legislation (legal bans in specific locations like Hawaii)
   - Octocrylene causes coral tissue damage via photodegradation into benzophenone — do NOT conflate this with Hawaii reef-safe sunscreen laws, which ban oxybenzone and octinoxate, not octocrylene
3. Never extrapolate. If an ingredient has concern A, do not assume concern B just because they sound related.
4. If the product is described as eco-friendly or the user mentions environmental concerns, do NOT retroactively change ingredient assessments to match that framing. Each ingredient stands on its own scientific evidence.
5. Cite the actual mechanism of concern (e.g. photodegrades into benzophenone, disrupts hormone receptors, irritates mucous membranes) not vague associations.

IMPORTANT — Be balanced and honest:
- If a product has an excellent ingredient profile, say so clearly and positively. Not every product needs problems invented.
- If worst_offenders is empty because everything is genuinely safe, leave it as an empty array.
- Celebrate clean labels — a Grade A product deserves genuine praise, not forced caveats.
- Only flag real concerns, not theoretical ones at normal usage levels.

For recommendations: be specific and actionable, not generic. Tailor advice to the actual product category.
If the product context was provided by the user, make the recommendations directly relevant to that category and use case.

ALTERNATIVE PRODUCT RULES — follow these strictly when populating the "alternatives" field:
1. Only recommend a specific named product as an alternative if you are highly confident it would score an A grade (no caution or avoid ingredients, clean formulation, minimal processing).
2. If no such A-grade product comes to mind for that category, DO NOT recommend any specific product by name.
3. Instead, tell the user what clean ingredients to look FOR in that category and which ingredients/chemicals to avoid.
4. Never recommend a product that has any ingredients you would flag as caution or avoid — even if it is "better" than the scanned product.
5. The standard is: would this alternative pass KnowLabel's own analysis with flying colors? If not, don't mention it.

Example application: For energy drinks, instead of recommending a specific brand, say "Look for drinks with green tea extract, B vitamins, and natural caffeine sources. Avoid sucralose, artificial flavors, and proprietary blends."

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

    # Strip markdown code fences if present
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

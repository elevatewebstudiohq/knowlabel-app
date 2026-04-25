# KnowLabel Phase 2 Feature Queue
*Build after collecting initial user feedback — batch these changes together*

## Queued Features

### 1. Auto-populate product context from photo
- When user uploads/takes a photo, Google Vision reads ALL text on label
- AI identifies: product name, brand, flavor/variant, category automatically
- Auto-fills product context fields — user only fills gaps
- Two entry points: "📷 Scan a Product" OR "✏️ Enter Details Manually"
- Only prompt for more info if photo couldn't determine something
- Example: photo of Gatorade → auto-fills name=Gatorade, flavor=White Cherry, category=Food & Beverage

### 2. User accounts + Stripe ($4.99/month Pro)
- Free tier: X scans/month
- Pro tier: unlimited scans + history + allergen profile saved

### 3. Scan history
- Save past scans per user account
- Compare products side by side

### 4. Google Vision upgrade for OCR accuracy
- Already implemented ✅ (Apr 24 2026)

---

## Feedback to Collect First
- What do users find confusing about the UI?
- What's missing from the analysis?
- What would make them pay $4.99/month?
- OCR accuracy on real-world labels in the wild
- Most common product categories being scanned

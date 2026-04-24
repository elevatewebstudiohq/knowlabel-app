# HEARTBEAT.md

## Active Monitoring Tasks

### Check Padmé's last session
At every heartbeat, check if Padmé has a new completed or failed session since last check.
Padmé = flux agent. File: /home/node/.openclaw/agents/flux/sessions/
If newest session is newer than last check AND contains ERROR or "timed out" → alert Nestor immediately and fix.
If newest session contains "Done:" or "SUCCESS" → read result and report to Nestor.

### Store status (as of Apr 21 2026)
- ✅ All descriptions done (mugs, shirts, totes, phone cases)
- ✅ Mother's Day Dog Mom 4-pack — live
- ✅ Bernese Mountain Dog Mom 4-pack — live (3/4 fixed; tote 400 error was likely transient)
- ✅ Rhodesian Ridgeback Mom 4-pack — live, all 13 MD tags confirmed
- ✅ Husky Mom 4-pack — live, all 13 MD tags, mug both sides ✅
- ✅ Mini Schnauzer Mom 4-pack — live, all 13 MD tags, mug both sides ✅
- ✅ Havanese Mom 4-pack — live, all 13 MD tags, mug both sides ✅
- ✅ Tote shipping fixed — 17/17 totes updated to free shipping profile
- Store total: ~44 products on Etsy, Etsy ads running

### ⚠️ Open manual task (Nestor)
- Log into Printify UI and set lifestyle mockup shots as primary images for Mother's Day collection (4 breeds × 4 products = 16 listings). ~2 min per listing.

### Known script bugs (for Padmé/Flux)
- `fix_ridgeback_tags.py` has phone case tag-overwrite bug — phone case ID swap block overwrites tags with []. Fix before next use.
- `fix_tote_backs.py` returns 400 on all 11 original tote IDs — IDs may be stale or payload format needs review.
- ⚠️ All Printify automation scripts lost in workspace restructure (Apr 24) — rebuild in Padmé's workspace (/home/node/.openclaw/agents/flux/workspace/automation/) if needed.

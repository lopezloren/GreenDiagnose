# GreenDiagnose — Starter Codebase

This is a working skeleton implementing your approved design: species-specific CNN classification, refined by a rule-based inference engine, fully accountless, no runtime admin.

## Files
| File | What it does |
|---|---|
| `schema.sql` | Full database schema, seeded with your 10 species. Run this first. |
| `app.py` | Flask app — all 6 API routes wired to real logic, matching your Chapter 2 DFD's 4 processes exactly |
| `rule_engine.py` | The certainty-factor inference engine — **fully working now**, no trained model needed to test it |
| `cnn_classifier.py` | Species-specific image classification — structure is real; needs your trained `.h5` files once Sprint 3/4 model training is done |
| `db.py` | MySQL connection helper |
| `requirements.txt` | Python dependencies |

## Setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up the database
mysql -u root -p < schema.sql

# 4. Create a .env file (not committed to git) with your DB credentials:
echo "DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=greendiagnose" > .env

# 5. Run the app
python app.py
```

## What Actually Works Right Now
- The full API flow (start session → classify → get questions → submit answers → diagnose) runs end-to-end **as soon as you populate the `disease`, `symptom`, `disease_symptom_rule`, and `treatment` tables** — this is your Sprint 1 rule-drafting work, not code.
- `classify_image()` will error until you've trained and saved at least one species' model — that's expected, and matches your Sprint 3/4 timeline. Test the rest of the flow first using a fake/manual `predicted_disease_id` while models are still training.

## The One Formula You Need to Own for Chapter 3
`rule_engine.py` combines the CNN's confidence and the rule-based symptom score using a simple 50/50 weighted average (`CNN_WEIGHT` / `RULE_WEIGHT` constants at the top of the file). This is a real methodology decision — tune these values during Sprint 4 based on what your horticulturist validation actually shows works, then **document the final value and your reasoning** in your Chapter 3 write-up. Right now it's a reasonable placeholder, not a validated number.

## Next Concrete Steps
1. Populate `disease`, `symptom`, `disease_symptom_rule`, `treatment` for at least one species (start with whichever has the smallest disease list) so you can test the full flow early
2. Build the frontend screens against these exact API routes — they map directly to the mockups we designed (Home → Upload → Questionnaire → Results)
3. Start model training in Colab per the skeleton at the bottom of `cnn_classifier.py`

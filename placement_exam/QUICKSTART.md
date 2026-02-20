# ESL Placement Test - Quick Start Guide

This is a quick reference for generating the Google Form placement test. For full documentation, see [README.md](README.md).

## Prerequisites

1. **Python 3.9+** installed
2. **Google account** (personal Gmail or Google Workspace)
3. **Google Cloud Project** with Forms API enabled

## First-Time Setup (5 minutes)

### 1. Install Dependencies

```bash
cd placement_exam
python3 -m pip install -r requirements.txt
```

### 2. Get Google API Credentials

1. Go to: https://console.cloud.google.com/
2. Create a new project: "Placement Test Generator"
3. Enable **Google Forms API**:
   - APIs & Services → Library → Search "Google Forms API" → Enable
4. Create **OAuth 2.0 credentials**:
   - APIs & Services → Credentials → Create Credentials → OAuth client ID
   - Application type: **Desktop app**
   - Download JSON file
5. Save downloaded file as: `placement_exam/credentials.json`
6. Configure OAuth consent screen:
   - APIs & Services → OAuth consent screen
   - User type: External
   - Add scope: `https://www.googleapis.com/auth/forms.body`
   - Add yourself as test user

## Generate the Form (30 seconds)

```bash
cd placement_exam/scripts
python3 create_placement_form.py
```

On first run:
- Browser opens → Sign in with your Google account
- Grant permission to "Create and edit your Google Forms"
- Script saves `token.json` for future runs

Output shows:
- ✓ Progress steps
- 📝 **Edit URL** (for you)
- 👥 **Respondent URL** (for students)

## Post-Generation (2 minutes)

After script completes, do these steps manually:

1. **🔴 CRITICAL: Enable accepting responses**:
   - Open Edit URL
   - Click the toggle at the top: "Start accepting responses"
   - Forms created via API default to NOT accepting (Send button grayed out)

2. **Link to Google Sheets**:
   - Responses → Link to Sheets

3. **Enable email collection**:
   - Settings (⚙️) → Collect email addresses

4. **Test the form**:
   - Submit 3 dummy responses (Path A, B, C)
   - Verify scores:
     - Path A: out of 10
     - Path B/C: out of 25

## Test the Question Bank

Before generating, validate the question bank:

```bash
cd placement_exam/scripts
python3 validate_question_bank.py
```

This checks:
- ✓ No duplicate IDs
- ✓ Exactly one correct answer per question
- ✓ Proper band distribution (10/8/7)
- ✓ All required fields present

## Troubleshooting

### "Send" button is grayed out / Form won't accept responses
→ **Solution**: Open the edit URL and click the toggle at the top to "Start accepting responses"
→ Forms created via API default to NOT accepting responses

### "credentials.json not found"
→ You need to create OAuth credentials (see Setup step 2)

### "Access blocked: This app hasn't been verified"
→ Click "Advanced" → "Go to [app name] (unsafe)"
→ This is normal for personal projects

### Form branching doesn't work
→ May need to configure manually:
- Open form edit URL
- Set "Go to section based on answer" for:
  - Self-assessment gate (all → Band 1)
  - Post-Band 1 routing (Path A → Submit, B/C → Band 2)

## File Structure

```
placement_exam/
├── credentials.json          # OAuth credentials (you create this)
├── token.json               # OAuth token (auto-generated)
├── bases/
│   └── question_bank.json   # 25 test questions
└── scripts/
    ├── create_placement_form.py      # Main generator
    └── validate_question_bank.py     # Validator
```

## What the Script Creates

The generated form includes:

**Section 0: Gate**
- Bilingual instructions (PT/EN)
- Self-assessment question (3 paths)

**Section 1: Band 1 (Foundation)**
- Worked example
- 10 questions (Q1-Q10)
- Post-Band 1 routing question

**Section 2: Band 2 (Developing)** [Path B/C only]
- 8 questions (Q11-Q18)

**Section 3: Band 3 (Expanding)** [Path B/C only]
- 7 questions (Q19-Q25)

## Key Features

✅ **Quiz mode** - Automatic grading
✅ **Three-path branching** - Path A (10 questions), Path B/C (25 questions)
✅ **Bilingual** - All instructions in Portuguese and English
✅ **Worked example** - For Path A students
✅ **Anchor questions** - Q1 (easy), Q25 (hard)
✅ **Reproducible** - Same input → same form

## Need Help?

- **Full setup guide**: [README.md](README.md)
- **Test design**: [docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md](docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md)
- **API guide**: [docs/PROGRAMMATIC_PLACEMENT_EXAM.md](docs/PROGRAMMATIC_PLACEMENT_EXAM.md)
- **Google Forms API**: https://developers.google.com/workspace/forms

---

**Security Note**: Never commit `credentials.json` or `token.json` to version control. They're already in `.gitignore`.

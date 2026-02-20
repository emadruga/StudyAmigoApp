# ESL Placement Test - Google Form Generator

This directory contains tools to programmatically generate the ESL placement test as a Google Form.

## Overview

The placement test is a 25-question ESL reading assessment with three-path branching:
- **Path A**: Students with no English background answer 10 foundation questions (Band 1 only)
- **Path B/C**: Students with high school or course English answer all 25 questions (Bands 1, 2, 3)

The form includes:
- Bilingual instructions (Portuguese/English)
- Quiz mode with automatic grading
- Worked example for Path A students
- Section headers with time estimates

## Directory Structure

```
placement_exam/
├── README.md                           # This file
├── requirements.txt                    # Python dependencies
├── credentials.json                    # OAuth credentials (GITIGNORED - you create this)
├── token.json                          # OAuth token (GITIGNORED - auto-generated)
│
├── docs/
│   ├── PLAN_FOR_PLACEMENT_EXAM_v1.2.md # Test design specification
│   └── PROGRAMMATIC_PLACEMENT_EXAM.md  # API implementation guide
│
├── bases/
│   └── question_bank.json              # 25-question bank
│
└── scripts/
    └── create_placement_form.py        # Main generator script
```

## Setup (One-Time)

### 1. Install Dependencies

```bash
cd placement_exam
python3 -m pip install -r requirements.txt
```

### 2. Set Up Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (e.g., "Placement Test Generator")
3. Enable the **Google Forms API**:
   - Navigate to **APIs & Services → Library**
   - Search for "Google Forms API"
   - Click **Enable**
4. Create **OAuth 2.0 credentials**:
   - Navigate to **APIs & Services → Credentials**
   - Click **Create Credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Download the resulting JSON file
5. Save the downloaded file as `placement_exam/credentials.json`

### 3. Configure OAuth Consent Screen

1. Navigate to **APIs & Services → OAuth consent screen**
2. User type: **External** (for personal Gmail) or **Internal** (for Google Workspace)
3. Fill in required fields (app name, support email)
4. Add the scope: `https://www.googleapis.com/auth/forms.body`
5. Add yourself as a test user (if in "Testing" publishing status)

## Usage

### Generate the Form

```bash
cd placement_exam/scripts
python3 create_placement_form.py
```

On first run, the script will:
1. Open a browser window asking you to sign in with your Google account
2. Request permission to "Create and edit your Google Forms"
3. Store a `token.json` file for subsequent runs (no re-authentication needed)

The script will output:
- ✓ Step-by-step progress
- 📝 Edit URL (for you to configure the form)
- 👥 Respondent URL (to share with students)

### Optional Arguments

```bash
# Use a different question bank
python3 create_placement_form.py --bank /path/to/custom_bank.json

# Custom form title
python3 create_placement_form.py --title "My Custom Placement Test"

# Custom credentials location
python3 create_placement_form.py --credentials /path/to/credentials.json
```

## Post-Generation Steps (Manual)

After the script completes, you must:

1. **🔴 CRITICAL: Enable accepting responses**:
   - Open the edit URL
   - Look for the toggle at the top of the form editor
   - Click to change from "Not accepting responses" to **"Accepting responses"**
   - **Why**: Forms created via API default to NOT accepting responses (Send button will be grayed out until you enable this)

2. **Link to Google Sheets**:
   - Click **Responses** → **Link to Sheets**
   - This creates a spreadsheet to collect responses

3. **Enable email collection**:
   - Click the Settings icon (⚙️)
   - Enable **Collect email addresses**

4. **Test the form**:
   - Submit 3 dummy responses (one for each path A, B, C)
   - Verify scores calculate correctly:
     - Path A: score out of 10
     - Path B/C: score out of 25

## Question Bank Format

The question bank (`bases/question_bank.json`) contains all questions with metadata:

```json
{
  "version": "1.0",
  "questions": [
    {
      "id": "B1_VOCAB_001",
      "band": 1,
      "type": "vocabulary_matching",
      "anchor": "easy",
      "question_text": "What does \"important\" mean?",
      "options": [
        { "text": "Importante", "is_correct": true },
        { "text": "Impossível", "is_correct": false },
        { "text": "Importar", "is_correct": false },
        { "text": "Impressionante", "is_correct": false }
      ],
      "point_value": 1,
      "cognate": true,
      "rationale": "...",
      "distractor_rationale": { ... },
      "status": "active"
    }
  ]
}
```

### Key Fields

- **id**: Unique identifier (e.g., `B1_VOCAB_001`)
- **band**: Difficulty level (1=Foundation, 2=Developing, 3=Expanding)
- **type**: Question type (vocabulary_matching, sentence_completion, reading_comprehension, grammar_recognition)
- **anchor**: "easy" for Q1 (anchor-easy), "hard" for Q25 (anchor-hard), null for others
- **options**: Array of 4 options with exactly one correct answer
- **status**: "active" (use in test), "retired" (poor performance), "draft" (not ready)

## Troubleshooting

### "Send" button is grayed out / Form won't accept responses

**Solution**: This is the most common issue. Open the edit URL and look for the toggle at the top of the form editor. Click it to change from "Not accepting responses" to "Accepting responses".

**Why this happens**: Google Forms created via API default to NOT accepting responses. This is a security/publishing feature that requires manual activation.

### "credentials.json not found"

You need to create OAuth credentials in Google Cloud Console (see Setup step 2).

### "Access blocked: This app hasn't been verified"

If you see this during authentication:
1. Click "Advanced"
2. Click "Go to [your app name] (unsafe)"
3. This is expected for personal projects in Testing mode

### Form branching doesn't work

The script attempts to set up branching via the API, but this feature has limitations. If branching doesn't work:
1. Open the form in edit mode
2. Manually configure "Go to section based on answer" for:
   - Self-assessment gate (all paths → Band 1)
   - Post-Band 1 routing question (Path A → Submit, Path B/C → Band 2)

### Questions appear in wrong order

The script creates items with explicit `location.index`. If order is wrong, check that:
- The question bank has exactly 10 Band 1, 8 Band 2, and 7 Band 3 questions
- No duplicate IDs exist in the question bank

## Security Notes

- **`credentials.json`** and **`token.json`** are added to `.gitignore` and must never be committed
- The OAuth scope `forms.body` grants read/write access to form structure only
- The script cannot read form responses or access other Google Drive files
- Tokens expire after a period of inactivity; you may need to re-authenticate

## References

- [Google Forms API Documentation](https://developers.google.com/workspace/forms)
- [Google Forms API Python Quickstart](https://developers.google.com/workspace/forms/api/quickstart/python)
- [PLAN_FOR_PLACEMENT_EXAM_v1.2.md](docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md) - Test design
- [PROGRAMMATIC_PLACEMENT_EXAM.md](docs/PROGRAMMATIC_PLACEMENT_EXAM.md) - Implementation guide

## Support

For issues or questions about:
- **Test design**: See `docs/PLAN_FOR_PLACEMENT_EXAM_v1.2.md`
- **API implementation**: See `docs/PROGRAMMATIC_PLACEMENT_EXAM.md`
- **Google Forms API**: See [official documentation](https://developers.google.com/workspace/forms)

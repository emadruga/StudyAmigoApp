# Changelog

## 2026-02-20 - Initial Release

### Created
- `scripts/create_placement_form.py` - Main Google Form generator
- `scripts/validate_question_bank.py` - Question bank validator
- `requirements.txt` - Python dependencies
- `README.md` - Full documentation
- `QUICKSTART.md` - Quick reference guide
- Updated `.gitignore` to protect credentials

### Fixed (2026-02-20 evening)
- **Issue**: Google Forms API error "Displayed text cannot contain newlines"
- **Root cause**: API doesn't allow `\n` characters in question/item `title` fields
- **Solution**: Updated helper methods to:
  - Split text on `\n\n` to separate description from title
  - Move multi-line content to `description` field
  - Remove remaining newlines from title fields
- **Affected methods**:
  - `_create_graded_question()` - Handles reading comprehension passages
  - `_create_choice_question()` - Handles bilingual gate questions  
  - `_create_text_item()` - Handles instruction blocks
  - `_create_page_break()` - Handles section headers

### Documentation Updates (2026-02-20 evening)
- **Added**: Troubleshooting for "Send button grayed out" issue
- **Clarified**: Forms created via API default to "Not accepting responses"
- **Updated**: Manual post-generation steps with critical "Enable responses" as step 1
- **Location**: README.md, QUICKSTART.md

### Status
✅ Question bank validated (25 questions, proper distribution)
✅ Script handles API newline restrictions
✅ Form successfully created and tested
⚠️  Manual step required: Enable "Accepting responses" toggle in form editor
⚠️  Manual step required: Set up branching (API limitations)

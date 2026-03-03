# SuperMemo-2 Scheduling Algorithm Unit Tests

## 🚀 Quick Start

**Run all tests:**
```bash
cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
python -m unittest test_supermemo_2.py -v
```

**What you're looking for:**
- ❌ **Tests FAIL** → Linear growth bug still present (intervals: 1,2,3,4,5...)
- ✅ **Tests PASS** → Exponential growth working (intervals: 1,2,5,12,30...)

---

## Purpose

These tests verify the correctness of the SuperMemo-2 (SM-2) card scheduling algorithm implementation in `app.py`, specifically focusing on:

1. **Card State Transitions**: New → Learning → Review (Young) → Review (Mature)
2. **Interval Growth**: Exponential growth (not linear)
3. **Maturity Achievement**: Cards can reach Mature state (ivl ≥ 21 days) within reasonable timeframe
4. **Ease Factor Adjustments**: Hard/Good/Easy buttons affect ease factor correctly
5. **Relearning**: Failed Review cards enter Relearning state and can graduate back

## Critical Bug Being Tested

The tests specifically verify the fix for the **line 1702 interval calculation bug** identified in `CARD_PROGRESSION_ANALYSIS.md`:

**Original Bug** (linear growth):
```python
new_interval = max(current_interval + 1, int(current_interval * interval_adjust * interval_factor))
```
When `interval_adjust = interval_factor = 1.0`, this resulted in `new_interval = current_interval + 1` (linear).

**Expected Behavior** (exponential growth):
```python
ease_multiplier = current_factor / 1000.0  # e.g., 2500 / 1000 = 2.5
new_interval = int(current_interval * ease_multiplier)
```
This produces exponential growth: 1 → 2 → 5 → 12 → 30 days.

---

## Running the Tests

### Prerequisites

1. Python 3.8+ installed
2. Flask and dependencies installed (`pip install -r ../requirements.txt` from test directory)
3. `app.py` must be in the `/server` directory (parent directory of this test folder)

### Method 1: Using unittest from test directory (Recommended)

```bash
cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
python -m unittest test_supermemo_2.py -v
```

### Method 1b: Using unittest from server directory

```bash
cd /Users/emadruga/proj/StudyAmigoApp/server
python -m unittest test_supermemo_2.test_supermemo_2 -v
```

**Expected output** (if bug is NOT fixed):
```
test_review_card_interval_growth_exponential (__main__.TestSuperMemo2Scheduling) ... FAIL
test_review_card_reaches_mature_state (__main__.TestSuperMemo2Scheduling) ... FAIL
test_e01_scenario_maturity_achievable (__main__.TestSuperMemo2Scheduling) ... FAIL
```

**Expected output** (if bug IS fixed):
```
test_review_card_interval_growth_exponential (__main__.TestSuperMemo2Scheduling) ... ok
test_review_card_reaches_mature_state (__main__.TestSuperMemo2Scheduling) ... ok
test_e01_scenario_maturity_achievable (__main__.TestSuperMemo2Scheduling) ... ok
```

### Method 2: Using pytest (if installed)

```bash
cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
python -m pytest test_supermemo_2.py -v
```

### Method 3: Direct execution

```bash
cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
python test_supermemo_2.py
```

---

## Test Descriptions

### Core Scheduling Tests

| Test Name | Purpose | Pass Criteria |
|-----------|---------|---------------|
| `test_new_card_to_learning_transition` | New cards move to Learning on first review | type=1, queue=1 after first answer |
| `test_learning_card_graduation` | Learning cards graduate to Review | type=2, queue=2, ivl=1 after completing steps |
| `test_learning_card_easy_button_graduates_immediately` | Easy button skips remaining Learning steps | type=2, queue=2 after pressing Easy |

### Critical Interval Growth Tests (Bug Verification)

| Test Name | Purpose | Pass Criteria |
|-----------|---------|---------------|
| **`test_review_card_interval_growth_exponential`** | ⚠️ Intervals grow exponentially, not linearly | Growth rate > 1.5x on average |
| **`test_review_card_reaches_mature_state`** | ⚠️ Cards reach ivl≥21 within 5 reviews | Maturity achieved in ≤5 "Good" reviews |
| **`test_e01_scenario_maturity_achievable`** | ⚠️ E01 students can achieve maturity in 21 days | ≥30% of cards mature after 21 days |
| `test_interval_comparison_linear_vs_exponential` | Direct comparison of linear vs exponential | Intervals match [1,2,5,12,30], not [1,2,3,4,5] |

### Ease Factor Tests

| Test Name | Purpose | Pass Criteria |
|-----------|---------|---------------|
| `test_review_card_hard_button_decreases_factor` | Hard button decreases factor by 150 | factor = initial - 150 |
| `test_review_card_good_button_maintains_factor` | Good button maintains factor | factor unchanged |
| `test_review_card_easy_button_increases_factor` | Easy button increases factor by 150 | factor = initial + 150 |
| `test_factor_minimum_boundary` | Factor never goes below 1300 | factor ≥ 1300 after many Hard presses |

### Relearning Tests

| Test Name | Purpose | Pass Criteria |
|-----------|---------|---------------|
| `test_review_card_again_enters_relearning` | Failed Review card enters Relearning | type=3, queue=1, lapses++ |
| `test_relearning_card_can_graduate_back_to_review` | Relearning cards can graduate back | type=2, queue=2 after completing relearning |

---

## Interpreting Results

### If Tests FAIL (Bug Still Present)

**Symptom**: Tests with ⚠️ marker fail with messages like:
```
AssertionError: Card did not reach Mature state (ivl>=21) after 10 reviews. Final interval: 11.
Full sequence: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].
This indicates the linear growth bug is still present.
```

**What This Means**:
- Intervals are growing linearly (+1 day each time) instead of exponentially
- Cards cannot reach Mature state in reasonable time
- E01 students will have 0% maturity after 3 weeks
- **The bug fix was not applied correctly**

**Next Steps**:
1. Review the fix in `app.py` line 1702
2. Ensure `ease_multiplier = current_factor / 1000.0` is being used
3. Run tests again

### If Tests PASS (Bug Fixed)

**Symptom**: All tests pass, especially the ⚠️ critical tests.

**What This Means**:
- Intervals grow exponentially as expected
- Cards reach Mature state in 4-5 reviews
- E01 students will achieve 30-50% maturity after 3 weeks
- **The bug fix is working correctly**

**Next Steps**:
1. Deploy to production
2. Restore maturity weight to 0.30 in assessment formula (for E02+)
3. Monitor real student data to confirm

---

## Test Data and Diagnostics

Some tests output diagnostic information to help you understand the results:

```
[DIAGNOSTIC] Interval progression:
  Actual:      [1, 2, 5, 12, 30]
  Expected (exponential): [1, 2, 5, 12, 30]
  Expected (linear bug):  [1, 2, 3, 4, 5]
```

```
[E01 SIMULATION] After 21 days:
  Mature cards: 4/10 (40%)
  Intervals: [25, 30, 21, 28, 15, 18, 12, 9, 7, 5]
```

These help verify the fix is working as expected.

---

## Troubleshooting

### Test fails with "No module named 'app'"

**Solution**: Make sure you're running tests from the test directory:
```bash
cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
python -m unittest test_supermemo_2.py -v
```

Or from the server directory using the full module path:
```bash
cd /Users/emadruga/proj/StudyAmigoApp/server
python -m unittest test_supermemo_2.test_supermemo_2 -v
```

### Test fails with "Database is locked"

**Solution**: Close any SQLite browser or Anki desktop app that might have the database open.

### Test fails with "Cannot import name 'init_anki_db'"

**Solution**: Verify that `app.py` has the function `init_anki_db` defined (around line 142).

### Tests take too long to run

**Solution**: Tests should complete in < 10 seconds. If they take longer:
1. Check if temporary files are being cleaned up
2. Verify you're not running in debug mode
3. Consider running specific tests:
   ```bash
   cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
   python -m unittest test_supermemo_2.TestSuperMemo2Scheduling.test_review_card_reaches_mature_state -v
   ```

---

## After Fixing the Bug

Once all tests pass:

1. **Update E01 Assessment Formula**:
   - For E01 (< 21 days): `Q = 0.85 × retention + 0.15 × maturity` (B1 correction)
   - For E02+ (≥ 21 days): `Q = 0.70 × retention + 0.30 × maturity` (normal)

2. **Monitor Production Data**:
   - After E01 completes, run query to verify students achieved maturity:
   ```sql
   SELECT
       COUNT(CASE WHEN ivl >= 21 THEN 1 END) * 100.0 / COUNT(*) as maturity_pct
   FROM cards
   WHERE type = 2;
   ```
   - Expected: 30-50% for good students

3. **Document the Fix**:
   - Update `docs/SUPERMEMO-2.md` with corrected algorithm
   - Add note about the bug and fix date in `CARD_PROGRESSION_ANALYSIS.md`

---

**Last Updated**: March 3, 2026

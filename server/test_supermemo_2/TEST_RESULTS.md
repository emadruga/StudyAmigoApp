# SuperMemo-2 Unit Test Results

**Date**: March 3, 2026
**Run from**: `server/` directory
**Command**: `python -m unittest test_supermemo_2.test_supermemo_2 -v`

---

## Result: ALL PASSED (14/14)

```
Ran 14 tests in 0.406s

OK
```

---

## Test Details

| Test | Class | Result |
|------|-------|--------|
| `test_line_1702_bug_fixed` | `TestRegressionBugs` | ✅ ok |
| `test_e01_scenario_maturity_achievable` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_factor_minimum_boundary` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_interval_comparison_linear_vs_exponential` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_learning_card_easy_button_graduates_immediately` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_learning_card_graduation` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_new_card_to_learning_transition` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_relearning_card_can_graduate_back_to_review` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_review_card_again_enters_relearning` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_review_card_easy_button_increases_factor` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_review_card_good_button_maintains_factor` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_review_card_hard_button_decreases_factor` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_review_card_interval_growth_exponential` | `TestSuperMemo2Scheduling` | ✅ ok |
| `test_review_card_reaches_mature_state` | `TestSuperMemo2Scheduling` | ✅ ok |

---

## Key Diagnostics

### Interval Progression (exponential growth confirmed)

```
Actual:      [1, 2, 5, 12, 30]
Expected (exponential): [1, 2, 5, 12, 30]
Expected (linear bug):  [1, 2, 3, 4, 5]
```

### E01 Simulation (21-day scenario)

```
Mature cards: 10/10 (100%)
Intervals: [467, 467, 467, 467, 467, 467, 467, 467, 467, 467]
```

---

## Bugs Fixed in This Session

### 1. `server/app.py` — Line 1702 interval growth bug

**Before** (linear growth):
```python
new_interval = max(current_interval + 1, int(current_interval * interval_adjust * interval_factor))
```

**After** (exponential growth):
```python
if ease == 2:  # Hard
    new_interval = max(1, int(current_interval * hard_factor))
elif ease == 3:  # Good
    ease_multiplier = current_factor / 1000.0
    new_interval = max(current_interval + 1, int(current_interval * ease_multiplier))
else:  # ease == 4, Easy
    ease_multiplier = current_factor / 1000.0
    new_interval = max(current_interval + 1, int(current_interval * ease_multiplier * easy_bonus))
```

### 2. `test_supermemo_2.py` — Inverted assertion

`assertLess` → `assertGreater` in `test_review_card_interval_growth_exponential` (line 217).

### 3. `test_supermemo_2.py` — UNIQUE constraint collision

Replaced `int(time.time() * 1000)` ID generation with a monotonic `itertools.count` counter to prevent collisions when two cards are created within the same millisecond.

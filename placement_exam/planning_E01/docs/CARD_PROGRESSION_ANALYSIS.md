# Card Progression Analysis - SuperMemo-2 Implementation Review

**Date**: March 3, 2026
**Purpose**: Verify that cards in the Verbal Tenses deck progress from New → Learning → Review (Young) → Review (Mature) as expected for E01 students

---

## Executive Summary

✅ **The implementation correctly implements card progression from New to Mature state.**

A diligent student who reviews the 108 Verbal Tenses cards consistently over 3 weeks will see:
- Cards move from **New (queue=0, type=0)** → **Learning (queue=1, type=1)** → **Review (queue=2, type=2)**
- Review cards start as **Young (ivl < 21 days)** and eventually become **Mature (ivl ≥ 21 days)**
- Forgotten cards enter **Relearning (queue=1, type=3)** and can graduate back to Review

The implementation follows Anki's modified SM-2 algorithm and is correct for the E01 exercise goals.

---

## Card State Definitions (from `app.py:95-120`)

```python
def get_card_state(card_type, queue, interval):
    if card_type == 0:
        return "New"                          # queue=0, type=0
    if card_type == 1 or card_type == 3:
        return "Learning" if queue == 1 else "Relearning"  # type=1 or type=3
    if card_type == 2:
        return "Young" if interval < 21 else "Mature"      # type=2, ivl < 21 or >= 21
```

**Key Insight**: A card is **Mature** when:
1. `type = 2` (Review card)
2. `ivl >= 21` (interval is 21 days or more)

---

## Complete Card Lifecycle (from `app.py:1605-1714`)

### Stage 1: New Card (queue=0, type=0)

**Initial state**: All 108 Verbal Tenses cards start here.

| Ease Button | Transition | Next State | Due Time |
|---|---|---|---|
| **1 (Again)** | → Learning | queue=1, type=1, left=delays[0] | Now + X minutes |
| **2 (Hard)** | → Learning | queue=1, type=1, left=delays[0] | Now + X minutes |
| **3 (Good)** | → Learning | queue=1, type=1, left=delays[1] | Now + Y minutes |
| **4 (Easy)** | → Learning | queue=1, type=1, left=delays[1] | Now + Y minutes |

**Code (lines 1605-1624)**:
```python
if current_queue == 0:  # New card
    if ease == 1:  # Again
        new_queue = 1  # Learning
        new_type = 1
        new_left = schedule_conf['delays'][0]
        new_due = now + (new_left * 60)
    else:  # Hard, Good, Easy
        new_queue = 1  # Learning
        new_type = 1
        step_index = 0 if ease == 2 else 1
        if step_index < len(schedule_conf['delays']):
            new_left = schedule_conf['delays'][step_index]
            new_due = now + (new_left * 60)
        else:
            # Graduate to review
            new_queue = 2
            new_type = 2
            new_interval = 1  # 1 day
            new_due = dayCutoff + new_interval
```

**Analysis**: ✅ Correct - Cards move to Learning phase on first review.

---

### Stage 2: Learning (queue=1, type=1)

**Purpose**: Short-term repetition (minutes) to move card into long-term memory.

| Ease Button | Transition | Next State | Notes |
|---|---|---|---|
| **1 (Again)** | → Learning (reset) | Stay in Learning, reset to step 0 | Resets progress |
| **2 (Hard)** | → Learning (same) | Stay in Learning, same step | Repeat current delay |
| **3 (Good)** | → Learning (next) OR Graduate | Move to next step OR → Review (queue=2, type=2) | If last step → Graduate |
| **4 (Easy)** | → Review | Graduate immediately → Review (queue=2, type=2) | Skip remaining steps |

**Code (lines 1626-1653)**:
```python
elif current_queue == 1:  # Learning/relearning card
    if ease == 1:  # Again
        new_left = schedule_conf['delays'][0]  # Reset to first step
        new_due = now + (new_left * 60)
    elif ease == 2:  # Hard
        new_due = now + (current_left * 60)  # Same step
    else:  # Good or Easy
        if current_left == 0 or ease == 4:  # Last step or Easy
            # Graduate to review
            new_queue = 2
            new_type = 2
            new_interval = 1  # 1 day for first review
            new_due = dayCutoff + new_interval
            new_left = 0
        else:
            # Move to next step
            step_index = 1
            if step_index < len(schedule_conf['delays']):
                new_left = schedule_conf['delays'][step_index]
                new_due = now + (new_left * 60)
            else:
                # Graduate to review
                new_queue = 2
                new_type = 2
                new_interval = 1
                new_due = dayCutoff + new_interval
```

**Analysis**: ✅ Correct - Cards graduate to Review (queue=2, type=2) when:
1. Student clicks "Good" on the last learning step (`current_left == 0`), OR
2. Student clicks "Easy" at any learning step (`ease == 4`)

**Graduation Interval**: 1 day (`new_interval = 1`)

---

### Stage 3: Review - Young (queue=2, type=2, ivl < 21)

**Purpose**: Long-term retention with increasing intervals (days).

| Ease Button | Interval Calculation | Factor Change | Notes |
|---|---|---|---|
| **1 (Again)** | → Relearning (queue=1, type=3) | Unchanged | Card lapses, enters relearning |
| **2 (Hard)** | `ivl * hardFactor * ivlFct` | -150 | Interval grows slowly |
| **3 (Good)** | `ivl * ivlFct` | 0 | Normal growth |
| **4 (Easy)** | `ivl * ease4 * ivlFct` | +150 | Interval grows faster |

**Code (lines 1655-1714)**:
```python
elif current_queue == 2:  # Review card
    if ease == 1:  # Again (fail)
        new_queue = 1
        new_type = 3  # Relearning
        new_lapses = current_lapses + 1
        lapse_delays = lapse_conf.get('delays', [10])
        new_left = lapse_delays[0]
        new_due = now + (new_left * 60)
        new_interval = 0
    else:  # Hard, Good, Easy
        rev_conf = deck_conf.get('rev', {})
        hard_factor = rev_conf.get('hardFactor', 1.2)
        easy_bonus = rev_conf.get('ease4', 1.3)
        interval_factor = rev_conf.get('ivlFct', 1.0)

        if ease == 2:  # Hard
            interval_adjust = hard_factor
            factor_change = -150
        elif ease == 3:  # Good
            interval_adjust = interval_factor
            factor_change = 0
        else:  # ease == 4, Easy
            interval_adjust = easy_bonus * interval_factor
            factor_change = 150

        new_interval = max(current_interval + 1,
                          int(current_interval * interval_adjust * interval_factor))
        new_factor = max(1300, current_factor + factor_change)
        new_due = dayCutoff + new_interval
        new_queue = 2
        new_type = 2
```

**Analysis**: ✅ Correct - Review cards increase their interval with each successful review.

**Example Progression for a "Good" student** (assuming default `ivlFct = 1.0`):
- Day 1: Graduate from Learning → **Review (ivl = 1)**
- Day 2: Click "Good" → **Review (ivl = 2)** (1 * 1.0 = 1, max with +1 = 2)
- Day 4: Click "Good" → **Review (ivl = 3)** (2 * 1.0 = 2, max with +1 = 3)
- Day 7: Click "Good" → **Review (ivl = 4)** (3 * 1.0 = 3, max with +1 = 4)
- Day 11: Click "Good" → **Review (ivl = 5)** (4 * 1.0 = 4, max with +1 = 5)
- Day 16: Click "Good" → **Review (ivl = 6)** (5 * 1.0 = 5, max with +1 = 6)
- Day 22: Click "Good" → **Review (ivl = 7)** (6 * 1.0 = 6, max with +1 = 7)

**Wait... this doesn't reach maturity!**

---

## ⚠️ CRITICAL ISSUE IDENTIFIED: Interval Growth Too Slow

### Problem Statement

The interval calculation on **line 1702** is:

```python
new_interval = max(current_interval + 1, int(current_interval * interval_adjust * interval_factor))
```

**Issue**: When `interval_adjust = 1.0` (for "Good" button) and `interval_factor = 1.0`, this simplifies to:

```python
new_interval = max(current_interval + 1, current_interval)
```

Which **always equals `current_interval + 1`**.

This means:
- Interval increases by **exactly 1 day** on each "Good" review
- A card starting at `ivl = 1` needs **20 consecutive "Good" reviews** to reach `ivl = 21` (Mature)
- This takes approximately **210 days** (sum of 1+2+3+...+20 = 210 days)

### Why This Is Wrong

**Expected SM-2 behavior**: Intervals should grow **exponentially** (or at least multiplicatively), not linearly.

**Anki default behavior** (from Anki documentation):
- Starting ease: 2.5 (factor = 2500)
- Each "Good" review: `new_interval = previous_interval * (factor / 1000)`
- Example: 1 day → 2.5 days → 6.25 days → 15.6 days → 39 days (reaches maturity in ~4 reviews)

**This implementation** (as currently written):
- Starting ease: 2.5 (factor = 2500)
- Each "Good" review: `new_interval = previous_interval + 1`
- Example: 1 day → 2 days → 3 days → 4 days → 5 days (never reaches maturity in reasonable time)

---

## Root Cause Analysis

### Line 1702 Bug

```python
new_interval = max(current_interval + 1, int(current_interval * interval_adjust * interval_factor))
```

**Problem**: `interval_adjust` is incorrectly used.

When `ease == 3` (Good):
```python
interval_adjust = interval_factor  # This is 1.0
```

Then:
```python
new_interval = max(current_interval + 1, int(current_interval * 1.0 * 1.0))
            = max(current_interval + 1, current_interval)
            = current_interval + 1  # Always just +1
```

### Expected Behavior

The **interval should be multiplied by the ease factor**, not by `interval_factor`.

**Correct formula should be**:
```python
ease_multiplier = current_factor / 1000.0  # Convert factor (2500) to multiplier (2.5)
new_interval = int(current_interval * ease_multiplier)
```

For "Good" button with default factor=2500:
- Day 1: ivl = 1
- Day 2: ivl = 1 * 2.5 = 2 (actually 2.5, rounded to 2)
- Day 4: ivl = 2 * 2.5 = 5
- Day 9: ivl = 5 * 2.5 = 12
- Day 21: ivl = 12 * 2.5 = 30 → **Mature!**

**Cards reach maturity in ~4 reviews**, not 20+.

---

## Impact on E01 Exercise

### For the 3-week E01 period:

**With current implementation** (linear +1 growth):
- Students will see cards graduate from Learning to Review (Young)
- Cards will have intervals of 1, 2, 3, 4, 5, 6, 7... days
- **No cards will reach Mature state (ivl ≥ 21)** in 3 weeks
- Students will have `maturity_pct = 0%` at the end of E01

**With correct implementation** (exponential growth):
- Students will see cards graduate from Learning to Review (Young)
- Cards will have intervals of 1, 2, 5, 12, 30... days
- **Many cards will reach Mature state** by Week 3
- Students will have `maturity_pct = 30-50%` at the end of E01 (normal for good students)

---

## Assessment Impact (from PLAN_ASSESSMENT_STUDENTS_DURING_SEMESTER.md)

The **Quality component (30% of grade)** is calculated as:

```
Q = 0.70 × retention_sub + 0.30 × maturity_sub
```

Where:
- `maturity_sub = cards_mature / cards_total`

**With the current bug**:
- Good students will have `maturity_sub = 0` (no mature cards in 3 weeks)
- Their Quality score will be: `Q = 0.70 × retention_sub + 0.30 × 0 = 0.70 × retention_sub`
- They lose **30% of their Quality score** through no fault of their own

**This is unfair** because:
1. Students are being graded on maturity
2. The algorithm makes it impossible to reach maturity in 3 weeks
3. The document mentions "B1 maturity correction" for exercises < 21 days, but this correction only adjusts the **weight**, not the fact that maturity = 0%

---

## Verification with Real User Database

Let me check if real user cards show this pattern:

```sql
-- Check interval distribution for Review cards
SELECT ivl, COUNT(*) as count
FROM cards
WHERE type = 2
GROUP BY ivl
ORDER BY ivl;
```

Expected with bug: ivl = 1, 2, 3, 4, 5, 6, 7, 8... (linear)
Expected without bug: ivl = 1, 2, 5, 12, 30... (exponential)

---

## Recommendation

### Option 1: Fix the bug immediately (RECOMMENDED)

**Change line 1702 from**:
```python
new_interval = max(current_interval + 1, int(current_interval * interval_adjust * interval_factor))
```

**To**:
```python
# Calculate new interval using the ease factor (not interval_factor)
if ease == 2:  # Hard
    new_interval = max(1, int(current_interval * hard_factor))
elif ease == 3:  # Good
    ease_multiplier = current_factor / 1000.0  # Convert factor to multiplier
    new_interval = max(current_interval + 1, int(current_interval * ease_multiplier))
else:  # ease == 4, Easy
    ease_multiplier = current_factor / 1000.0
    new_interval = max(current_interval + 1, int(current_interval * ease_multiplier * easy_bonus))
```

This will:
- Make intervals grow exponentially (as intended in SM-2)
- Allow cards to reach Mature state in 3-4 weeks (realistic for E01)
- Fix the unfair grading issue

### Option 2: Adjust the assessment formula for E01

If you don't want to change the scheduling code before E01 starts, adjust the Quality formula for E01:

```python
# For exercises < 21 days (E01, E02, E03):
Q = 1.00 × retention_sub + 0.00 × maturity_sub  # Don't grade on maturity for short exercises
```

This is already mentioned in PLAN_ASSESSMENT_STUDENTS_DURING_SEMESTER.md as "B1 maturity correction" but should set maturity weight to **0.0**, not 0.15.

---

## Conclusion

### Current State: ❌ INCORRECT (but partially functional)

1. ✅ Cards **do** progress from New → Learning → Review
2. ✅ Review cards **do** increase their intervals
3. ❌ Intervals grow **linearly** (+1 day each time) instead of **exponentially**
4. ❌ Cards **cannot reach Mature state** in any reasonable timeframe
5. ❌ This **breaks the maturity assessment metric** for E01

### For E01 Specifically:

**Does it work for the pedagogical goals?**
- ✅ Students learn SRS mechanics (4 buttons, spaced intervals)
- ✅ Students see cards graduate from New → Learning → Review
- ✅ Students experience spaced repetition (cards come back after days)
- ⚠️ Students won't see "Mature" state (but this is somewhat expected for a 3-week exercise)

**Does it work for the assessment goals?**
- ❌ Maturity metric is broken (all students will have 0% mature cards)
- ✅ Retention metric works correctly
- ✅ Volume, Consistency, and Engagement metrics work correctly
- **Workaround**: Set maturity weight to 0.0 for E01 (use B1 correction)

---

## Final Recommendation

**For E01 launch (this week)**:
1. ✅ Keep the current code (don't introduce risk by changing scheduling algorithm before E01 starts)
2. ✅ Set maturity weight to **0.0** in the assessment formula for E01 (not 0.15)
3. ✅ Inform students that "Mature" cards are expected in E02+, not E01

**For E02 and beyond**:
1. ⚠️ Fix the interval calculation bug (line 1702) to use `current_factor / 1000.0` instead of `interval_factor`
2. ✅ Test with real data to verify cards reach maturity in 3-4 weeks
3. ✅ Restore maturity weight to 0.30 for E02+ once the bug is fixed

---

**Last updated**: March 3, 2026

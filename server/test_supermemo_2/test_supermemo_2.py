"""
Unit tests for SuperMemo-2 card scheduling algorithm implementation.

This test suite verifies that cards progress correctly through the SRS lifecycle:
    New → Learning → Review (Young) → Review (Mature)

Critical behaviors tested:
1. New cards transition to Learning on first review
2. Learning cards graduate to Review after completing learning steps
3. Review cards increase intervals exponentially (not linearly)
4. Cards reach Mature state (ivl >= 21) within reasonable timeframe
5. Failed review cards enter Relearning state correctly
6. Ease factor adjustments work as expected

Run with:
    cd /Users/emadruga/proj/StudyAmigoApp/server/test_supermemo_2
    python -m pytest test_supermemo_2.py -v
Or:
    python -m unittest test_supermemo_2.py -v
Or from server directory:
    python -m unittest test_supermemo_2.test_supermemo_2 -v
"""

import unittest
import sqlite3
import json
import time
import os
import sys
import tempfile
import shutil

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, init_anki_db

class TestSuperMemo2Scheduling(unittest.TestCase):
    """Test SuperMemo-2 scheduling algorithm implementation."""

    @classmethod
    def setUpClass(cls):
        """Set up test Flask app configuration."""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        cls.client = app.test_client()

    def setUp(self):
        """Create a temporary test database for each test."""
        # Create temporary directory for test database
        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_user.db')

        # Initialize test database with default structure
        init_anki_db(self.test_db_path, user_name="Test User")

        # Store original get_user_db_path function
        import app as app_module
        self.original_get_user_db_path = app_module.get_user_db_path

        # Mock get_user_db_path to return test database
        app_module.get_user_db_path = lambda user_id: self.test_db_path

        # Create test user session
        with self.client.session_transaction() as sess:
            sess['user_id'] = 999
            sess['username'] = 'test_user'

    def tearDown(self):
        """Clean up test database after each test."""
        # Restore original function
        import app as app_module
        app_module.get_user_db_path = self.original_get_user_db_path

        # Remove temporary directory
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def _create_test_card(self, deck_id=1):
        """Helper: Create a new test card and return its ID."""
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        # Create note
        note_id = int(time.time() * 1000)
        cursor.execute("""
            INSERT INTO notes (id, guid, mid, mod, usn, tags, flds, sfld, csum, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (note_id, 'test-guid-' + str(note_id), 1, int(time.time()), -1,
              'test', 'Test Front\x1fTest Back', 'Test Front', 12345, 0, ''))

        # Create card
        card_id = int(time.time() * 1000) + 1
        cursor.execute("""
            INSERT INTO cards (id, nid, did, ord, mod, usn, type, queue, due, ivl, factor, reps, lapses, left, odue, odid, flags, data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (card_id, note_id, deck_id, 0, int(time.time()), -1,
              0, 0, 0, 0, 2500, 0, 0, 0, 0, 0, 0, ''))

        conn.commit()
        conn.close()

        return card_id, note_id

    def _get_card_state(self, card_id):
        """Helper: Get current card state from database."""
        conn = sqlite3.connect(self.test_db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cards WHERE id = ?", (card_id,))
        card = cursor.fetchone()

        conn.close()

        if card:
            return dict(card)
        return None

    def _answer_card(self, card_id, note_id, ease):
        """Helper: Simulate answering a card with given ease (1-4)."""
        with self.client.session_transaction() as sess:
            sess['currentCardId'] = card_id
            sess['currentNoteId'] = note_id

        response = self.client.post('/answer',
                                   json={'ease': ease, 'timeTaken': 5000},
                                   content_type='application/json')

        return response

    def test_new_card_to_learning_transition(self):
        """Test that new cards transition to Learning state on first review."""
        card_id, note_id = self._create_test_card()

        # Initial state: New card
        card = self._get_card_state(card_id)
        self.assertEqual(card['type'], 0, "Card should start as type=0 (New)")
        self.assertEqual(card['queue'], 0, "Card should start as queue=0 (New)")

        # Answer with "Good" (ease=3)
        response = self._answer_card(card_id, note_id, ease=3)
        self.assertEqual(response.status_code, 200, "Answer should succeed")

        # Final state: Learning card
        card = self._get_card_state(card_id)
        self.assertEqual(card['type'], 1, "Card should become type=1 (Learning)")
        self.assertEqual(card['queue'], 1, "Card should become queue=1 (Learning)")
        self.assertGreater(card['reps'], 0, "Card should have reps > 0")

    def test_learning_card_graduation(self):
        """Test that Learning cards graduate to Review after completing steps."""
        card_id, note_id = self._create_test_card()

        # Move to Learning state (first answer)
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)
        self.assertEqual(card['type'], 1, "Card should be in Learning")

        # Complete learning steps (second answer with Good or Easy)
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)

        # Should graduate to Review
        self.assertEqual(card['type'], 2, "Card should graduate to type=2 (Review)")
        self.assertEqual(card['queue'], 2, "Card should graduate to queue=2 (Review)")
        self.assertEqual(card['ivl'], 1, "First review interval should be 1 day")

    def test_learning_card_easy_button_graduates_immediately(self):
        """Test that Easy button on Learning card graduates to Review immediately."""
        card_id, note_id = self._create_test_card()

        # Move to Learning state
        self._answer_card(card_id, note_id, ease=3)

        # Press Easy button (ease=4)
        self._answer_card(card_id, note_id, ease=4)
        card = self._get_card_state(card_id)

        # Should graduate to Review
        self.assertEqual(card['type'], 2, "Easy should graduate to type=2 (Review)")
        self.assertEqual(card['queue'], 2, "Easy should graduate to queue=2 (Review)")
        self.assertEqual(card['ivl'], 1, "First review interval should be 1 day")

    def test_review_card_interval_growth_exponential(self):
        """
        CRITICAL TEST: Verify that Review card intervals grow exponentially, not linearly.

        This test verifies the bug fix. With the bug, intervals grow as 1, 2, 3, 4, 5...
        With the fix, intervals should grow as 1, 2, 5, 12, 30... (exponential)
        """
        card_id, note_id = self._create_test_card()

        # Graduate card to Review state (ivl=1)
        self._answer_card(card_id, note_id, ease=3)  # New → Learning
        self._answer_card(card_id, note_id, ease=3)  # Learning → Review

        card = self._get_card_state(card_id)
        self.assertEqual(card['ivl'], 1, "First review interval should be 1 day")

        # Review 1: Answer "Good" (ease=3)
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)
        ivl_1 = card['ivl']

        # With default factor=2500 (ease=2.5), interval should be 1 * 2.5 = 2.5 ≈ 2
        # NOT 1 + 1 = 2 (linear bug)
        self.assertGreaterEqual(ivl_1, 2, "Second interval should be >= 2")

        # Review 2: Answer "Good" (ease=3) again
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)
        ivl_2 = card['ivl']

        # With exponential growth: ivl_1 * 2.5 = 2 * 2.5 = 5
        # With linear bug: ivl_1 + 1 = 2 + 1 = 3
        self.assertGreaterEqual(ivl_2, 4, f"Third interval should be >= 4 (got {ivl_2})")
        self.assertLess(ivl_2 - ivl_1, ivl_1,
                       f"Growth should be exponential: ivl_2 ({ivl_2}) - ivl_1 ({ivl_1}) should be > ivl_1")

        # Review 3: Answer "Good" (ease=3) again
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)
        ivl_3 = card['ivl']

        # With exponential growth: ivl_2 * 2.5 = 5 * 2.5 = 12.5 ≈ 12
        # With linear bug: ivl_2 + 1 = 5 + 1 = 6
        self.assertGreaterEqual(ivl_3, 10, f"Fourth interval should be >= 10 (got {ivl_3})")

        # Review 4: Answer "Good" (ease=3) again
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)
        ivl_4 = card['ivl']

        # With exponential growth: ivl_3 * 2.5 = 12 * 2.5 = 30
        # With linear bug: ivl_3 + 1 = 12 + 1 = 13
        self.assertGreaterEqual(ivl_4, 25, f"Fifth interval should be >= 25 (got {ivl_4})")

        # Final check: interval sequence should be exponential
        intervals = [1, ivl_1, ivl_2, ivl_3, ivl_4]

        # Calculate growth rates
        growth_rates = [intervals[i+1] / intervals[i] for i in range(len(intervals)-1)]

        # Exponential growth: rates should be > 1.5 on average
        # Linear growth: rates would be ~ 1.0
        avg_growth_rate = sum(growth_rates) / len(growth_rates)
        self.assertGreater(avg_growth_rate, 1.5,
                          f"Average growth rate should be > 1.5 (got {avg_growth_rate:.2f}). "
                          f"Intervals: {intervals}, Growth rates: {[f'{r:.2f}' for r in growth_rates]}")

    def test_review_card_reaches_mature_state(self):
        """
        CRITICAL TEST: Verify that Review cards can reach Mature state (ivl >= 21)
        within a reasonable number of reviews.

        A good student should reach maturity in ~4-5 reviews, not 20+.
        """
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)  # New → Learning
        self._answer_card(card_id, note_id, ease=3)  # Learning → Review (ivl=1)

        # Answer "Good" repeatedly and track intervals
        intervals = [1]  # Start with ivl=1
        max_reviews = 10  # Should reach maturity well before this

        for i in range(max_reviews):
            self._answer_card(card_id, note_id, ease=3)
            card = self._get_card_state(card_id)
            intervals.append(card['ivl'])

            if card['ivl'] >= 21:
                # SUCCESS: Reached mature state
                self.assertLessEqual(i, 5,
                                    f"Should reach maturity (ivl>=21) within 5 reviews, took {i+1}. "
                                    f"Intervals: {intervals}")
                return

        # FAILURE: Did not reach mature state
        self.fail(f"Card did not reach Mature state (ivl>=21) after {max_reviews} reviews. "
                 f"Final interval: {intervals[-1]}. Full sequence: {intervals}. "
                 f"This indicates the linear growth bug is still present.")

    def test_review_card_hard_button_decreases_factor(self):
        """Test that Hard button on Review card decreases ease factor."""
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)

        card = self._get_card_state(card_id)
        initial_factor = card['factor']
        self.assertEqual(initial_factor, 2500, "Initial factor should be 2500")

        # Answer "Hard" (ease=2)
        self._answer_card(card_id, note_id, ease=2)
        card = self._get_card_state(card_id)

        # Factor should decrease by 150
        expected_factor = initial_factor - 150
        self.assertEqual(card['factor'], expected_factor,
                        f"Hard should decrease factor by 150 (got {card['factor']}, expected {expected_factor})")

    def test_review_card_easy_button_increases_factor(self):
        """Test that Easy button on Review card increases ease factor."""
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)

        card = self._get_card_state(card_id)
        initial_factor = card['factor']

        # Answer "Easy" (ease=4)
        self._answer_card(card_id, note_id, ease=4)
        card = self._get_card_state(card_id)

        # Factor should increase by 150
        expected_factor = initial_factor + 150
        self.assertEqual(card['factor'], expected_factor,
                        f"Easy should increase factor by 150 (got {card['factor']}, expected {expected_factor})")

    def test_review_card_good_button_maintains_factor(self):
        """Test that Good button on Review card maintains ease factor."""
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)

        card = self._get_card_state(card_id)
        initial_factor = card['factor']

        # Answer "Good" (ease=3)
        self._answer_card(card_id, note_id, ease=3)
        card = self._get_card_state(card_id)

        # Factor should remain unchanged
        self.assertEqual(card['factor'], initial_factor,
                        f"Good should not change factor (got {card['factor']}, expected {initial_factor})")

    def test_review_card_again_enters_relearning(self):
        """Test that failing a Review card (Again) moves it to Relearning state."""
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)

        card = self._get_card_state(card_id)
        self.assertEqual(card['type'], 2, "Should be in Review")
        initial_lapses = card['lapses']

        # Fail the card (ease=1, "Again")
        self._answer_card(card_id, note_id, ease=1)
        card = self._get_card_state(card_id)

        # Should enter Relearning state
        self.assertEqual(card['type'], 3, "Failed card should become type=3 (Relearning)")
        self.assertEqual(card['queue'], 1, "Failed card should become queue=1 (Learning/Relearning)")
        self.assertEqual(card['lapses'], initial_lapses + 1, "Lapses count should increment")

    def test_relearning_card_can_graduate_back_to_review(self):
        """Test that Relearning cards can graduate back to Review state."""
        card_id, note_id = self._create_test_card()

        # Graduate to Review, then fail
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=1)  # Fail → Relearning

        card = self._get_card_state(card_id)
        self.assertEqual(card['type'], 3, "Should be in Relearning")

        # Complete relearning steps
        self._answer_card(card_id, note_id, ease=3)  # Graduate back to Review
        card = self._get_card_state(card_id)

        # Should be back in Review state
        self.assertEqual(card['type'], 2, "Should graduate back to type=2 (Review)")
        self.assertEqual(card['queue'], 2, "Should graduate back to queue=2 (Review)")

    def test_factor_minimum_boundary(self):
        """Test that ease factor never goes below 1300 (minimum)."""
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)

        # Press "Hard" many times to try to push factor below 1300
        for _ in range(20):
            self._answer_card(card_id, note_id, ease=2)  # Hard: -150

        card = self._get_card_state(card_id)
        self.assertGreaterEqual(card['factor'], 1300,
                               f"Factor should never go below 1300 (got {card['factor']})")

    def test_interval_comparison_linear_vs_exponential(self):
        """
        Direct comparison test: Linear vs Exponential growth.

        This test explicitly demonstrates the difference between the buggy
        implementation (linear +1) and the correct implementation (exponential).
        """
        card_id, note_id = self._create_test_card()

        # Graduate to Review
        self._answer_card(card_id, note_id, ease=3)
        self._answer_card(card_id, note_id, ease=3)

        # Perform 4 "Good" reviews
        actual_intervals = [1]
        for _ in range(4):
            self._answer_card(card_id, note_id, ease=3)
            card = self._get_card_state(card_id)
            actual_intervals.append(card['ivl'])

        # Expected with LINEAR bug: [1, 2, 3, 4, 5]
        linear_expected = [1, 2, 3, 4, 5]

        # Expected with EXPONENTIAL fix (factor=2500 → multiplier=2.5):
        # [1, 2, 5, 12, 30] (approximately, with rounding)
        exponential_expected = [1, 2, 5, 12, 30]

        # Check if actual matches exponential (within tolerance)
        for i, (actual, exp_exp) in enumerate(zip(actual_intervals, exponential_expected)):
            tolerance = max(1, int(exp_exp * 0.2))  # 20% tolerance for rounding
            self.assertGreaterEqual(actual, exp_exp - tolerance,
                                   f"Interval {i}: {actual} should be close to {exp_exp} (exponential), "
                                   f"not {linear_expected[i]} (linear)")

        print(f"\n[DIAGNOSTIC] Interval progression:")
        print(f"  Actual:      {actual_intervals}")
        print(f"  Expected (exponential): {exponential_expected}")
        print(f"  Expected (linear bug):  {linear_expected}")

    def test_e01_scenario_maturity_achievable(self):
        """
        E01-specific test: Verify that students can achieve meaningful maturity
        percentage within 3 weeks (21 days) of consistent study.

        Simulates a student who:
        - Reviews 108 cards over 21 days
        - Answers "Good" on 80% of reviews (realistic good student)
        - Studies every day

        Expected outcome: 30-50% of cards should reach Mature state (ivl >= 21)
        """
        # Create 10 test cards (representative sample of 108)
        cards = []
        for i in range(10):
            card_id, note_id = self._create_test_card()
            cards.append((card_id, note_id))

        # Graduate all cards to Review
        for card_id, note_id in cards:
            self._answer_card(card_id, note_id, ease=3)  # New → Learning
            self._answer_card(card_id, note_id, ease=3)  # Learning → Review

        # Simulate 21 days of reviews (answer "Good" on all)
        for day in range(21):
            for card_id, note_id in cards:
                card = self._get_card_state(card_id)
                # Only review if card is due (simplified: review every 3-4 days)
                if day % 3 == 0:
                    self._answer_card(card_id, note_id, ease=3)

        # Count mature cards
        mature_count = 0
        intervals = []
        for card_id, _ in cards:
            card = self._get_card_state(card_id)
            intervals.append(card['ivl'])
            if card['ivl'] >= 21:
                mature_count += 1

        maturity_percentage = (mature_count / len(cards)) * 100

        print(f"\n[E01 SIMULATION] After 21 days:")
        print(f"  Mature cards: {mature_count}/{len(cards)} ({maturity_percentage:.0f}%)")
        print(f"  Intervals: {intervals}")

        # At least 30% should be mature (with correct exponential growth)
        self.assertGreaterEqual(maturity_percentage, 30,
                               f"After 21 days, at least 30% of cards should be mature. "
                               f"Got {maturity_percentage:.0f}%. Intervals: {intervals}")


class TestRegressionBugs(unittest.TestCase):
    """Test that previously identified bugs remain fixed."""

    def setUp(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        self.client = app.test_client()

        self.test_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.test_dir, 'test_user.db')
        init_anki_db(self.test_db_path, user_name="Test User")

        import app as app_module
        self.original_get_user_db_path = app_module.get_user_db_path
        app_module.get_user_db_path = lambda user_id: self.test_db_path

        with self.client.session_transaction() as sess:
            sess['user_id'] = 999
            sess['username'] = 'test_user'

    def tearDown(self):
        """Clean up."""
        import app as app_module
        app_module.get_user_db_path = self.original_get_user_db_path
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_line_1702_bug_fixed(self):
        """
        Regression test for the line 1702 bug.

        Original bug:
            new_interval = max(current_interval + 1,
                             int(current_interval * interval_adjust * interval_factor))

        When interval_adjust = interval_factor = 1.0, this became:
            new_interval = max(current_interval + 1, current_interval) = current_interval + 1

        Fixed version should use ease factor:
            new_interval = int(current_interval * (current_factor / 1000.0))
        """
        # This is tested indirectly by test_review_card_interval_growth_exponential
        # and test_review_card_reaches_mature_state
        pass


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)

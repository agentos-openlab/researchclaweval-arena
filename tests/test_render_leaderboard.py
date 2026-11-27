"""Public ranking rules, independent of the historical snapshot."""
import subprocess
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import render_leaderboard as ranking


def entry(framework, score, *, topic='arc_wbe_2026', model='Model A', protocol='v1', status='verified'):
    return {
        'topic': topic, 'framework': framework, 'model': model, 'protocol': protocol,
        'status': status, 'value': score,
        'source_sha256': 'a' * 64 if score is not None else None,
        'reviewed_runs': int(score is not None),
    }


class RankingTests(unittest.TestCase):
    def test_score_directions_and_ties(self):
        rows = ranking.rank([
            entry('a', 3), entry('b', 2), entry('c', 2),
            entry('a', 0.3, topic='psydefdetect'), entry('b', 0.4, topic='psydefdetect'),
        ])
        self.assertEqual(
            [(r['topic'], r['framework'], r['rank']) for r in rows],
            [('arc_wbe_2026','b',1), ('arc_wbe_2026','c',1), ('arc_wbe_2026','a',3),
             ('psydefdetect','b',1), ('psydefdetect','a',2)],
        )

    def test_models_and_protocols_never_share_a_rank(self):
        rows = ranking.rank([
            entry('a', 10), entry('b', 12, model='Model B'), entry('c', 24, protocol='v2'),
        ])
        self.assertEqual([r['rank'] for r in rows], [1, 1, 1])

    def test_self_reported_and_missing_results_do_not_rank(self):
        rows = ranking.rank([
            entry('a', None, status='unverified'),
            entry('b', 20, topic='babylm', status='self_reported'),
        ])
        self.assertEqual([r['rank'] for r in rows], [None, None])
        with self.assertRaises(ValueError):
            ranking.rank([entry('c', 20, topic='babylm')])

    def test_score_requires_a_source_and_finite_number(self):
        for invalid in (dict(entry('a', 1), source_sha256=None), entry('a', float('inf'))):
            with self.assertRaises(ValueError):
                ranking.rank([invalid])

    def test_checked_in_outputs_match_generator(self):
        command = [sys.executable, str(ranking.ROOT / 'scripts/render_leaderboard.py'), '--check']
        subprocess.run(command, check=True)


if __name__ == '__main__':
    unittest.main()

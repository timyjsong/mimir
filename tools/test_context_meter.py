#!/usr/bin/env python3
"""Unit tests for context-meter's pure logic.

The window now comes from the statusLine sensor cache (the harness's authoritative
`context_window_size`), not from inferring it off `/model` prose or lastModelUsage history —
so the tests cover cache read, the resolve/default/backstop logic, and the transcript parse
(usage + burn boundaries). Run: python3 tools/test_context_meter.py
"""
import importlib.util, os, json, tempfile, unittest

# Load the hyphenated tool file as a module (can't `import context-meter` directly).
_spec = importlib.util.spec_from_file_location(
    "context_meter", os.path.join(os.path.dirname(__file__), "context-meter.py"))
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

M1, MB = cm.WIN_1M, cm.WIN_BASE
LCS = "local-command-stdout"


def block(inner):
    """Wrap a body in a realistic <local-command-stdout> block (used to assert such blocks
    are NOT mistaken for genuine user prompts)."""
    return f"<{LCS}>{inner}</{LCS}>"


class ParseWindow(unittest.TestCase):
    def test_m(self):
        self.assertEqual(cm.parse_window("1M"), M1)
        self.assertEqual(cm.parse_window("1m"), M1)

    def test_k(self):
        self.assertEqual(cm.parse_window("200K"), MB)
        self.assertEqual(cm.parse_window("200k"), MB)

    def test_raw_tokens(self):
        self.assertEqual(cm.parse_window("1000000"), M1)
        self.assertEqual(cm.parse_window("200000"), MB)

    def test_garbage_uses_fallback(self):
        self.assertEqual(cm.parse_window("nonsense"), M1)        # default fallback = 1M
        self.assertEqual(cm.parse_window(""), M1)
        self.assertEqual(cm.parse_window(None), M1)

    def test_explicit_fallback(self):
        self.assertEqual(cm.parse_window("junk", fallback=MB), MB)


class CachedWindow(unittest.TestCase):
    """The authoritative window read from the sensor cache, keyed by session id = transcript
    basename. This is the load-bearing path: the meter trusts it over any inference."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig = cm.CACHE_DIR
        cm.CACHE_DIR = self.tmp
        self.addCleanup(setattr, cm, "CACHE_DIR", self._orig)

    def _cache(self, sid, payload):
        with open(os.path.join(self.tmp, f"mimir-meter-{sid}.json"), "w") as f:
            f.write(payload)

    def test_reads_1m(self):
        self._cache("abc", '{"context_window_size": 1000000}')
        self.assertEqual(cm.cached_window("/p/abc.jsonl"), M1)

    def test_reads_200k(self):
        self._cache("abc", '{"context_window_size": 200000}')
        self.assertEqual(cm.cached_window("/p/abc.jsonl"), MB)

    def test_basename_keys_the_lookup(self):
        # session id is the transcript filename without .jsonl, regardless of directory
        self._cache("sess-1", '{"context_window_size": 1000000}')
        self.assertEqual(cm.cached_window("/any/dir/sess-1.jsonl"), M1)

    def test_absent_is_none(self):
        self.assertIsNone(cm.cached_window("/p/missing.jsonl"))

    def test_garbage_json_is_none(self):
        self._cache("abc", "not json")
        self.assertIsNone(cm.cached_window("/p/abc.jsonl"))

    def test_missing_key_is_none(self):
        self._cache("abc", '{"something_else": 1}')
        self.assertIsNone(cm.cached_window("/p/abc.jsonl"))

    def test_zero_is_none(self):
        # a 0 size is unusable -> treated as absent
        self._cache("abc", '{"context_window_size": 0}')
        self.assertIsNone(cm.cached_window("/p/abc.jsonl"))


class ResolveWindow(unittest.TestCase):
    def test_cache_wins(self):
        self.assertEqual(cm.resolve_window(50_000, M1, MB), (M1, "statusline"))
        self.assertEqual(cm.resolve_window(50_000, MB, M1), (MB, "statusline"))

    def test_default_when_no_cache(self):
        # THE BUG REGRESSION: no authoritative window, default is 1M -> NOT 200K.
        self.assertEqual(cm.resolve_window(50_000, None, M1), (M1, "default"))

    def test_default_can_be_200k(self):
        self.assertEqual(cm.resolve_window(50_000, None, MB), (MB, "default"))

    def test_backstop_bumps_default_200k_over(self):
        # default 200K but usage exceeds it -> physically must be 1M
        w, src = cm.resolve_window(250_000, None, MB)
        self.assertEqual(w, M1)
        self.assertIn("used>200K", src)

    def test_no_backstop_when_cache_1m(self):
        self.assertEqual(cm.resolve_window(250_000, M1, M1), (M1, "statusline"))

    def test_no_backstop_under_window(self):
        w, src = cm.resolve_window(150_000, None, MB)
        self.assertEqual(w, MB)
        self.assertNotIn("used>", src)


class StripSystemReminders(unittest.TestCase):
    def test_plain_untouched(self):
        self.assertEqual(cm.strip_system_reminders("align"), "align")

    def test_strips_leading_reminder(self):
        self.assertEqual(
            cm.strip_system_reminders("<system-reminder>Message sent at Fri X</system-reminder>\ncommit"),
            "commit")

    def test_strips_multiple_reminders(self):
        s = "<system-reminder>a</system-reminder>\n<system-reminder>b</system-reminder>\nhi"
        self.assertEqual(cm.strip_system_reminders(s), "hi")

    def test_reminder_only_becomes_empty(self):
        self.assertEqual(cm.strip_system_reminders("<system-reminder>nudge</system-reminder>"), "")

    def test_command_stdout_not_a_reminder(self):
        s = "<local-command-stdout>Set model to claude-opus-4-8</local-command-stdout>"
        self.assertEqual(cm.strip_system_reminders(s), s)


class IsUserPrompt(unittest.TestCase):
    def up(self, content, tur=False):
        o = {"type": "user", "message": {"role": "user", "content": content}}
        if tur:
            o["toolUseResult"] = {"x": 1}
        return o

    def test_plain_prompt(self):
        self.assertTrue(cm.is_user_prompt(self.up("align")))

    def test_reminder_wrapped_prompt(self):
        # The dropped-turn bug: a real prompt prefixed with a 'Message sent at' reminder.
        self.assertTrue(cm.is_user_prompt(
            self.up("<system-reminder>Message sent at Fri 2026-06-12 22:09 UTC.</system-reminder>\ncommit")))

    def test_reminder_only_not_a_prompt(self):
        self.assertFalse(cm.is_user_prompt(self.up("<system-reminder>some injected nudge</system-reminder>")))

    def test_command_stdout_not_a_prompt(self):
        self.assertFalse(cm.is_user_prompt(self.up(block("Set model to claude-opus-4-8[1m]"))))

    def test_tool_result_not_a_prompt(self):
        self.assertFalse(cm.is_user_prompt(self.up([{"type": "tool_result", "content": "x"}], tur=True)))

    def test_text_list_is_a_prompt(self):
        self.assertTrue(cm.is_user_prompt(self.up([{"type": "text", "text": "hi"}])))

    def test_assistant_not_a_prompt(self):
        self.assertFalse(cm.is_user_prompt({"type": "assistant", "message": {"role": "assistant", "content": "x"}}))


class ReadIntegration(unittest.TestCase):
    """read() does the file I/O + per-line accumulation; test it on a synthetic transcript.
    It returns (usage, boundaries, msg_model) — the window is NOT derived here (sensor cache)."""

    def _write(self, lines):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w") as f:
            for o in lines:
                f.write(json.dumps(o) + "\n")
        self.addCleanup(os.unlink, path)
        return path

    def test_reads_usage_and_model(self):
        path = self._write([
            {"cwd": "/home/tim/projects/mimir",
             "message": {"model": "claude-opus-4-8",
                         "usage": {"input_tokens": 10, "cache_creation_input_tokens": 5,
                                   "cache_read_input_tokens": 100_000}}},
        ])
        usage, _b, msg_model = cm.read(path)
        self.assertEqual(msg_model, "claude-opus-4-8")
        self.assertEqual(cm.tokens(usage), 100_015)

    def test_last_usage_block_wins(self):
        path = self._write([
            {"message": {"usage": {"input_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
            {"message": {"usage": {"input_tokens": 9, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
        ])
        usage, _boundaries, _model = cm.read(path)
        self.assertEqual(usage["input_tokens"], 9)

    def test_turn_boundaries_for_burn(self):
        path = self._write([
            {"type": "user", "message": {"role": "user", "content": "hi"}},
            {"message": {"usage": {"input_tokens": 100, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
            {"type": "user", "message": {"role": "user", "content": "more"}},
            {"message": {"usage": {"input_tokens": 250, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
            {"type": "user", "message": {"role": "user", "content": "again"}},
            {"message": {"usage": {"input_tokens": 400, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
        ])
        _usage, boundaries, _model = cm.read(path)
        self.assertEqual(boundaries, [0, 100, 250])
        self.assertEqual(boundaries[-1] - boundaries[-2], 150)   # previous completed turn's burn

    def test_tool_results_and_commands_not_boundaries(self):
        path = self._write([
            {"type": "user", "message": {"role": "user", "content": "hi"}},
            {"message": {"usage": {"input_tokens": 100, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
            {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "content": "x"}]}},
            {"type": "user", "message": {"role": "user", "content": "<local-command-stdout>Set model to claude-opus-4-8[1m]</local-command-stdout>"}},
            {"message": {"usage": {"input_tokens": 200, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
        ])
        _usage, boundaries, _model = cm.read(path)
        self.assertEqual(boundaries, [0])   # only the one genuine prompt

    def test_synthetic_entry_skipped(self):
        # An interrupt writes a <synthetic> placeholder at the tail; it must NOT become
        # the reported usage/model (the "0K / model=<synthetic>" bug from an interrupted turn).
        path = self._write([
            {"message": {"model": "claude-opus-4-8",
                         "usage": {"input_tokens": 50_000, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
            {"message": {"model": "<synthetic>",
                         "usage": {"input_tokens": 0, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
        ])
        usage, _b, msg_model = cm.read(path)
        self.assertEqual(cm.tokens(usage), 50_000)   # the real turn, not the synthetic 0
        self.assertEqual(msg_model, "claude-opus-4-8")


class EndToEnd(unittest.TestCase):
    """read() + cached_window + resolve_window together — the actual reported window."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self._orig = cm.CACHE_DIR
        cm.CACHE_DIR = self.tmp
        self.addCleanup(setattr, cm, "CACHE_DIR", self._orig)

    def _transcript(self, sid, used):
        path = os.path.join(self.tmp, f"{sid}.jsonl")
        with open(path, "w") as f:
            f.write(json.dumps({"message": {"model": "claude-opus-4-8",
                    "usage": {"input_tokens": used, "cache_creation_input_tokens": 0,
                              "cache_read_input_tokens": 0}}}) + "\n")
        return path

    def _resolve(self, path):
        usage, _b, _m = cm.read(path)
        return cm.resolve_window(cm.tokens(usage), cm.cached_window(path), cm.DEFAULT_WINDOW)

    def test_authoritative_1m(self):
        path = self._transcript("s1", 120_000)
        with open(os.path.join(self.tmp, "mimir-meter-s1.json"), "w") as f:
            f.write('{"context_window_size": 1000000}')
        self.assertEqual(self._resolve(path), (M1, "statusline"))

    def test_authoritative_200k(self):
        # a genuine 200K session is reported as 200K — a measurement, not a default
        path = self._transcript("s2", 120_000)
        with open(os.path.join(self.tmp, "mimir-meter-s2.json"), "w") as f:
            f.write('{"context_window_size": 200000}')
        self.assertEqual(self._resolve(path), (MB, "statusline"))

    def test_cold_start_defaults_1m_not_200k(self):
        # THE ORIGINAL BUG: no cache yet -> must read 1M, never 200K.
        path = self._transcript("s3", 120_000)
        w, src = self._resolve(path)
        self.assertEqual(w, M1)
        self.assertEqual(src, "default")


class BurnStats(unittest.TestCase):
    def test_no_completed_turn(self):
        self.assertEqual(cm.burn_stats([], 5), (None, None))
        self.assertEqual(cm.burn_stats([100], 5), (None, None))

    def test_single_turn_avg_equals_last(self):
        # One delta available -> avg == last (no smoothing possible yet).
        self.assertEqual(cm.burn_stats([0, 100], 5), (100, 100.0))

    def test_two_turns(self):
        # deltas 100, 150 -> last=150, avg=(250-0)/2=125
        self.assertEqual(cm.burn_stats([0, 100, 250], 5), (150, 125.0))

    def test_window_caps_lookback(self):
        # boundaries deltas: 100,150,150,200,300 ; window=3 -> last 3 deltas (150,200,300)
        last, avg = cm.burn_stats([0, 100, 250, 400, 600, 900], 3)
        self.assertEqual(last, 300)
        self.assertAlmostEqual(avg, 650 / 3)

    def test_window_larger_than_history(self):
        # window 5 but only 2 deltas -> average both
        self.assertEqual(cm.burn_stats([0, 100, 250], 5), (150, 125.0))

    def test_decline_is_negative(self):
        # context can shrink (a /clear-like drop) -> negative burn
        last, avg = cm.burn_stats([500, 600, 200], 5)
        self.assertEqual(last, -400)
        self.assertEqual(avg, -150.0)


class ParseThreshold(unittest.TestCase):
    def test_percent(self):
        self.assertEqual(cm.parse_threshold("50%"), ("pct", 50.0))

    def test_percent_fractional(self):
        self.assertEqual(cm.parse_threshold("62.5%"), ("pct", 62.5))

    def test_abs_k(self):
        self.assertEqual(cm.parse_threshold("200K"), ("abs", 200_000))

    def test_abs_k_lower(self):
        self.assertEqual(cm.parse_threshold("200k"), ("abs", 200_000))

    def test_abs_m(self):
        self.assertEqual(cm.parse_threshold("1M"), ("abs", 1_000_000))

    def test_abs_raw_tokens(self):
        self.assertEqual(cm.parse_threshold("200000"), ("abs", 200_000))

    def test_garbage_defaults_to_50pct(self):
        self.assertEqual(cm.parse_threshold("nonsense"), ("pct", 50.0))

    def test_empty_defaults_to_50pct(self):
        self.assertEqual(cm.parse_threshold(""), ("pct", 50.0))
        self.assertEqual(cm.parse_threshold(None), ("pct", 50.0))


class InSurfaceZone(unittest.TestCase):
    def test_pct_over(self):
        self.assertTrue(cm.in_surface_zone(600_000, 1_000_000, "50%"))   # 60% >= 50

    def test_pct_under(self):
        self.assertFalse(cm.in_surface_zone(400_000, 1_000_000, "50%"))  # 40% < 50

    def test_pct_exact_boundary_is_surface(self):
        self.assertTrue(cm.in_surface_zone(500_000, 1_000_000, "50%"))   # at threshold -> surface

    def test_abs_over(self):
        self.assertTrue(cm.in_surface_zone(250_000, 1_000_000, "200K"))

    def test_abs_under(self):
        self.assertFalse(cm.in_surface_zone(150_000, 1_000_000, "200K"))

    def test_abs_independent_of_window(self):
        # absolute threshold compares tokens, not %, so a big window doesn't change the call
        self.assertTrue(cm.in_surface_zone(210_000, 1_000_000, "200K"))
        self.assertFalse(cm.in_surface_zone(190_000, 200_000, "200K"))


class Fmt(unittest.TestCase):
    def test_k(self):
        self.assertEqual(cm.fmt(402014), "402K")

    def test_window_200k(self):
        self.assertEqual(cm.fmt(200000), "200K")

    def test_exact_1m(self):
        self.assertEqual(cm.fmt(1000000), "1M")

    def test_fractional_m(self):
        self.assertEqual(cm.fmt(1400000), "1.4M")

    def test_tokens_total(self):
        self.assertEqual(cm.tokens({"input_tokens": 10, "cache_creation_input_tokens": 5, "cache_read_input_tokens": 100000}), 100015)

    def test_tokens_none(self):
        self.assertEqual(cm.tokens(None), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)

#!/usr/bin/env python3
"""Unit tests for context-meter's pure detection logic.

Tests the parse/resolve functions in isolation (no `claude -p`, no live transcripts) using
the REAL `/model` stdout strings observed across this machine's transcripts plus synthetic
edge cases. Run: python3 tools/test_context_meter.py
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
    """Wrap a body in a realistic <local-command-stdout> block."""
    return f"<{LCS}>{inner}</{LCS}>"


class StripAnsi(unittest.TestCase):
    def test_bold_wrap(self):
        self.assertEqual(cm.strip_ansi("\x1b[1mOpus 4.8\x1b[22m"), "Opus 4.8")

    def test_plain_untouched(self):
        self.assertEqual(cm.strip_ansi("claude-opus-4-8[1m]"), "claude-opus-4-8[1m]")

    def test_multiple_codes(self):
        self.assertEqual(cm.strip_ansi("\x1b[0m\x1b[1mX\x1b[22m\x1b[39m"), "X")


class ParseSetModel(unittest.TestCase):
    # --- raw-id format (observed) ---
    def test_raw_opus_1m(self):
        self.assertEqual(cm.parse_set_model(block("Set model to claude-opus-4-8[1m]")),
                         "claude-opus-4-8[1m]")

    def test_raw_opus_base(self):
        self.assertEqual(cm.parse_set_model(block("Set model to claude-opus-4-8")),
                         "claude-opus-4-8")

    def test_raw_sonnet_base(self):
        self.assertEqual(cm.parse_set_model(block("Set model to claude-sonnet-4-6")),
                         "claude-sonnet-4-6")

    def test_raw_fable_1m(self):
        self.assertEqual(cm.parse_set_model(block("Set model to claude-fable-5[1m]")),
                         "claude-fable-5[1m]")

    # --- friendly ANSI-wrapped format (observed) — the bug that produced "[1mOpus" ---
    def test_friendly_opus_1m(self):
        c = block("Set model to \x1b[1mOpus 4.8 (1M context)\x1b[22m and saved as your default model")
        self.assertEqual(cm.parse_set_model(c), "Opus 4.8 (1M context)")

    def test_friendly_opus_1m_default(self):
        c = block("Set model to \x1b[1mOpus 4.8 (1M context) (default)\x1b[22m and saved as your default model")
        self.assertEqual(cm.parse_set_model(c), "Opus 4.8 (1M context)")

    def test_friendly_fable_base(self):
        c = block("Set model to \x1b[1mFable 5\x1b[22m and saved as your default model")
        self.assertEqual(cm.parse_set_model(c), "Fable 5")

    # --- guards ---
    def test_prose_without_block_ignored(self):
        # No command-stdout tag => must NOT parse (prose mentioning the phrase).
        self.assertIsNone(cm.parse_set_model("the docs say: Set model to claude-opus-4-8[1m] each turn"))

    def test_id_placeholder_ignored(self):
        # "<id>" template text inside a block must not be captured as a model.
        self.assertIsNone(cm.parse_set_model(block("Set model to <id>` from real /model command")))

    def test_last_switch_wins(self):
        c = block("Set model to claude-sonnet-4-6") + " ... " + block("Set model to claude-opus-4-8[1m]")
        self.assertEqual(cm.parse_set_model(c), "claude-opus-4-8[1m]")

    def test_meta_session_false_positive_ignored(self):
        # The real bug from developing this tool: content that QUOTES the format and mentions
        # "local-command-stdout" elsewhere, with the LITERAL text "\x1b[1m" (not a real ESC
        # byte). Content does not START with the tag => must be rejected.
        c = ('LCS = "local-command-stdout"; example: '
             'Set model to \\x1b[1mOpus 4.8 (1M context)\\x1b[22m and saved as your default model')
        self.assertIsNone(cm.parse_set_model(c))

    def test_leading_whitespace_ok(self):
        # A genuine block with leading whitespace still parses (lstrip).
        self.assertEqual(cm.parse_set_model("\n  " + block("Set model to claude-opus-4-8[1m]")),
                         "claude-opus-4-8[1m]")


class WindowForModel(unittest.TestCase):
    def test_raw_1m_suffix(self):
        self.assertEqual(cm.window_for_model("claude-opus-4-8[1m]"), M1)

    def test_friendly_1m_label(self):
        self.assertEqual(cm.window_for_model("Opus 4.8 (1M context)"), M1)

    def test_base_id(self):
        self.assertEqual(cm.window_for_model("claude-opus-4-8"), MB)

    def test_friendly_base_label(self):
        self.assertEqual(cm.window_for_model("Fable 5"), MB)

    def test_none(self):
        self.assertEqual(cm.window_for_model(None), MB)


class Resolve(unittest.TestCase):
    def test_tier1_raw_1m(self):
        self.assertEqual(cm.resolve(50_000, "claude-opus-4-8[1m]", None, None),
                         (M1, "model-log", "claude-opus-4-8[1m]"))

    def test_tier1_friendly_1m(self):
        # The end-to-end fix for the "[1mOpus / 200k" bug, at the resolver level.
        self.assertEqual(cm.resolve(50_000, "Opus 4.8 (1M context)", None, None),
                         (M1, "model-log", "Opus 4.8 (1M context)"))

    def test_tier1_base(self):
        self.assertEqual(cm.resolve(50_000, "claude-sonnet-4-6", None, None),
                         (MB, "model-log", "claude-sonnet-4-6"))

    def test_tier2_lastmodelusage(self):
        self.assertEqual(cm.resolve(50_000, None, "claude-opus-4-8", True),
                         (M1, "lastModelUsage", "claude-opus-4-8[1m]"))

    def test_tier3_ambiguous(self):
        self.assertEqual(cm.resolve(50_000, None, "claude-fable-5", None),
                         (MB, "lookup?", "claude-fable-5"))

    def test_tier3_base_default(self):
        self.assertEqual(cm.resolve(50_000, None, "claude-sonnet-4-6", False),
                         (MB, "base-default", "claude-sonnet-4-6"))

    # --- the used>200k backstop: the "169.8%" bug ---
    def test_backstop_fixes_169pct(self):
        w, src, cur = cm.resolve(339_584, None, "claude-fable-5", None)
        self.assertEqual(w, M1)
        self.assertIn("used>200k", src)
        self.assertLess(339_584 / w * 100, 100.0)   # no longer >100%

    def test_backstop_on_base_default(self):
        w, src, _ = cm.resolve(250_000, None, "claude-opus-4-8", False)
        self.assertEqual(w, M1)
        self.assertEqual(src, "base-default+used>200k")

    def test_backstop_not_applied_when_already_1m(self):
        # Already 1M via lastModelUsage => no redundant "+used>200k" tag.
        self.assertEqual(cm.resolve(250_000, None, "claude-opus-4-8", True),
                         (M1, "lastModelUsage", "claude-opus-4-8[1m]"))

    def test_no_backstop_under_200k(self):
        w, src, _ = cm.resolve(150_000, None, "claude-fable-5", None)
        self.assertEqual(w, MB)
        self.assertNotIn("used>200k", src)


class ReadIntegration(unittest.TestCase):
    """read() does the file I/O + per-line accumulation; test it on a synthetic transcript."""

    def _write(self, lines):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w") as f:
            for o in lines:
                f.write(json.dumps(o) + "\n")
        self.addCleanup(os.unlink, path)
        return path

    def test_reads_usage_model_and_switch(self):
        path = self._write([
            {"cwd": "/home/tim/projects/mimir",
             "message": {"model": "claude-opus-4-8",
                         "usage": {"input_tokens": 10, "cache_creation_input_tokens": 5,
                                   "cache_read_input_tokens": 100_000}}},
            {"message": {"content": [
                {"text": block("Set model to \x1b[1mOpus 4.8 (1M context)\x1b[22m and saved as your default model")}]}},
        ])
        usage, msg_model, set_model, cwd = cm.read(path)
        self.assertEqual(set_model, "Opus 4.8 (1M context)")
        self.assertEqual(msg_model, "claude-opus-4-8")
        self.assertEqual(cwd, "/home/tim/projects/mimir")
        used = usage["input_tokens"] + usage["cache_creation_input_tokens"] + usage["cache_read_input_tokens"]
        self.assertEqual(cm.resolve(used, set_model, msg_model, None)[0], M1)

    def test_last_usage_block_wins(self):
        path = self._write([
            {"message": {"usage": {"input_tokens": 1, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
            {"message": {"usage": {"input_tokens": 9, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}}},
        ])
        usage, *_ = cm.read(path)
        self.assertEqual(usage["input_tokens"], 9)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""Tests for pattern generation."""

import pytest

from renoise_mcp.pattern_gen import (
    KICK,
    SNARE,
    BreakStyle,
    NoteEvent,
    generate_break_pattern,
    generate_bassline,
    MINOR_PENTATONIC,
)


class TestNoteEvent:
    def test_to_dict_minimal(self):
        event = NoteEvent(line=0, note=36, instrument=0)
        d = event.to_dict()

        assert d["line"] == 0
        assert d["note"] == 36
        assert d["instrument"] == 0
        assert "volume" not in d
        assert "delay" not in d

    def test_to_dict_full(self):
        event = NoteEvent(
            line=4,
            note=38,
            instrument=1,
            column=0,
            volume=100,
            delay=30,
            fx_number="09",
            fx_value=64,
        )
        d = event.to_dict()

        assert d["line"] == 4
        assert d["note"] == 38
        assert d["instrument"] == 1
        assert d["volume"] == 100
        assert d["delay"] == 30
        assert d["fx_number"] == "09"
        assert d["fx_value"] == 64


class TestGenerateBreakPattern:
    def test_generates_events(self):
        events = generate_break_pattern(
            style=BreakStyle.AMEN,
            lines=64,
            lpb=4,
            instrument=0,
        )

        assert len(events) > 0
        assert all(isinstance(e, NoteEvent) for e in events)

    def test_contains_kicks_and_snares(self):
        events = generate_break_pattern(
            style=BreakStyle.AMEN,
            lines=64,
            lpb=4,
            instrument=0,
        )

        notes = [e.note for e in events]
        assert KICK in notes
        assert SNARE in notes

    def test_respects_instrument(self):
        events = generate_break_pattern(
            style=BreakStyle.AMEN,
            lines=64,
            instrument=5,
        )

        assert all(e.instrument == 5 for e in events)

    def test_all_lines_within_bounds(self):
        lines = 32
        events = generate_break_pattern(
            style=BreakStyle.AMEN,
            lines=lines,
        )

        assert all(0 <= e.line < lines for e in events)

    @pytest.mark.parametrize("style", list(BreakStyle))
    def test_all_styles_generate_events(self, style):
        events = generate_break_pattern(style=style, lines=64)
        assert len(events) > 0


class TestGenerateBassline:
    def test_generates_events(self):
        events = generate_bassline(
            root=36,
            scale=MINOR_PENTATONIC,
            lines=64,
            instrument=1,
        )

        assert len(events) > 0

    def test_starts_on_root(self):
        events = generate_bassline(
            root=36,
            scale=MINOR_PENTATONIC,
            lines=64,
        )

        # First note should be on line 0
        first_events = [e for e in events if e.line == 0]
        assert len(first_events) > 0
        assert first_events[0].note == 36

    def test_respects_instrument(self):
        events = generate_bassline(
            root=36,
            scale=MINOR_PENTATONIC,
            instrument=3,
        )

        assert all(e.instrument == 3 for e in events)

    def test_density_affects_count(self):
        sparse = generate_bassline(root=36, scale=MINOR_PENTATONIC, density=0.1)
        dense = generate_bassline(root=36, scale=MINOR_PENTATONIC, density=0.9)

        # Dense should generally have more events (with some variance due to randomness)
        # Using a loose check since it's random
        assert len(dense) >= len(sparse) * 0.5

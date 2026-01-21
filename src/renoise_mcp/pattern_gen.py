"""Pattern generation utilities for drum and bass production."""

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias

# MIDI note constants for common drum sounds
KICK = 36
SNARE = 38
CLOSED_HAT = 42
OPEN_HAT = 46
CRASH = 49
RIDE = 51


class BreakStyle(Enum):
    """Styles of breakbeat patterns."""

    AMEN = "amen"
    THINK = "think"
    FUNKY_DRUMMER = "funky_drummer"
    APACHE = "apache"
    STRAIGHT = "straight"
    TWO_STEP = "two_step"


@dataclass
class NoteEvent:
    """A single note event in a pattern."""

    line: int
    note: int
    instrument: int = 0
    column: int = 0
    volume: int | None = None
    delay: int | None = None
    fx_number: str | None = None
    fx_value: int | None = None

    def to_dict(self) -> dict:
        """Convert to dict for write_pattern_data."""
        d = {
            "line": self.line,
            "column": self.column,
            "note": self.note,
            "instrument": self.instrument,
        }
        if self.volume is not None:
            d["volume"] = self.volume
        if self.delay is not None:
            d["delay"] = self.delay
        if self.fx_number is not None:
            d["fx_number"] = self.fx_number
            d["fx_value"] = self.fx_value or 0
        return d


Pattern: TypeAlias = list[NoteEvent]


def generate_break_pattern(
    style: BreakStyle,
    lines: int = 64,
    lpb: int = 4,
    instrument: int = 0,
    intensity: float = 0.7,
    variation: float = 0.2,
    swing: int = 0,
) -> Pattern:
    """Generate a breakbeat pattern.

    Args:
        style: The style of break to generate
        lines: Number of lines in the pattern
        lpb: Lines per beat (affects grid resolution)
        instrument: Instrument index to use
        intensity: How dense the pattern is (0-1)
        variation: How much random variation (0-1)
        swing: Swing amount for off-beats (0-255 delay value)

    Returns:
        List of NoteEvent objects
    """
    events: Pattern = []

    # Calculate grid positions
    # For dnb at 4 LPB, a bar is 16 lines
    bar_length = lpb * 4
    num_bars = lines // bar_length

    if style == BreakStyle.AMEN:
        events = _generate_amen_pattern(
            lines, lpb, instrument, intensity, variation, swing
        )
    elif style == BreakStyle.TWO_STEP:
        events = _generate_two_step_pattern(
            lines, lpb, instrument, intensity, variation, swing
        )
    elif style == BreakStyle.STRAIGHT:
        events = _generate_straight_pattern(
            lines, lpb, instrument, intensity, variation, swing
        )
    elif style == BreakStyle.THINK:
        events = _generate_think_pattern(
            lines, lpb, instrument, intensity, variation, swing
        )
    else:
        # Default to amen-style
        events = _generate_amen_pattern(
            lines, lpb, instrument, intensity, variation, swing
        )

    return events


def _generate_amen_pattern(
    lines: int,
    lpb: int,
    instrument: int,
    intensity: float,
    variation: float,
    swing: int,
) -> Pattern:
    """Generate an amen-style break.

    Classic amen pattern structure (at 4 LPB per bar of 16 lines):
    - Kick on 1, ghost on 3, kick on 7
    - Snare on 5, 13
    - Hats throughout with swing
    """
    events: Pattern = []
    bar = lpb * 4  # 16 lines per bar at 4 LPB

    for bar_num in range(lines // bar):
        offset = bar_num * bar

        # Main kicks
        events.append(NoteEvent(line=offset + 0, note=KICK, instrument=instrument, volume=127))

        # Second kick (sometimes ghost)
        if random.random() < 0.7 + (intensity * 0.3):
            vol = random.randint(80, 110) if random.random() < variation else 100
            events.append(NoteEvent(line=offset + 6, note=KICK, instrument=instrument, volume=vol))

        # Snares on 2 and 4 (lines 4 and 12 at 4 LPB)
        events.append(NoteEvent(line=offset + 4, note=SNARE, instrument=instrument, volume=127))
        events.append(NoteEvent(line=offset + 12, note=SNARE, instrument=instrument, volume=127))

        # Ghost snares based on intensity
        if intensity > 0.5 and random.random() < intensity:
            ghost_positions = [2, 10, 14]
            for pos in ghost_positions:
                if random.random() < variation:
                    vol = random.randint(40, 70)
                    events.append(
                        NoteEvent(line=offset + pos, note=SNARE, instrument=instrument, volume=vol)
                    )

        # Hi-hats
        for i in range(0, bar, 2):
            if random.random() < intensity:
                hat = CLOSED_HAT if random.random() > 0.2 else OPEN_HAT
                vol = random.randint(60, 100) if random.random() < variation else 80
                delay = swing if i % 4 == 2 else 0
                events.append(
                    NoteEvent(
                        line=offset + i,
                        note=hat,
                        instrument=instrument,
                        column=1,  # Separate column for hats
                        volume=vol,
                        delay=delay if delay > 0 else None,
                    )
                )

    return events


def _generate_two_step_pattern(
    lines: int,
    lpb: int,
    instrument: int,
    intensity: float,
    variation: float,
    swing: int,
) -> Pattern:
    """Generate a two-step dnb pattern.

    Two-step has a more sparse, syncopated feel:
    - Kick on 1, kick late in bar
    - Snare on 2 and 4
    - Minimal hats
    """
    events: Pattern = []
    bar = lpb * 4

    for bar_num in range(lines // bar):
        offset = bar_num * bar

        # Kicks
        events.append(NoteEvent(line=offset + 0, note=KICK, instrument=instrument, volume=127))

        # Second kick - syncopated position
        kick2_pos = 10 if bar_num % 2 == 0 else 11
        if random.random() < 0.8:
            events.append(
                NoteEvent(line=offset + kick2_pos, note=KICK, instrument=instrument, volume=110)
            )

        # Snares
        events.append(NoteEvent(line=offset + 4, note=SNARE, instrument=instrument, volume=127))
        events.append(NoteEvent(line=offset + 12, note=SNARE, instrument=instrument, volume=127))

        # Sparse hats - two-step feel
        hat_positions = [0, 4, 8, 12]
        for pos in hat_positions:
            if random.random() < intensity * 0.8:
                events.append(
                    NoteEvent(
                        line=offset + pos,
                        note=CLOSED_HAT,
                        instrument=instrument,
                        column=1,
                        volume=random.randint(60, 90),
                    )
                )

    return events


def _generate_straight_pattern(
    lines: int,
    lpb: int,
    instrument: int,
    intensity: float,
    variation: float,
    swing: int,
) -> Pattern:
    """Generate a straight/4-on-floor influenced dnb pattern."""
    events: Pattern = []
    bar = lpb * 4

    for bar_num in range(lines // bar):
        offset = bar_num * bar

        # Kicks on every beat
        for beat in range(4):
            pos = offset + (beat * lpb)
            vol = 127 if beat == 0 else random.randint(90, 115)
            events.append(NoteEvent(line=pos, note=KICK, instrument=instrument, volume=vol))

        # Snares on 2 and 4
        events.append(NoteEvent(line=offset + 4, note=SNARE, instrument=instrument, volume=127))
        events.append(NoteEvent(line=offset + 12, note=SNARE, instrument=instrument, volume=127))

        # 8th note hats
        for i in range(0, bar, 2):
            hat = OPEN_HAT if i % 4 == 2 else CLOSED_HAT
            events.append(
                NoteEvent(
                    line=offset + i,
                    note=hat,
                    instrument=instrument,
                    column=1,
                    volume=random.randint(70, 100),
                    delay=swing if i % 4 == 2 else None,
                )
            )

    return events


def _generate_think_pattern(
    lines: int,
    lpb: int,
    instrument: int,
    intensity: float,
    variation: float,
    swing: int,
) -> Pattern:
    """Generate a think-break style pattern.

    The think break has a distinctive syncopated feel with
    emphasis on the "and" of beats.
    """
    events: Pattern = []
    bar = lpb * 4

    for bar_num in range(lines // bar):
        offset = bar_num * bar

        # Characteristic think break kick pattern
        kick_positions = [0, 3, 6, 10]
        for pos in kick_positions:
            if pos == 0 or random.random() < intensity:
                vol = 127 if pos == 0 else random.randint(90, 115)
                events.append(
                    NoteEvent(line=offset + pos, note=KICK, instrument=instrument, volume=vol)
                )

        # Snares with ghost notes
        events.append(NoteEvent(line=offset + 4, note=SNARE, instrument=instrument, volume=127))
        events.append(NoteEvent(line=offset + 12, note=SNARE, instrument=instrument, volume=127))

        # Ghost snare on the "and"
        if random.random() < intensity:
            events.append(
                NoteEvent(line=offset + 7, note=SNARE, instrument=instrument, volume=60)
            )

        # Hats with swing
        for i in range(0, bar, 2):
            if random.random() < intensity:
                events.append(
                    NoteEvent(
                        line=offset + i,
                        note=CLOSED_HAT,
                        instrument=instrument,
                        column=1,
                        volume=random.randint(50, 80),
                        delay=swing if i % 4 == 2 else None,
                    )
                )

    return events


def generate_bassline(
    root: int,
    scale: list[int],
    lines: int = 64,
    lpb: int = 4,
    instrument: int = 1,
    density: float = 0.5,
    octave_range: int = 2,
) -> Pattern:
    """Generate a bassline pattern.

    Args:
        root: Root note (MIDI number, e.g., 36 for C2)
        scale: Scale intervals from root (e.g., [0, 2, 3, 5, 7, 10] for minor)
        lines: Number of lines
        lpb: Lines per beat
        instrument: Instrument index
        density: How many notes (0-1)
        octave_range: Range of octaves to use

    Returns:
        List of NoteEvent objects
    """
    events: Pattern = []
    bar = lpb * 4

    # Build available notes
    notes = []
    for octave in range(octave_range):
        for interval in scale:
            notes.append(root + (octave * 12) + interval)

    # Generate pattern
    current_note = root
    for bar_num in range(lines // bar):
        offset = bar_num * bar

        # Root on the 1
        events.append(
            NoteEvent(line=offset, note=current_note, instrument=instrument, volume=127)
        )

        # Fill in based on density
        positions = [2, 4, 6, 8, 10, 12, 14]
        for pos in positions:
            if random.random() < density:
                # Tend toward root and fifth
                if random.random() < 0.6:
                    note = current_note
                elif random.random() < 0.3:
                    note = current_note + 7  # Fifth
                else:
                    note = random.choice(notes)

                vol = random.randint(90, 120)
                events.append(
                    NoteEvent(line=offset + pos, note=note, instrument=instrument, volume=vol)
                )

        # Occasionally change root note
        if random.random() < 0.3:
            current_note = random.choice([root, root + scale[2], root + scale[4]])

    return events


def add_sample_offsets(
    events: Pattern,
    offset_map: dict[int, list[int]] | None = None,
) -> Pattern:
    """Add sample offset (09xx) effects for break chopping.

    Args:
        events: Existing pattern events
        offset_map: Dict mapping line positions to offset values.
                   If None, generates random offsets for variety.

    Returns:
        Pattern with offset effects added
    """
    if offset_map is None:
        # Generate variety through random offsets
        for event in events:
            if event.note in [KICK, SNARE] and random.random() < 0.3:
                event.fx_number = "09"
                event.fx_value = random.choice([0x00, 0x20, 0x40, 0x60, 0x80, 0xA0, 0xC0])
    else:
        for event in events:
            if event.line in offset_map:
                event.fx_number = "09"
                event.fx_value = random.choice(offset_map[event.line])

    return events


def add_retrigs(
    events: Pattern,
    probability: float = 0.1,
    retrig_speeds: list[int] | None = None,
) -> Pattern:
    """Add retrigger effects (Rxy) for drill/fills.

    Args:
        events: Existing pattern events
        probability: Chance of adding retrig to each snare
        retrig_speeds: List of retrig values to choose from

    Returns:
        Pattern with retrigs added
    """
    if retrig_speeds is None:
        retrig_speeds = [0x03, 0x04, 0x06, 0x08]  # Common retrig speeds

    for event in events:
        if event.note == SNARE and random.random() < probability:
            event.fx_number = "0R"
            # First digit is volume change, second is speed
            event.fx_value = random.choice(retrig_speeds)

    return events


# Common scales for dnb
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
MINOR_PENTATONIC = [0, 3, 5, 7, 10]
DORIAN = [0, 2, 3, 5, 7, 9, 10]
PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]  # Dark, Middle Eastern feel

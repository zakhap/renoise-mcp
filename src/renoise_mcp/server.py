"""MCP Server for Renoise control via OSC."""

import os
from mcp.server.fastmcp import FastMCP

from .osc_client import RenoiseConfig, RenoiseOSC
from .pattern_gen import (
    MINOR_PENTATONIC,
    MINOR_SCALE,
    BreakStyle,
    add_retrigs,
    add_sample_offsets,
    generate_bassline,
    generate_break_pattern,
)

# Initialize MCP server
mcp = FastMCP("renoise-mcp")

# Initialize Renoise OSC client with config from environment
_config = RenoiseConfig(
    host=os.environ.get("RENOISE_HOST", "127.0.0.1"),
    port=int(os.environ.get("RENOISE_PORT", "8000")),
)
renoise = RenoiseOSC(_config)


# =============================================================================
# Transport Tools
# =============================================================================


@mcp.tool()
def play() -> str:
    """Start playback in Renoise."""
    renoise.play()
    return "Playback started"


@mcp.tool()
def stop() -> str:
    """Stop playback in Renoise."""
    renoise.stop()
    return "Playback stopped"


@mcp.tool()
def panic() -> str:
    """Stop all sounds immediately (panic button)."""
    renoise.panic()
    return "Panic - all sounds stopped"


@mcp.tool()
def set_bpm(bpm: int) -> str:
    """Set the tempo in beats per minute.

    Args:
        bpm: Tempo in BPM (20-999)
    """
    renoise.set_bpm(bpm)
    return f"BPM set to {bpm}"


@mcp.tool()
def set_lpb(lpb: int) -> str:
    """Set lines per beat (affects pattern resolution).

    Args:
        lpb: Lines per beat (1-255). Common values: 4 (standard), 8 (high resolution)
    """
    renoise.set_lpb(lpb)
    return f"LPB set to {lpb}"


# =============================================================================
# Note Triggering (real-time preview, not recorded)
# =============================================================================


@mcp.tool()
def trigger_note(
    instrument: int,
    note: int,
    velocity: int = 100,
    track: int = -1,
) -> str:
    """Trigger a note to hear it (not recorded to pattern).

    Args:
        instrument: Instrument index (0-based)
        note: MIDI note number (0-119, e.g., 60 = C-4)
        velocity: Note velocity (0-127)
        track: Track to play on (-1 for selected track)
    """
    renoise.trigger_note_on(instrument, track, note, velocity)
    return f"Triggered note {note} on instrument {instrument}"


@mcp.tool()
def stop_note(
    instrument: int,
    note: int,
    track: int = -1,
) -> str:
    """Stop a triggered note.

    Args:
        instrument: Instrument index
        note: MIDI note number to stop
        track: Track (-1 for selected)
    """
    renoise.trigger_note_off(instrument, track, note)
    return f"Stopped note {note}"


# =============================================================================
# Track Control
# =============================================================================


@mcp.tool()
def mute_track(track: int, muted: bool = True) -> str:
    """Mute or unmute a track.

    Args:
        track: Track index (0-based)
        muted: True to mute, False to unmute
    """
    renoise.set_track_mute(track, muted)
    return f"Track {track} {'muted' if muted else 'unmuted'}"


@mcp.tool()
def solo_track(track: int, soloed: bool = True) -> str:
    """Solo or unsolo a track.

    Args:
        track: Track index (0-based)
        soloed: True to solo, False to unsolo
    """
    renoise.set_track_solo(track, soloed)
    return f"Track {track} {'soloed' if soloed else 'unsoloed'}"


@mcp.tool()
def set_track_volume(track: int, volume: float) -> str:
    """Set track volume.

    Args:
        track: Track index (0-based)
        volume: Volume level (0.0 to 1.0)
    """
    renoise.set_track_volume(track, volume)
    return f"Track {track} volume set to {volume}"


# =============================================================================
# Pattern Operations
# =============================================================================


@mcp.tool()
def set_note(
    pattern: int,
    track: int,
    line: int,
    note: int,
    instrument: int = 0,
    volume: int = 127,
    column: int = 0,
) -> str:
    """Set a single note in a pattern.

    Args:
        pattern: Pattern index (0-based)
        track: Track index (0-based)
        line: Line number (0-based)
        note: MIDI note (0-119), or 120 for note-off
        instrument: Instrument index
        volume: Note volume (0-127)
        column: Note column (0-based)
    """
    renoise.set_pattern_note(
        pattern=pattern,
        track=track,
        line=line,
        column=column,
        note=note,
        instrument=instrument,
        volume=volume,
    )
    return f"Note {note} set at pattern {pattern}, track {track}, line {line}"


@mcp.tool()
def set_effect(
    pattern: int,
    track: int,
    line: int,
    effect: str,
    value: int,
    column: int = 0,
) -> str:
    """Set an effect command in a pattern.

    Args:
        pattern: Pattern index (0-based)
        track: Track index (0-based)
        line: Line number (0-based)
        effect: Effect command (e.g., "09" for sample offset, "0R" for retrig)
        value: Effect value (0-255)
        column: Effect column (0-based)

    Common effects:
        09xx - Sample offset (xx = position in sample)
        0Rxy - Retrigger (x = volume change, y = speed)
        0Qxx - Delay note by xx ticks
        0Dxx - Pitch slide down
        0Uxx - Pitch slide up
    """
    renoise.set_pattern_effect(
        pattern=pattern,
        track=track,
        line=line,
        column=column,
        effect=effect,
        value=value,
    )
    return f"Effect {effect}{value:02X} set at pattern {pattern}, track {track}, line {line}"


@mcp.tool()
def clear_pattern(pattern: int) -> str:
    """Clear all data from a pattern.

    Args:
        pattern: Pattern index (0-based)
    """
    renoise.clear_pattern(pattern)
    return f"Pattern {pattern} cleared"


@mcp.tool()
def set_pattern_length(pattern: int, lines: int) -> str:
    """Set the length of a pattern in lines.

    Args:
        pattern: Pattern index (0-based)
        lines: Number of lines (1-512)
    """
    renoise.set_pattern_length(pattern, lines)
    return f"Pattern {pattern} length set to {lines} lines"


# =============================================================================
# Sequencing
# =============================================================================


@mcp.tool()
def jump_to_pattern(position: int) -> str:
    """Jump to a position in the sequence immediately.

    Args:
        position: Sequence position (0-based)
    """
    renoise.trigger_sequence(position)
    return f"Jumped to sequence position {position}"


@mcp.tool()
def schedule_pattern(position: int) -> str:
    """Schedule the next pattern (will switch at end of current pattern).

    Args:
        position: Sequence position to switch to
    """
    renoise.schedule_sequence(position)
    return f"Scheduled sequence position {position}"


# =============================================================================
# Lua Evaluation (Power Tool)
# =============================================================================


@mcp.tool()
def evaluate_lua(code: str) -> str:
    """Evaluate arbitrary Lua code in Renoise.

    This is the most powerful tool - anything possible in Renoise's Lua API
    can be done here. Use for operations not covered by other tools.

    Args:
        code: Lua code to evaluate in Renoise

    Example:
        evaluate_lua("renoise.song().transport.bpm = 174")
    """
    renoise.evaluate_lua(code)
    return f"Evaluated Lua code ({len(code)} chars)"


# =============================================================================
# High-Level Composition Tools
# =============================================================================


@mcp.tool()
def generate_breakbeat(
    pattern: int,
    track: int,
    style: str = "amen",
    lines: int = 64,
    bpm: int = 174,
    instrument: int = 0,
    intensity: float = 0.7,
    variation: float = 0.2,
    add_chops: bool = True,
) -> str:
    """Generate a breakbeat pattern.

    Args:
        pattern: Pattern index to write to (0-based)
        track: Track index (0-based)
        style: Break style - "amen", "two_step", "think", "straight"
        lines: Pattern length in lines
        bpm: Tempo (will also set song BPM)
        instrument: Instrument index for drums
        intensity: Pattern density (0-1)
        variation: Random variation amount (0-1)
        add_chops: Whether to add sample offset effects for variety

    Returns:
        Description of generated pattern
    """
    # Set BPM
    renoise.set_bpm(bpm)
    renoise.set_pattern_length(pattern, lines)

    # Map style string to enum
    style_map = {
        "amen": BreakStyle.AMEN,
        "two_step": BreakStyle.TWO_STEP,
        "think": BreakStyle.THINK,
        "straight": BreakStyle.STRAIGHT,
        "funky_drummer": BreakStyle.FUNKY_DRUMMER,
        "apache": BreakStyle.APACHE,
    }
    break_style = style_map.get(style.lower(), BreakStyle.AMEN)

    # Generate pattern
    events = generate_break_pattern(
        style=break_style,
        lines=lines,
        lpb=4,
        instrument=instrument,
        intensity=intensity,
        variation=variation,
    )

    # Add chops if requested
    if add_chops:
        events = add_sample_offsets(events)

    # Write to Renoise
    data = [e.to_dict() for e in events]
    renoise.write_pattern_data(pattern, track, data)

    return f"Generated {style} breakbeat: {len(events)} events at {bpm} BPM"


@mcp.tool()
def generate_bass_pattern(
    pattern: int,
    track: int,
    root_note: int = 36,
    scale: str = "minor",
    lines: int = 64,
    instrument: int = 1,
    density: float = 0.5,
) -> str:
    """Generate a bassline pattern.

    Args:
        pattern: Pattern index (0-based)
        track: Track index (0-based)
        root_note: Root MIDI note (e.g., 36 = C2, 41 = F2)
        scale: Scale to use - "minor", "minor_pentatonic", "dorian", "phrygian"
        lines: Pattern length
        instrument: Instrument index for bass
        density: How many notes (0-1)

    Returns:
        Description of generated pattern
    """
    # Map scale name to intervals
    scale_map = {
        "minor": MINOR_SCALE,
        "minor_pentatonic": MINOR_PENTATONIC,
        "dorian": [0, 2, 3, 5, 7, 9, 10],
        "phrygian": [0, 1, 3, 5, 7, 8, 10],
        "major": [0, 2, 4, 5, 7, 9, 11],
    }
    scale_intervals = scale_map.get(scale.lower(), MINOR_SCALE)

    events = generate_bassline(
        root=root_note,
        scale=scale_intervals,
        lines=lines,
        lpb=4,
        instrument=instrument,
        density=density,
    )

    data = [e.to_dict() for e in events]
    renoise.write_pattern_data(pattern, track, data)

    return f"Generated {scale} bassline from note {root_note}: {len(events)} events"


@mcp.tool()
def add_drum_fill(
    pattern: int,
    track: int,
    start_line: int,
    length: int = 4,
    instrument: int = 0,
    intensity: float = 0.8,
) -> str:
    """Add a drum fill (snare roll/buildup).

    Args:
        pattern: Pattern index
        track: Track index
        start_line: Line to start the fill
        length: Length of fill in lines
        instrument: Drum instrument index
        intensity: Fill density (0-1)

    Returns:
        Description of fill added
    """
    events = []

    # Build up retrig fill
    for i in range(length):
        line = start_line + i
        # Increasing density toward end
        density = 0.5 + (i / length) * 0.5

        if i == length - 1:
            # Last hit - accent
            events.append(
                {
                    "line": line,
                    "note": 38,  # Snare
                    "instrument": instrument,
                    "volume": 127,
                    "fx_number": "0R",
                    "fx_value": 0x02,  # Fast retrig
                }
            )
        elif i >= length - 2:
            # Building intensity
            events.append(
                {
                    "line": line,
                    "note": 38,
                    "instrument": instrument,
                    "volume": 100 + (i * 5),
                    "fx_number": "0R",
                    "fx_value": 0x04,
                }
            )
        else:
            events.append(
                {
                    "line": line,
                    "note": 38,
                    "instrument": instrument,
                    "volume": 80,
                }
            )

    renoise.write_pattern_data(pattern, track, events)
    return f"Added {length}-line drum fill starting at line {start_line}"


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()

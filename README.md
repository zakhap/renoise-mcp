# renoise-mcp

MCP server for controlling Renoise via OSC. Lets Claude compose music by writing patterns, triggering notes, and controlling playback.

## Requirements

- [Renoise](https://www.renoise.com/) (demo or full version)
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
cd osc-mcp
uv sync
```

Or with pip:
```bash
pip install -e .
```

## Renoise Setup

1. Open Renoise
2. Go to `Edit > Preferences > OSC`
3. Enable OSC server
4. Set protocol to UDP
5. Set port to 8000 (or configure via environment variable)

## Claude Code Configuration

Add to your `~/.claude.json` or Claude Desktop MCP settings:

```json
{
  "mcpServers": {
    "renoise": {
      "command": "uv",
      "args": ["--directory", "/path/to/osc-mcp", "run", "renoise-mcp"],
      "env": {
        "RENOISE_HOST": "127.0.0.1",
        "RENOISE_PORT": "8000"
      }
    }
  }
}
```

## Tools

### Transport
- `play()` - Start playback
- `stop()` - Stop playback
- `panic()` - Stop all sounds immediately
- `set_bpm(bpm)` - Set tempo (20-999)
- `set_lpb(lpb)` - Set lines per beat

### Note Operations
- `trigger_note(instrument, note, velocity, track)` - Play a note (real-time, not recorded)
- `stop_note(instrument, note, track)` - Stop a triggered note
- `set_note(pattern, track, line, note, instrument, volume, column)` - Write note to pattern
- `set_effect(pattern, track, line, effect, value, column)` - Write effect command

### Track Control
- `mute_track(track, muted)` - Mute/unmute track
- `solo_track(track, soloed)` - Solo/unsolo track
- `set_track_volume(track, volume)` - Set track volume (0-1)

### Pattern Operations
- `clear_pattern(pattern)` - Clear all data from pattern
- `set_pattern_length(pattern, lines)` - Set pattern length (1-512)
- `jump_to_pattern(position)` - Jump to sequence position
- `schedule_pattern(position)` - Schedule next pattern

### High-Level Composition
- `generate_breakbeat(pattern, track, style, lines, bpm, instrument, intensity, variation, add_chops)` - Generate a breakbeat pattern
- `generate_bass_pattern(pattern, track, root_note, scale, lines, instrument, density)` - Generate a bassline
- `add_drum_fill(pattern, track, start_line, length, instrument, intensity)` - Add a drum fill

### Power Tool
- `evaluate_lua(code)` - Execute arbitrary Lua code in Renoise

## Usage Examples

### Basic: Set up a 174 BPM dnb track
```
set_bpm(174)
set_lpb(4)
set_pattern_length(0, 64)
```

### Generate an amen-style break
```
generate_breakbeat(
    pattern=0,
    track=0,
    style="amen",
    bpm=174,
    intensity=0.8,
    variation=0.3
)
```

### Generate a bassline
```
generate_bass_pattern(
    pattern=0,
    track=1,
    root_note=36,  # C2
    scale="minor_pentatonic",
    density=0.6
)
```

### Manual note placement
```
# Kick on beat 1
set_note(pattern=0, track=0, line=0, note=36, instrument=0)

# Snare on beat 2
set_note(pattern=0, track=0, line=4, note=38, instrument=0)

# Add sample offset effect
set_effect(pattern=0, track=0, line=8, effect="09", value=64)
```

### Direct Lua for advanced operations
```
evaluate_lua("""
    local song = renoise.song()
    song:pattern(1):track(1):line(1):note_column(1).note_value = 48
""")
```

## Break Styles

- `amen` - Classic amen break pattern with ghost notes
- `two_step` - Syncopated two-step dnb pattern
- `think` - Think break style with characteristic syncopation
- `straight` - Four-on-floor influenced pattern

## Scales

- `minor` - Natural minor
- `minor_pentatonic` - Minor pentatonic (great for dnb bass)
- `dorian` - Dorian mode
- `phrygian` - Phrygian mode (dark, Middle Eastern feel)
- `major` - Major scale

## Effect Commands Reference

Common Renoise effect commands:
- `09xx` - Sample offset (xx = position, 00-FF)
- `0Rxy` - Retrigger (x = volume change, y = speed)
- `0Qxx` - Delay note by xx ticks
- `0Dxx` - Pitch slide down
- `0Uxx` - Pitch slide up
- `0Bxx` - Play sample backwards
- `0Yxx` - Probability (xx% chance to play)

## Architecture

```
Claude Code
    │
    │ MCP Protocol
    ▼
renoise-mcp server (Python)
    │
    │ OSC (UDP)
    ▼
Renoise
```

The server translates MCP tool calls into OSC messages that Renoise understands. Complex operations use the `/renoise/evaluate` endpoint to run Lua code directly in Renoise.

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Format/lint
uv run ruff check --fix
uv run ruff format
```

## License

MIT

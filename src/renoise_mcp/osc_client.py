"""OSC client for communicating with Renoise."""

from dataclasses import dataclass
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder


@dataclass
class RenoiseConfig:
    """Configuration for Renoise OSC connection."""

    host: str = "127.0.0.1"
    port: int = 8000


class RenoiseOSC:
    """OSC client for Renoise.

    Provides methods for all Renoise OSC endpoints plus Lua evaluation
    for operations not directly exposed via OSC.
    """

    def __init__(self, config: RenoiseConfig | None = None):
        self.config = config or RenoiseConfig()
        self._client = udp_client.SimpleUDPClient(self.config.host, self.config.port)

    def _send(self, address: str, *args) -> None:
        """Send an OSC message to Renoise."""
        self._client.send_message(address, list(args) if args else [])

    # =========================================================================
    # Transport
    # =========================================================================

    def play(self) -> None:
        """Start playback."""
        self._send("/renoise/transport/start")

    def stop(self) -> None:
        """Stop playback."""
        self._send("/renoise/transport/stop")

    def continue_playback(self) -> None:
        """Continue playback from current position."""
        self._send("/renoise/transport/continue")

    def panic(self) -> None:
        """Stop all sounds immediately."""
        self._send("/renoise/transport/panic")

    def set_bpm(self, bpm: int) -> None:
        """Set beats per minute (20-999)."""
        bpm = max(20, min(999, bpm))
        self._send("/renoise/song/bpm", bpm)

    def set_lpb(self, lpb: int) -> None:
        """Set lines per beat (1-255)."""
        lpb = max(1, min(255, lpb))
        self._send("/renoise/song/lpb", lpb)

    def set_edit_mode(self, enabled: bool) -> None:
        """Enable/disable edit mode."""
        self._send("/renoise/song/edit/mode", 1 if enabled else 0)

    # =========================================================================
    # Note Triggering (real-time, not recorded to pattern)
    # =========================================================================

    def trigger_note_on(
        self,
        instrument: int,
        track: int,
        note: int,
        velocity: int,
    ) -> None:
        """Trigger a note on.

        Args:
            instrument: Instrument index (0-based, or -1 for selected)
            track: Track index (0-based, or -1 for selected)
            note: MIDI note number (0-119)
            velocity: Velocity (0-127)
        """
        self._send("/renoise/trigger/note_on", instrument, track, note, velocity)

    def trigger_note_off(
        self,
        instrument: int,
        track: int,
        note: int,
    ) -> None:
        """Trigger a note off.

        Args:
            instrument: Instrument index (0-based, or -1 for selected)
            track: Track index (0-based, or -1 for selected)
            note: MIDI note number (0-119)
        """
        self._send("/renoise/trigger/note_off", instrument, track, note)

    # =========================================================================
    # Track Control
    # =========================================================================

    def set_track_mute(self, track: int, muted: bool) -> None:
        """Mute/unmute a track."""
        address = f"/renoise/song/track/{track + 1}/mute"
        self._send(address, 1 if muted else 0)

    def set_track_solo(self, track: int, soloed: bool) -> None:
        """Solo/unsolo a track."""
        address = f"/renoise/song/track/{track + 1}/solo"
        self._send(address, 1 if soloed else 0)

    def set_track_volume(self, track: int, volume: float) -> None:
        """Set track pre-fx volume (0.0-1.0)."""
        volume = max(0.0, min(1.0, volume))
        address = f"/renoise/song/track/{track + 1}/prefx_volume"
        self._send(address, volume)

    def set_track_panning(self, track: int, panning: float) -> None:
        """Set track post-fx panning (-50 to 50)."""
        panning = max(-50.0, min(50.0, panning))
        address = f"/renoise/song/track/{track + 1}/postfx_panning"
        self._send(address, panning)

    # =========================================================================
    # Pattern Sequencing
    # =========================================================================

    def trigger_sequence(self, position: int) -> None:
        """Jump to a sequence position immediately."""
        self._send("/renoise/song/sequence/trigger", position)

    def schedule_sequence(self, position: int) -> None:
        """Schedule next sequence position (will switch at pattern end)."""
        self._send("/renoise/song/sequence/schedule_set", position)

    # =========================================================================
    # Lua Evaluation (the power tool)
    # =========================================================================

    def evaluate_lua(self, code: str) -> None:
        """Evaluate arbitrary Lua code in Renoise.

        This is the most powerful tool - anything that can be done via
        the Renoise Lua API can be done through this.

        Args:
            code: Lua code to evaluate
        """
        self._send("/renoise/evaluate", code)

    # =========================================================================
    # Pattern Operations via Lua
    # =========================================================================

    def set_pattern_note(
        self,
        pattern: int,
        track: int,
        line: int,
        column: int,
        note: int | None = None,
        instrument: int | None = None,
        volume: int | None = None,
        panning: int | None = None,
        delay: int | None = None,
    ) -> None:
        """Set a note in a pattern.

        Args:
            pattern: Pattern index (0-based)
            track: Track index (0-based)
            line: Line index (0-based)
            column: Note column index (0-based)
            note: MIDI note (0-119), 120=OFF, or None to leave unchanged
            instrument: Instrument index (0-254), or None
            volume: Volume (0-128), or None
            panning: Panning (0-128), or None
            delay: Delay (0-255), or None
        """
        # Build Lua code to set the note
        lua_parts = [
            f"local nc = renoise.song():pattern({pattern + 1})"
            f":track({track + 1}):line({line + 1}):note_column({column + 1})"
        ]

        if note is not None:
            lua_parts.append(f"nc.note_value = {note}")
        if instrument is not None:
            lua_parts.append(f"nc.instrument_value = {instrument}")
        if volume is not None:
            lua_parts.append(f"nc.volume_value = {volume}")
        if panning is not None:
            lua_parts.append(f"nc.panning_value = {panning}")
        if delay is not None:
            lua_parts.append(f"nc.delay_value = {delay}")

        self.evaluate_lua("\n".join(lua_parts))

    def set_pattern_effect(
        self,
        pattern: int,
        track: int,
        line: int,
        column: int,
        effect: str,
        value: int,
    ) -> None:
        """Set an effect command in a pattern.

        Args:
            pattern: Pattern index (0-based)
            track: Track index (0-based)
            line: Line index (0-based)
            column: Effect column index (0-based)
            effect: Effect command (e.g., "09" for sample offset)
            value: Effect value (0-255)
        """
        lua = f"""
local fc = renoise.song():pattern({pattern + 1}):track({track + 1}):line({line + 1}):effect_column({column + 1})
fc.number_string = "{effect}"
fc.amount_value = {value}
"""
        self.evaluate_lua(lua)

    def clear_pattern_line(
        self,
        pattern: int,
        track: int,
        line: int,
    ) -> None:
        """Clear all note and effect columns on a line."""
        lua = f"""
local line = renoise.song():pattern({pattern + 1}):track({track + 1}):line({line + 1})
line:clear()
"""
        self.evaluate_lua(lua)

    def clear_pattern(self, pattern: int) -> None:
        """Clear an entire pattern."""
        lua = f"renoise.song():pattern({pattern + 1}):clear()"
        self.evaluate_lua(lua)

    def set_pattern_length(self, pattern: int, lines: int) -> None:
        """Set the number of lines in a pattern (1-512)."""
        lines = max(1, min(512, lines))
        lua = f"renoise.song():pattern({pattern + 1}).number_of_lines = {lines}"
        self.evaluate_lua(lua)

    def create_instrument(self, name: str) -> None:
        """Create a new instrument."""
        lua = f"""
local song = renoise.song()
local idx = #song.instruments + 1
song:insert_instrument_at(idx)
song.instruments[idx].name = "{name}"
"""
        self.evaluate_lua(lua)

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def write_pattern_data(
        self,
        pattern: int,
        track: int,
        data: list[dict],
    ) -> None:
        """Write multiple notes/effects to a pattern efficiently.

        Args:
            pattern: Pattern index (0-based)
            track: Track index (0-based)
            data: List of dicts with keys:
                - line: int (required)
                - column: int (default 0)
                - note: int or None
                - instrument: int or None
                - volume: int or None
                - delay: int or None
                - fx_column: int or None (for effect)
                - fx_number: str or None (e.g., "09")
                - fx_value: int or None
        """
        lua_lines = [
            f"local track = renoise.song():pattern({pattern + 1}):track({track + 1})"
        ]

        for entry in data:
            line_idx = entry["line"] + 1  # Lua is 1-indexed

            # Note data
            if any(k in entry for k in ["note", "instrument", "volume", "delay"]):
                col = entry.get("column", 0) + 1
                lua_lines.append(f"local nc = track:line({line_idx}):note_column({col})")
                if "note" in entry and entry["note"] is not None:
                    lua_lines.append(f"nc.note_value = {entry['note']}")
                if "instrument" in entry and entry["instrument"] is not None:
                    lua_lines.append(f"nc.instrument_value = {entry['instrument']}")
                if "volume" in entry and entry["volume"] is not None:
                    lua_lines.append(f"nc.volume_value = {entry['volume']}")
                if "delay" in entry and entry["delay"] is not None:
                    lua_lines.append(f"nc.delay_value = {entry['delay']}")

            # Effect data
            if "fx_number" in entry and entry["fx_number"] is not None:
                fx_col = entry.get("fx_column", 0) + 1
                lua_lines.append(f"local fc = track:line({line_idx}):effect_column({fx_col})")
                lua_lines.append(f'fc.number_string = "{entry["fx_number"]}"')
                if "fx_value" in entry and entry["fx_value"] is not None:
                    lua_lines.append(f"fc.amount_value = {entry['fx_value']}")

        self.evaluate_lua("\n".join(lua_lines))

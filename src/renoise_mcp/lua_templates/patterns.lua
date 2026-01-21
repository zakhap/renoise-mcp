-- Lua templates for complex Renoise operations
-- These are used by the MCP server via evaluate_lua()

-- =============================================================================
-- Pattern Utilities
-- =============================================================================

-- Copy a pattern to another slot
-- Usage: copy_pattern(1, 2) -- copies pattern 1 to pattern 2
function copy_pattern(src_idx, dst_idx)
    local song = renoise.song()
    local src = song:pattern(src_idx)
    local dst = song:pattern(dst_idx)

    dst:copy_from(src)
end

-- Duplicate current pattern
function duplicate_current_pattern()
    local song = renoise.song()
    local seq = song.sequencer
    local current_pos = song.transport.playback_pos.sequence
    local current_pattern = seq:pattern(current_pos)

    -- Insert new pattern after current
    local new_idx = #song.patterns + 1
    song:insert_pattern_at(new_idx)
    song:pattern(new_idx):copy_from(song:pattern(current_pattern))

    -- Add to sequence after current position
    seq:insert_sequence_at(current_pos + 1, new_idx)
end

-- =============================================================================
-- Track Utilities
-- =============================================================================

-- Get track by name
function get_track_by_name(name)
    local song = renoise.song()
    for i, track in ipairs(song.tracks) do
        if track.name == name then
            return i, track
        end
    end
    return nil, nil
end

-- Create a new track with name
function create_track(name, index)
    local song = renoise.song()
    index = index or (#song.tracks)
    song:insert_track_at(index)
    song.tracks[index].name = name
    return index
end

-- =============================================================================
-- Note Writing Utilities
-- =============================================================================

-- Write a sequence of notes quickly
-- notes is a table: { {line=0, note=48, inst=0}, {line=4, note=48, inst=0}, ... }
function write_notes(pattern_idx, track_idx, notes, column)
    column = column or 1
    local track = renoise.song():pattern(pattern_idx):track(track_idx)

    for _, n in ipairs(notes) do
        local nc = track:line(n.line + 1):note_column(column)
        if n.note then nc.note_value = n.note end
        if n.inst then nc.instrument_value = n.inst end
        if n.vol then nc.volume_value = n.vol end
        if n.delay then nc.delay_value = n.delay end
    end
end

-- Clear a range of lines
function clear_lines(pattern_idx, track_idx, start_line, end_line)
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    for i = start_line, end_line do
        track:line(i + 1):clear()
    end
end

-- =============================================================================
-- Instrument Utilities
-- =============================================================================

-- Load a sample into an instrument
function load_sample(instrument_idx, file_path)
    local inst = renoise.song().instruments[instrument_idx]
    local sample = inst:insert_sample_at(1)
    sample.sample_buffer:load_from(file_path)
end

-- Set instrument name
function set_instrument_name(instrument_idx, name)
    renoise.song().instruments[instrument_idx].name = name
end

-- =============================================================================
-- Transport Queries
-- =============================================================================

-- Get current playback position as table
function get_playback_position()
    local pos = renoise.song().transport.playback_pos
    return {
        sequence = pos.sequence,
        line = pos.line
    }
end

-- Get current BPM
function get_bpm()
    return renoise.song().transport.bpm
end

-- Get current LPB
function get_lpb()
    return renoise.song().transport.lpb
end

-- =============================================================================
-- Pattern Queries
-- =============================================================================

-- Get pattern length
function get_pattern_length(pattern_idx)
    return renoise.song():pattern(pattern_idx).number_of_lines
end

-- Get number of patterns
function get_pattern_count()
    return #renoise.song().patterns
end

-- Get sequence length
function get_sequence_length()
    return #renoise.song().sequencer.pattern_sequence
end

-- =============================================================================
-- Effects
-- =============================================================================

-- Add a DSP effect to a track
function add_effect(track_idx, effect_path)
    -- effect_path is like "Audio/Effects/Native/Filter"
    local track = renoise.song().tracks[track_idx]
    return track:insert_device_at(effect_path, #track.devices + 1)
end

-- Set effect parameter
function set_effect_param(track_idx, device_idx, param_idx, value)
    local device = renoise.song().tracks[track_idx].devices[device_idx]
    device.parameters[param_idx].value = value
end

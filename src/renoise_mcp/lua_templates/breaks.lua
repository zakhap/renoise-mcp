-- Lua templates for break manipulation in Renoise
-- Specialized functions for chopping and manipulating breakbeats

-- =============================================================================
-- Break Chopping
-- =============================================================================

-- Chop a break into slices using sample offset commands
-- Assumes the break is loaded in instrument at inst_idx
function chop_break_basic(pattern_idx, track_idx, inst_idx, num_slices)
    num_slices = num_slices or 8
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local lines_per_slice = renoise.song():pattern(pattern_idx).number_of_lines / num_slices

    for i = 0, num_slices - 1 do
        local line = math.floor(i * lines_per_slice) + 1
        local nc = track:line(line):note_column(1)
        local fc = track:line(line):effect_column(1)

        nc.note_value = 48  -- C-4
        nc.instrument_value = inst_idx

        -- Sample offset: divide 256 by num_slices
        fc.number_string = "09"
        fc.amount_value = math.floor((i * 256) / num_slices)
    end
end

-- Shuffle/randomize slice order
function shuffle_break(pattern_idx, track_idx, inst_idx, num_slices)
    num_slices = num_slices or 8
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local pattern_length = renoise.song():pattern(pattern_idx).number_of_lines
    local lines_per_slice = pattern_length / num_slices

    -- Create shuffled order
    local order = {}
    for i = 0, num_slices - 1 do
        table.insert(order, i)
    end

    -- Fisher-Yates shuffle
    for i = #order, 2, -1 do
        local j = math.random(i)
        order[i], order[j] = order[j], order[i]
    end

    -- Write shuffled pattern
    for i = 0, num_slices - 1 do
        local line = math.floor(i * lines_per_slice) + 1
        local nc = track:line(line):note_column(1)
        local fc = track:line(line):effect_column(1)

        nc.note_value = 48
        nc.instrument_value = inst_idx

        fc.number_string = "09"
        fc.amount_value = math.floor((order[i + 1] * 256) / num_slices)
    end
end

-- Create a "drill" effect (rapid retrigger)
function drill_break(pattern_idx, track_idx, start_line, length, retrig_speed)
    retrig_speed = retrig_speed or 3
    local track = renoise.song():pattern(pattern_idx):track(track_idx)

    for i = 0, length - 1 do
        local line = start_line + i + 1
        local fc = track:line(line):effect_column(1)

        fc.number_string = "0R"
        -- Retrig format: xy where x=volume change (0=none), y=speed
        fc.amount_value = retrig_speed
    end
end

-- Add ghost notes to a break
function add_ghosts(pattern_idx, track_idx, inst_idx, probability, volume)
    probability = probability or 0.3
    volume = volume or 40
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local pattern_length = renoise.song():pattern(pattern_idx).number_of_lines

    for line = 1, pattern_length do
        local nc = track:line(line):note_column(1)

        -- Only add ghost if line is empty and random check passes
        if nc.note_value == 121 and math.random() < probability then
            nc.note_value = 48  -- C-4
            nc.instrument_value = inst_idx
            nc.volume_value = math.random(volume - 10, volume + 10)
        end
    end
end

-- =============================================================================
-- Break Transformations
-- =============================================================================

-- Reverse every other slice
function reverse_alternate(pattern_idx, track_idx)
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local pattern_length = renoise.song():pattern(pattern_idx).number_of_lines

    local slice_length = 4  -- Assuming 4 lines per slice
    local num_slices = pattern_length / slice_length

    for slice = 0, num_slices - 1 do
        if slice % 2 == 1 then  -- Every other slice
            local start_line = slice * slice_length + 1
            for i = 0, slice_length - 1 do
                local fc = track:line(start_line + i):effect_column(1)
                fc.number_string = "0B"  -- Reverse
                fc.amount_value = 0
            end
        end
    end
end

-- Add swing to hi-hats
function add_swing(pattern_idx, track_idx, swing_amount)
    swing_amount = swing_amount or 30  -- Delay in ticks (0-255)
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local pattern_length = renoise.song():pattern(pattern_idx).number_of_lines

    -- Add delay to off-beat hits (every other even line)
    for line = 1, pattern_length do
        if line % 4 == 3 then  -- Off-beat position
            local nc = track:line(line):note_column(1)
            if nc.note_value ~= 121 then  -- If there's a note
                nc.delay_value = swing_amount
            end
        end
    end
end

-- Half-time feel (only play every other hit)
function half_time(pattern_idx, track_idx)
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local pattern_length = renoise.song():pattern(pattern_idx).number_of_lines

    local hit_count = 0
    for line = 1, pattern_length do
        local nc = track:line(line):note_column(1)
        if nc.note_value ~= 121 then
            hit_count = hit_count + 1
            if hit_count % 2 == 0 then
                nc:clear()
            end
        end
    end
end

-- Double-time (double the hits)
function double_time(pattern_idx, track_idx, inst_idx)
    local track = renoise.song():pattern(pattern_idx):track(track_idx)
    local pattern_length = renoise.song():pattern(pattern_idx).number_of_lines

    for line = 1, pattern_length do
        local nc = track:line(line):note_column(1)
        if nc.note_value ~= 121 then
            -- Add retrigger to double the hit
            local fc = track:line(line):effect_column(1)
            fc.number_string = "0R"
            fc.amount_value = 0x08  -- Retrig at half speed
        end
    end
end

-- =============================================================================
-- Classic Break Patterns
-- =============================================================================

-- Write classic amen break pattern
function write_amen_classic(pattern_idx, track_idx, inst_idx)
    local track = renoise.song():pattern(pattern_idx):track(track_idx)

    -- Classic amen offsets for 8-slice chop
    local slices = {
        {line=1,  offset=0x00},  -- Kick
        {line=5,  offset=0x40},  -- Snare
        {line=7,  offset=0x20},  -- Kick ghost
        {line=9,  offset=0x00},  -- Kick
        {line=13, offset=0x40},  -- Snare
        {line=15, offset=0x60},  -- Hat
    }

    for _, s in ipairs(slices) do
        local nc = track:line(s.line):note_column(1)
        local fc = track:line(s.line):effect_column(1)

        nc.note_value = 48
        nc.instrument_value = inst_idx

        fc.number_string = "09"
        fc.amount_value = s.offset
    end
end

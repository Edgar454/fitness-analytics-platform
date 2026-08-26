local token_key = KEYS[1]
local lease_key = KEYS[2]

local now_ms = tonumber(ARGV[1])
local rate_limit = tonumber(ARGV[2])
local rate_window_ms = tonumber(ARGV[3])
local max_concurrent = tonumber(ARGV[4])
local lease_ttl_ms = tonumber(ARGV[5])
local lease_id = ARGV[6]

-- ============================================================
-- 1. Remove expired concurrency leases
-- ============================================================

redis.call(
    "ZREMRANGEBYSCORE",
    lease_key,
    "-inf",
    now_ms
)

local active = redis.call(
    "ZCARD",
    lease_key
)

-- ============================================================
-- 2. Refill token bucket
-- ============================================================

local state = redis.call(
    "HMGET",
    token_key,
    "tokens",
    "timestamp"
)

local tokens = tonumber(state[1])
local timestamp = tonumber(state[2])

if tokens == nil or timestamp == nil then
    tokens = rate_limit
    timestamp = now_ms
end

local elapsed = math.max(0, now_ms - timestamp)

local refill =
    (elapsed / rate_window_ms) * rate_limit

tokens = math.min(
    rate_limit,
    tokens + refill
)

timestamp = now_ms

-- ============================================================
-- 3. Check concurrency
-- ============================================================

if active >= max_concurrent then

    redis.call(
        "HMSET",
        token_key,
        "tokens",
        tokens,
        "timestamp",
        timestamp
    )

    -- Retry shortly.
    return {0, 100}
end

-- ============================================================
-- 4. Check rate limit
-- ============================================================

if tokens < 1 then

    local missing = 1 - tokens

    local wait_ms = math.ceil(
        missing * rate_window_ms / rate_limit
    )

    redis.call(
        "HMSET",
        token_key,
        "tokens",
        tokens,
        "timestamp",
        timestamp
    )

    return {0, wait_ms}
end

-- ============================================================
-- 5. Admission granted
-- ============================================================

tokens = tokens - 1

redis.call(
    "HMSET",
    token_key,
    "tokens",
    tokens,
    "timestamp",
    timestamp
)

-- ============================================================
-- 6. Create concurrency lease
-- ============================================================

local expiration = now_ms + lease_ttl_ms

redis.call(
    "ZADD",
    lease_key,
    expiration,
    lease_id
)

-- ============================================================
-- 7. Keep Redis keys from living forever
-- ============================================================

redis.call(
    "PEXPIRE",
    token_key,
    math.max(rate_window_ms * 2, 1000)
)

redis.call(
    "PEXPIRE",
    lease_key,
    lease_ttl_ms
)

return {1, lease_id}
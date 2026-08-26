local lease_key = KEYS[1]
local lease_id = ARGV[1]

redis.call(
    "ZREM",
    lease_key,
    lease_id
)

return 1
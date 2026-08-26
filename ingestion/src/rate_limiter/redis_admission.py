from __future__ import annotations

import asyncio
import time
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from redis.asyncio import Redis

from .models import AdmissionConfig, AdmissionLease,AdmissionTimeoutError


SCRIPTS_DIR = Path(__file__).parent / "scripts"

ACQUIRE_SCRIPT = (
    SCRIPTS_DIR / "acquire.lua"
).read_text()

RELEASE_SCRIPT = (
    SCRIPTS_DIR / "release.lua"
).read_text()


class RedisAdmissionController:
    """
    Distributed provider admission controller.

    Enforces:

    - provider-wide request rate
    - provider-wide concurrency

    Redis is the shared source of truth, allowing multiple
    workers/processes to participate in the same limits.
    """

    def __init__(
        self,
        redis: Redis,
        config: AdmissionConfig,
    ) -> None:
        self._redis = redis
        self._config = config

        self._token_key = (
            f"admission:{config.provider}:tokens"
        )

        self._lease_key = (
            f"admission:{config.provider}:leases"
        )

        self._acquire_script = self._redis.register_script(
            ACQUIRE_SCRIPT
        )

        self._release_script = self._redis.register_script(
            RELEASE_SCRIPT
        )

    
    @asynccontextmanager
    async def acquire(self, max_wait: float | None = None) -> AsyncIterator[AdmissionLease]:
        lease = await self._acquire(max_wait=max_wait)
        try:
            yield lease
        finally:
            await self._release(lease)

    async def _acquire(self, max_wait: float | None = None) -> AdmissionLease:
        lease_id = str(uuid.uuid4())
        rate_window_ms = int(self._config.rate_window.total_seconds() * 1000)
        lease_ttl_ms = int(self._config.lease_ttl.total_seconds() * 1000)

        deadline = time.monotonic() + max_wait if max_wait is not None else None

        while True:
            if deadline is not None and time.monotonic() >= deadline:
                raise AdmissionTimeoutError(
                    f"Timed out waiting for admission to provider {self._config.provider!r} after {max_wait}s"
                )

            now_ms = int(time.time() * 1000)
            result = await self._acquire_script(
                keys=[self._token_key, self._lease_key],
                args=[now_ms, self._config.rate_limit, rate_window_ms,
                    self._config.max_concurrent, lease_ttl_ms, lease_id],
            )

            admitted = int(result[0])
            if admitted == 1:
                return AdmissionLease(lease_id=lease_id)

            retry_after_ms = max(1, int(result[1]))
            jitter_ms = min(50, max(1, retry_after_ms // 10))
            sleep_s = (retry_after_ms + jitter_ms) / 1000

            if deadline is not None:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise AdmissionTimeoutError(
                        f"Timed out waiting for admission to provider {self._config.provider!r} after {max_wait}s"
                    )
                sleep_s = min(sleep_s, remaining)

            await asyncio.sleep(sleep_s)

    async def _release(
        self,
        lease: AdmissionLease,
    ) -> None:
        await self._release_script(
            keys=[self._lease_key],
            args=[lease.lease_id],
        )
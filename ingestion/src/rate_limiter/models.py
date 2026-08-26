from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True, slots=True)
class AdmissionConfig:
    """
    Limits applied to a single external provider.

    rate_limit:
        Maximum number of requests allowed during rate_window.

    max_concurrent:
        Maximum number of requests that may be in flight simultaneously.

    lease_ttl:
        Maximum lifetime of a concurrency lease. This protects against
        abandoned leases when a worker crashes.
    """

    provider: str
    rate_limit: int
    rate_window: timedelta
    max_concurrent: int
    lease_ttl: timedelta = timedelta(hours=1)

    def __post_init__(self) -> None:
        if self.rate_limit <= 0:
            raise ValueError("rate_limit must be greater than zero")

        if self.max_concurrent <= 0:
            raise ValueError("max_concurrent must be greater than zero")

        if self.rate_window.total_seconds() <= 0:
            raise ValueError("rate_window must be greater than zero")

        if self.lease_ttl.total_seconds() <= 0:
            raise ValueError("lease_ttl must be greater than zero")


@dataclass(frozen=True, slots=True)
class AdmissionLease:
    """
    Represents a successfully admitted external request.

    The lease_id is used to release the concurrency slot after the
    request finishes.
    """

    lease_id: str

class AdmissionTimeoutError(TimeoutError):
    """Raised when acquire() couldn't obtain a lease within max_wait."""
from datetime import timedelta

from ingestion.src.rate_limiter.models import AdmissionConfig


ADMISSION_CONFIGS = {
    "google_health": AdmissionConfig(
        provider="google_health",
        rate_limit=10,
        rate_window=timedelta(seconds=1),
        max_concurrent=5,
    ),
    "fatsecret": AdmissionConfig(
        provider="fatsecret",
        rate_limit=8,
        rate_window=timedelta(seconds=1),
        max_concurrent=4,
    ),
    "lyfta": AdmissionConfig(
        provider="lyfta",
        rate_limit=6,
        rate_window=timedelta(seconds=1),
        max_concurrent=3,
    ),
}
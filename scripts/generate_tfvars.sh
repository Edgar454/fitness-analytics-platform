#!/usr/bin/env bash

set -euo pipefail

OUTPUT_FILE="${1:-terraform/terraform.tfvars}"

mkdir -p "$(dirname "$OUTPUT_FILE")"

cat > "$OUTPUT_FILE" <<EOF
region = "${AWS_REGION:-eu-west-1}"
project_name = "sportfolio"

bucket_name = "edgar-fitness-terraform-state"
progress_photo_bucket_name = "edgar-fitness-progess-photos"

alert_email = "mevaed4@gmail.com"
load_test_enabled = ${LOAD_TEST_:-false}

# Lambda
lambda_zip_path = "${LAMBDA_ZIP_PATH:-}"

active_user_window_days = ${ACTIVE_USER_WINDOW_DAYS:-30}

# cache
redis_url = "${REDIS_URL:-}"

# Database
database_host     = "${DATABASE_HOST:-}"
db_user           = "${DB_USER:-}"
database_password = "${DATABASE_PASSWORD:-}"
cert_path         = "${CERT_PATH:-}"
EOF

echo "Generated $OUTPUT_FILE"
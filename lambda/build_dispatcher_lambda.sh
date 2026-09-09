#!/bin/bash

set -e

PACKAGE_DIR="lambda_package"
ZIP_FILE="dispatcher.zip"

echo "Cleaning previous build..."
rm -rf "$PACKAGE_DIR" "$ZIP_FILE"

echo "Creating package directory..."
mkdir -p "$PACKAGE_DIR"

echo "Installing dependencies..."
pip install \
    -r lambda/lambda_requirements.txt \
    -t "$PACKAGE_DIR"

echo "Copying application code..."
cp -r ingestion "$PACKAGE_DIR/"

echo "Copying Lambda handler..."
cp lambda/dispatcher_handler.py "$PACKAGE_DIR/handler.py"

echo "Creating ZIP..."
cd "$PACKAGE_DIR"
zip -r "../$ZIP_FILE" .
cd ..

echo "Cleaning temporary files..."
rm -rf "$PACKAGE_DIR"

echo "Lambda package created: $ZIP_FILE"
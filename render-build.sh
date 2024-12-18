#!/usr/bin/env bash

# Update package list
apt-get update

# Install Tesseract OCR and its dependencies
apt-get install -y tesseract-ocr libtesseract-dev
sudo apt-get install libzbar0
# Install Python dependencies
pip install -r requirements.txt

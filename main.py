from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import create_engine, text
from werkzeug.security import generate_password_hash, check_password_hash
import ast
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import uuid
from datetime import datetime, date, timedelta
from collections import defaultdict
from fuzzywuzzy import fuzz
import pytesseract
from PIL import Image
import re
import random
import easyocr

app = Flask(__name__)
CORS(app)
@app.route('/manageLabel', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        image_file = request.files.get('image')
        print(image_file)
        if not image_file:
            return jsonify({'error': 'No image file provided.'}), 400
    
    detected_text = perform_ocr(image_file)
    on_ing = False
    ingredients = []
    for d in detected_text.split(' '):
        if on_ing:
            ingredients.append(d)
        score = fuzz.ratio(d, 'INGREDIENTS')
        if score > 85:
            on_ing = True
        if on_ing and "." in d:
            on_ing = False
    print(ingredients)
    if detected_text:
        nutritional_values = parse_nutritional_values(detected_text)
        ingredients = parse_ingredients(detected_text)

        print("Nutritional Values:", nutritional_values)
        print("Ingredients:", ingredients)
    
def parse_nutritional_values(text):
    patterns = {
        "serving_size": r"serving size.*?(\d+.*?[gml])",
        "calories": r"calories\s+(\d+)",
        "total_fat": r"total fat.*?(\d+g)",
        "saturated_fat": r"saturated fat.*?(\d+g)",
        "cholesterol": r"cholesterol.*?(\d+mg)",
        "sodium": r"sodium.*?(\d+mg)",
        "total_carbohydrate": r"total carbohydrate.*?(\d+g)",
        "dietary_fiber": r"dietary fiber.*?(\d+g)",
        "total_sugars": r"total sugars.*?(\d+g)",
        "added_sugars": r"added sugars.*?(\d+g).*?(\d+%)",
        "protein": r"protein.*?(\d+g)",
        "vitamin_d": r"vitamin d.*?(\d+mcg)",
        "calcium": r"calcium.*?(\d+mg)",
        "iron": r"iron.*?(\d+mg)",
        "potassium": r"potassium.*?(\d+mg)",
        "vitamin_a": r"vitamin a.*?(\d+%)",
        "vitamin_c": r"vitamin c.*?(\d+%)",
        "vitamin_b6": r"vitamin b6.*?(\d+%)",
        "folic_acid": r"folic acid.*?(\d+mcg)",
        "magnesium": r"magnesium.*?(\d+mg)",
        "zinc": r"zinc.*?(\d+mg)"
    }

    nutritional_values = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            nutritional_values[key] = match.group(1)
    return nutritional_values

def parse_ingredients(text):
    match = re.search(r"ingredients[:\s]+([a-zA-Z0-9,.\s]+)", text, re.IGNORECASE)
    if match:
        ingredients = match.group(1).strip()
        return ingredients
    return None

def perform_ocr(image_path):
    reader = easyocr.Reader(['en'], gpu=True)
    result = reader.readtext(image_path)
    text = ' '.join([r[1] for r in result])
    return text

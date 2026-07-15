import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Initialize the Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    if not client:
        return jsonify({"error": "Groq API Key is missing. Please verify your .env file layout."}), 500

    data = request.json or {}
    product_name = data.get('product_name', 'Product')
    product_description = data.get('product_description', '')
    audience = data.get('audience', 'General public')
    usps = data.get('usps', '')
    variations = int(data.get('variations', 2))
    tone = data.get('tone', 'professional')
    platforms = data.get('platforms', ['instagram'])

    # Strict system architecture prompt formatting to feed the UI canvas structures
    system_prompt = (
        "You are an expert programmatic ad copywriter. You must output a raw, valid JSON object ONLY. "
        "Do not wrap your response in markdown blocks like ```json ... ```. No conversational filler text. "
        "Your output must strictly follow this exact schema layout:\n\n"
        "{\n"
        "  \"slogans\": [\"Slogan Line 1\", \"Slogan Line 2\"],\n"
        "  \"ad_variations\": {\n"
        "    \"instagram\": [\n"
        "      { \"emoji_caption\": \"...\", \"hook\": \"...\", \"hashtags\": [\"tag1\", \"tag2\"], \"cta_text\": \"...\" }\n"
        "    ],\n"
        "    \"google\": [\n"
        "      { \"headlines\": [\"Headline 1\"], \"descriptions\": [\"Description text block\"] }\n"
        "    ],\n"
        "    \"facebook\": [\n"
        "      { \"primary_text\": \"...\", \"headline\": \"...\", \"link_description\": \"...\", \"social_proof_angle\": \"...\" }\n"
        "    ]\n"
        "  },\n"
        "  \"performance_tips\": [\"Optimization tip 1\", \"Optimization tip 2\"]\n"
        "}\n\n"
        f"Only generate components for these specific requested platforms: {', '.join(platforms)}. "
        f"Generate exactly {variations} separate variations per requested platform using a {tone} tone profile."
    )

    user_prompt = f"Product: {product_name}\nContext: {product_description}\nAudience: {audience}\nUSPs: {usps}"

    try:
        # Request strict JSON output formatting using the upgraded LLaMA 3.3 model
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )

        raw_response = completion.choices[0].message.content.strip()
        parsed_response = json.loads(raw_response)

        # CRITICAL LAYER: Injecting the metadata object expected by the UI script
        parsed_response["metadata"] = {
            "product_name": product_name,
            "tone": tone,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        return jsonify(parsed_response)

    except Exception as e:
        return jsonify({"error": f"Inference pipeline execution failure: {str(e)}"}), 500

@app.route('/api/refine', methods=['POST'])
def refine():
    if not client:
        return jsonify({"error": "Groq API Key is missing."}), 500

    data = request.json or {}
    original_copy = data.get('original_copy', '')
    feedback = data.get('feedback', '')
    platform = data.get('platform', 'instagram')
    tone = data.get('tone', 'professional')

    system_prompt = (
        "You are an expert copy editor. Output a raw, valid JSON object ONLY. Do not use markdown wraps. "
        "Structure format:\n"
        "{\n"
        "  \"refined_text\": \"Your revised, polished output content string goes here.\",\n"
        "  \"changes_made\": [\"Action log statement 1\", \"Action log statement 2\"]\n"
        "}"
    )

    user_prompt = f"Target Platform: {platform}\nTarget Tone: {tone}\nOriginal Content:\n{original_copy}\n\nDirectives: {feedback}"

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        return jsonify(json.loads(completion.choices[0].message.content.strip()))
    except Exception as e:
        return jsonify({"error": f"Refinery pipeline error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
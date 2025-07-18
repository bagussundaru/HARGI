from flask import Blueprint, request, jsonify
import pandas as pd
from src.config import Config
import json
import re
from datetime import datetime
import requests

chatbot_bp = Blueprint('chatbot', __name__)

# Konfigurasi Nebius AI API
NEBIUS_API_KEY = "eyJhbGciOiJIUzI1NiIsImtpZCI6IlV6SXJWd1h0dnprLVRvdzlLZWstc0M1akptWXBvX1VaVkxUZlpnMDRlOFUiLCJ0eXAiOiJKV1QifQ.eyJzdWIiOiJnb29nbGUtb2F1dGgyfDExNDE3OTYwNTEwMjcyNDQ2MjIxNyIsInNjb3BlIjoib3BlbmlkIG9mZmxpbmVfYWNjZXNzIiwiaXNzIjoiYXBpX2tleV9pc3N1ZXIiLCJhdWQiOlsiaHR0cHM6Ly9uZWJpdXMtaW5mZXJlbmNlLmV1LmF1dGgwLmNvbS9hcGkvdjIvIl0sImV4cCI6MTkxMDQ4OTk5NywidXVpZCI6ImRiYTFiMzM5LWUzYTctNGE0Zi04ODVjLWIzNTc2ZTIxMzM0MiIsIm5hbWUiOiJjaGF0Ym90IiwiZXhwaXJlc19hdCI6IjIwMzAtMDctMTdUMDM6Mzk6NTcrMDAwMCJ9.SsDwbCSdA2iA8elng2j5pCjpJJIdmBFW4h5juK1sY7U"
NEBIUS_API_URL = "https://api.studio.nebius.ai/v1/chat/completions"
NEBIUS_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct"

def call_nebus_ai(prompt, context_data=None):
    """
    Panggilan ke Nebius AI API dengan model Meta-Llama-3.1-70B-Instruct
    """
    try:
        # Siapkan konteks data untuk AI
        context_info = ""
        if context_data is not None and not context_data.empty:
            # Buat ringkasan data untuk konteks AI
            total_projects = len(context_data)
            context_info = f"Data HAR GI tersedia dengan {total_projects} proyek. "
            
            if 'STATUS' in context_data.columns:
                status_counts = context_data['STATUS'].value_counts().to_dict()
                context_info += f"Status: {dict(list(status_counts.items())[:3])}. "
            
            if 'LOKASI' in context_data.columns:
                lokasi_counts = context_data['LOKASI'].value_counts().head(3).to_dict()
                context_info += f"Top lokasi: {dict(list(lokasi_counts.items())[:3])}. "
        
        # Buat system prompt untuk AI
        system_prompt = f"""Anda adalah asisten AI untuk Dashboard HAR GI (Hasil Akhir Rencana Gardu Induk) PLN. 
Anda membantu menganalisis data proyek gardu induk.

{context_info}

Jawab pertanyaan user dengan informatif dan akurat berdasarkan data yang tersedia. 
Gunakan bahasa Indonesia yang profesional dan mudah dipahami.
Jika data tidak tersedia, berikan penjelasan yang membantu."""
        
        # Siapkan payload untuk API Nebius
        payload = {
            "model": NEBIUS_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        # Headers untuk API request
        headers = {
            "Authorization": f"Bearer {NEBIUS_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Panggil API Nebius
        response = requests.post(NEBIUS_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            return ai_response.strip()
        else:
            # Fallback jika API gagal
            return f"Maaf, layanan AI sedang tidak tersedia. Status: {response.status_code}"
    
    except requests.exceptions.Timeout:
        return "Maaf, permintaan timeout. Silakan coba lagi."
    except requests.exceptions.RequestException as e:
        return f"Maaf, terjadi kesalahan koneksi: {str(e)}"
    except Exception as e:
        return f"Maaf, terjadi kesalahan dalam memproses pertanyaan Anda: {str(e)}"

def load_excel_data_for_chatbot():
    """
    Load Excel data untuk analisis chatbot
    """
    try:
        excel_file = Config.find_excel_file()
        if excel_file:
            df = pd.read_excel(excel_file, sheet_name='REALISASI HAR GI', header=4)
            # Clean column names
            df.columns = df.columns.str.strip()
            return df
        else:
            # Return sample data jika Excel tidak ditemukan
            return pd.DataFrame({
                'RENCANA': ['2024-01-15', '2024-02-20', '2024-03-10'],
                'LOKASI': ['Jakarta', 'Bandung', 'Surabaya'],
                'STATUS': ['Selesai', 'Dalam Proses', 'Perencanaan'],
                'KATEGORI': ['Pembangunan', 'Pemeliharaan', 'Upgrade']
            })
    except Exception as e:
        print(f"Error loading Excel data: {e}")
        return None

@chatbot_bp.route('/api/chatbot', methods=['POST'])
def chatbot_response():
    """
    Endpoint untuk menerima pesan dari user dan memberikan respons AI
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Pesan tidak boleh kosong'
            }), 400
        
        # Load data Excel untuk konteks
        excel_data = load_excel_data_for_chatbot()
        
        # Panggil Nebus AI (simulasi)
        ai_response = call_nebus_ai(user_message, excel_data)
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Terjadi kesalahan: {str(e)}'
        }), 500

@chatbot_bp.route('/api/chatbot/suggestions', methods=['GET'])
def get_suggestions():
    """
    Endpoint untuk memberikan saran pertanyaan
    """
    suggestions = [
        "Berapa total proyek HAR GI?",
        "Bagaimana status proyek saat ini?",
        "Lokasi mana yang memiliki proyek terbanyak?",
        "Berapa proyek yang selesai tahun ini?",
        "Apa saja kategori proyek yang ada?",
        "Proyek mana yang sedang dalam proses?"
    ]
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })
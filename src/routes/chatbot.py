from flask import Blueprint, request, jsonify
import pandas as pd
from src.config import Config
import json
import re
from datetime import datetime
import requests

chatbot_bp = Blueprint('chatbot', __name__)

import os

# Konfigurasi Nebius AI API - menggunakan environment variable untuk keamanan
NEBIUS_API_KEY = os.getenv('NEBIUS_API_KEY')
NEBIUS_API_URL = "https://api.studio.nebius.ai/v1/chat/completions"
NEBIUS_MODEL = "meta-llama/Meta-Llama-3.1-70B-Instruct"

def call_nebus_ai(prompt, context_data=None):
    """
    Panggilan ke Nebius AI API dengan model Meta-Llama-3.1-70B-Instruct
    """
    try:
        # Validasi API key
        if not NEBIUS_API_KEY:
            return "Maaf, layanan chatbot sedang tidak tersedia. API key tidak dikonfigurasi."
        # Siapkan konteks data untuk AI
        context_info = ""
        if context_data is not None and not context_data.empty:
            # Buat ringkasan data untuk konteks AI
            total_projects = len(context_data)
            context_info = f"Data HAR GI tersedia dengan {total_projects} proyek. "
            
            if 'STATUS' in context_data.columns:
                status_counts = context_data['STATUS'].value_counts().to_dict()
                context_info += f"Status: {dict(list(status_counts.items())[:5])}. "
            
            if 'LOKASI GI / GIS / GITET' in context_data.columns:
                lokasi_counts = context_data['LOKASI GI / GIS / GITET'].value_counts().head(5).to_dict()
                context_info += f"Top lokasi: {dict(list(lokasi_counts.items())[:5])}. "
            
            if 'TAHUN' in context_data.columns:
                tahun_counts = context_data['TAHUN'].value_counts().to_dict()
                context_info += f"Distribusi tahun: {dict(list(tahun_counts.items())[:3])}. "
            
            if 'KATEGORI' in context_data.columns:
                kategori_counts = context_data['KATEGORI'].value_counts().head(3).to_dict()
                context_info += f"Kategori: {dict(list(kategori_counts.items())[:3])}. "
            
            if 'SUB BIDANG' in context_data.columns:
                sub_bidang_counts = context_data['SUB BIDANG'].value_counts().to_dict()
                context_info += f"Sub bidang: {dict(list(sub_bidang_counts.items())[:3])}. "
        
        # Buat system prompt untuk AI
        system_prompt = f"""Anda adalah asisten AI untuk Dashboard HAR GI (Hasil Akhir Rencana Gardu Induk) PLN. 
Anda membantu menganalisis data proyek gardu induk dengan informasi berikut:

{context_info}

Anda dapat menjawab pertanyaan tentang:
- Total proyek dan distribusi status (SELESAI/BELUM SELESAI)
- Lokasi gardu induk (kolom: LOKASI GI / GIS / GITET)
- Distribusi proyek per tahun (kolom: TAHUN)
- Kategori pekerjaan (kolom: KATEGORI)
- Sub bidang (kolom: SUB BIDANG)
- Sifat pekerjaan (kolom: SIFAT PEKERJAAN)
- Analisis timeline rencana vs realisasi

Jawab dengan data spesifik dan angka yang akurat. Gunakan bahasa Indonesia yang profesional.
Jika user menanyakan data yang tidak tersedia, jelaskan kolom data apa saja yang tersedia."""
        
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
            
            # Clean data - remove rows with all NaN values
            df = df.dropna(how='all')
            
            # Convert date columns if they exist
            if 'RENCANA' in df.columns:
                df['RENCANA'] = pd.to_datetime(df['RENCANA'], errors='coerce')
            if 'REALISASI' in df.columns:
                df['REALISASI'] = pd.to_datetime(df['REALISASI'], errors='coerce')
            
            # Clean text columns
            text_columns = ['LOKASI GI / GIS / GITET', 'STATUS', 'KATEGORI', 'SUB BIDANG', 'SIFAT PEKERJAAN']
            for col in text_columns:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.upper()
            
            print(f"Successfully loaded {len(df)} records from Excel")
            return df
        else:
            print("Excel file not found, using sample data")
            # Return sample data jika Excel tidak ditemukan
            return pd.DataFrame({
                'RENCANA': ['2024-01-15', '2024-02-20', '2024-03-10'],
                'LOKASI GI / GIS / GITET': ['GI JAKARTA', 'GI BANDUNG', 'GI SURABAYA'],
                'STATUS': ['SELESAI', 'BELUM SELESAI', 'SELESAI'],
                'KATEGORI': ['BAY PHT PHT', 'BAY BAY TRAFO', 'BAY PHT PHT'],
                'TAHUN': [2024, 2024, 2024],
                'SUB BIDANG': ['HARGI', 'HARGI', 'HARGI']
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
        # Validate request
        if not request.is_json:
            return jsonify({
                'success': False,
                'error': 'Request harus berformat JSON'
            }), 400
        
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Pesan tidak boleh kosong'
            }), 400
        
        print(f"Chatbot request: {user_message}")
        
        # Load data Excel untuk konteks
        excel_data = load_excel_data_for_chatbot()
        
        if excel_data is None:
            return jsonify({
                'success': False,
                'error': 'Gagal memuat data Excel. Silakan coba lagi.'
            }), 500
        
        # Panggil Nebius AI
        ai_response = call_nebus_ai(user_message, excel_data)
        
        print(f"AI response: {ai_response[:100]}...")
        
        return jsonify({
            'success': True,
            'response': ai_response,
            'timestamp': datetime.now().isoformat(),
            'data_info': {
                'total_records': len(excel_data) if excel_data is not None else 0,
                'columns_available': list(excel_data.columns) if excel_data is not None else []
            }
        })
    
    except Exception as e:
        print(f"Chatbot error: {str(e)}")
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
        "Bagaimana distribusi status proyek (selesai vs belum selesai)?",
        "Lokasi GI mana yang memiliki proyek terbanyak?",
        "Bagaimana distribusi proyek per tahun?",
        "Apa saja kategori pekerjaan yang tersedia?",
        "Berapa proyek yang ditangani sub bidang HARGI?",
        "Apa saja sifat pekerjaan yang ada?",
        "Berapa proyek yang sudah selesai di tahun 2024?",
        "Lokasi mana saja yang ada proyek gardu induk?",
        "Bagaimana perbandingan rencana vs realisasi proyek?"
    ]
    
    return jsonify({
        'success': True,
        'suggestions': suggestions
    })
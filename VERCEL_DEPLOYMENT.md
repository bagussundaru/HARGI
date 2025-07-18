# Vercel Deployment Guide untuk HAR GI Dashboard

## 🚨 Masalah yang Ditemukan dan Solusi

### 1. **API Key Security Issue**
**Masalah:** API key Nebius AI di-hardcode dalam kode (SANGAT BERBAHAYA!)
**Solusi:** Dipindahkan ke environment variable

### 2. **Environment Variables yang Diperlukan**
Untuk deployment Vercel yang sukses, Anda HARUS mengatur environment variables berikut di Vercel Dashboard:

```
PYTHONPATH=src
FLASK_DEBUG=false
SECRET_KEY=production-secret-key-hargi-dashboard-2024
CORS_ORIGINS=*
EXCEL_FILE_PATH=./DASHBOARDHARGI.xlsx
NEBIUS_API_KEY=your-actual-nebius-api-key-here
```

### 3. **Langkah Deployment**

#### A. Setup Environment Variables di Vercel
1. Buka Vercel Dashboard
2. Pilih project HAR GI
3. Masuk ke Settings > Environment Variables
4. Tambahkan semua environment variables di atas
5. **PENTING:** Ganti `NEBIUS_API_KEY` dengan API key yang sebenarnya

#### B. Deploy
1. Push kode ke GitHub
2. Vercel akan otomatis deploy
3. Pastikan tidak ada error di build logs

### 4. **File yang Diperbaiki**
- `src/routes/chatbot.py` - API key dipindahkan ke env var
- `api/index.py` - Error handling untuk import
- `vercel.json` - Environment variables configuration
- `runtime.txt` - Python version update
- `.env.example` - Documentation untuk env vars

### 5. **Troubleshooting**

#### Error 500 FUNCTION_INVOCATION_FAILED
**Penyebab umum:**
- Environment variables tidak diset
- API key tidak valid
- Import error
- File Excel tidak ditemukan

**Solusi:**
1. Cek Vercel Function Logs
2. Pastikan semua env vars sudah diset
3. Validasi API key Nebius
4. Pastikan file DASHBOARDHARGI.xlsx ada di root project

#### Debugging
```bash
# Local testing
cp .env.example .env
# Edit .env dengan nilai yang benar
python src/main.py
```

### 6. **Security Best Practices**
- ✅ API keys di environment variables
- ✅ Secret key untuk production
- ✅ CORS configuration
- ✅ Debug mode disabled di production

### 7. **Monitoring**
Setelah deployment:
1. Test semua endpoints
2. Monitor Vercel Function Logs
3. Test chatbot functionality
4. Verify Excel data loading

---

**⚠️ CRITICAL:** Jangan pernah commit API keys ke repository!
**✅ SOLUTION:** Selalu gunakan environment variables untuk credentials.
import os

class Config:
    # Excel file path - will use environment variable in production
    EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'D:\\DASHBOARDHARGI.xlsx')
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
import os

class Config:
    # Excel file path - will use environment variable in production
    EXCEL_FILE_PATH = os.getenv('EXCEL_FILE_PATH', 'D:\\DASHBOARDHARGI.xlsx')
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    
    @staticmethod
    def find_excel_file():
        """Dynamically find Excel file in multiple locations"""
        possible_paths = [
            Config.EXCEL_FILE_PATH,  # Default configured path
            'DASHBOARDHARGI.xlsx',  # Project root (for Vercel)
            './DASHBOARDHARGI.xlsx',  # Relative path (for Vercel)
            'D:\\DASHBOARDHARGI.xlsx',  # Primary location (local)
            'D:\\DASHBOARDHARGI2.xlsx',  # Alternative location (local)
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'DASHBOARDHARGI.xlsx'),  # Project root
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'DASHBOARDHARGI2.xlsx'),  # Project root alternative
            os.path.join(os.getcwd(), 'DASHBOARDHARGI.xlsx'),  # Current working directory
            os.path.join(os.getcwd(), 'DASHBOARDHARGI2.xlsx'),  # Current working directory alternative
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    @staticmethod
    def set_excel_path(new_path):
        """Set new Excel file path dynamically"""
        if os.path.exists(new_path):
            Config.EXCEL_FILE_PATH = new_path
            return True
        return False
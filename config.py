import os

class Config:
    # Azure OpenAI Configuration
    AZURE_OPENAI_API_KEY = os.environ.get('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_ENDPOINT = os.environ.get('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_VERSION = os.environ.get('AZURE_OPENAI_API_VERSION', '2024-12-01-preview')
    AZURE_OPENAI_DEPLOYMENT_NAME = os.environ.get('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-35-turbo')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'xlsx', 'xls', 'csv'}
    
    # Data Source Configuration
    FACTSET_API_KEY = os.environ.get('FACTSET_API_KEY')
    XPRESSFEED_API_KEY = os.environ.get('XPRESSFEED_API_KEY')
    
    # Notification Configuration
    NOTIFICATION_WEBHOOK_URL = os.environ.get('NOTIFICATION_WEBHOOK_URL')
    EMAIL_SMTP_SERVER = os.environ.get('EMAIL_SMTP_SERVER')
    EMAIL_SMTP_PORT = os.environ.get('EMAIL_SMTP_PORT', 587)
    EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    # Monitoring Configuration
    SIGNAL_CHECK_INTERVAL = int(os.environ.get('SIGNAL_CHECK_INTERVAL', 300))  # 5 minutes
    PRICE_CHANGE_THRESHOLD = float(os.environ.get('PRICE_CHANGE_THRESHOLD', 0.05))  # 5%
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

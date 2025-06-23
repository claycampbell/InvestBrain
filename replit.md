# Investment Thesis Intelligence System

## Overview

The Investment Thesis Intelligence System is a sophisticated Flask-based web application designed to analyze, monitor, and validate investment theses using advanced AI capabilities. The system processes investment statements, extracts actionable signals, and provides real-time monitoring with comprehensive analytics.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.1 with SQLAlchemy 2.0 ORM
- **Database**: SQLite for development, PostgreSQL-ready for production
- **AI Integration**: Azure OpenAI API for thesis analysis and signal extraction
- **External APIs**: FactSet and Xpressfeed for market data, Eagle API for financial metrics
- **Deployment**: Gunicorn WSGI server with autoscale deployment target

### Frontend Architecture  
- **UI Framework**: Bootstrap 5.3 with dark theme support
- **Visualization**: ApexCharts for financial data visualization
- **Interactivity**: Vanilla JavaScript with Chart.js integration
- **Theme Support**: Dynamic light/dark mode switching

### Data Processing Pipeline
- **Document Processing**: Support for PDF, Excel (xlsx/xls), and CSV file uploads
- **Signal Classification**: 6-level hierarchical signal system (Level 0-5)
- **Monitoring System**: Real-time signal tracking with configurable thresholds
- **Analytics Engine**: Advanced performance scoring and thesis evaluation

## Key Components

### Core Services
1. **Thesis Analyzer**: AI-powered investment thesis decomposition and analysis
2. **Signal Classifier**: Multi-level signal extraction and categorization system
3. **Chained Analysis Service**: Sequential prompt-based analysis for improved reliability
4. **Document Processor**: Automated research document analysis and integration
5. **Azure OpenAI Service**: Centralized AI API management with retry logic
6. **Data Adapter Service**: External data source integration and management

### Monitoring and Analytics
1. **Signal Monitoring**: Real-time tracking of thesis validation signals
2. **Advanced Analytics**: Performance scoring, pattern recognition, and insights
3. **Backtesting Service**: Historical validation against market scenarios
4. **Simulation Service**: Forward-looking thesis performance modeling
5. **Alternative Company Service**: AI-powered discovery of comparable investments

### Data Management
1. **Metric Selector**: Intelligent financial metric selection for analysis
2. **Data Registry**: Centralized data source management and prioritization
3. **Sparkline Service**: Micro-chart generation for key performance indicators
4. **Query Parser**: Structured financial query processing for Level 0 signals

## Data Flow

1. **Input Processing**: Users submit investment thesis text and optional research documents
2. **AI Analysis**: Azure OpenAI processes thesis through chained analysis workflow:
   - Core claim extraction
   - Assumption identification
   - Mental model classification
   - Signal generation
3. **Signal Classification**: Extracted signals are categorized into 6 hierarchical levels
4. **Monitoring Setup**: System establishes real-time monitoring for key signals
5. **Analytics Generation**: Performance metrics and insights are calculated
6. **Dashboard Display**: Results presented through interactive web interface

## External Dependencies

### AI Services
- **Azure OpenAI**: Primary AI analysis engine (GPT models)
- API endpoint, key, and deployment name configured via environment variables

### Financial Data APIs
- **FactSet API**: Primary financial data source (priority 1)
- **Xpressfeed API**: Secondary data source (priority 2)  
- **Eagle API**: Alternative metrics and research data
- Graceful fallback to test data when APIs unavailable

### Infrastructure
- **PostgreSQL 16**: Production database with connection pooling
- **Gunicorn**: Production WSGI server with auto-scaling
- **Replit Environment**: Development and deployment platform

## Deployment Strategy

### Development Environment
- **Platform**: Replit with Nix package management
- **Database**: SQLite with automatic schema creation
- **Hot Reload**: Gunicorn with reload flag for development
- **Port Configuration**: Internal 5000, external 80

### Production Deployment
- **Target**: Autoscale deployment with Gunicorn
- **Process Management**: Multi-worker configuration
- **Health Checks**: Port monitoring on 5000
- **Environment**: Stable Nix channel 24_05

### Configuration Management
- Environment-based configuration with development/production modes
- Secure secret management for API keys and tokens
- Graceful degradation when external services unavailable

## Changelog
- June 23, 2025: Completed Eagle API Integration with Mock Data Support
  - Fixed Eagle API data integration in analysis dashboard
  - Resolved data type handling issues in signal processing 
  - Enhanced signal classification to handle mixed data formats
  - Eagle API signals now properly appear in "Internal Research Data" section
  - System uses EAGLE_API_TOKEN environment variable when available, gracefully falls back to mock data
- June 23, 2025: Added Significance Mapping and Smart Prioritization features
  - Implemented AI-powered research vs signal analysis
  - Created visual mapping dashboard for thesis connections
  - Added priority matrix and actionable insights system
- June 23, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.
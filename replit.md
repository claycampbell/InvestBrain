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
- June 25, 2025: Complete Core Directory Dependency Removal 
  - Eliminated ALL core directory dependencies from routes.py and entire system
  - Updated Eagle metrics service to use Azure OpenAI directly instead of core directory LLMManager
  - Fixed routes.py to import services directly instead of through core directory
  - Configured Azure OpenAI service with proper timeouts (30s) and retry logic for reliability
  - ReliableAnalysisService operates as primary analysis mechanism without core dependencies
  - System attempts genuine AI analysis first before any fallback mechanisms
  - Primary flow: ReliableAnalysisService → Azure OpenAI (extended timeout) → Eagle API → database storage
  - Eagle API integration extracts authentic metrics from 155+ available financial metrics
  - All services now operate independently without core directory coupling
  - Analysis workflow generates AI-powered insights and saves complete results to database
- June 25, 2025: Established ReliableAnalysisService as Primary Analysis Mechanism
  - Made ReliableAnalysisService the main analysis pathway instead of replacement for fallback
  - Primary flow: ReliableAnalysisService → Azure OpenAI → Eagle API → authentic data processing
  - Fallback only triggers for authentication errors or complete system failures
  - Removed fallback-first logic, ensuring authentic data sources are always attempted first
  - Enhanced error handling to distinguish between network issues and authentication problems
  - System prioritizes real data from Azure OpenAI and Eagle API over synthetic alternatives
  - Comprehensive analysis includes company identification, metrics extraction, and monitoring setup
- June 24, 2025: Completed Centralized Architecture Refactoring with Network-Resilient Analysis
  - Created core/llm_manager.py for centralized AI operations with comprehensive fallback mechanisms
  - Built core/analysis_engine.py for business logic orchestration and workflow management  
  - Implemented core/data_manager.py for unified external service connections and data access
  - Refactored main analysis endpoints to use new three-layer architecture
  - Added structured fallback responses for all AI operations when Azure OpenAI is unavailable
  - Implemented aggressive timeout handling (2 seconds) with immediate fallback activation
  - System successfully provides complete thesis analysis even during Azure OpenAI network timeouts
  - Verified functionality: Analysis workflow generates meaningful results with fallback mode activated
  - Basic endpoints (home, monitoring, analytics) load instantly without AI dependencies
  - End-to-end analysis flow functional with proper database integration and monitoring setup
- June 23, 2025: Enhanced Significance Analysis Reliability
  - Implemented robust fallback mechanisms for Azure OpenAI connection failures
  - Added comprehensive error handling and logging throughout analysis pipeline
  - Created keyword-based connection analysis as backup method for significance mapping
  - Enhanced smart prioritization with deterministic fallback algorithms
  - System now provides meaningful analysis even when AI services are temporarily unavailable
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
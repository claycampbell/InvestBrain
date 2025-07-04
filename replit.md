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
- June 27, 2025: Enhanced Dynamic Analysis Generation System - COMPLETED
  - Implemented contextual analysis system generating sector-specific content instead of static fallback data
  - Added travel-specific counter-thesis scenarios (Travel Demand Disruption, Platform Disintermediation)
  - Created comprehensive alternative company analysis with detailed investment metrics
  - Built sector-based content generation for Travel & Tourism, Technology, Financial Services, Healthcare, Energy, Consumer & Retail
  - Enhanced causal chain events with sector-specific catalysts and explanations
  - Generated contextual assumptions based on company and sector characteristics
  - Integrated dynamic content generation into main analysis workflow
  - Counter-thesis scenarios now include specific trigger conditions and data signals for monitoring
  - Alternative company analysis includes similarity scores, rationale, investment merit, and growth profiles
  - System successfully generates travel-specific content for Expedia analysis with 3 detailed alternatives
- June 27, 2025: Major restructuring: Thesis Validation Framework for One Pager Generation - COMPLETED
  - Replaced composite metrics with specific validation components in one pager reports
  - Implemented Core Claim Validation Framework with primary/supporting/contrarian validators
  - Added Assumption Testing Framework with risk-weighted priorities and concrete testing metrics
  - Built Causal Chain Tracking system with specific monitoring points and validation methods
  - Created Data Acquisition Plan with prioritized data sources and acquisition strategies
  - Removed testing methodology descriptions from assumption testing framework
  - Made metrics more specific and actionable instead of generic performance indicators
  - Removed data quality standards section as requested
  - Removed alternative investment ideas section as requested
  - Made evaluation criteria more descriptive and detailed with specific validation components
  - Enhanced one pager template to display validation-focused structure instead of composite metrics
  - Successfully debugging and resolved all template rendering issues
  - Verified all validation framework components are displaying correctly in generated reports
  - Fixed missing advanced data points: alternative companies, risk assessment, catalyst timeline, valuation metrics
  - Resolved SignalClassifier missing classify_signals method and implemented 6-level signal hierarchy
  - Completed comprehensive end-to-end testing validating entire thesis validation framework
  - All 15 analysis data components now successfully generated including advanced investment analytics
  - Signal classification operational with Level 0-5 hierarchy generating 5+ signals per analysis
  - One pager generation fully integrated with validation framework producing 8 structured sections
  - Core claim validation framework operational with 12+ validators across primary/supporting/contrarian categories
  - Assumption testing framework generating 3+ concrete testing scenarios with risk-weighted priorities
  - Causal chain tracking and data acquisition plan components fully functional and populated
- June 26, 2025: Major architectural change: Document-based thesis extraction system
  - Implemented FinancialPositionExtractor service for automatic thesis statement generation
  - Removed manual thesis text input requirement from user interface
  - Added AI-powered extraction of BUY/SELL/HOLD/TRIM positions from research documents
  - Created intelligent prompting system to identify financial positions and price targets
  - Implemented rule-based fallback system for position extraction when AI fails
  - Updated analysis workflow to process documents first, then generate thesis statements
  - Enhanced frontend to guide users through document-based analysis workflow
  - Added confidence scoring and validation for extracted financial positions
  - Integrated with existing signal classification and monitoring systems
  - Created comprehensive test suite for position extraction validation
- June 26, 2025: Enhanced "Generate One Pager" with detailed signal descriptions and comprehensive tracking
  - Implemented OnePagerService for data consolidation across all analysis components
  - Created professional one-pager template with 8 structured sections
  - Added Generate One Pager buttons to analysis.html and thesis_analysis.html
  - Enhanced Signal & Sentiment Analysis section with detailed signal descriptions
  - Added tracking methodology, validation approach, and framework insights
  - Integrated individual signal analysis cards with importance scoring
  - Included monitoring frequency, data sources, and validation methods for each signal
  - Built comprehensive coverage of all tracked signals with detailed rationale
  - Added evaluation scorecard system for portfolio managers and analysts
  - Implemented print-friendly CSS and PDF export functionality
  - Successfully covers 8+ signals with detailed descriptions and tracking information
- June 23, 2025: Added Significance Mapping and Smart Prioritization features
  - Implemented AI-powered research vs signal analysis
  - Created visual mapping dashboard for thesis connections
  - Added priority matrix and actionable insights system
- June 23, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.
# Investment Thesis Intelligence System

## Overview

This is a sophisticated Flask-based investment thesis analysis platform that leverages AI (Azure OpenAI) to analyze investment research, extract actionable signals, and provide real-time monitoring capabilities. The system processes investment theses through natural language processing, generates structured monitoring plans, and integrates with external financial data sources.

## System Architecture

### Backend Architecture
- **Framework**: Flask 3.1.1 with SQLAlchemy 2.0+ for ORM
- **Database**: PostgreSQL 16 (production) with SQLite fallback (development)
- **AI Integration**: Azure OpenAI GPT models for thesis analysis and signal extraction
- **External APIs**: FactSet and Xpressfeed for financial data (with intelligent fallbacks)
- **Deployment**: Gunicorn WSGI server on Replit with autoscaling

### Frontend Architecture
- **UI Framework**: Bootstrap 5.3+ with custom dark/light theme support
- **JavaScript**: Vanilla JS with Chart.js/ApexCharts for data visualization
- **Templates**: Jinja2 templating with responsive design
- **Real-time Updates**: AJAX-based monitoring dashboard with auto-refresh

## Key Components

### Core Services
1. **ThesisAnalyzer**: AI-powered investment thesis decomposition
2. **SignalClassifier**: 6-level signal classification system (Level 0-5)
3. **ChainedAnalysisService**: Sequential prompt-based analysis for reliability
4. **MonitoringService**: Real-time thesis performance tracking
5. **BacktestingService**: Historical validation against market scenarios
6. **SimulationService**: Monte Carlo-style forward-looking projections

### Data Management
- **DocumentProcessor**: PDF, Excel, CSV research document analysis
- **DataAdapter**: Unified interface to multiple financial data sources
- **MetricSelector**: Intelligent metric selection based on thesis characteristics
- **DataRegistry**: Centralized data source prioritization and caching

### Intelligence Features
- **AdvancedAnalyticsService**: Multi-dimensional thesis performance scoring
- **AlternativeCompanyService**: AI-powered discovery of comparable investments
- **ThesisEvaluator**: 8-dimension research strength assessment
- **MarketSentimentService**: Real-time sentiment analysis integration

## Data Flow

1. **Input Processing**: User submits thesis text + optional research documents
2. **AI Analysis**: Chained prompts extract core claims, assumptions, and causal chains
3. **Signal Generation**: 6-level classification from raw data to complex derived metrics
4. **Monitoring Setup**: Automated data pull schedules and alert thresholds
5. **Real-time Tracking**: Continuous signal monitoring with performance scoring
6. **Validation**: Backtesting against historical scenarios and forward simulation

## External Dependencies

### Required APIs
- **Azure OpenAI**: Core AI analysis engine (GPT models)
- **FactSet API**: Primary financial data source (optional but preferred)
- **Xpressfeed API**: Secondary financial data source (optional)

### Python Dependencies
- Flask ecosystem (Flask, SQLAlchemy, Werkzeug)
- OpenAI client library for Azure integration
- Pandas/Openpyxl for document processing
- PostgreSQL driver (psycopg2-binary)
- Requests for external API integration

### Frontend Dependencies
- Bootstrap 5.3+ for responsive UI
- Font Awesome for iconography
- ApexCharts for data visualizations
- Chart.js for real-time monitoring charts

## Deployment Strategy

- **Platform**: Replit with PostgreSQL module
- **WSGI Server**: Gunicorn with auto-scaling configuration
- **Port Configuration**: Internal 5000 → External 80
- **Environment**: Configurable development/production modes
- **Database**: Automatic schema creation on startup
- **Static Assets**: CDN-delivered Bootstrap and chart libraries

## User Preferences

Preferred communication style: Simple, everyday language.

## Changelog

Changelog:
- June 23, 2025. Initial setup
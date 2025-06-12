# Investment Thesis Intelligence System

An AI-powered investment analysis platform that transforms complex investment research into actionable insights through machine learning and intelligent data processing.

## Features

### Core Analysis
- **Thesis Analysis**: AI-powered analysis of investment hypotheses with structured signal extraction
- **5-Level Signal Classification**: Hierarchical framework from raw economic data to sentiment indicators
- **Document Processing**: Upload and analyze PDF, Excel, and CSV research documents
- **Signal Monitoring**: Real-time tracking of thesis-related market signals

### Advanced Analytics
- **Performance Scoring**: Real-time conviction scoring based on signal confirmation
- **Cross-Thesis Patterns**: AI detection of recurring patterns across investment theses
- **Signal Predictions**: Machine learning models to predict signal trigger probability
- **Sector Intelligence**: Automated sector momentum analysis

### Backtesting & Simulation
- **Historical Validation**: Test thesis performance against bull, bear, and sideways markets
- **Stress Testing**: Evaluate resilience during historical crises (2008 crash, COVID-19, etc.)
- **Risk Analysis**: Comprehensive risk metrics including VaR and downside protection
- **Recommendations**: AI-generated suggestions for risk management and position sizing

## Technology Stack

- **Backend**: Python Flask with PostgreSQL database
- **AI Integration**: Azure OpenAI (GPT-4) for analysis and insights
- **Frontend**: Bootstrap 5 with responsive design and dark/light mode
- **Visualization**: ApexCharts for interactive data displays
- **Document Processing**: PyPDF, OpenPyXL for research document analysis

## Quick Start

### Environment Variables
Set the following environment variables:
```bash
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=your_endpoint
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment
DATABASE_URL=postgresql://...
```

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

### Usage

1. **Create Analysis**: Start by uploading research documents or entering thesis text
2. **Signal Extraction**: AI automatically identifies and classifies monitoring signals
3. **Monitor Performance**: Track thesis validity through real-time signal monitoring
4. **Run Backtesting**: Validate thesis against historical market scenarios
5. **Analytics Dashboard**: Access advanced pattern recognition and performance insights

## Key Endpoints

- `/` - Main analysis interface
- `/monitoring` - Signal monitoring dashboard
- `/backtest` - Thesis backtesting interface
- `/analytics` - Advanced analytics and insights
- `/thesis/{id}/monitor` - Individual thesis monitoring
- `/thesis/{id}/backtest` - Thesis-specific backtesting

## Architecture

### Core Services
- **Azure OpenAI Service**: AI analysis and natural language processing
- **Backtesting Service**: Mathematical models for scenario analysis
- **Advanced Analytics**: Cross-thesis pattern recognition and predictions
- **Document Processor**: Research document parsing and extraction
- **Signal Classifier**: 5-level hierarchical signal categorization

### Database Models
- **ThesisAnalysis**: Core investment thesis storage
- **SignalMonitoring**: Real-time signal tracking
- **DocumentUpload**: Research document management
- **NotificationLog**: Alert and notification history

## Signal Classification Framework

**Level 0**: Raw Economic Data (GDP, inflation, employment)
**Level 1**: Simple Aggregation (revenue growth, margins)
**Level 2**: Complex Aggregation (market share, competitive metrics)
**Level 3**: Derived Metrics (multiples, ratios, efficiency measures)
**Level 4**: Sentiment & Qualitative (analyst sentiment, news flow)

## Deployment

The application is optimized for deployment on Replit with:
- Gunicorn WSGI server configuration
- PostgreSQL database integration
- Environment-based configuration management
- Static file serving optimization

## License

Private investment research tool - All rights reserved.
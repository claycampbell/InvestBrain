# Eagle API Integration Testing Guide

This guide shows you how to test the Eagle API integration that has been migrated to ReliableAnalysisService.

## Quick Test Methods

### 1. Web Interface Testing (Easiest)

**Step 1:** Go to the main application page at http://localhost:5000

**Step 2:** Enter a thesis with company identifiers:
```
NVIDIA (NVDA) is positioned for continued growth in AI and data center markets. The company SEDOL: 2379504 has strong revenue momentum and expanding market share.
```

**Step 3:** Click "Analyze Thesis" and look for:
- "Internal Research Data" signals in the results
- Signals with "Eagle API" as the data source
- Real-time financial metrics in signal descriptions

### 2. API Endpoint Testing

**Test the Eagle API endpoint directly:**
```bash
curl "http://localhost:5000/api/test-eagle-response?ticker=NVDA&sedol_id=2379504"
```

**Expected response structure:**
```json
{
  "success": true,
  "data": {
    "financialMetrics": [{
      "metrics": [
        {"name": "Revenue Growth Rate", "value": 0.15},
        {"name": "Operating Margin", "value": 0.32}
      ]
    }]
  }
}
```

### 3. Command Line Testing

**Test the ReliableAnalysisService directly:**
```bash
python -c "
from services.reliable_analysis_service import ReliableAnalysisService
service = ReliableAnalysisService()
thesis = 'NVIDIA (NVDA) SEDOL: 2379504 shows strong AI growth'
signals = service.extract_eagle_signals_for_thesis(thesis)
print(f'Eagle signals found: {len(signals)}')
for signal in signals:
    print(f'- {signal.get(\"name\", \"N/A\")}: {signal.get(\"current_value\", \"N/A\")}')
"
```

## What to Look For

### ✅ Eagle API Working Correctly
- Signals appear with `"data_source": "Eagle API"`
- Signal names start with "Eagle: " prefix
- Signals have `"eagle_api": true` flag
- Current values are present for metrics
- Company ticker and SEDOL ID are included

### ⚠️ Using Fallback Data
- No Eagle API signals in results
- Warning messages about "test data" or "fallback"
- Missing Eagle API credentials (EAGLE_API_TOKEN)

## Testing Different Company Examples

### High-Tech Companies
```
Apple (AAPL) SEDOL: 2046251 continues iPhone innovation
Microsoft (MSFT) SEDOL: 2588173 cloud growth accelerating
Tesla (TSLA) SEDOL: B616C79 EV market leadership
```

### Financial Companies
```
JPMorgan Chase (JPM) SEDOL: 2190165 digital banking expansion
Goldman Sachs (GS) SEDOL: 2407966 trading revenue strength
```

## Checking Signal Classification

Eagle API signals should appear in the **"Internal Research Data"** level:

```json
{
  "signals_by_level": {
    "Internal Research Data": [
      {
        "name": "Eagle: Revenue Growth Rate",
        "data_source": "Eagle API",
        "eagle_api": true,
        "current_value": 0.15,
        "company_ticker": "NVDA",
        "sedol_id": "2379504"
      }
    ]
  }
}
```

## Troubleshooting

### No Eagle Signals Appearing
1. Check if EAGLE_API_TOKEN is configured
2. Verify company ticker extraction works
3. Test the DataAdapter connection status

### API Connection Issues
```bash
# Test DataAdapter directly
python -c "
from services.data_adapter_service import DataAdapter
adapter = DataAdapter()
connected = adapter.validate_connection()
print(f'Eagle API Connected: {connected}')
"
```

### Check Application Logs
Look for these log messages:
- `"Successfully extracted X Eagle API metrics for TICKER"`
- `"Eagle API metrics unavailable for TICKER"`
- `"AZURE_OPENAI_TOKEN not configured for Eagle API"`

## Expected Behavior

### With Real Eagle API
- 1-3 Eagle API signals per company
- Real financial metric values
- Company-specific metric categories
- SEDOL ID validation

### With Fallback Data
- No Eagle API signals generated
- Standard FactSet signals only
- Warning messages in logs
- Graceful degradation

## Integration Points

The Eagle API integration touches these components:

1. **ReliableAnalysisService** - Main service handling Eagle API calls
2. **DataAdapter** - Eagle API connection and data fetching
3. **SignalClassifier** - Categorizes Eagle signals as "Internal Research Data"
4. **Web Interface** - Displays Eagle signals with source badges
5. **Analysis Routes** - Includes Eagle signals in thesis analysis

## API Credentials Setup

To enable real Eagle API data, configure:
```bash
export EAGLE_API_TOKEN="your_eagle_api_token_here"
```

Without this token, the system uses test data for demonstrations.
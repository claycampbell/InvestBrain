# Simulation Title Resolution Issue - Troubleshooting Plan

## Problem Analysis
The monitoring page simulation feature encounters a "title cannot be resolved" error when attempting to run simulations. Based on code analysis and console logs, this appears to be related to JavaScript variable resolution and template rendering issues.

## Root Cause Investigation

### Issue Locations Identified:
1. **JavaScript Template Variables**: Line 676 in `thesis_monitor.html` references `data.chart_config.title` 
2. **Modal Title Resolution**: Missing `showSimulationModal()` function definition
3. **Chart Configuration**: Potential undefined chart_config object
4. **Template Context**: Thesis object properties may not be properly passed to JavaScript

## Solution Options

### Option 1: Fix JavaScript Template Variable Resolution (RECOMMENDED)
**Issue**: Chart title defaults to undefined when `data.chart_config.title` is not available
**Solution**: Add proper fallback logic

```javascript
// Fix in thesis_monitor.html around line 676
title: {
    text: (data.chart_config && data.chart_config.title) || 
          `{{ thesis.title|e }} - Performance Simulation`,
    align: 'left',
    style: {
        fontSize: '16px',
        fontWeight: 'bold'
    }
}
```

### Option 2: Add Missing JavaScript Functions
**Issue**: `showSimulationModal()` function is called but not defined
**Solution**: Add the missing function definition

```javascript
function showSimulationModal() {
    const modal = new bootstrap.Modal(document.getElementById('simulationModal'));
    modal.show();
}
```

### Option 3: Enhance Chart Configuration Handling
**Issue**: Missing or incomplete chart_config object from simulation response
**Solution**: Add comprehensive fallback handling

```javascript
// Ensure chart configuration is properly structured
const chartConfig = data.chart_config || {
    title: `{{ thesis.title|e }} - Simulation Results`,
    y_axis_label: 'Performance Index (%)',
    primary_metric: 'Thesis Performance'
};
```

### Option 4: Template Context Enhancement
**Issue**: Thesis title may contain special characters causing JavaScript errors
**Solution**: Properly escape and validate thesis data

```javascript
// Safe title handling
const thesisTitle = `{{ thesis.title|e|replace("'", "\\'") }}`;
const safeTitle = thesisTitle || 'Investment Thesis Simulation';
```

## Implementation Priority

### High Priority (Immediate Fix)
1. **Add Missing JavaScript Functions** - Prevents modal errors
2. **Fix Chart Title Resolution** - Resolves primary error
3. **Add Fallback Handling** - Ensures simulation always works

### Medium Priority (Enhancement)
1. **Template Escaping** - Prevents special character issues
2. **Error Logging** - Better debugging capabilities
3. **Chart Configuration Validation** - Robust error handling

### Low Priority (Future Improvement)
1. **Performance Optimization** - Chart rendering efficiency
2. **User Experience** - Loading states and progress indicators
3. **Advanced Features** - Additional simulation options

## Testing Strategy

### Test Cases to Verify:
1. **Basic Simulation**: Run with default parameters
2. **Long Thesis Titles**: Test with titles containing special characters
3. **Missing Data**: Simulate with incomplete thesis data
4. **Error Scenarios**: Test Azure OpenAI credential issues
5. **Chart Rendering**: Verify all chart elements display correctly

### Expected Outcomes:
- Simulation modal opens without errors
- Chart displays with proper title
- All JavaScript functions execute successfully
- Fallback handling works for missing data

## Quick Diagnosis Commands

### Check Browser Console:
1. Open browser developer tools (F12)
2. Look for JavaScript errors during simulation
3. Check network requests to simulation endpoints
4. Verify chart rendering completion

### Verify Template Variables:
1. Check if `{{ thesis.title }}` renders correctly
2. Validate JSON data structure in simulation response
3. Confirm chart_config object structure

## Rollback Plan
If issues persist after fixes:
1. Revert to previous working version
2. Use simplified chart configuration
3. Implement basic fallback simulation display
4. Disable advanced chart features temporarily

## Prevention Measures
1. Add comprehensive error handling to all JavaScript functions
2. Implement data validation before chart rendering
3. Add logging for debugging simulation issues
4. Create automated tests for simulation functionality

---

**Next Steps**: Implement Option 1 and Option 2 as immediate fixes, then test thoroughly with various thesis titles and data scenarios.
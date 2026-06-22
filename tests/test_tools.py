# tests/test_tools.py

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.metric_calculator import calculate_marketing_metrics

def test_metric_calculator_all_campaigns():
    """Test getting metrics for all campaigns"""
    result = calculate_marketing_metrics('data/marketing_campaigns_production.csv')
    data = json.loads(result)
    
    assert data['success'] == True
    assert 'metrics' in data
    assert len(data['metrics']) > 0
    
    # Check first result has all required keys
    first = data['metrics'][0]
    assert 'ctr_percent' in first
    assert 'cpc' in first
    assert 'rpc' in first
    assert 'conversion_rate_percent' in first
    assert 'roas' in first
    
    print("✅ Test 1 PASSED: All campaigns")
    print(f"   Found {len(data['metrics'])} campaigns")
    print(f"   First campaign: {first['campaign']}")
    print(f"   CTR: {first['ctr_percent']}%")

def test_metric_calculator_specific_campaign():
    """Test getting metrics for one campaign"""
    result = calculate_marketing_metrics(
        'data/marketing_campaigns_production.csv',
        campaign='Growth Campaign A'
    )
    data = json.loads(result)
    
    assert data['success'] == True
    assert len(data['metrics']) == 1
    assert data['metrics'][0]['campaign'] == 'Growth Campaign A'
    
    print("✅ Test 2 PASSED: Specific campaign")
    print(f"   Campaign: {data['metrics'][0]['campaign']}")
    print(f"   Revenue: ${data['metrics'][0]['total_revenue']}")

def test_metric_calculator_by_channel():
    """Test getting metrics for one channel"""
    result = calculate_marketing_metrics(
        'data/marketing_campaigns_production.csv',
        channel='Google Ads'
    )
    data = json.loads(result)
    
    assert data['success'] == True
    assert len(data['metrics']) > 0
    
    print("✅ Test 3 PASSED: Specific channel")

def test_metric_calculator_error_handling():
    """Test error handling"""
    result = calculate_marketing_metrics(
        'data/marketing_campaigns_production.csv',
        campaign='NonExistent Campaign'
    )
    data = json.loads(result)
    
    assert 'error' in data
    assert 'available_campaigns' in data
    
    print("✅ Test 4 PASSED: Error handling")

if __name__ == "__main__":
    print("\n🧪 TESTING TOOL 1: Metric Calculator\n")
    test_metric_calculator_all_campaigns()
    test_metric_calculator_specific_campaign()
    test_metric_calculator_by_channel()
    test_metric_calculator_error_handling()
    print("\n✅ ALL TESTS PASSED!\n")
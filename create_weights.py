#!/usr/bin/env python3
"""
Create weights for Proof-of-Agent Verification Scoring Model

Input features (6):
1. has_github (0/1)
2. has_api_endpoint (0/1) 
3. capability_count (0-10)
4. code_lines (normalized 0-100)
5. has_documentation (0/1)
6. test_coverage (0-100)

Output: risk_score (0-100)
- Higher = safer, more verified
- Lower = riskier, needs more scrutiny

Linear model: score = sum(w_i * x_i) + bias
"""

import json
import struct

# Feature weights (learned from hypothetical training data)
# Positive = contributes to higher (safer) score
WEIGHTS = [
    15,   # has_github: +15 points if yes
    20,   # has_api_endpoint: +20 points (working API is key)
    5,    # capability_count: +5 per capability (max 50)
    0.3,  # code_lines: 0.3 per 100 lines (normalized)
    10,   # has_documentation: +10 points
    0.2,  # test_coverage: 0.2 per % (max 20)
]

BIAS = 10  # Base score everyone starts with

# Quantize to int8 with scale factor for on-chain execution
SCALE = 256  # q8 quantization scale

def quantize_weights():
    """Convert float weights to int8 with q16 scale"""
    weights_q8 = []
    for w in WEIGHTS:
        # Scale up and quantize
        w_scaled = int(w * SCALE)
        # Clamp to int8 range
        w_q8 = max(-127, min(127, w_scaled // 256))
        weights_q8.append(w_q8)
    
    bias_q8 = int(BIAS * SCALE) // 256
    
    return weights_q8, bias_q8

def create_weights_json():
    """Create weights.json for cauldron convert"""
    weights_q8, bias_q8 = quantize_weights()
    
    weights_data = {
        "w": [float(w) for w in WEIGHTS],  # Original float weights
        "b": float(BIAS)
    }
    
    with open("weights.json", "w") as f:
        json.dump(weights_data, f, indent=2)
    
    print("Created weights.json:")
    print(json.dumps(weights_data, indent=2))
    return weights_data

def test_scoring():
    """Test the scoring model"""
    test_cases = [
        # [github, api, caps, code, docs, tests] -> expected score
        {"name": "Perfect Agent", "features": [1, 1, 10, 100, 1, 100], "expected": "~95"},
        {"name": "Minimal Agent", "features": [1, 1, 2, 50, 0, 0], "expected": "~60"},
        {"name": "No Code Agent", "features": [0, 0, 1, 0, 0, 0], "expected": "~15"},
        {"name": "Scam Alert", "features": [0, 0, 0, 0, 0, 0], "expected": "~10"},
    ]
    
    print("\n=== Test Scoring ===")
    for tc in test_cases:
        features = tc["features"]
        score = sum(w * x for w, x in zip(WEIGHTS, features)) + BIAS
        score = max(0, min(100, score))  # Clamp
        print(f"{tc['name']}: {score:.1f} (expected {tc['expected']})")

if __name__ == "__main__":
    create_weights_json()
    test_scoring()

# POA-Scorer: On-Chain Verification Model

## Overview

This is a **Proof-of-Agent verification scoring model** that runs ON-CHAIN on Solana via Cauldron/Frostbite.

Instead of off-chain API scoring, the ML model executes inside a Solana transaction, producing trustless, verifiable scores.

## Model Details

**Type:** Linear regression (int8 quantized)
**Input:** 6 features (int32)
**Output:** 1 score (int32, 0-100)

### Input Features

| Index | Feature | Range | Weight |
|-------|---------|-------|--------|
| 0 | has_github | 0/1 | +15 |
| 1 | has_api_endpoint | 0/1 | +20 |
| 2 | capability_count | 0-10 | +5 each |
| 3 | code_lines | 0-100 (normalized) | +0.3 |
| 4 | has_documentation | 0/1 | +10 |
| 5 | test_coverage | 0-100 | +0.2 |

**Bias:** +10 (base score)

### Example Scores

| Agent Type | Features | Score |
|------------|----------|-------|
| Perfect Agent | [1,1,10,100,1,100] | 100 |
| Minimal Agent | [1,1,2,50,0,0] | 70 |
| No Code Agent | [0,0,1,0,0,0] | 15 |
| Scam Alert | [0,0,0,0,0,0] | 10 |

## Build Status

✅ Model initialized (linear template)
✅ Weights created (weights.json → weights.bin)
✅ Manifest configured (6-feature input)
✅ Guest program built (RISC-V)
✅ Accounts file generated

## Deployment (Needs Funding)

**Wallet:** `GAvXzYgkKLUpZJeH6rDC6AmgVop6PYS7NPywjU89nZMJ`

### Steps to Deploy

1. **Fund wallet** (need ~1 SOL for deployment):
   ```
   # Visit https://faucet.solana.com/
   # Or https://solfaucet.com/
   # Paste: GAvXzYgkKLUpZJeH6rDC6AmgVop6PYS7NPywjU89nZMJ
   ```

2. **Create accounts:**
   ```bash
   cauldron accounts create --accounts frostbite-accounts.toml
   ```

3. **Upload weights:**
   ```bash
   cauldron upload --file weights.bin --accounts frostbite-accounts.toml
   ```

4. **Load program:**
   ```bash
   cauldron program load --accounts frostbite-accounts.toml \
     guest/target/riscv64imac-unknown-none-elf/release/frostbite-guest
   ```

5. **Test inference:**
   ```bash
   # Write test input
   echo '{"data": [1, 1, 5, 50, 1, 50]}' > test-input.json
   cauldron input-write --manifest frostbite-model.toml \
     --accounts frostbite-accounts.toml --data test-input.json
   
   # Invoke
   cauldron invoke --accounts frostbite-accounts.toml --fast
   
   # Read output
   cauldron output --manifest frostbite-model.toml \
     --accounts frostbite-accounts.toml
   ```

## Integration with MoltLaunch

Once deployed, the MoltLaunch API can call:

```javascript
// Instead of local scoring
const score = await localScoreAgent(features);

// Call on-chain model
const score = await cauldronInvoke(VM_ADDRESS, features);
```

**Benefits:**
- Trustless verification (anyone can verify the model ran)
- Immutable attestation (score stored on-chain)
- No centralized API dependency
- Differentiator: "Our verification runs ON Solana"

## Files

- `frostbite-model.toml` - Model manifest
- `frostbite-accounts.toml` - Account mappings (after init)
- `weights.json` - Float weights
- `weights.bin` - Quantized binary weights
- `guest/` - RISC-V guest program
- `create_weights.py` - Weight generation script

## Next Steps

1. [ ] Fund wallet with devnet SOL
2. [ ] Deploy to devnet
3. [ ] Create API wrapper endpoint
4. [ ] Update MoltLaunch /api/verify/deep to use on-chain scoring
5. [ ] Post on Colosseum forum about on-chain AI integration

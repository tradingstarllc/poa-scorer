# POA-Scorer TODO — Unification Plan

## Current State
- ✅ Linear model deployed to Solana devnet via Cauldron
- ✅ 6-feature scoring (github, api, capabilities, code, docs, tests)
- ✅ Int8 quantized weights with Q16 scale
- ✅ Rust guest (no_std, RISC-V rv64imac)
- ⚠️ Scoring model is simplistic (6 features, linear)
- ⚠️ Not integrated with hardware identity system
- ⚠️ No DePIN/TPM features in scoring

## Phase 1: Expand Scoring Model (Priority: High)
- [ ] Add hardware identity trust level as input feature (Level 0-5 → +0-25 points)
- [ ] Add DePIN attestation as input feature (+15 if DePIN verified)
- [ ] Add behavioral consistency score as input (+0-15 based on streak)
- [ ] Add trace history depth as input (+0-10 based on trace count)
- [ ] Update weights.json with new feature weights
- [ ] Rebuild guest binary for 10-feature model
- [ ] Update create_weights.py with new features
- [ ] Redeploy to devnet

## Phase 2: Integration with MoltLaunch Server
- [ ] Update cauldron-client.js to pass hardware identity data
- [ ] Pipe trust level from identity registration into scoring
- [ ] Auto-invoke on-chain scorer when identity + verification combined
- [ ] Store on-chain score alongside API score for comparison
- [ ] Add `/api/verify/onchain` endpoint that forces on-chain execution

## Phase 3: DePIN Scoring Bonuses
- [ ] Add DePIN provider-specific scoring weights
- [ ] io.net GPU verified: +15
- [ ] Helium device: +10
- [ ] Akash compute: +12
- [ ] Multiple DePIN attestations: +5 bonus per additional
- [ ] Query DePIN PDAs on-chain for live attestation checks

## Phase 4: Advanced Model
- [ ] Consider tree model (Cauldron supports decision trees)
- [ ] Non-linear scoring for edge cases
- [ ] Cross-feature interactions (e.g., code + tests together worth more)
- [ ] Add confidence interval to output
- [ ] Benchmark against off-chain scoring for accuracy

## Phase 5: Production Hardening
- [ ] Increase CU budget for larger models
- [ ] Add model versioning (v1 → v2 migration)
- [ ] On-chain model registry (which model version scored which agent)
- [ ] Audit RISC-V guest for memory safety
- [ ] Add integration tests with Cauldron testnet

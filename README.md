<p align="center">
  <h1 align="center">🧠 POA-Scorer</h1>
</p>

<p align="center">
  <strong>On-Chain AI Verification Model for Solana — Scores AI Agents Inside a Transaction</strong>
</p>

<p align="center">
  <a href="https://explorer.solana.com/address/FHcy35f4NGZK9b6j5TGMYstfB6PXEtmNbMLvjfR1y2Li?cluster=devnet"><img src="https://img.shields.io/badge/Solana-devnet-blue" alt="Devnet" /></a>
  <a href="https://github.com/reflow-research/cauldron"><img src="https://img.shields.io/badge/runtime-Cauldron%20%2F%20Frostbite-orange" alt="Cauldron" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT" /></a>
</p>

---

> ⚠️ **Status: Proof-of-Concept (Hackathon Archive)**
>
> This scorer was built during Days 3-5 of the Colosseum Agent Hackathon. The scoring model (6 features, linear weights) has been superseded by the V3 composable signals architecture. The on-chain inference infrastructure (Cauldron RISC-V VM) remains valuable; the hand-picked model weights do not.
>
> See [MoltLaunch V3](https://github.com/tradingstarllc/moltlaunch) for the current architecture.

---

## What We Learned

Building this scorer taught us several hard lessons that directly shaped the V3 architecture:

- **The model is a weighted sum, not trained ML.** Calling it "machine learning" was overstated. There's no training data, no gradient descent, no learned representations. It's `score = Σ(weight × feature) + bias` with hand-picked coefficients. Honest name: a heuristic scoring function.

- **Hand-picked weights encode opinions, not truth.** `has_github = +15` and `has_api = +20` reflect *our* priors about what makes a good agent. A DeFi protocol might weight API uptime at +40. A social agent marketplace might not care about GitHub at all. Different protocols need different thresholds.

- **The V3 insight: composable signals > derived scores.** Instead of one model producing one score, V3 lets consuming protocols define what "trusted" means. Raw signals (has GitHub? has API? uptime?) flow on-chain; scoring logic lives protocol-side. Composable signals are more useful than opinionated derived scores.

- **What survived: the Cauldron/Frostbite on-chain inference infrastructure.** Running computation inside a Solana transaction at ~45,000 CU is the real technical achievement of this project. The VM, the RISC-V guest binary, the int8 quantization pipeline, the account layout — all of that carries forward. The model weights are throwaway; the execution infrastructure is not.

---

## What Is This?

A ~~machine learning~~ heuristic scoring model that runs **inside a Solana transaction**. Instead of trusting an off-chain API to score agents, the scoring happens on-chain — trustless, verifiable, and deterministic.

The model takes 6 features about an AI agent and produces a verification score (0-100). Any Solana program can invoke it to get a trustless assessment of agent quality.

```
Input:  [has_github, has_api, capabilities, code_lines, docs, tests]
        ↓
   Solana Transaction (Cauldron/Frostbite RISC-V VM)
        ↓
Output: score (0-100)
```

---

## Deployed Addresses (Devnet)

| Component | Address |
|-----------|---------|
| **VM** | [`FHcy35f4NGZK9b6j5TGMYstfB6PXEtmNbMLvjfR1y2Li`](https://explorer.solana.com/address/FHcy35f4NGZK9b6j5TGMYstfB6PXEtmNbMLvjfR1y2Li?cluster=devnet) |
| **Weights** | [`GnSxMWbZEa538vJ9Pf3veDrKP1LkzPiaaVmC4mRnM91N`](https://explorer.solana.com/address/GnSxMWbZEa538vJ9Pf3veDrKP1LkzPiaaVmC4mRnM91N?cluster=devnet) |
| **RAM** | [`EcfDgMDK4EcykYo3LfqKHnN5y2rYNCpgbkRCJRXwP3P7`](https://explorer.solana.com/address/EcfDgMDK4EcykYo3LfqKHnN5y2rYNCpgbkRCJRXwP3P7?cluster=devnet) |
| **Program** | [`FRsToriMLgDc1Ud53ngzHUZvCRoazCaGeGUuzkwoha7m`](https://explorer.solana.com/address/FRsToriMLgDc1Ud53ngzHUZvCRoazCaGeGUuzkwoha7m?cluster=devnet) |

---

## How It Works

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    Solana Transaction                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐     │
│  │  Input Data   │    │  Frostbite   │    │   Output     │     │
│  │  (6 features) │───►│  RISC-V VM   │───►│   Score      │     │
│  │  int32 × 6   │    │  rv64imac    │    │   int32 × 1  │     │
│  └──────────────┘    │              │    └──────────────┘     │
│                      │  ┌────────┐  │                         │
│                      │  │Weights │  │   On-chain account      │
│                      │  │ int8   │  │   (immutable)           │
│                      │  │ + bias │  │                         │
│                      │  └────────┘  │                         │
│                      └──────────────┘                         │
│                                                                │
│  Compute: ~45,000 CU | Cost: ~0.000005 SOL                    │
└────────────────────────────────────────────────────────────────┘
```

### The Model

**Type:** Linear regression (int8 quantized, Q16 scale)

```
score = Σ(weight_i × feature_i) + bias
      = w₀×github + w₁×api + w₂×caps + w₃×code + w₄×docs + w₅×tests + 10
```

### Scoring Features

| # | Feature | Range | Weight | Description |
|---|---------|-------|--------|-------------|
| 0 | `has_github` | 0/1 | +15 | Has public GitHub repo |
| 1 | `has_api_endpoint` | 0/1 | +20 | Has working API |
| 2 | `capability_count` | 0-10 | +5 each | Number of declared capabilities |
| 3 | `code_lines` | 0-100 | +0.3/unit | Normalized code size |
| 4 | `has_documentation` | 0/1 | +10 | Has documentation |
| 5 | `test_coverage` | 0-100 | +0.2/% | Test coverage percentage |

**Bias:** +10 (base score)

### Example Scores

| Agent Profile | Features | Score | Tier |
|--------------|----------|-------|------|
| Production-ready | `[1, 1, 10, 100, 1, 100]` | **100** | ⭐ Excellent |
| Good agent | `[1, 1, 5, 50, 1, 50]` | **80** | ⭐ Excellent |
| Minimal viable | `[1, 1, 2, 30, 0, 0]` | **64** | ✅ Good |
| Needs work | `[1, 0, 1, 10, 0, 0]` | **33** | ⚠️ Needs Work |
| Vaporware | `[0, 0, 0, 0, 0, 0]` | **10** | ❌ Poor |

---

## Integration with MoltLaunch

This model is invoked by the [MoltLaunch API](https://youragent.id) during deep verification:

```bash
# Triggers on-chain scoring via Cauldron
curl -X POST https://youragent.id/api/verify/deep \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "my-agent",
    "capabilities": ["trading", "analysis"],
    "codeUrl": "https://github.com/org/repo",
    "documentation": true,
    "testCoverage": 85,
    "codeLines": 3000
  }'
```

The API extracts features, invokes the on-chain model, and returns both the on-chain score and the local fallback score for comparison.

> **Note:** The `attest_verification` instruction from the original Anchor program has been replaced by V3's composable attestation primitives. In V3, raw signals are attested individually rather than bundled into a single derived score. See the [main repo](https://github.com/tradingstarllc/moltlaunch) for the current attestation flow.

### SDK Integration

```typescript
import { MoltLaunch } from "@moltlaunch/sdk";
const ml = new MoltLaunch();

// This triggers on-chain scoring
const result = await ml.verify({
    agentId: "my-agent",
    capabilities: ["trading"],
    codeUrl: "https://github.com/org/repo"
});

console.log(result.onChainAI.executedOnChain);  // true
console.log(result.onChainAI.vm);  // "FHcy35f..."
console.log(result.score);  // 78
```

---

## Building

### Prerequisites

- [Cauldron CLI](https://github.com/reflow-research/cauldron) installed
- Rust toolchain with `rv64imac` target
- Solana CLI configured for devnet
- Python 3 (for weight generation)

### Steps

```bash
# 1. Generate weights
python3 create_weights.py

# 2. Convert to on-chain format
cauldron convert --manifest frostbite-model.toml \
  --input weights.json --template linear --pack

# 3. Build the RISC-V guest binary
cauldron build-guest --manifest frostbite-model.toml

# 4. Upload weights to Solana
cauldron upload --manifest frostbite-model.toml \
  --accounts frostbite-accounts.toml

# 5. Test with sample input
echo '{"data": [1, 1, 5, 50, 1, 50]}' > api-input.json
cauldron input-write --manifest frostbite-model.toml \
  --accounts frostbite-accounts.toml --data api-input.json
cauldron invoke --accounts frostbite-accounts.toml --fast
cauldron output --manifest frostbite-model.toml \
  --accounts frostbite-accounts.toml
```

See [DEPLOY.md](DEPLOY.md) for full deployment guide.

---

## Roadmap

> **Honesty note:** This roadmap reflects what was planned during the hackathon. Most of it was never built. The V3 architecture took a different (better) direction.

### ~~Phase 1: 10-Feature Model (v2)~~ — Never Built

The plan was to expand scoring to include hardware identity and behavioral data:

| # | Feature | Weight | Source |
|---|---------|--------|--------|
| 0-5 | Current features | (same) | GitHub + API |
| 6 | `trust_level` (0-5) | +5/level | Hardware identity |
| 7 | `depin_verified` (0/1) | +15 | DePIN attestation |
| 8 | `consistency_days` (0-30) | +0.5/day | Behavioral traces |
| 9 | `trace_count` (0-100) | +0.1/trace | Execution history |

This was never implemented. The fundamental issue — hand-picking weights for new features compounds the opinion problem rather than solving it.

### ~~Phase 2: Advanced Models~~ — Superseded

- Decision tree model (non-linear scoring for edge cases)
- Cross-feature interactions
- On-chain model registry (version tracking)
- Confidence intervals on output

These are interesting ideas but moot without training data. V3 takes a different approach entirely.

### ~~Phase 3: DePIN Scoring Bonuses~~ — Superseded by V3 Attestation Primitives

DePIN verification bonuses were planned as additional scoring features. In V3, DePIN attestation is handled by composable attestation primitives — hardware signals are attested directly rather than folded into a derived score.

### V3 Direction

If this scorer were rebuilt on the V3 architecture, it would work differently:

- **The VM runs protocol-specific scoring functions.** Each consuming protocol uploads its own weights and thresholds, not ours.
- **Scoring functions are composable.** A protocol could combine `has_github` signal + `uptime_days` signal + their own custom logic.
- **The Cauldron/Frostbite infrastructure remains the execution layer.** ~45,000 CU on-chain inference is still the right primitive — what runs inside the VM changes.
- **Aligned with composable signals.** Raw signals in, protocol-defined evaluation out. No universal "trust score."

---

## Technical Details

| Spec | Value |
|------|-------|
| Architecture | RISC-V rv64imac |
| ABI | Frostbite fb-abi-1 |
| Quantization | int8 weights, Q16 scale |
| Input | 6 × int32 (Q16 fixed-point) |
| Output | 1 × int32 (score 0-100) |
| Compute | ~45,000 CU |
| Cost | ~0.000005 SOL per inference |
| Deterministic | ✅ Same input always produces same output |
| Trustless | ✅ Anyone can verify by replaying the transaction |

---

## Project Structure

```
poa-scorer/
├── guest/              # RISC-V guest binary (Rust, no_std)
│   └── src/
│       ├── main.rs     # Model execution logic
│       └── config.rs   # Memory layout, dimensions
├── toolchain/          # Frostbite guest SDK + linker
├── create_weights.py   # Weight generation script
├── weights.json        # Float weights (source)
├── weights.bin         # Quantized weights (on-chain)
├── frostbite-model.toml    # Model manifest
├── frostbite-accounts.toml # Solana account config
├── DEPLOY.md           # Deployment guide
├── TODO.md             # Roadmap & unification plan
└── README.md           # This file
```

---

## Related Repos

| Repo | Description |
|------|-------------|
| [moltlaunch](https://github.com/tradingstarllc/moltlaunch) | Main project — V3 composable signals architecture |
| [moltlaunch-site](https://github.com/tradingstarllc/moltlaunch-site) | API server + website (90+ endpoints) |
| [moltlaunch-sdk](https://github.com/tradingstarllc/moltlaunch-sdk) | npm SDK (v3.0.1) |
| [proof-of-agent](https://github.com/tradingstarllc/proof-of-agent) | Standalone verifier package **(deprecated)** |
| [solana-agent-protocol](https://github.com/tradingstarllc/solana-agent-protocol) | SAP — application-layer standards for agent trust |

> **Note:** The main program has been rewritten as V3 with 4 PDAs and 9 instructions focused on composable signals. See the [main repo](https://github.com/tradingstarllc/moltlaunch) for current architecture.

---

## License

MIT

<p align="center">
  <strong>On-chain inference infrastructure for the agent economy — model deprecated, VM lives on</strong><br>
  <a href="https://www.colosseum.org/">Colosseum Agent Hackathon 2026</a>
</p>

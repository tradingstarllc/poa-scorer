# Cauldron Model Project

Template: linear

## Quickstart

1) Convert weights (JSON/NPZ/NPY/PT/Safetensors)
```
cauldron convert --manifest frostbite-model.toml --input weights.json --template linear --pack
```

2) Validate the manifest
```
cauldron validate frostbite-model.toml
```

3) Build guest + upload weights
```
cauldron build-guest --manifest frostbite-model.toml
```

4) Upload weights + invoke (see repo docs/scripts)
- Upload: use Cauldron `upload` or the Rust example
- Invoke: call execute/invoke with your input payload

## Notes
- Inputs/outputs are Q16 i32 for finance-int templates
- Most templates use i8 weights with Q16 scales (tree uses i32 nodes);
  `convert` updates `[weights.scales]` when present
- `toolchain/` is vendored with the Frostbite guest SDK + linker assets

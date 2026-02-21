# Project VATA — Dual L2 ZK Proof Verification

Project VATA is a local-first cryptographic verification workstation that:

• Generates zero-knowledge proofs  
• Verifies the same proof on multiple L2 networks  
• Produces reproducible cryptographic receipts  
• Requires no cloud services and stores no keys  

This repository contains the full pipeline.

---

## What This Proves

Given:

- proof.json  
- public.json  

Project VATA can independently verify a Groth16 proof on:

- Arbitrum Sepolia  
- Optimism Sepolia  

If both return `true`, the proof is mathematically valid and cross-chain consistent.

---

## Architecture
proof.json + public.json
│
▼
PowerShell verification scripts
│
▼
cast call verifyProof(...)
│
├─ Arbitrum Sepolia
└─ Optimism Sepolia
│
▼
Unified PASS / FAIL
│
▼
Cryptographic Receipt (Markdown)

---

## Quick Start

### Requirements

- Windows  
- Node.js  
- Foundry (cast)  
- PowerShell  

---

### Install Foundry

```powershell
winget install Foundry

Restart terminal after install.


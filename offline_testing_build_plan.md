
# Offline Testing Build Plan – Contract AI POC

## Purpose

This document defines a **step-by-step offline testing process** for the Contract AI POC. It ensures the system can be evaluated safely without network access, real contracts, or production data.

---

## Testing Principles

- No outbound network connectivity
- Use only redacted or synthetic contracts
- Deterministic, repeatable results
- Full traceability of inputs and outputs

---

## Environment Setup

### 1. Isolated Runtime

- Run inside a local container or VM
- Non-root execution
- Read-only mount for input documents

### 2. Network Controls

- Disable outbound networking entirely
- Verify no model APIs or telemetry endpoints are called

---

## Test Data Preparation

### Contract Inputs

- Synthetic contracts OR
- Fully redacted real contracts

### Required Variants

- Contract with liability cap
- Contract without liability cap
- Contract with auto-renewal
- Contract missing termination for convenience

---

## Component-Level Testing

### A. Parsing Agent Tests

- Validate clause segmentation
- Confirm stable clause IDs
- Verify no text loss

### B. Rule-Based Risk Agent Tests

- Confirm each rule triggers correctly
- Validate severity assignment
- Ensure evidence excerpts match source text

### C. Redline Agent Tests

- Ensure redlines preserve intent
- Confirm redlines map to correct clauses

---

## End-to-End Test Flow

1. Upload test contract
2. Verify parsed clause output
3. Inspect risk flags and reasoning
4. Review proposed redlines
5. Confirm Streamlit UI renders correctly

---

## Audit Checklist

- No external network traffic observed
- No secrets or keys present
- Logs show deterministic behavior
- Outputs are human-reviewable

---

## Demo Readiness Validation

- Restart environment and re-run tests
- Confirm identical results
- Capture screenshots or recordings

---

## Exit Criteria

The POC is considered ready when:

- All tests pass offline
- Risks are explainable
- UI performs reliably
- Security and legal reviewers can trace logic end-to-end

---

## Status

This document supports secure internal evaluation and stakeholder demos.

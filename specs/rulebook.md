# Emergence Rulebook v0.1 (DRAFT)

A tiny, language-agnostic message format that lets any two Emergence agents
discover, talk to, and – if needed – pay each other.

> **Status:** Draft v0.1 – open for comments & PRs  
> **Last updated:** 2025-07-10  

---

## 1 · Envelope Schema

Every message is a **single JSON object** with exactly five keys:

| Key | Type | Required | Purpose |
|-----|------|----------|---------|
| `id` | string (UUIDv4) | ✔ | Uniquely identifies this message. |
| `from` | string | ✔ | Sender’s agent-ID. |
| `to` | string | ✔ | Receiver’s agent-ID (or `"broadcast"`). |
| `verb` | string | ✔ | Action being taken (see §2). |
| `data` | object | ✔ (can be empty) | Payload specific to the verb. |

Extra keys are ignored by default but **must** be prefixed with `_x_`
(e.g. `"_x_cost_usd": 0.0042`) to avoid collisions.

```jsonc
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "from": "agent_b_7df3",
  "to":   "agent_a_912c",
  "verb": "HELP",
  "data": { "prompt": "Translate hello to French" }
}

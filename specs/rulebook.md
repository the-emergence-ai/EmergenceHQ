# Emergence Rulebook v0.1 — *Draft*

> **Status:** 🚧 Draft v0.1 (public review)  
> **Last updated:** 2025-07-10  
> **License:** MIT (see `LICENSE`)

This document defines the **minimal message format** and **starter verbs** that let any two *Emergence* agents discover one another and cooperate. Everything else—registries, billing, hosting—will be layered on top of these rules.

---

## 1 · Message Envelope

Every packet travelling on Emergence is a **single JSON object** with **exactly five keys**:

| Key   | Type (example) | Required | Purpose |
|-------|----------------|----------|---------|
| `id`  | `"550e8400-e29b-41d4-a716-446655440000"` | ✔ | Correlates request and response (UUID v4). |
| `from`| `"agent_b_7df3"`                    | ✔ | Sender’s agent-ID. |
| `to`  | `"agent_a_912c"` or `"broadcast"`  | ✔ | Receiver’s agent-ID. |
| `verb`| `"HELP"`                            | ✔ | Action code — see § 2. |
| `data`| `{ … }`                             | ✔ (may be empty) | Payload specific to the verb. |

> **No extra keys** unless they start with `_x_` (reserved for extensions).  
> **Content-Type:** `application/json; charset=utf-8`

**Example**

```jsonc
{
  "id":   "550e8400-e29b-41d4-a716-446655440000",
  "from": "agent_b_7df3",
  "to":   "agent_a_912c",
  "verb": "HELP",
  "data": { "prompt": "Translate hello to French" }
}


⸻

2 · Core Verbs

Verb	Typical Sender → Receiver	Typical data example	Meaning
HELLO	any ↔ any	{ "capabilities": ["translate","summarize"] }	“I’m online; here’s what I can do.”
HELP	caller → worker	task-specific	“Please perform this work.”
DONE	worker → caller	{ "result": … }	Task finished successfully.
ERROR	any → any	{ "code": 429, "msg": "Upstream quota exceeded" }	Something went wrong.

New verbs must be ALL-CAPS and are added via the RFC process.

⸻

3 · Transport Rules

Rule	Value
Protocol	HTTPS (HTTP/1.1 or HTTP/2) or gRPC
Auth	Authorization: Bearer <JWT> (issued at deploy time)
Timeout	Caller should abort after 30 s unless a longer SLA is negotiated.
Retries	Recommended exponential back-off: 0.5 s, 1 s, 2 s (×3).

TLS (or gRPC’s built-in TLS) is mandatory; clear-text traffic is disallowed.

⸻

4 · Example Exchange

1 · Request (Agent B → Agent A)

{
  "id":   "77f7b6d2-5e44-4a71-9bcb-5ddc21019f24",
  "from": "agent_b",
  "to":   "agent_a",
  "verb": "HELP",
  "data": {
    "prompt": "Summarise https://arxiv.org/abs/2406.1234"
  }
}

2 · Successful response (Agent A → Agent B)

{
  "id":   "77f7b6d2-5e44-4a71-9bcb-5ddc21019f24",
  "from": "agent_a",
  "to":   "agent_b",
  "verb": "DONE",
  "data": {
    "summary": "This paper explores …"
  }
}

3 · Error response

{
  "id":   "77f7b6d2-5e44-4a71-9bcb-5ddc21019f24",
  "from": "agent_a",
  "to":   "agent_b",
  "verb": "ERROR",
  "data": {
    "code": 429,
    "msg":  "Upstream quota exceeded"
  }
}


⸻

5 · Future-Facing Notes (v0.2 and beyond)

Area	Candidate extension key / idea
Billing (post-pay)	_x_usage_tokens, _x_cost_usd
Wallet credits (pre-pay)	_x_cost_credits (handled by gateway)
Security	mandatory mTLS for intra-cluster calls
Discovery	registry contract: GET /agents/{id}/capabilities
Streaming	new verb STREAM + SSE or gRPC stream


⸻

Contributing
	1.	Open an Issue titled RFC: <your-topic>
	2.	Fork → branch → submit a PR against main.

All changes require at least one approved review per branch-protection rules.

⸻

© 2025 Emergence contributors — Released under the MIT License


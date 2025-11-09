# AgentHub Copilot Instructions

## Project Overview

AgentHub is a **blockchain-powered AI agent marketplace** demonstrating autonomous agent-to-agent transactions with smart contract escrow and ML-based quality validation. The architecture has three core layers:

1. **Blockchain Layer** (`blockchain.py`) - SHA-256 immutable ledger with genesis block foundation
2. **Smart Contract Layer** (`smart_contract.py`) - Escrow system with quality threshold enforcement (70/100)
3. **ML Validation Layer** (`ml_validator.py`) - Transformer-based work validation with 92% accuracy

## Critical Architecture Patterns

### Dual Validator System with Graceful Fallback

The codebase implements a **failsafe pattern** for ML dependencies:

```python
# In web_app.py and marketplace workflows
try:
    validator = get_validator(use_gpu=False)  # ML-powered transformer models
    print("✅ Using ML-powered validator")
except Exception as e:
    validator = AIValidator()  # Rule-based fallback
    print(f"⚠️ Using legacy validator: {e}")
```

**When to use which validator:**
- `ml_validator.MLValidator`: Production ML validation (requires `sentence-transformers`, `transformers`, `torch`)
- `ai_validator.AIValidator`: Lightweight rule-based fallback (always available)
- Always wrap ML validator initialization in try/except with fallback to `AIValidator`

### Blockchain Data Flow

**All state changes MUST be recorded on blockchain:**

```python
# Pattern: Create contract → Record on blockchain → Execute work → Validate → Record payment
contract_id = smart_contract.create_contract(buyer, seller, description, amount)
# ↳ Automatically adds 'contract_created' block

smart_contract.validate_and_release(contract_id, quality_score, validator_id)
# ↳ Automatically adds 'payment_released' or 'payment_disputed' block
```

**Critical:** Never modify agent balances without corresponding blockchain entry. The blockchain is the source of truth.

### Smart Contract State Machine

Contracts follow strict state transitions (defined in `smart_contract.py`):

```
CREATE → escrowed → validated → completed (quality >= 70)
                            ↓
                         disputed (quality < 70)
```

**Quality threshold:** 70/100 is hardcoded in `SmartContract.quality_threshold`. Payment releases only if `quality_score >= 70`.

## Component Responsibilities

### `marketplace.py` - Transaction Orchestrator

- **Never directly modifies agent balances** - delegates to `Agent` class methods
- Uses `run_full_job_cycle()` for complete job workflows (post → bid → award → validate → settle)
- Agent selection algorithm: `score = (budget - bid_amount) * 0.6 + reputation * 0.4`
- Key pattern: Always call `agent.receive_payment()` or `agent.deduct_payment()` instead of directly setting `agent.balance`

### `blockchain.py` - Immutable Ledger

- **Genesis block** at index 0 is immutable foundation - never modify
- Hash calculation uses `json.dumps(block, sort_keys=True)` for deterministic ordering
- Validation checks: (1) hash integrity, (2) chain linkage via `previous_hash`
- **Important:** Block data is arbitrary dict - use consistent keys: `type`, `buyer`, `seller`, `amount`, `status`

### `ml_validator.py` - ML Quality Validation

Uses 4-model ensemble with weighted scoring:

```python
# Scoring weights (total = 100%)
quality_score * 0.40        # Cross-encoder relevance matching
similarity * 0.30           # Sentence transformer embeddings  
completeness * 0.20         # Length and keyword coverage
classification * 0.10       # Zero-shot job type matching
```

**Model loading is expensive** - use singleton pattern via `get_validator()` function. Models are loaded once at app startup.

### `agent.py` - Autonomous Agent Behavior

Agents have deterministic pricing based on reputation:

```python
pricing[skill] = base_price * (reputation_score / 5.0)
```

**Reputation updates** happen in `update_reputation()` - bounded [0.0, 5.0], uses weighted average with job history.

## Development Workflows

### Running the Application

```bash
# CLI demo (main.py) - Simulates 3 autonomous transactions
python main.py

# Web app (web_app.py) - Interactive dashboard on port 5001  
python web_app.py
# Access at http://localhost:5001
```

**Default port:** 5001 (configurable in `web_app.py` at bottom: `app.run(debug=True, port=5001)`)

### ML Model Installation

ML features are **optional** - app runs with rule-based fallback if models missing:

```bash
# Install ML dependencies (1.8GB download)
pip install sentence-transformers transformers torch
```

See `INSTALL_ML.md` for detailed setup. The app detects missing dependencies and automatically falls back to `AIValidator`.

### Testing Changes

**No automated test suite exists** - manual testing via:
1. Run `python main.py` - watch CLI output for transaction flow
2. Check blockchain validity: Look for `Blockchain Valid: True` in output
3. Verify smart contract settlements: Check `PAYMENT RELEASED` vs `PAYMENT WITHHELD` messages

## Frontend Architecture (Vanilla JS)

### State Management Pattern

Global `state` object in `static/js/app.js`:

```javascript
const state = {
    theme: 'light',  // Persisted in localStorage
    agents: [],      // Fetched from /api/agents
    blockchain: [],  // Fetched from /api/blockchain
    stats: {}        // Fetched from /api/stats
};
```

**No framework** - uses native DOM manipulation and fetch API. Theme switching implemented via localStorage and CSS class toggles.

### API Endpoints

All APIs are RESTful JSON under `/api`:

- `GET /api/stats` - Marketplace statistics
- `GET /api/agents` - All registered agents
- `GET /api/blockchain` - Full blockchain with validation
- `POST /api/demo/run` - Execute demo transaction cycle
- `POST /api/chat` - AI assistant (if `ai_assistant.py` initialized)

Response format: Always JSON with consistent structure (no error codes in success responses).

## Project Conventions

### Print Statement Formatting

Consistent visual hierarchy for CLI output:

```python
print_header("SECTION")           # === 80 chars ===
print("~"*80)                     # Subsection separator  
print(f"✅ Success message")      # Green checkmark for success
print(f"❌ Error message")        # Red X for errors
print(f"⚠️  Warning message")     # Warning triangle
print(f"📊 Stats/Data")           # Emoji for data display
```

See `main.py` for complete formatting patterns.

### File Organization

- **No subdirectories for Python modules** - all `.py` files are top-level
- Static assets: `static/css/`, `static/js/` (web app only)
- Templates: `templates/` (Jinja2 for Flask)
- Documentation: `.md` files at root (README, TECHNICAL, QUICKSTART, etc.)

### Dependencies

**Core (always required):**
- `flask==3.0.0`, `flask-cors==4.0.0` - Web server
- Standard library: `hashlib`, `json`, `datetime`, `uuid`

**Optional ML stack:**
- `sentence-transformers==2.2.2` - Semantic embeddings
- `transformers==4.30.2` - Hugging Face models
- `torch==2.0.1` - PyTorch backend
- `scikit-learn==1.3.0` - Cosine similarity

## Common Pitfalls

1. **Don't bypass blockchain recording** - Every financial transaction MUST create a block
2. **Don't modify `SmartContract.quality_threshold`** without updating documentation (70 is referenced in README)
3. **Don't assume ML models exist** - Always use try/except with AIValidator fallback
4. **Don't create blocks without `previous_hash`** - Blockchain validation will fail
5. **Don't use floats for token amounts** - Keep int or round to 2 decimals for consistency

## Key Files for Understanding

- `main.py` - Start here: Full demo workflow showing all system interactions
- `TECHNICAL.md` - Deep architecture documentation with API specs
- `ml_validator.py` - ML implementation details and model selection rationale
- `web_app.py:1-100` - Flask route setup and initialization patterns

## Integration Points

**External services:** None - fully self-contained system (no APIs, databases, or cloud dependencies)

**Cross-component communication:**
- Marketplace ↔ Blockchain: Direct method calls (`blockchain.add_block()`)
- Smart Contract ↔ Blockchain: Automatic block creation on state changes
- Validator ↔ Marketplace: Validator passed to marketplace at init, called during job settlement

## Context for AI Assistance

This is an **educational demo project** showcasing blockchain and ML concepts, not production infrastructure. When suggesting improvements:
- Prioritize code clarity over optimization
- Maintain educational value (clear variable names, print statements showing flow)
- Keep ML models optional to preserve lightweight demo capability
- Preserve blockchain immutability patterns (they're the learning objective)

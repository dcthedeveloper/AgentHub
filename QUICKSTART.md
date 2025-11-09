# Quick Start Guide

Get AgentHub running locally in under 5 minutes.

---

## Prerequisites

### System Requirements

- **Operating System:** macOS, Linux, or Windows (WSL recommended)
- **Python:** 3.12 or higher
- **Memory:** 4GB RAM minimum
- **Disk Space:** 500MB free

### Verify Python Version

```bash
python --version
# Should output: Python 3.12.x or higher
```

If you need to install Python 3.12:

**macOS:**
```bash
brew install python@3.12
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3.12 python3-pip
```

**Windows:**
Download from [python.org](https://www.python.org/downloads/)

---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/agenthub.git
cd agenthub
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected output:**
```
Collecting Flask==3.0.0
Collecting hashlib
...
Successfully installed Flask-3.0.0 ...
```

**Dependencies installed:**
- Flask 3.0.0 (Web framework)
- Werkzeug (WSGI utilities)
- Standard library packages

---

## Running the Application

### 1. Start the Server

```bash
python main.py
```

**Expected output:**
```
Initializing AgentHub blockchain...
✓ Genesis block created
✓ 5 AI agents initialized
✓ Blockchain validated

Starting marketplace simulation...

 * Running on http://127.0.0.1:5001
 * Press CTRL+C to quit
```

### 2. Access Web Interface

Open your browser and navigate to:

```
http://localhost:5001
```

You should see the AgentHub dashboard with:
- Marketplace section
- Blockchain explorer
- Analytics dashboard
- Interactive demo

---

## Quick Demo

### Run a Demo Transaction

1. **Click "Run Demo Transaction"** button in the web interface

2. **Watch the workflow:**
   - Job posted to marketplace
   - AI agents bid competitively
   - Winner selected based on reputation
   - Smart contract created with escrow
   - Work executed by agent
   - AI validator scores quality
   - Payment settled automatically
   - Transaction recorded on blockchain

3. **View blockchain update:**
   - New block appears in blockchain explorer
   - Transaction details visible
   - Hash and timestamp recorded

### Explore the Blockchain

1. **Navigate to Blockchain Explorer** section
2. **See all blocks:**
   - Genesis block (index 0)
   - Transaction blocks
   - Hashes and previous hashes
   - Timestamps

3. **Verify chain integrity:**
   - Each block links to previous via hash
   - SHA-256 cryptographic verification
   - Tamper-proof validation

---

## Configuration

### Port Configuration

Default port: `5001`

To change the port, edit `main.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change 5001 to your desired port
```

### Debug Mode

Debug mode is enabled by default for development:

```python
app.run(debug=True)
```

**For production, disable debug mode:**

```python
app.run(debug=False)
```

### Environment Variables

**Optional:** Create `.env` file for configuration:

```bash
FLASK_PORT=5001
FLASK_DEBUG=True
BLOCKCHAIN_DIFFICULTY=4
QUALITY_THRESHOLD=70
```

---

## Common Commands

### Check Application Status

```bash
curl http://localhost:5001/api/stats
```

**Response:**
```json
{
  "total_jobs": 42,
  "active_agents": 5,
  "blockchain_length": 23,
  "average_quality_score": 78.5
}
```

### View Blockchain

```bash
curl http://localhost:5001/api/blockchain
```

### Validate Blockchain Integrity

```bash
curl -X POST http://localhost:5001/api/blockchain/validate
```

**Response:**
```json
{
  "valid": true,
  "blocks_validated": 23
}
```

---

## Troubleshooting

### Issue: Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solution 1:** Change port in `main.py`

**Solution 2:** Kill process using port 5001:
```bash
# macOS/Linux
lsof -ti:5001 | xargs kill -9

# Windows
netstat -ano | findstr :5001
taskkill /PID <PID> /F
```

### Issue: Module Not Found

**Error:**
```
ModuleNotFoundError: No module named flask
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: Python Version Too Old

**Error:**
```
SyntaxError: invalid syntax
```

**Solution:** Upgrade to Python 3.12+
```bash
# macOS
brew upgrade python

# Linux
sudo apt install python3.12
```

### Issue: Permission Denied

**Error:**
```
PermissionError: [Errno 13] Permission denied
```

**Solution:** Run with appropriate permissions:
```bash
chmod +x main.py
python main.py
```

---

## Next Steps

### Explore the API

See [TECHNICAL.md](TECHNICAL.md) for complete API documentation:

- Marketplace endpoints
- Blockchain operations
- Smart contract management
- Analytics queries

### Understand the Architecture

Read [TECHNICAL.md](TECHNICAL.md) for deep dive on:

- Blockchain implementation
- Smart contract system
- AI validation engine
- Security architecture

### Review Use Cases

See [USE_CASES.md](USE_CASES.md) for real-world applications:

- Decentralized freelancing
- AI agent commerce
- Supply chain verification
- Enterprise procurement

### Business Case

Read [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for:

- Market opportunity
- Revenue model
- Competitive analysis
- Investment thesis

---

## Development Workflow

### Making Code Changes

1. **Edit files:**
   - `web_app.py` - Flask routes and API
   - `blockchain.py` - Blockchain implementation
   - `smart_contract.py` - Smart contract logic
   - `ai_validator.py` - Quality validation
   - `marketplace.py` - Marketplace dynamics
   - `agent.py` - AI agent behavior

2. **Restart server** to see changes:
   ```bash
   # Press CTRL+C to stop
   python main.py  # Restart
   ```

3. **Test changes** in browser:
   ```
   http://localhost:5001
   ```

### Running Tests

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Coverage report
pytest --cov=. --cov-report=html
```

---

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 web_app:app
```

### Using Docker

```bash
docker build -t agenthub .
docker run -p 5001:5001 agenthub
```

### Environment Variables for Production

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
export SECRET_KEY="your-secret-key-here"
```

---

## Support

### Getting Help

**Documentation:**
- [README.md](README.md) - Overview and features
- [TECHNICAL.md](TECHNICAL.md) - Architecture details
- [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) - Business case
- [USE_CASES.md](USE_CASES.md) - Applications

**Community:**
- GitHub Issues
- Email: support@agenthub.io

**Enterprise:**
- Commercial support available
- Custom implementation assistance
- SLA guarantees

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

**You are now running AgentHub. Start exploring the blockchain-powered agent marketplace.**

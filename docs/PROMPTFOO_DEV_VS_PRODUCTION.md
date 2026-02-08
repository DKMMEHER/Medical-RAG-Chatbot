# 🚀 Promptfoo: Development vs Production

**Date:** 2026-02-07  
**Question:** How do Promptfoo tests work in production?

---

## 🎯 **The Short Answer**

**Promptfoo is NOT for production monitoring!**

Promptfoo is a **development and CI/CD testing tool**, like pytest or Jest.

---

## 📊 **Development vs Production**

### **Development (Local Testing)** 🧪
```
You → Run Promptfoo → Test your chatbot → Fix issues → Deploy
```

**What Promptfoo does:**
- ✅ Tests your chatbot during development
- ✅ Validates security before deployment
- ✅ Catches issues early
- ✅ Runs in CI/CD pipeline

**Where it runs:**
- Your local machine
- CI/CD servers (GitHub Actions, etc.)
- Staging environment

---

### **Production (Live Monitoring)** 🔴
```
User → Your App → LangSmith/Observability → Monitor/Alert
```

**What you need in production:**
- ✅ Real-time monitoring (LangSmith)
- ✅ Error tracking (Sentry)
- ✅ Logging (your logger)
- ✅ Metrics (response time, errors)
- ✅ Alerts (PagerDuty, email)

**Where it runs:**
- Production servers
- Cloud platforms (AWS, Azure, GCP)
- Monitoring services

---

## 🔄 **Complete Testing Strategy**

### **Phase 1: Development (Local)** 💻
```powershell
# You write code
# Run Promptfoo tests locally
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml

# Fix any issues
# Commit code
```

**Tools:**
- Promptfoo (security testing)
- pytest (unit tests)
- Manual testing

---

### **Phase 2: CI/CD (Automated)** 🤖
```yaml
# GitHub Actions runs automatically
- Run pytest
- Run Promptfoo tests
- If all pass → Deploy
- If any fail → Block deployment
```

**Tools:**
- GitHub Actions / GitLab CI
- Promptfoo (automated testing)
- pytest (unit tests)

---

### **Phase 3: Staging (Pre-Production)** 🧪
```
# Deploy to staging environment
# Run comprehensive tests
# Manual QA testing
# If all good → Deploy to production
```

**Tools:**
- Promptfoo (full test suite)
- Manual testing
- Load testing

---

### **Phase 4: Production (Live)** 🚀
```
# Users interact with your app
# LangSmith monitors every request
# Logs capture errors
# Alerts notify you of issues
```

**Tools:**
- **LangSmith** (you already have this!)
- **Sentry** (error tracking)
- **CloudWatch/Azure Monitor** (infrastructure)
- **Custom logging** (your logger)

---

## ✅ **What You Already Have in Production**

### **1. LangSmith Observability** 🔍
```python
# In your app.py
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer

# This monitors EVERY production request!
tracer = LangChainTracer(
    project_name="medical-chatbot-prod"
)
```

**What LangSmith does in production:**
- ✅ Tracks every user query
- ✅ Records LLM responses
- ✅ Measures latency
- ✅ Detects errors
- ✅ Provides analytics
- ✅ Alerts on issues

**Dashboard:** https://smith.langchain.com/

---

### **2. Content Analyzer** 🛡️
```python
# In your app.py
from src.content_analyzer.analyzer import ContentAnalyzer

analyzer = ContentAnalyzer()
result = analyzer.analyze_content(query)

if result.contains_pii:
    # Block request in production!
    return "Cannot process PII"
```

**What it does in production:**
- ✅ Detects PII in real-time
- ✅ Blocks toxic content
- ✅ Validates medical queries
- ✅ Protects users

---

### **3. Logging** 📝
```python
# In your app.py
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info(f"User query: {query}")
logger.error(f"Error: {error}")
```

**What it does in production:**
- ✅ Records all requests
- ✅ Tracks errors
- ✅ Helps debugging
- ✅ Audit trail

---

## 🔧 **How to Use Promptfoo in Your Workflow**

### **1. Local Development** 💻
```powershell
# Before committing code
promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml

# If tests pass → commit
# If tests fail → fix issues
```

---

### **2. CI/CD Pipeline** 🤖

**Create `.github/workflows/test.yml`:**
```yaml
name: Test Medical Chatbot

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run pytest
        run: pytest tests/unit/
      
      - name: Install Promptfoo
        run: npm install -g promptfoo
      
      - name: Run Promptfoo Security Tests
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          promptfoo eval -c tests/promptfoo/promptfoo-security-simple.yaml
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: tests/promptfoo/results/
```

**What this does:**
- ✅ Runs on every commit
- ✅ Blocks bad code from merging
- ✅ Ensures security before deployment
- ✅ Saves test results

---

### **3. Scheduled Testing** ⏰

**Create `.github/workflows/scheduled-tests.yml`:**
```yaml
name: Scheduled Security Audit

on:
  schedule:
    # Run every day at 2 AM
    - cron: '0 2 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  security-audit:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Install Promptfoo
        run: npm install -g promptfoo
      
      - name: Run Full Security Audit
        env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          promptfoo eval -c tests/promptfoo/promptfoo-redteam.yaml
      
      - name: Send results to Slack
        if: failure()
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "🚨 Security audit failed! Check GitHub Actions."
            }
```

**What this does:**
- ✅ Runs daily security audits
- ✅ Tests against production-like data
- ✅ Alerts team if issues found
- ✅ Catches regressions

---

## 📊 **Production Monitoring (What You Need)**

### **1. LangSmith (You Already Have!)** ✅
```python
# Already in your app.py
from langsmith import Client

client = Client()

# Monitors every request automatically!
```

**Features:**
- Real-time request tracking
- Error detection
- Performance metrics
- User feedback collection
- A/B testing

**Dashboard:** https://smith.langchain.com/

---

### **2. Add Production Guardrails** 🛡️

**Create `src/guardrails/production_monitor.py`:**
```python
"""
Production monitoring and guardrails
"""
from typing import Dict, Any
from src.utils.logger import get_logger
from src.content_analyzer.analyzer import ContentAnalyzer

logger = get_logger(__name__)

class ProductionGuardrails:
    """Monitor and protect production requests"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.blocked_count = 0
        self.total_count = 0
    
    def validate_request(self, query: str) -> Dict[str, Any]:
        """
        Validate user request before processing
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "flags": list
            }
        """
        self.total_count += 1
        flags = []
        
        # Check for PII
        result = self.analyzer.analyze_content(query)
        if result.contains_pii:
            self.blocked_count += 1
            logger.warning(f"Blocked PII request: {query[:50]}...")
            return {
                "allowed": False,
                "reason": "Request contains personal information",
                "flags": ["pii"]
            }
        
        # Check for toxic content
        if result.is_toxic:
            self.blocked_count += 1
            logger.warning(f"Blocked toxic request: {query[:50]}...")
            return {
                "allowed": False,
                "reason": "Request contains inappropriate content",
                "flags": ["toxic"]
            }
        
        # Check query length
        if len(query) > 1000:
            self.blocked_count += 1
            logger.warning(f"Blocked long request: {len(query)} chars")
            return {
                "allowed": False,
                "reason": "Request too long",
                "flags": ["length"]
            }
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "Request validated",
            "flags": []
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get production metrics"""
        block_rate = (self.blocked_count / self.total_count * 100) if self.total_count > 0 else 0
        return {
            "total_requests": self.total_count,
            "blocked_requests": self.blocked_count,
            "block_rate_percent": block_rate
        }
```

**Use in `app.py`:**
```python
from src.guardrails.production_monitor import ProductionGuardrails

guardrails = ProductionGuardrails()

def process_query(query: str):
    # Validate request
    validation = guardrails.validate_request(query)
    
    if not validation["allowed"]:
        logger.warning(f"Request blocked: {validation['reason']}")
        return f"I cannot process this request: {validation['reason']}"
    
    # Process normally
    response = chatbot.process(query)
    return response
```

---

### **3. Add Error Tracking (Sentry)** 🚨

**Install:**
```powershell
pip install sentry-sdk
```

**Add to `app.py`:**
```python
import sentry_sdk

# Initialize Sentry
sentry_sdk.init(
    dsn="your-sentry-dsn",
    environment="production",
    traces_sample_rate=1.0,
)

# Errors are automatically tracked!
```

---

### **4. Add Health Checks** ❤️

**Create `src/health/health_check.py`:**
```python
"""
Production health checks
"""
from typing import Dict, Any
import time

class HealthCheck:
    """Monitor system health"""
    
    def check_vectorstore(self) -> bool:
        """Check if vector store is accessible"""
        try:
            # Try to load vector store
            from src.memory.connect_memory import load_vector_store
            vectorstore = load_vector_store()
            return True
        except Exception as e:
            return False
    
    def check_llm(self) -> bool:
        """Check if LLM is accessible"""
        try:
            from src.model.llm_factory import create_llm
            llm = create_llm()
            # Try a simple call
            response = llm.invoke("test")
            return True
        except Exception as e:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        start_time = time.time()
        
        vectorstore_ok = self.check_vectorstore()
        llm_ok = self.check_llm()
        
        elapsed = time.time() - start_time
        
        status = "healthy" if (vectorstore_ok and llm_ok) else "degraded"
        
        return {
            "status": status,
            "checks": {
                "vectorstore": "ok" if vectorstore_ok else "error",
                "llm": "ok" if llm_ok else "error"
            },
            "response_time_ms": int(elapsed * 1000)
        }
```

**Add endpoint in `app.py`:**
```python
from src.health.health_check import HealthCheck

health_checker = HealthCheck()

# Add health check endpoint
@app.route('/health')
def health():
    status = health_checker.get_status()
    return jsonify(status)
```

---

## 📋 **Complete Testing & Monitoring Strategy**

| Phase | Tool | Purpose | Where |
|-------|------|---------|-------|
| **Development** | Promptfoo | Security testing | Local |
| **Development** | pytest | Unit testing | Local |
| **CI/CD** | Promptfoo | Automated testing | GitHub Actions |
| **CI/CD** | pytest | Automated testing | GitHub Actions |
| **Staging** | Promptfoo | Pre-deploy validation | Staging server |
| **Production** | LangSmith | Request monitoring | Production |
| **Production** | Guardrails | Real-time protection | Production |
| **Production** | Sentry | Error tracking | Production |
| **Production** | Health Checks | System monitoring | Production |
| **Production** | Logs | Audit trail | Production |

---

## ✅ **Summary**

### **Promptfoo is for:**
- ✅ Development testing
- ✅ CI/CD validation
- ✅ Pre-deployment checks
- ✅ Security audits
- ❌ NOT for production monitoring

### **Production monitoring uses:**
- ✅ LangSmith (you have this!)
- ✅ Content Analyzer (you have this!)
- ✅ Logging (you have this!)
- 📝 TODO: Add Sentry
- 📝 TODO: Add health checks
- 📝 TODO: Add production guardrails

### **Workflow:**
```
1. Write code
2. Run Promptfoo locally → Fix issues
3. Commit code
4. CI/CD runs Promptfoo → Blocks if fails
5. Deploy to staging → Run full tests
6. Deploy to production → LangSmith monitors
7. Users interact → Guardrails protect
8. Errors happen → Sentry alerts
9. Daily → Scheduled Promptfoo audit
```

**Promptfoo ensures quality BEFORE deployment.**  
**LangSmith ensures quality DURING production.** 

**You need both!** 🚀

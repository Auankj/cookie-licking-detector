# 🍪 Cookie Licking Detector

**Automatically detect and manage stale GitHub issue claims to keep your open source project healthy**

> "Cookie-licking" is when someone claims a GitHub issue but never follows through, blocking other contributors. This system detects claim patterns in issue comments and automatically tracks, nudges, and releases stale claims.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 What Problem Does This Solve?

Open source maintainers often face "cookie lickers" - contributors who claim issues with comments like "I'll work on this!" but never submit a PR. This blocks other contributors and creates frustration.

**Cookie Licking Detector** automatically:
- ✅ Detects claim patterns in issue comments with 95% confidence
- ✅ Tracks claim activity and monitors progress  
- ✅ Sends polite nudges after configurable grace periods (default: 7 days)
- ✅ Auto-releases stale claims so others can contribute
- ✅ Provides analytics on claim patterns and contributor behavior

---

## ✨ Features

### 🧠 Intelligent Pattern Detection
- **Multi-level confidence scoring**: 95% for direct claims ("I'll take this"), 90% for assignments ("Please assign to me"), 70% for questions
- **Context-aware analysis**: Boosts confidence when maintainers reply
- **False positive prevention**: Ignores comments like "This looks interesting"

### 📊 Claim Lifecycle Management
- **Automatic tracking**: Detects claims from GitHub webhook events
- **Progress monitoring**: Tracks linked PRs and commits
- **Grace period system**: Configurable timeframes before nudging (default: 7 days)
- **Smart notifications**: Polite email and GitHub comment reminders
- **Auto-release**: Frees up issues after multiple failed nudges

### 🎨 Web Dashboard
- **Real-time stats**: Active claims, repository health, contributor metrics
- **Repository management**: Register and monitor multiple GitHub repos
- **Claim insights**: View all claims with status, confidence scores, and timelines
- **User analytics**: Track contributor patterns and reliability

### 🏗️ Production-Ready Architecture
- **FastAPI** backend with async/await support
- **PostgreSQL** database with optimized indexes
- **Redis** for job queues and distributed locking
- **Celery** for background task processing
- **GitHub webhooks** for real-time event processing
- **SendGrid** integration for email notifications

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **PostgreSQL 14+**
- **Redis 6+**
- **GitHub Personal Access Token** ([Create one here](https://github.com/settings/tokens))
- **SendGrid API Key** (optional, for email notifications)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/auankj/cookie-licking-detector.git
cd cookie-licking-detector
```

### 2️⃣ Set Up Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `.env` with your configuration:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost/cookie_detector

# Redis
REDIS_URL=redis://localhost:6379/0

# GitHub
GITHUB_TOKEN=ghp_your_github_personal_access_token

# SendGrid (optional)
SENDGRID_API_KEY=SG.your_sendgrid_api_key
SENDGRID_FROM_EMAIL=noreply@yourdomain.com

# Security
SECRET_KEY=your_secret_key_here
```

### 3️⃣ Initialize Database

```bash
# Run Alembic migrations
alembic upgrade head

# Create a test user (optional)
python create_test_user.py
```

### 4️⃣ Start Services

**Terminal 1 - API Server:**
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**
```bash
python3 -m celery -A app.core.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Periodic Tasks):**
```bash
python3 -m celery -A app.core.celery_app beat --loglevel=info
```

### 5️⃣ Access the Application

- 🌐 **Web Dashboard**: http://localhost:8000/
- 📚 **API Documentation**: http://localhost:8000/docs
- 🔍 **ReDoc**: http://localhost:8000/redoc
- ❤️ **Health Check**: http://localhost:8000/health

---

## 🔌 Setting Up GitHub Webhooks

To receive real-time claim detection, configure webhooks for your repositories:

### Option 1: Using ngrok (Development)

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Copy the https URL (e.g., https://abc123.ngrok-free.app)
```

### Option 2: Production Server

Use your production domain (e.g., `https://yourdomain.com`)

### Configure Webhook on GitHub

1. Go to your repository → **Settings** → **Webhooks** → **Add webhook**
2. **Payload URL**: `https://your-url.com/api/v1/webhooks/github`
3. **Content type**: `application/json`
4. **Events**: Select "Issue comments"
5. **Active**: ✅ Check this box
6. Click **Add webhook**

### Register Repository in Dashboard

1. Login to http://localhost:8000/
2. Go to **Repositories** tab
3. Click **Add Repository**
4. Enter: `owner/repo` (e.g., `auankj/my-project`)
5. Configure grace period and nudge settings
6. Click **Register**

🎉 **You're all set!** The system will now detect claims automatically.

---

## � How It Works

### 1. **Claim Detection**

When someone comments on an issue:
```
"I'll work on this!" → 95% confidence CLAIM detected
"Can I take this?" → 70% confidence CLAIM detected  
"This looks interesting" → 0% (not a claim)
```

The system analyzes the comment using pattern matching and creates a claim record.

### 2. **Progress Tracking**

The system monitors:
- ✅ Linked pull requests
- ✅ Commit activity
- ✅ Issue comments from the claimant

Any activity resets the grace period timer.

### 3. **Nudge System**

After the grace period (default: 7 days):
1. **First nudge**: Polite reminder via GitHub comment and email
2. **Wait period**: Another grace period
3. **Second nudge**: Final reminder
4. **Auto-release**: If still no activity, claim is released

### 4. **Analytics**

Track contributor behavior:
- Active claims per repository
- Average claim duration
- Completion rates
- Repeat "cookie lickers"

---

## 🛠️ Development

### Project Structure

```
cookie-licking-detector/
├── app/
│   ├── api/              # API routes
│   │   ├── auth_routes.py
│   │   ├── repository_routes.py
│   │   ├── claim_routes.py
│   │   └── webhook_routes.py
│   ├── core/             # Core configuration
│   │   ├── config.py
│   │   ├── celery_app.py
│   │   └── security.py
│   ├── db/               # Database
│   │   ├── models/       # SQLAlchemy models
│   │   └── session.py
│   ├── services/         # Business logic
│   │   ├── github_service.py
│   │   ├── claim_detector.py
│   │   └── notification_service.py
│   ├── tasks/            # Celery tasks
│   │   ├── comment_analysis.py
│   │   ├── nudge_tasks.py
│   │   └── progress_tracking.py
│   └── main.py           # FastAPI application
├── alembic/              # Database migrations
├── static/               # Frontend assets
│   └── webapp/           # Web dashboard
├── tests/                # Test suite
├── .env                  # Environment variables
├── requirements.txt      # Python dependencies
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/unit/test_claim_detector.py
```

### Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black app/ tests/

# Sort imports
isort app/ tests/

# Lint
flake8 app/ tests/

# Type check
mypy app/
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

### 1. Fork the Repository

Click the **Fork** button at the top of this page.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/cookie-licking-detector.git
cd cookie-licking-detector
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Make Your Changes

- Write clean, documented code
- Add tests for new features
- Update documentation as needed
- Follow the existing code style

### 5. Test Your Changes

```bash
# Run tests
pytest

# Check code style
black app/ --check
flake8 app/
```

### 6. Commit and Push

```bash
git add .
git commit -m "feat: Add your feature description"
git push origin feature/your-feature-name
```

### 7. Open a Pull Request

Go to your fork on GitHub and click **New Pull Request**.

### Contribution Guidelines

- **Bug Reports**: Open an issue with detailed steps to reproduce
- **Feature Requests**: Describe the use case and expected behavior
- **Code Contributions**: Follow the style guide and add tests
- **Documentation**: Improvements to docs are always welcome!

---

## 📊 API Reference

### Authentication

```bash
# Login
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password"
}

# Response: JWT token
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Repositories

```bash
# List repositories
GET /api/v1/repositories
Authorization: Bearer <token>

# Register repository
POST /api/v1/repositories
{
  "owner": "auankj",
  "name": "my-project",
  "grace_period_days": 7,
  "max_nudges": 2
}
```

### Claims

```bash
# List all claims
GET /api/v1/claims?status=ACTIVE

# Get claim details
GET /api/v1/claims/{claim_id}

# Manually release claim
POST /api/v1/claims/{claim_id}/release
```

### Webhooks

```bash
# GitHub webhook endpoint
POST /api/v1/webhooks/github
```

For complete API documentation, visit http://localhost:8000/docs

---

## 🔒 Security

### Reporting Security Issues

**Please do not open public issues for security vulnerabilities.**

Email security concerns to: [your-email@example.com]

### Security Features

- ✅ JWT authentication with secure token handling
- ✅ Password hashing with bcrypt
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ CORS configuration
- ✅ Rate limiting on API endpoints
- ✅ Environment variable protection (.env not committed)
- ✅ Webhook signature verification

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## � Acknowledgments

- Inspired by the need to keep open source projects healthy and contributor-friendly
- Built with [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), and [Celery](https://docs.celeryq.dev/)
- Pattern detection inspired by common GitHub contribution patterns

---

## 📞 Support

- **Documentation**: Check the [docs](./docs) folder
- **Issues**: [GitHub Issues](https://github.com/auankj/cookie-licking-detector/issues)
- **Discussions**: [GitHub Discussions](https://github.com/auankj/cookie-licking-detector/discussions)

---

## 🗺️ Roadmap

- [ ] Machine learning-based pattern detection
- [ ] Slack/Discord integration for notifications
- [ ] Multi-language support
- [ ] Mobile app for claim management
- [ ] Browser extension for maintainers
- [ ] Advanced analytics and reporting
- [ ] GitLab and Bitbucket support

---

**Made with ❤️ for the open source community**
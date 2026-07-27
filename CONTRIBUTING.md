# Contributing to NEXUS

First off, thank you for considering contributing to NEXUS! It's people like you that make NEXUS such a great tool.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct: be respectful, collaborative, and constructive.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues — your problem might already be reported. When you create a bug report, please include:

- A clear, descriptive title
- Steps to reproduce the behavior
- What you expected vs. what actually happened
- Your environment (OS, Python version, Node version)
- Any relevant logs or screenshots

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Enhancements

Feature requests are welcome. Please use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and provide:

- A clear use case
- Why this would benefit most users
- How it should work

### Your First Code Contribution

#### Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/nexus.git
cd nexus
cp .env.example .env

# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

#### Pull Request Process

1. **Fork** the repo and create your branch from `main`:
   ```bash
   git checkout -b feat/your-feature-name
   # or
   git checkout -b fix/your-bug-name
   ```

2. **Follow the commit convention** (we use [Conventional Commits](https://www.conventionalcommits.org)):
   ```
   feat: add monte carlo scenario export
   fix: resolve null pointer in causal engine
   docs: update API reference for /analyze endpoint
   refactor: split demand planning engine into sub-modules
   ```

3. **Backend standards**:
   - All new endpoints must have type hints and docstrings
   - Authentication-sensitive routes must use `Depends(require_auth)`
   - New engines go in `backend/app/engines/` or a new `features/` domain
   - No hardcoded secrets or API keys

4. **Frontend standards**:
   - Use TypeScript — no `any` types
   - Shared components go in `frontend/components/`
   - Page-specific components stay inside the page directory

5. **Test your changes** before submitting:
   ```bash
   # Backend: verify import loads cleanly
   cd backend
   python -c "from app.main import app; print('OK')"

   # Frontend: verify build passes
   cd frontend
   npm run build
   ```

6. **Open a Pull Request** with:
   - A descriptive title
   - What changed and why
   - Screenshots for UI changes

## Project Structure

See [README.md](README.md#project-structure) for the full directory breakdown.

## Need Help?

Open a [Discussion](https://github.com/YOUR_USERNAME/nexus/discussions) — we're happy to help you find the right place to contribute.

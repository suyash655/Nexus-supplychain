# Contributing to NEXUS

Thank you for your interest in contributing to NEXUS. This project focuses on high-reliability ML pipelines, explainable supply chain analytics, and human-in-the-loop agent systems.

## Code of Conduct

All contributors are expected to uphold a welcoming, respectful, and constructive environment.

## Ways to Contribute

- **Reporting Bugs:** File an issue using the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md).
- **Proposing Enhancements:** Submit proposals using the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).
- **Submitting Code:** Pull requests are welcomed for bug fixes, test expansions, and documentation clarifications.

## Development Setup

### 1. Repository Setup
```bash
git clone https://github.com/suyash655/Nexus-supplychain.git
cd Nexus-supplychain
cp .env.example backend/.env
```

### 2. Backend Environment (Python 3.11+)
```bash
cd backend
python -m venv ../.venv
# Linux/macOS:
source ../.venv/bin/activate
# Windows:
..\.venv\Scripts\activate

pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Run backend tests:
```bash
pytest backend/tests -v
```

### 3. Frontend Environment (Node.js 20+)
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Run frontend tests:
```bash
npm test
npm run lint
```

## Pull Request Guidelines

1. **Focused Changes:** Keep commits atomic and logically separated. Follow conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).
2. **Deterministic Behavior:** Never introduce unvalidated external LLM dependencies in core pathways; maintain offline fallback capability.
3. **Tests:** Ensure existing tests pass and include unit or regression tests for new logic.
4. **Security:** Do not commit secrets, database dumps, or credentials.

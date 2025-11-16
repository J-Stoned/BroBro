# Contributing to BroBro

Thank you for your interest in contributing to BroBro! This document provides guidelines and instructions for contributing to the project.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 20+** (LTS) - [Download](https://nodejs.org/)
- **Python 3.9+** - [Download](https://www.python.org/)
- **Git** - [Download](https://git-scm.com/)

### Initial Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd brobro
   ```

2. **Install dependencies**
   ```bash
   # Install root dependencies
   npm install

   # Install frontend dependencies
   cd web/frontend
   npm install
   cd ../..

   # Install backend dependencies
   cd web/backend
   pip install -r requirements.txt
   cd ../..
   ```

3. **Configure environment variables**
   ```bash
   # Copy example files
   cp .env.example .env
   cp web/backend/.env.example web/backend/.env
   cp web/frontend/.env.development web/frontend/.env.development
   ```

4. **Fill in required credentials in `.env` files**
   - `GOOGLE_API_KEY` - From [Google AI Studio](https://aistudio.google.com/apikey)
   - `GEMINI_FILE_SEARCH_STORE_ID` - Your knowledge base store ID
   - `ANTHROPIC_API_KEY` - From [Anthropic Console](https://console.anthropic.com/account/keys)

## Development Workflow

### Code Organization

The project is organized into three main areas:

- **Frontend** (`web/frontend/`) - React + Vite + TypeScript
- **Backend** (`web/backend/`) - FastAPI + Python
- **Desktop App** (`brobro-desktop/`) - Electron + React

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards below
   - Keep commits focused and descriptive
   - Test your changes thoroughly

3. **Run tests locally**
   ```bash
   # Frontend tests
   cd web/frontend
   npm test

   # Backend tests
   cd web/backend
   pytest
   ```

4. **Check code quality**
   ```bash
   # Lint frontend
   cd web/frontend
   npm run lint

   # Format code
   npm run format
   ```

## Coding Standards

### TypeScript/JavaScript

**File Naming:**
- Components: `PascalCase.jsx` (e.g., `ChatContainer.jsx`)
- Utilities: `camelCase.js` (e.g., `apiClient.js`)
- Configuration: `kebab-case.js` (e.g., `vite-config.js`)

**Code Style:**
- Use `const` by default, `let` when needed, never `var`
- Use arrow functions for callbacks
- Prefer `async/await` over `.then()` chains
- Use meaningful variable names

**Example:**
```javascript
// Good
const handleSearch = async (query) => {
  try {
    const results = await apiClient.search(query);
    setResults(results);
  } catch (error) {
    logger.error('Search failed', error);
  }
};

// Avoid
let res;
function srch(q) {
  apiClient.search(q).then(r => {
    res = r;
  });
}
```

### Python

**File Naming:**
- Modules: `snake_case.py` (e.g., `gemini_search.py`)
- Classes: `PascalCase` (e.g., `class GeminiSearchClient`)

**Code Style:**
- Follow PEP 8 guidelines
- Use type hints for function parameters and returns
- Use logging instead of print statements
- Handle exceptions properly

**Example:**
```python
# Good
async def search(query: str, limit: int = 10) -> List[SearchResult]:
    """Search the knowledge base.

    Args:
        query: Search query string
        limit: Maximum number of results

    Returns:
        List of search results
    """
    try:
        results = await self.gemini_client.search(query, limit)
        return results
    except Exception as e:
        logger.error(f"Search failed: {query}", exc_info=True)
        raise
```

### React Components

**Component Structure:**
```javascript
import { useState, useEffect } from 'react';
import './ComponentName.css';

export const ComponentName = ({ prop1, prop2 }) => {
  const [state, setState] = useState(null);

  useEffect(() => {
    // Side effects
  }, []);

  const handleAction = () => {
    // Handler logic
  };

  return (
    <div className="component">
      {/* JSX */}
    </div>
  );
};
```

**Props Validation:**
- Use TypeScript for type safety
- Document complex props in JSDoc comments
- Use optional chaining (?.) for nested properties

## Commit Guidelines

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `refactor` - Code refactoring
- `test` - Tests
- `chore` - Build, dependencies, config

**Examples:**
```
feat(search): Add filters for search results
fix(api): Handle timeout errors gracefully
docs(contributing): Update development guide
refactor(components): Extract SearchBar to separate component
```

## Testing

### Frontend Tests

```bash
cd web/frontend
npm test
npm run test:watch     # Watch mode
npm run test:coverage  # Coverage report
```

**Testing Guidelines:**
- Write tests for new features
- Aim for 80%+ code coverage
- Use descriptive test names
- Test user interactions, not implementation details

### Backend Tests

```bash
cd web/backend
pytest
pytest --cov=.  # With coverage
pytest -v       # Verbose output
```

**Testing Guidelines:**
- Write tests for API endpoints
- Test error cases
- Use fixtures for test data
- Mock external services (Gemini API)

## Pull Request Process

1. **Before submitting:**
   - Ensure all tests pass
   - Run linting and formatting
   - Update documentation if needed
   - Test locally with multiple browsers/OSs

2. **Create pull request with:**
   - Clear title describing the change
   - Description of what changed and why
   - Reference related issues
   - Screenshots for UI changes

3. **PR checklist:**
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] No breaking changes (or clearly noted)
   - [ ] Commit messages are descriptive

4. **After submission:**
   - Address review comments
   - Resolve conflicts if any
   - Re-request review when ready

## Reporting Bugs

### Bug Report Template

```markdown
**Description**
Brief description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Expected vs actual result

**Environment**
- OS: Windows/Mac/Linux
- Node.js version:
- Browser (if applicable):

**Additional Context**
Logs, screenshots, or other helpful info
```

## Architecture Decisions

When making significant architectural changes:

1. Create an issue to discuss the proposed change
2. Document the decision in `docs/architecture/`
3. Update relevant documentation
4. Get approval before implementing

## Resources

- **Architecture:** [docs/architecture.md](docs/architecture.md)
- **API Documentation:** http://localhost:8000/docs (when running)
- **Frontend Setup:** [web/frontend/](web/frontend/)
- **Backend Setup:** [web/backend/](web/backend/)

## Questions?

- Check existing issues and discussions
- Review the documentation in `docs/`
- Ask in project discussions

## Code of Conduct

Please be respectful, inclusive, and constructive in all interactions. We're building this together!

---

**Thank you for contributing to BroBro!** 🚀

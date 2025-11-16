# Coding Standards

This document will define the coding standards for the GHL Wiz project.

## TypeScript Standards

### Naming Conventions
- **Classes**: PascalCase (e.g., `OAuthManager`, `RateLimiter`)
- **Interfaces**: PascalCase with descriptive names (e.g., `GHLContact`, `WorkflowConfig`)
- **Functions/Methods**: camelCase (e.g., `getAccessToken`, `createWorkflow`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)
- **Variables**: camelCase (e.g., `contactId`, `workflowData`)

### Code Organization
- One class/interface per file
- Group related functionality in modules
- Use barrel exports (index.ts) for clean imports
- Keep functions small and focused (single responsibility)

### Error Handling
- Always use try-catch for async operations
- Provide meaningful error messages
- Log errors with context
- Never swallow errors silently

### Documentation
- JSDoc comments for all public functions and classes
- Include parameter descriptions and return types
- Document edge cases and assumptions
- Add examples for complex functionality

## JavaScript Standards

### Module System
- Use ES modules (`import`/`export`)
- Avoid CommonJS (`require`) in new code
- Use named exports for better refactoring

### Async/Await
- Prefer async/await over raw promises
- Always handle promise rejections
- Use Promise.all() for parallel operations

## Testing Standards

### Unit Tests
- Test file naming: `*.test.ts` or `*.spec.ts`
- One test file per source file
- Use descriptive test names: `describe('ClassName', () => { it('should do X when Y', ...) })`
- Aim for 80%+ code coverage

### Integration Tests
- Place in `tests/integration/`
- Test real MCP server interactions
- Mock external APIs (GHL, YouTube)

## Code Quality Tools

### ESLint
- Configuration: `.eslintrc.json`
- Run before commits: `npm run lint`
- Fix auto-fixable issues: `npm run lint:fix`

### Prettier
- Configuration: `.prettierrc.json`
- Format on save (VS Code setting)
- Run before commits: `npm run format`

### TypeScript Compiler
- Strict mode enabled
- No implicit any
- Strict null checks
- No unused locals/parameters

## Git Standards

### Commit Messages
- Format: `<type>(<scope>): <subject>`
- Types: feat, fix, docs, style, refactor, test, chore
- Examples:
  - `feat(mcp): add OAuth token refresh`
  - `fix(rate-limiter): handle burst limit correctly`
  - `docs(readme): update installation instructions`

### Branching
- Main branch: `main`
- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Release branches: `release/v1.0.0`

## File Organization

See [source-tree.md](./source-tree.md) for complete project structure.

---

**Note:** This document will be expanded during Epic 1 (Story 1.1: Project Structure & Configuration)

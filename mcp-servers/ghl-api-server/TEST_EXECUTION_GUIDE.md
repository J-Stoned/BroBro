# Test Execution Guide - Story 3.1

**QA Engineer:** Claude Agent
**Developer:** James Rodriguez
**Story:** 3.1 - MCP Server Foundation
**Date:** 2025-10-26

---

## Quick Start

### For James (Developer)

After implementing each component, run the corresponding test:

```bash
# Install test dependencies first
npm install

# Test logger (after implementing src/utils/logger.ts)
npm test -- tests/utils/logger.test.ts

# Test server (after implementing src/index.ts)
npm test -- tests/index.test.ts

# Test test_connection tool (after implementing src/tools/test.ts)
npm run test:integration

# Run all tests with coverage
npm run test:coverage
```

### For QA Engineer

Monitor test status as components are delivered:

```bash
# Watch mode for continuous validation
npm run test:watch

# Generate coverage report after each component
npm run test:coverage

# Run specific test suite
npm test -- <path-to-test-file>
```

---

## Component-by-Component Testing

### 1. Logger Utility (AC #9)

**File:** `src/utils/logger.ts`
**Tests:** `tests/utils/logger.test.ts`
**Test Count:** 25 tests

#### Run Tests
```bash
npm test -- tests/utils/logger.test.ts
```

#### Success Criteria
- ✅ All 4 log levels work (DEBUG, INFO, WARN, ERROR)
- ✅ Timestamps are ISO 8601 format
- ✅ Log output format is `[timestamp] [level] message`
- ✅ ERROR logs go to console.error
- ✅ WARN logs go to console.warn
- ✅ INFO/DEBUG logs go to console.log

#### Expected Output
```
PASS tests/utils/logger.test.ts
  Logger Utility
    Log Levels
      ✓ should support DEBUG log level
      ✓ should support INFO log level
      ✓ should support WARN log level
      ✓ should support ERROR log level
      ...
    Timestamp Formatting
      ✓ should include ISO 8601 timestamp in log output
      ...

Test Suites: 1 passed, 1 total
Tests:       25 passed, 25 total
```

#### Troubleshooting
- **Import errors**: Ensure `src/utils/logger.ts` exports `logger` and `LogLevel`
- **Tests fail**: Uncomment TODO sections in test file
- **Format mismatch**: Verify logger format matches `[timestamp] [level] message`

---

### 2. Error Handler (Optional for Story 3.1)

**File:** `src/utils/error-handler.ts`
**Tests:** `tests/utils/error-handler.test.ts`
**Test Count:** 30+ tests

**Note:** Error handler is not in Story 3.1 AC but is recommended for production readiness.

#### Run Tests
```bash
npm test -- tests/utils/error-handler.test.ts
```

#### Success Criteria
- ✅ Error classification works (network, auth, rate limit, validation)
- ✅ Retry logic with exponential backoff
- ✅ Max retry limits respected
- ✅ Non-retryable errors fail immediately
- ✅ Error messages formatted with context

#### Skip If Not Implemented
If James defers error handler to a later story, skip these tests. All tests will pass with placeholder assertions.

---

### 3. MCP Server Initialization (AC #4, #5, #7)

**File:** `src/index.ts`
**Tests:** `tests/index.test.ts`
**Test Count:** 35+ tests

#### Run Tests
```bash
npm test -- tests/index.test.ts
```

#### Success Criteria
- ✅ Server initializes with FastMCP
- ✅ Server name is `ghl-api`, version is `1.0.0`
- ✅ stdio transport configured
- ✅ HTTP transport scaffolded (commented out)
- ✅ Environment variables loaded
- ✅ Logger initialized before server start
- ✅ test_connection tool registered
- ✅ Server starts in <2 seconds
- ✅ Graceful shutdown on SIGTERM/SIGINT
- ✅ MCP handshake successful

#### Expected Output
```
PASS tests/index.test.ts
  MCP Server Entry Point
    Server Initialization
      ✓ should initialize FastMCP server with correct configuration
      ✓ should configure stdio transport by default
      ...
    Server Startup
      ✓ should start server successfully
      ✓ should start in under 2 seconds
      ...

Test Suites: 1 passed, 1 total
Tests:       35 passed, 35 total
```

#### Troubleshooting
- **Server doesn't start**: Check logger is imported correctly
- **Handshake fails**: Verify FastMCP is properly configured
- **Slow startup**: Ensure no blocking I/O in initialization

---

### 4. test_connection Tool (AC #8)

**File:** `src/tools/test.ts`
**Tests:** `tests/integration/mcp-tools.test.ts`
**Test Count:** 30+ tests

#### Run Tests
```bash
npm run test:integration
```

#### Success Criteria
- ✅ Tool invocation successful
- ✅ Accepts empty object `{}`
- ✅ Returns `{ status, server, version, timestamp }`
- ✅ `status` is `"connected"`
- ✅ `server` is `"ghl-api"`
- ✅ `version` is `"1.0.0"`
- ✅ `timestamp` is ISO 8601 format
- ✅ Zod validation works
- ✅ Tool completes in <100ms
- ✅ MCP protocol compliance

#### Expected Response Format
```json
{
  "status": "connected",
  "server": "ghl-api",
  "version": "1.0.0",
  "timestamp": "2025-10-26T12:34:56.789Z"
}
```

#### Expected Output
```
PASS tests/integration/mcp-tools.test.ts
  MCP Tools Integration Tests
    test_connection Tool
      Tool Invocation
        ✓ should successfully invoke test_connection tool
        ✓ should accept empty object as input
        ...
      Response Format
        ✓ should return status="connected" on success
        ✓ should return ISO 8601 timestamp in response
        ...

Test Suites: 1 passed, 1 total
Tests:       30 passed, 30 total
```

#### Troubleshooting
- **Tool not found**: Ensure tool is registered in `src/index.ts`
- **Wrong response format**: Verify handler returns correct object structure
- **Validation errors**: Check Zod schema matches empty object `z.object({})`

---

## Full Test Suite Execution

### After All Components Complete

```bash
npm run test:coverage
```

### Expected Coverage Report

```
---------------------------|---------|----------|---------|---------|-------------------
File                       | % Stmts | % Branch | % Funcs | % Lines | Uncovered Line #s
---------------------------|---------|----------|---------|---------|-------------------
All files                  |   85.71 |    83.33 |   87.50 |   85.71 |
 src                       |   90.00 |    85.00 |   92.00 |   90.00 |
  index.ts                 |   90.00 |    85.00 |   92.00 |   90.00 | 45-47
 src/tools                 |  100.00 |   100.00 |  100.00 |  100.00 |
  test.ts                  |  100.00 |   100.00 |  100.00 |  100.00 |
 src/utils                 |   91.00 |    87.00 |   89.00 |   91.00 |
  logger.ts                |   92.00 |    88.00 |   90.00 |   92.00 | 67-69
  error-handler.ts         |   90.00 |    86.00 |   88.00 |   90.00 | 102-105
---------------------------|---------|----------|---------|---------|-------------------
```

**Threshold:** Must meet >80% coverage on all metrics (global threshold in `jest.config.js`)

---

## Activating Tests (For QA)

Tests are written with `TODO` comments to allow implementation to proceed first.

### To Activate a Test Suite

1. James completes implementation (e.g., `src/utils/logger.ts`)
2. Open corresponding test file (`tests/utils/logger.test.ts`)
3. Find `// TODO: Import actual logger once implemented` sections
4. Uncomment the TODO code blocks
5. Remove or comment out placeholder `expect(true).toBe(true)`
6. Run tests: `npm test -- tests/utils/logger.test.ts`
7. Fix any failures with James
8. Achieve green tests

### Example: Activating Logger Tests

**Before (Placeholder):**
```typescript
it('should support INFO log level', async () => {
  // TODO: Import actual logger once implemented
  // const { logger } = await import('../../src/utils/logger.js');
  // logger.info('Info message');
  // expect(consoleLogSpy).toHaveBeenCalled();

  expect(true).toBe(true); // Placeholder until implementation
});
```

**After (Activated):**
```typescript
it('should support INFO log level', async () => {
  const { logger } = await import('../../src/utils/logger.js');
  logger.info('Info message');
  expect(consoleLogSpy).toHaveBeenCalled();
  const logOutput = consoleLogSpy.mock.calls[0][0] as string;
  expect(logOutput).toContain('[INFO]');
  expect(logOutput).toContain('Info message');
});
```

---

## Test Execution Checklist

Use this checklist to track validation progress:

### Phase 1: Utilities
- [ ] Logger tests run and pass
- [ ] Logger coverage >90%
- [ ] Error handler tests run (if implemented)
- [ ] Error handler coverage >85% (if implemented)

### Phase 2: Server
- [ ] Server initialization tests pass
- [ ] Server starts in <2 seconds
- [ ] MCP handshake successful
- [ ] Graceful shutdown works
- [ ] Server coverage >85%

### Phase 3: Tools
- [ ] test_connection tool invocation works
- [ ] Response format correct
- [ ] Zod validation works
- [ ] Tool completes in <100ms
- [ ] Tool coverage 100%

### Phase 4: Integration
- [ ] Full test suite passes
- [ ] Coverage >80% globally
- [ ] No TypeScript errors
- [ ] No linting errors
- [ ] All 10 ACs validated

---

## Continuous Validation

### Watch Mode (Recommended for Active Development)

```bash
npm run test:watch
```

This will:
- Re-run tests automatically when files change
- Show only failed tests after first run
- Provide instant feedback to James

### CI Mode (For Automated Testing)

```bash
npm run test:ci
```

This will:
- Run all tests once
- Generate coverage report
- Use 2 workers for parallel execution
- Exit with error code if tests fail

---

## Common Issues and Solutions

### Issue: "Cannot find module 'src/utils/logger.js'"
**Solution:** File not yet implemented. Tests will pass with placeholders until activated.

### Issue: Tests timing out
**Solution:**
- Increase timeout in `jest.config.js` (currently 15000ms)
- Check for missing `await` on async operations
- Verify no open connections

### Issue: Coverage not meeting threshold
**Solution:**
- Add tests for uncovered branches
- Check for untested error paths
- Review coverage report: `npm run test:coverage`

### Issue: ES module import errors
**Solution:**
- Ensure `.js` extensions in all imports
- Verify `"type": "module"` in `package.json`
- Check `tsconfig.json` has `"module": "NodeNext"`

### Issue: Zod validation not working
**Solution:**
- Verify Zod is installed: `npm list zod`
- Check schema definition in tool
- Review error messages for validation issues

---

## Success Metrics

Before marking Story 3.1 as **COMPLETE**, ensure:

1. **All Tests Pass**
   - ✅ 0 failed tests
   - ✅ 90+ tests passing

2. **Coverage Thresholds Met**
   - ✅ >80% statement coverage
   - ✅ >80% branch coverage
   - ✅ >80% function coverage
   - ✅ >80% line coverage

3. **Performance Requirements**
   - ✅ Server starts in <2 seconds
   - ✅ test_connection completes in <100ms

4. **Quality Gates**
   - ✅ No TypeScript compilation errors
   - ✅ No ESLint warnings
   - ✅ All fixtures and mocks working
   - ✅ Test documentation complete

5. **Acceptance Criteria**
   - ✅ All 10 ACs validated (programmatically or manually)

---

## Next Steps

After Story 3.1 validation complete:

1. Mark all tests as ✅ PASSING in story documentation
2. Generate final coverage report
3. Document any deviations or issues found
4. Update `3.1.story.md` with QA results
5. Prepare test infrastructure for Story 3.2 (OAuth)

---

## Contact

**Questions or Issues?**
- QA Engineer: Claude Agent (Parallel Validation)
- Developer: James Rodriguez
- Scrum Master: Bob

**Last Updated:** 2025-10-26
**Status:** Test Infrastructure Ready - Awaiting Implementation

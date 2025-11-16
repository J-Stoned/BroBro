# Implementation Decisions Log

This document tracks architectural decisions, deviations from the original design, trade-offs, and lessons learned during the GHL API MCP Server implementation.

**Purpose:**
- Document why certain implementation choices were made
- Track deviations from the original architecture
- Record alternative approaches considered
- Capture lessons learned for future stories
- Provide context for future maintainers

**Update Frequency:**
- Add entries as significant decisions are made
- Review and update at story completion
- Archive completed stories' decisions

---

## Table of Contents

1. [Decision Format](#decision-format)
2. [Story 3.1 Decisions](#story-31-decisions)
3. [Story 3.2 Decisions](#story-32-decisions) (Future)
4. [Archived Decisions](#archived-decisions)

---

## Decision Format

Each decision entry should follow this template:

```markdown
### [DECISION-ID] Decision Title

**Date:** YYYY-MM-DD
**Story:** X.Y
**Decision Maker:** Name/Role
**Status:** Proposed | Accepted | Rejected | Superseded

**Context:**
What is the situation and context that led to this decision?

**Decision:**
What decision was made?

**Alternatives Considered:**
1. Alternative 1 - Why rejected
2. Alternative 2 - Why rejected

**Consequences:**
- Positive consequence 1
- Positive consequence 2
- Negative consequence 1 (trade-off)

**Rationale:**
Why was this decision made? What factors were most important?

**Implementation Notes:**
Any specific implementation details or gotchas.

**Related Decisions:**
- Links to related decisions
```

---

## Story 3.1 Decisions

### [DEC-3.1-001] ES Modules Instead of CommonJS

**Date:** 2025-10-26
**Story:** 3.1
**Decision Maker:** Alex Kim (Solutions Architect)
**Status:** Accepted

**Context:**
Node.js supports both CommonJS (require/module.exports) and ES Modules (import/export). The architecture document specified ES2022 target but didn't explicitly mandate module system. FastMCP documentation shows examples using both.

**Decision:**
Use ES Modules (`"type": "module"` in package.json) with NodeNext module resolution for the entire project.

**Alternatives Considered:**
1. **CommonJS** - Rejected because:
   - ES Modules are the future of Node.js
   - Better tree-shaking for smaller bundles
   - Better TypeScript integration
   - FastMCP examples prefer ES Modules

2. **Mixed (dual package)** - Rejected because:
   - Adds complexity
   - Not needed for MCP server (no external consumers)
   - Harder to maintain

**Consequences:**
- **Positive:**
  - Modern JavaScript syntax
  - Better TypeScript integration
  - Future-proof codebase
  - Clearer import/export semantics

- **Negative:**
  - Must include `.js` extensions in TypeScript imports
  - Slightly more complex Jest configuration
  - Some older Node.js libraries may have compatibility issues

**Rationale:**
ES Modules align with the ES2022 target, provide better long-term maintainability, and are the recommended approach for new Node.js projects.

**Implementation Notes:**
- All TypeScript imports must use `.js` extension (TypeScript resolves to `.ts` at compile time)
- Jest requires `ts-jest/presets/default-esm` preset
- `package.json` must include `"type": "module"`
- `tsconfig.json` must use `"module": "NodeNext"` and `"moduleResolution": "NodeNext"`

**Related Decisions:**
- DEC-3.1-002 (TypeScript configuration)

---

### [DEC-3.1-002] Strict TypeScript Configuration

**Date:** 2025-10-26
**Story:** 3.1
**Decision Maker:** Alex Kim (Solutions Architect)
**Status:** Accepted

**Context:**
TypeScript's `strict` mode enables multiple type-checking flags. While this can catch more errors, it also increases initial development friction.

**Decision:**
Enable `strict: true` in tsconfig.json from day one, along with additional strict checks.

**Alternatives Considered:**
1. **Loose mode initially** - Rejected because:
   - Technical debt accumulates quickly
   - Harder to add strictness later
   - Architecture document specifies strict mode

2. **Gradual strictness** - Rejected because:
   - Project is greenfield (no legacy code)
   - Better to establish strict patterns early

**Consequences:**
- **Positive:**
  - Catches type errors at compile time
  - Better IDE autocomplete
  - Prevents common runtime errors
  - Enforces best practices

- **Negative:**
  - Requires more type annotations
  - Some external libraries may need type assertions
  - Slightly slower initial development

**Rationale:**
Strict TypeScript is a best practice for new projects and prevents technical debt. Since this is a greenfield project, we can establish strict patterns from the start.

**Implementation Notes:**
```json
{
  "strict": true,
  "noImplicitAny": true,
  "strictNullChecks": true,
  "strictFunctionTypes": true,
  "strictBindCallApply": true,
  "strictPropertyInitialization": true,
  "noImplicitThis": true,
  "alwaysStrict": true
}
```

**Related Decisions:**
- DEC-3.1-001 (ES Modules)

---

### [DEC-3.1-003] Centralized Logger from Start

**Date:** 2025-10-26
**Story:** 3.1
**Decision Maker:** Alex Kim (Solutions Architect)
**Status:** Accepted

**Context:**
Story 3.1 only requires basic server setup and test connection tool. Logging could be deferred to later stories when OAuth and API calls are implemented.

**Decision:**
Implement centralized logger utility in Story 3.1, even though only basic logging is needed initially.

**Alternatives Considered:**
1. **Use console.log directly** - Rejected because:
   - Hard to add structured logging later
   - No timestamp standardization
   - No log level filtering
   - Harder to debug in production

2. **Third-party logger (Winston, Pino)** - Rejected because:
   - Adds dependency overhead for simple use case
   - Can migrate later if needed
   - Custom logger is <100 lines

**Consequences:**
- **Positive:**
  - Consistent log format from day one
  - Easier debugging
  - Timestamps on all log messages
  - Log levels (DEBUG, INFO, WARN, ERROR)
  - Easy to extend (file logging, filtering)

- **Negative:**
  - Extra ~100 lines of code
  - Another utility to maintain

**Rationale:**
Logging is critical for debugging MCP servers (which run in background). Establishing good logging practices early prevents debugging difficulties later.

**Implementation Notes:**
- Logger is singleton export: `export const logger = new Logger()`
- All console.log/error calls should go through logger
- Format: `[timestamp] [level] message`
- Timestamps use ISO 8601 format

**Related Decisions:**
- None

---

### [DEC-3.1-004] Organize Tools by Category in Separate Files

**Date:** 2025-10-26
**Story:** 3.1
**Decision Maker:** Alex Kim (Solutions Architect)
**Status:** Accepted

**Context:**
Story 3.1 only has one tool (`test_connection`). We could implement it directly in `src/index.ts` or create a separate tools file structure.

**Decision:**
Create `src/tools/` directory structure from the start, with `src/tools/test.ts` for test tools.

**Alternatives Considered:**
1. **All tools in src/index.ts** - Rejected because:
   - File will grow to 1000+ lines by Story 3.6
   - Hard to maintain
   - No clear separation of concerns

2. **One file per tool** - Rejected because:
   - Too many files (20+ by end of Epic 3)
   - Related tools should be grouped
   - Harder to import

**Consequences:**
- **Positive:**
  - Clear organization from day one
  - Each category (workflows, contacts, etc.) in one file
  - Easy to find and maintain tools
  - Better for code review

- **Negative:**
  - More files to create initially
  - Need to import and register each category

**Rationale:**
The architecture document shows this organization. Setting up the structure in Story 3.1 prevents refactoring later.

**Implementation Notes:**
```
src/tools/
├── test.ts         # Story 3.1: test_connection
├── workflows.ts    # Story 3.4: workflow CRUD
├── contacts.ts     # Story 3.5: contact management
├── funnels.ts      # Story 3.5: funnel tools
└── calendars.ts    # Story 3.5: calendar operations
```

Each tool file exports a class with static `register(server)` method.

**Related Decisions:**
- None

---

### [DEC-3.1-005] Single Source of Truth for Version Number

**Date:** 2025-10-26
**Story:** 3.1
**Decision Maker:** Alex Kim (Solutions Architect)
**Status:** Accepted

**Context:**
The server version appears in multiple places:
- package.json
- FastMCP initialization
- test_connection tool response

Keeping these in sync manually is error-prone.

**Decision:**
Read version from package.json at runtime using `import pkg from './package.json'`.

**Alternatives Considered:**
1. **Hard-code version in multiple places** - Rejected because:
   - Easy to forget to update
   - Creates version mismatches
   - Error-prone during releases

2. **Build-time injection** - Rejected because:
   - Adds complexity to build process
   - Not needed for simple use case

**Consequences:**
- **Positive:**
  - Single source of truth (package.json)
  - Version automatically correct everywhere
  - No manual sync needed

- **Negative:**
  - Requires `resolveJsonModule: true` in tsconfig
  - Slightly less performant (not a real concern)

**Rationale:**
Reduces maintenance burden and prevents version mismatches.

**Implementation Notes:**
```typescript
// Enable in tsconfig.json
{
  "resolveJsonModule": true
}

// Import in src/index.ts
import pkg from '../package.json' assert { type: 'json' };

const server = new FastMCP({
  name: 'ghl-api',
  version: pkg.version
});
```

**Related Decisions:**
- None

---

### [DEC-3.1-006] Defer .env File Usage to Story 3.2

**Date:** 2025-10-26
**Story:** 3.1
**Decision Maker:** Alex Kim (Solutions Architect)
**Status:** Accepted

**Context:**
Story 3.1 has no environment variables to configure (no OAuth, no API keys). We could set up dotenv now or wait.

**Decision:**
Create `.env.example` template in Story 3.1, but defer actual environment variable loading to Story 3.2 (OAuth).

**Alternatives Considered:**
1. **Set up dotenv now** - Rejected because:
   - No environment variables needed in 3.1
   - Adds unused dependency
   - YAGNI (You Ain't Gonna Need It)

2. **No .env.example** - Rejected because:
   - Developers won't know what variables are needed
   - Good to document requirements early

**Consequences:**
- **Positive:**
  - No unused dependencies in 3.1
  - Clear documentation of future requirements
  - Simpler Story 3.1 implementation

- **Negative:**
  - Will need to add dotenv in Story 3.2
  - Slight duplication of setup work

**Rationale:**
Follow YAGNI principle - don't add dependencies until needed. The .env.example serves as documentation.

**Implementation Notes:**
- Create `.env.example` with all required variables (commented)
- Add to QUICKSTART.md that .env is for future stories
- Install dotenv in Story 3.2

**Related Decisions:**
- None

---

## Story 3.2 Decisions

*(To be filled during Story 3.2 implementation)*

### Template for Future Decisions

**Date:** YYYY-MM-DD
**Story:** 3.2
**Decision Maker:** Name
**Status:** Proposed

**Context:**

**Decision:**

**Alternatives Considered:**

**Consequences:**

**Rationale:**

**Implementation Notes:**

**Related Decisions:**

---

## Lessons Learned

### Story 3.1

#### What Went Well
- *(To be filled by James after implementation)*

#### What Could Be Improved
- *(To be filled by James after implementation)*

#### Unexpected Challenges
- *(To be filled by James after implementation)*

#### Tips for Future Stories
- *(To be filled by James after implementation)*

---

## Deviations from Architecture Document

### Story 3.1

No deviations from the architecture document `docs/architecture/13-mcp-server-architecture.md` were required.

All implementation decisions align with the original design:
- ✅ ES2022 target
- ✅ NodeNext module resolution
- ✅ FastMCP framework
- ✅ Zod for validation
- ✅ Organized tool structure
- ✅ Comprehensive logging

---

## Decision Review Schedule

- **End of Each Story:** Review and document decisions made
- **End of Epic 3:** Consolidate lessons learned
- **Before Major Refactoring:** Review relevant decisions

---

## Decision Status Definitions

- **Proposed:** Decision has been suggested but not finalized
- **Accepted:** Decision has been approved and implemented
- **Rejected:** Decision was considered but not accepted
- **Superseded:** Decision has been replaced by a newer decision
- **Deprecated:** Decision is no longer recommended but may still be in use

---

**Last Updated:** 2025-10-26
**Document Version:** 1.0
**Maintainer:** Alex Kim (Solutions Architect)

---

## Notes for James

**How to Use This Document:**

1. **Before Making a Decision:**
   - Check if a related decision already exists
   - Review alternatives considered in similar decisions

2. **When Making a Decision:**
   - Document the decision using the template
   - Include context, alternatives, and rationale
   - Mark status as "Proposed" initially

3. **After Implementation:**
   - Update status to "Accepted"
   - Add implementation notes and gotchas
   - Update "Lessons Learned" section

4. **When Deviating from Architecture:**
   - Document the deviation with clear rationale
   - Update "Deviations from Architecture" section
   - Inform Alex (Solutions Architect)

**Questions?**
- Ask Alex for architectural guidance
- Ask Bob for story clarification
- Document your reasoning even if uncertain

# GHL WHIZ - Complete Platform Testing Guide
**Epics 1-13 End-to-End Testing**

---

## 🎯 Overview

This guide covers how to test **all completed epics** of the GHL WHIZ platform, from the foundational knowledge base through the visual workflow builder and analytics.

**Platform Status:**
- ✅ Epics 1-2: Knowledge Base & Infrastructure (COMPLETE)
- ✅ Epics 4-5: Slash Commands & CLI (COMPLETE)
- ✅ Epics 7-9: Web Interface & Search (COMPLETE)
- ✅ Epic 10: Visual Workflow Builder (COMPLETE)
- ✅ Epic 11: API Integration & Deployment (COMPLETE)
- ✅ Epic 12: Advanced Workflow Features (COMPLETE)
- ✅ Epic 13: Analytics & Performance Monitoring (COMPLETE)

---

## 🚀 Quick Start - Testing the Platform

### Prerequisites

1. **ChromaDB Running** (Port 8001)
2. **Backend API Running** (Port 8000)
3. **Frontend Running** (Port 3000)

### Start All Services

```bash
# Terminal 1: Start ChromaDB
cd "c:\Users\justi\BroBro"
npm run start-chroma

# Terminal 2: Start Backend API
cd "c:\Users\justi\BroBro\web\backend"
python main.py

# Terminal 3: Start Frontend
cd "c:\Users\justi\BroBro\web\frontend"
npm run dev
```

**Expected Results:**
- ChromaDB: http://localhost:8001
- Backend API: http://localhost:8000
- Frontend: http://localhost:3000

---

## 📚 Epic-by-Epic Testing Guide

### Epics 1-2: Knowledge Base & Infrastructure ✅

**What to Test:**
- ChromaDB vector database with 275+ commands
- Semantic search functionality
- Command collection indexing

#### Test 1: Verify ChromaDB is Running
```bash
# Check ChromaDB status
curl http://localhost:8001/api/v1/heartbeat
```
**Expected**: `{"nanosecond heartbeat": <timestamp>}`

#### Test 2: Check Collection Count
```bash
# Check collections
curl http://localhost:8000/api/collections
```
**Expected**: JSON with `ghl-knowledge-base` and `ghl-docs` collections

#### Test 3: Test Search API
```bash
# Search for lead nurture
curl -X POST http://localhost:8000/api/search \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"lead nurture email sequence\",\"n_results\":5}"
```
**Expected**: JSON response with 5 relevant commands/docs

#### Test 4: Quick Search Endpoint
```bash
curl "http://localhost:8000/api/search/quick?q=appointment+booking&limit=3"
```
**Expected**: 3 results related to appointments

---

### Epics 4-5: Slash Commands & CLI ✅

**What to Test:**
- 275+ slash commands organized by category
- Command metadata and descriptions
- Help system

#### Test 1: List All Commands
```bash
# View all available commands
dir ".claude\commands" /b
```
**Expected**: 275+ .md files

#### Test 2: View Command Categories
```bash
# List commands by category
dir ".claude\commands\ghl-*.md" | findstr /C:"ghl-"
```
**Expected**: Commands grouped by category (lead-nurture, appointment, form, etc.)

#### Test 3: Read a Sample Command
```bash
# View a specific command
type ".claude\commands\ghl-lead-nurture.md"
```
**Expected**: Formatted command with:
- Description
- Use cases
- Best practices
- Josh Wash workflows

#### Test 4: Test Command Metadata
```python
# Run this in Python to verify command structure
import json

# Load knowledge base
with open('knowledge-base/ghl-commands.json', 'r') as f:
    commands = json.load(f)

# Verify structure
print(f"Total commands: {len(commands['commands'])}")
print(f"Categories: {len(set(c['category'] for c in commands['commands']))}")
```
**Expected**: 275+ commands, 15+ categories

---

### Epics 7-9: Web Interface & Search ✅

**What to Test:**
- Web interface at localhost:3000
- Multi-collection semantic search
- Search results rendering
- System status monitoring

#### Test 1: Access Web Interface
1. Open browser: http://localhost:3000
2. **Expected**: GHL WHIZ landing page with search interface

#### Test 2: Perform Semantic Search
1. In the web interface search box, type: `"lead nurture automation"`
2. Click "Search" or press Enter
3. **Expected**:
   - Results from both commands and docs
   - Relevance scores displayed
   - Source badges (command vs. doc)
   - Formatted content with syntax highlighting

#### Test 3: Filter by Collection
1. Search: `"appointment booking"`
2. Use collection filter dropdown
3. Select "Commands Only"
4. **Expected**: Results filtered to show only commands

#### Test 4: Test Advanced Search
1. Search: `"webhook automation with delay"`
2. **Expected**: Results combining multiple concepts (webhooks + automation + delays)

#### Test 5: Check System Status
1. Navigate to: http://localhost:8000/health
2. **Expected**: JSON response with:
   ```json
   {
     "status": "healthy",
     "chroma_connected": true,
     "collections": {
       "ghl-knowledge-base": <count>,
       "ghl-docs": <count>
     },
     "model_loaded": true
   }
   ```

#### Test 6: System Info Endpoint
1. Navigate to: http://localhost:8000/api/system/info
2. **Expected**: Detailed system information including:
   - ChromaDB host/port
   - Collection counts
   - Embedding model name
   - Total documents

---

### Epic 10: Visual Workflow Builder ✅

**What to Test:**
- Drag-and-drop workflow canvas
- 15+ node types
- Connections and validation
- Workflow save/load

#### Test 1: Access Workflow Builder
1. Navigate to: http://localhost:3000 (if different URL for builder, adjust)
2. Look for "Workflow Builder" or navigate to workflow canvas
3. **Expected**: Empty canvas with node palette

#### Test 2: Create a Simple Workflow
1. Drag **"Trigger"** node to canvas
2. Drag **"Action"** node to canvas
3. Connect trigger to action
4. **Expected**:
   - Nodes placed on canvas
   - Connection line drawn between nodes
   - No validation errors

#### Test 3: Test All Node Types (15+)
Try adding each node type:
- ✅ Trigger (form_submission, webhook, tag_added, etc.)
- ✅ Action (send_email, send_sms, update_contact, etc.)
- ✅ Condition (if/else logic)
- ✅ Delay (time-based wait)
- ✅ Loop (iterate over list)
- ✅ API Request (HTTP calls)
- ✅ Transform (data manipulation)
- ✅ Filter (data filtering)
- ✅ Branch (split flow)
- ✅ Merge (combine flows)
- ✅ Webhook Response
- ✅ Error Handler
- ✅ Variable Set
- ✅ Variable Get
- ✅ Custom Code

**Expected**: All node types render with correct icons and labels

#### Test 4: Node Properties Panel
1. Click on any node
2. **Expected**: Properties panel opens showing:
   - Node name (editable)
   - Node type
   - Configuration fields (specific to node type)
   - Description

#### Test 5: Workflow Validation
1. Create workflow with disconnected nodes
2. Click "Validate" or "Save"
3. **Expected**: Validation errors shown (e.g., "Node X has no connections")

#### Test 6: Save Workflow
1. Create a workflow
2. Name it: "Test Lead Nurture"
3. Click "Save"
4. **Expected**: Success message, workflow saved to localStorage

#### Test 7: Load Workflow
1. Refresh page
2. Click "Load Workflow"
3. Select "Test Lead Nurture"
4. **Expected**: Workflow restored on canvas with all nodes and connections

---

### Epic 11: API Integration & Deployment ✅

**What to Test:**
- GHL API integration
- OAuth connection flow
- Location-level permissions
- API endpoints

#### Test 1: GHL API Connection
1. Check if GHL routes are registered
```bash
curl http://localhost:8000/api/ghl/health
```
**Expected**: Health check response

#### Test 2: Test Location Endpoint
```bash
curl http://localhost:8000/api/ghl/locations
```
**Expected**: List of GHL locations (or auth error if not configured)

#### Test 3: OAuth Flow (if configured)
1. Navigate to: http://localhost:8000/api/ghl/oauth/authorize
2. **Expected**: Redirect to GHL OAuth consent screen

#### Test 4: API Request Logging
```bash
# Check backend logs for API calls
# Look for GHL API request logs in terminal
```
**Expected**: Request/response logging visible

---

### Epic 12: Advanced Workflow Features ✅

**What to Test:**
- Conditional logic builder
- Variable management
- Custom triggers
- Advanced actions
- Template marketplace
- Workflow scheduling
- Testing framework

#### Test 1: Conditional Logic Builder
1. Add a **Condition** node to canvas
2. Click to open properties
3. **Expected**: ConditionBuilder component with:
   - Field selector (Contact, Opportunity, Form fields)
   - 11 operators (equals, not_equals, contains, etc.)
   - Value input
   - AND/OR logic toggle
   - Add/remove conditions

#### Test 2: Create Complex Condition
1. Add condition: `contact.email contains "@gmail.com"`
2. Add second condition: `contact.status equals "lead"`
3. Set logic to "AND"
4. **Expected**: Preview shows: "contact.email contains '@gmail.com' AND contact.status equals 'lead'"

#### Test 3: Variable Manager
1. Open Variable Manager (in workflow properties or separate panel)
2. Click "Add Variable"
3. Create variable:
   - Name: `firstName`
   - Type: `text`
   - Default: `John`
4. **Expected**: Variable added, copy reference button shows `{{firstName}}`

#### Test 4: Use Variables in Actions
1. Add **Send Email** action node
2. In email body, type: `Hello {{firstName}}`
3. **Expected**: Variable reference highlighted or validated

#### Test 5: Test Workflow Templates
```bash
# API endpoint to list templates
curl http://localhost:8000/api/workflows/templates
```
**Expected**: JSON array with 3+ templates:
- Lead Nurture Email Sequence
- Appointment Reminder
- Abandoned Cart Recovery

#### Test 6: Load Template
```bash
# Get specific template
curl http://localhost:8000/api/workflows/templates/lead-nurture-email
```
**Expected**: Full workflow structure with nodes, connections, config

#### Test 7: Test Workflow (Dry Run)
```bash
# Test workflow execution
curl -X POST http://localhost:8000/api/workflows/test \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "test-123",
    "workflow": {
      "nodes": [...],
      "edges": [...]
    },
    "testData": {
      "contact": {"email": "test@example.com"}
    }
  }'
```
**Expected**: Test results with:
- Validation status
- Step execution results
- Errors (if any)

---

### Epic 13: Analytics & Performance Monitoring ✅

**What to Test:**
- Metrics collection
- Real-time dashboard
- Performance charts
- ROI calculator
- Comparative analysis
- Alert system
- Report generation

#### Test 1: Start Execution Tracking
```bash
# Start tracking a workflow execution
curl -X POST http://localhost:8000/api/analytics/executions/start \
  -H "Content-Type: application/json" \
  -d '{
    "executionId": "exec-test-001",
    "workflowId": "wf-lead-nurture",
    "workflowName": "Lead Nurture Campaign",
    "triggerType": "form_submission"
  }'
```
**Expected**: Success response with execution details

#### Test 2: Track Workflow Steps
```bash
# Start a step
curl -X POST http://localhost:8000/api/analytics/executions/step/start \
  -H "Content-Type: application/json" \
  -d '{
    "executionId": "exec-test-001",
    "stepId": "step-email-1",
    "stepName": "Send Welcome Email",
    "stepType": "send_email"
  }'

# Complete the step
curl -X POST http://localhost:8000/api/analytics/executions/step/complete \
  -H "Content-Type: application/json" \
  -d '{
    "executionId": "exec-test-001",
    "stepId": "step-email-1",
    "status": "completed",
    "outputData": {"emailsSent": 1}
  }'
```
**Expected**: Success responses

#### Test 3: Complete Execution
```bash
curl -X POST http://localhost:8000/api/analytics/executions/complete \
  -H "Content-Type: application/json" \
  -d '{
    "executionId": "exec-test-001",
    "status": "completed"
  }'
```
**Expected**: Success, execution marked complete

#### Test 4: View Global Metrics
```bash
curl http://localhost:8000/api/analytics/metrics/global
```
**Expected**: JSON with:
- totalExecutions
- successfulExecutions
- failedExecutions
- successRate
- averageDurationMs
- runningExecutions

#### Test 5: View Workflow-Specific Metrics
```bash
curl http://localhost:8000/api/analytics/metrics/workflow/wf-lead-nurture
```
**Expected**: Detailed metrics for that workflow

#### Test 6: Access Analytics Dashboard (Frontend)
1. Navigate to: http://localhost:3000 (or analytics route)
2. Import and render: `<AnalyticsDashboard />`
3. **Expected**: Dashboard with 5 KPI cards:
   - Total Executions
   - Success Rate (with color coding)
   - Failed Executions
   - Average Duration
   - Currently Running (with pulse animation)

#### Test 7: Test Execution Timeline
1. Render: `<ExecutionTimeline workflowId="wf-lead-nurture" />`
2. Select time range: 24h, 7d, 30d, 90d
3. **Expected**: 3 charts:
   - Execution Volume (line chart)
   - Success Rate Trend (line chart)
   - Average Duration Trend (line chart)

#### Test 8: View Performance Charts
1. Render: `<PerformanceCharts workflowId="wf-lead-nurture" />`
2. **Expected**:
   - Success Rate Area Chart (green/red gradients)
   - Bottleneck Analysis Bar Chart
   - Bottleneck detail cards (if any detected)

#### Test 9: Calculate ROI
1. Render: `<ROICalculator workflowId="wf-lead-nurture" workflowName="Lead Nurture" />`
2. Configure inputs:
   - Hourly Rate: $50
   - Manual Time: 30 minutes
   - Monthly Executions: 100
3. **Expected**: 4 ROI cards showing:
   - Time Saved per Execution
   - Cost Savings (monthly/annual)
   - ROI Percentage
   - Payback Period

#### Test 10: Export ROI Report
1. In ROI Calculator, click "Export Report"
2. **Expected**: Text file download with formatted report

#### Test 11: Comparative Analysis
1. Render: `<ComparativeAnalysis workflows={[...]} />`
2. Select 2-5 workflows
3. **Expected**:
   - Radar chart with 5 dimensions
   - Comparison table with 6 metrics
   - Winner summary panel

#### Test 12: Alert System
1. Render: `<AlertCenter />`
2. Click "Enable Notifications"
3. Grant browser notification permission
4. **Expected**:
   - Alert list (if any alerts exist)
   - Filter options (severity, acknowledged)
   - Alert rule configuration panel

#### Test 13: Generate Report
```bash
# Get available templates
curl http://localhost:8000/api/analytics/reports/templates
```
**Expected**: 5 templates:
1. Executive Summary
2. Detailed Performance
3. Bottleneck Analysis
4. ROI Analysis
5. Comparative Analysis

#### Test 14: Generate and Download Report
```bash
# Generate JSON report
curl -X POST http://localhost:8000/api/analytics/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "wf-lead-nurture",
    "templateId": "executive_summary",
    "format": "json",
    "includeBottlenecks": true
  }'
```
**Expected**: JSON report with sections

#### Test 15: Generate CSV Report
```bash
curl -X POST http://localhost:8000/api/analytics/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "workflowId": "wf-lead-nurture",
    "templateId": "detailed_performance",
    "format": "csv"
  }'
```
**Expected**: CSV-formatted report

---

## 🧪 Integration Testing Scenarios

### Scenario 1: Complete Workflow Lifecycle

1. **Create** a workflow in Visual Builder (Epic 10)
2. **Add** conditional logic and variables (Epic 12)
3. **Save** the workflow
4. **Test** execution tracking (Epic 13)
5. **Monitor** performance in Analytics Dashboard (Epic 13)
6. **Generate** ROI report (Epic 13)

### Scenario 2: Search → Build → Monitor

1. **Search** for "lead nurture" in Web Interface (Epics 7-9)
2. **Find** relevant command template
3. **Build** workflow from template (Epic 10, 12)
4. **Deploy** via API (Epic 11)
5. **Track** executions (Epic 13)
6. **Analyze** bottlenecks (Epic 13)

### Scenario 3: Template → Customize → Report

1. **Load** workflow template from marketplace (Epic 12)
2. **Customize** with variables and conditions (Epic 12)
3. **Execute** test runs (Epic 12)
4. **Track** performance (Epic 13)
5. **Compare** with other workflows (Epic 13)
6. **Export** comparative analysis report (Epic 13)

---

## 📊 Performance Benchmarks

### Expected Performance Metrics

#### Search Performance (Epics 1-2, 7-9)
- ✅ Search query response: <1 second
- ✅ ChromaDB query: <500ms
- ✅ Results rendering: <200ms

#### Workflow Builder (Epic 10)
- ✅ Canvas rendering: <500ms
- ✅ Node drag-and-drop: <50ms latency
- ✅ Save workflow: <300ms

#### API Integration (Epic 11)
- ✅ GHL API calls: <2 seconds
- ✅ OAuth flow: <5 seconds

#### Analytics (Epic 13)
- ✅ Metrics collection: <100ms per event
- ✅ Dashboard refresh: 5 seconds (configurable)
- ✅ Chart rendering: <1 second
- ✅ Report generation: <3 seconds

---

## 🐛 Troubleshooting Common Issues

### Issue 1: ChromaDB Not Connecting
**Symptom**: Backend fails to start, "Connection refused" error
**Solution**:
```bash
# Check if ChromaDB is running
curl http://localhost:8001/api/v1/heartbeat

# If not running, start it
npm run start-chroma
```

### Issue 2: Frontend Shows "Failed to Fetch"
**Symptom**: Web interface shows network errors
**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/health

# Check CORS configuration in backend/main.py
# Ensure frontend URL (localhost:3000) is in allow_origins
```

### Issue 3: Workflow Nodes Not Rendering
**Symptom**: Empty canvas or nodes don't appear
**Solution**:
1. Check browser console for errors
2. Verify React Flow is installed: `npm list reactflow`
3. Check that WorkflowCanvas component is properly imported

### Issue 4: Analytics Shows No Data
**Symptom**: Dashboard shows 0 executions
**Solution**:
```bash
# Generate test data
curl -X POST http://localhost:8000/api/analytics/executions/start \
  -H "Content-Type: application/json" \
  -d '{"executionId":"test-1","workflowId":"wf-1","workflowName":"Test"}'

curl -X POST http://localhost:8000/api/analytics/executions/complete \
  -H "Content-Type: application/json" \
  -d '{"executionId":"test-1","status":"completed"}'
```

### Issue 5: Search Returns No Results
**Symptom**: All searches return empty array
**Solution**:
```bash
# Check collections are populated
curl http://localhost:8000/api/collections

# Re-embed content if needed
cd "c:\Users\justi\BroBro"
python scripts/embed-content.py
```

---

## ✅ Testing Checklist

### Pre-Flight Checks
- [ ] ChromaDB running on port 8001
- [ ] Backend API running on port 8000
- [ ] Frontend running on port 3000
- [ ] No console errors in browser
- [ ] Backend logs show no errors

### Epic 1-2: Knowledge Base
- [ ] ChromaDB heartbeat responds
- [ ] Collections exist (ghl-knowledge-base, ghl-docs)
- [ ] Search API returns results
- [ ] 275+ commands indexed

### Epic 4-5: Slash Commands
- [ ] 275+ .md files in .claude/commands/
- [ ] Commands have proper metadata
- [ ] Help system accessible
- [ ] Commands grouped by category

### Epic 7-9: Web Interface
- [ ] Homepage loads at localhost:3000
- [ ] Search bar functional
- [ ] Results display correctly
- [ ] Collection filters work
- [ ] System health endpoint responds

### Epic 10: Workflow Builder
- [ ] Canvas renders
- [ ] 15+ node types available
- [ ] Drag-and-drop works
- [ ] Connections can be created
- [ ] Properties panel opens
- [ ] Workflows can be saved/loaded

### Epic 11: API Integration
- [ ] GHL API routes registered
- [ ] Health endpoint responds
- [ ] Location endpoint (auth dependent)
- [ ] Request logging visible

### Epic 12: Advanced Features
- [ ] Condition builder renders
- [ ] 11 condition operators available
- [ ] Variable manager functional
- [ ] Templates load correctly
- [ ] Workflow testing works
- [ ] Scheduling configured

### Epic 13: Analytics
- [ ] Execution tracking works
- [ ] Metrics endpoints respond
- [ ] Dashboard displays KPIs
- [ ] Charts render (Recharts)
- [ ] ROI calculator computes
- [ ] Reports generate in 3 formats
- [ ] Browser notifications work
- [ ] Alerts system functional

---

## 🎓 Next Steps After Testing

### If All Tests Pass ✅
1. **Document** any configuration needed for production
2. **Prepare** deployment scripts
3. **Set up** environment variables for production
4. **Configure** GHL OAuth credentials
5. **Deploy** to production environment

### If Tests Fail ❌
1. **Note** which epic/story failed
2. **Check** error messages in console/logs
3. **Verify** dependencies are installed
4. **Review** configuration files
5. **Consult** epic-specific documentation

---

## 📚 Additional Resources

### Documentation
- [PROJECT_STATUS.md](PROJECT_STATUS.md) - Overall project status
- [EPIC_10_COMPLETE.md](EPIC_10_COMPLETE.md) - Workflow Builder details
- [EPIC_11_IMPLEMENTATION_SUMMARY.md](EPIC_11_IMPLEMENTATION_SUMMARY.md) - API integration
- [EPIC_12_COMPLETE.md](EPIC_12_COMPLETE.md) - Advanced features
- [EPIC_13_COMPLETE.md](EPIC_13_COMPLETE.md) - Analytics implementation

### API Documentation
- Backend API: http://localhost:8000/docs (FastAPI auto-generated)
- Health Check: http://localhost:8000/health
- System Info: http://localhost:8000/api/system/info

### Support
- Check GitHub issues for known problems
- Review session summaries for implementation details
- Consult BMAD-METHOD documentation for architecture

---

**Happy Testing! 🚀**

The GHL WHIZ platform represents 13 epics of production-grade development. This testing guide ensures all components work together seamlessly to deliver a powerful GoHighLevel automation assistant.

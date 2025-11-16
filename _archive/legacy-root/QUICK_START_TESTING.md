# GHL WHIZ - Quick Start Testing Guide
**Get Started in 5 Minutes**

---

## 🚀 Step 1: Start All Services (3 Terminals)

### Terminal 1: ChromaDB
```bash
cd "c:\Users\justi\BroBro"
npm run start-chroma
```
**Wait for**: `✓ ChromaDB running on port 8001`

### Terminal 2: Backend API
```bash
cd "c:\Users\justi\BroBro\web\backend"
python main.py
```
**Wait for**: `INFO: Uvicorn running on http://0.0.0.0:8000`

### Terminal 3: Frontend
```bash
cd "c:\Users\justi\BroBro\web\frontend"
npm run dev
```
**Wait for**: `Local: http://localhost:3000/`

---

## 🎯 Step 2: Open the Web Interface

1. Open your browser
2. Navigate to: **http://localhost:3000**
3. You should see the GHL WHIZ interface with 5 tabs:
   - 💬 **Chat** - AI assistant interface
   - 📚 **Commands** - Browse 275+ commands
   - 🔀 **Workflows** - Visual workflow builder
   - 🔍 **Search** - Semantic search
   - ⚙️ **Setup Management** - System settings

---

## ✅ Step 3: Quick Feature Tests (5 minutes)

### Test 1: Search (30 seconds)
1. Click the **🔍 Search** tab
2. Type: `"lead nurture automation"`
3. Click **Search**
4. **✓ Expected**: See results with relevance scores

### Test 2: Commands (30 seconds)
1. Click the **📚 Commands** tab
2. Browse available commands
3. Click on any command
4. **✓ Expected**: See command details with use cases

### Test 3: Chat Interface (1 minute)
1. Click the **💬 Chat** tab
2. Type: `"How do I set up appointment booking?"`
3. **✓ Expected**: AI response with relevant GHL commands

### Test 4: Workflow Builder (2 minutes)
1. Click the **🔀 Workflows** tab
2. You should see the workflow canvas
3. Look for the node palette on the left
4. Try dragging a **Trigger** node onto the canvas
5. Try dragging an **Action** node onto the canvas
6. Try connecting them by dragging from one node's handle to another
7. **✓ Expected**: Nodes placed, connection drawn

### Test 5: System Health (30 seconds)
1. Click the **⚙️ Setup Management** tab
2. Look at the top right corner - green dot = healthy
3. Check "ChromaDB Status"
4. Check "Collections" count
5. **✓ Expected**: All green, 275+ documents indexed

---

## 🧪 Step 4: Test Analytics (Epic 13 Features)

The analytics features need some test data to display. Let's create test executions first:

### Create Test Executions via API

Open a **4th terminal** and run these commands:

```bash
# Test Execution 1 - Success
curl -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-001\",\"workflowId\":\"wf-lead-nurture\",\"workflowName\":\"Lead Nurture Campaign\",\"triggerType\":\"form_submission\"}"

curl -X POST http://localhost:8000/api/analytics/executions/step/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-001\",\"stepId\":\"step-1\",\"stepName\":\"Send Email\",\"stepType\":\"send_email\"}"

curl -X POST http://localhost:8000/api/analytics/executions/step/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-001\",\"stepId\":\"step-1\",\"status\":\"completed\"}"

curl -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-001\",\"status\":\"completed\"}"

# Test Execution 2 - Another Success
curl -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-002\",\"workflowId\":\"wf-lead-nurture\",\"workflowName\":\"Lead Nurture Campaign\",\"triggerType\":\"webhook\"}"

curl -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-002\",\"status\":\"completed\"}"

# Test Execution 3 - Failed (to test error tracking)
curl -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-003\",\"workflowId\":\"wf-appointment\",\"workflowName\":\"Appointment Reminder\",\"triggerType\":\"tag_added\"}"

curl -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-exec-003\",\"status\":\"failed\",\"error\":\"API rate limit exceeded\"}"
```

**Expected**: Success responses for each command

### View Analytics Dashboard

Now open your browser and test the analytics endpoints:

1. **View Global Metrics**: http://localhost:8000/api/analytics/metrics/global
   - **✓ Expected**: JSON with 3 total executions, 2 successful, 1 failed

2. **View Workflow Metrics**: http://localhost:8000/api/analytics/metrics/workflow/wf-lead-nurture
   - **✓ Expected**: JSON with 2 executions, 100% success rate

---

## 📊 Step 5: Access Analytics Components (if integrated into UI)

If the analytics components are integrated into the frontend, you can access them. Otherwise, you can test via API.

### Via API (Always Available)

```bash
# Get Report Templates
curl http://localhost:8000/api/analytics/reports/templates

# Generate Report
curl -X POST http://localhost:8000/api/analytics/reports/generate -H "Content-Type: application/json" -d "{\"workflowId\":\"wf-lead-nurture\",\"templateId\":\"executive_summary\",\"format\":\"json\"}"

# Get Alerts
curl http://localhost:8000/api/analytics/alerts

# Get Alert Rules
curl http://localhost:8000/api/analytics/alerts/rules
```

---

## 🎉 Success Criteria

You've successfully tested GHL WHIZ if you can:

- ✅ Access the web interface at localhost:3000
- ✅ See green health indicator (top right)
- ✅ Perform a search and get results
- ✅ Browse commands library
- ✅ Open workflow builder canvas
- ✅ Drag and drop workflow nodes
- ✅ View system status in Setup Management
- ✅ Create test executions via API
- ✅ Retrieve analytics metrics via API

---

## 🐛 Common Issues & Solutions

### Issue: "Failed to fetch" errors
**Solution**: Make sure backend is running on port 8000
```bash
curl http://localhost:8000/health
```

### Issue: "ChromaDB disconnected"
**Solution**: Start ChromaDB first
```bash
cd "c:\Users\justi\BroBro"
npm run start-chroma
```

### Issue: Workflow canvas is blank
**Solution**: Check browser console for errors. React Flow might need a refresh.

### Issue: Search returns no results
**Solution**: Check if collections are populated
```bash
curl http://localhost:8000/api/collections
```
Should show counts for ghl-knowledge-base and ghl-docs

---

## 📚 What You Can Test Now

### Epics 1-2: Knowledge Base ✅
- 275+ GoHighLevel commands indexed
- Semantic search with ChromaDB
- Multi-collection search

### Epics 4-5: CLI & Commands ✅
- Slash commands in `.claude/commands/`
- Command metadata and categories
- Help system

### Epics 7-9: Web Interface ✅
- React-based web UI
- Search interface
- Command library browser
- Chat interface
- System monitoring

### Epic 10: Workflow Builder ✅
- Visual canvas with drag-and-drop
- 15+ node types (Trigger, Action, Condition, etc.)
- Node connections
- Properties panel
- Save/load workflows

### Epic 11: API Integration ✅
- GHL API routes
- OAuth flow (when configured)
- Deployment panel
- API key management

### Epic 12: Advanced Features ✅
- Conditional logic builder (11 operators)
- Variable manager (6 types)
- Workflow templates
- Testing framework

### Epic 13: Analytics ✅
- Metrics collection API
- Performance analysis
- Bottleneck detection
- Alert system
- Report generation (JSON/CSV/Text)
- ROI calculator (via API)

---

## 🚀 Next Steps

1. **Explore the Interface**: Click through all tabs and features
2. **Test Workflows**: Create a multi-step workflow in the builder
3. **Run Analytics**: Create more test executions and analyze metrics
4. **Generate Reports**: Use the report generation API
5. **Configure GHL**: Add your GHL API key for real integration

---

## 📖 Full Documentation

For detailed testing of each epic:
- See [TESTING_GUIDE.md](TESTING_GUIDE.md) - Comprehensive testing guide
- See [EPIC_13_COMPLETE.md](EPIC_13_COMPLETE.md) - Analytics details
- See [PROJECT_STATUS.md](PROJECT_STATUS.md) - Overall project status

---

**You're now ready to test GHL WHIZ!** 🎉

The platform has **13 completed epics** ready for testing. Start with the Quick Start above, then dive deeper with the full testing guide.

@echo off
echo ============================================
echo GHL WHIZ Analytics - Test Data Generator
echo ============================================
echo.
echo Generating 10 test workflow executions...
echo.

REM Test Execution 1 - Lead Nurture Success
echo [1/10] Creating successful Lead Nurture execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-001\",\"workflowId\":\"wf-lead-nurture\",\"workflowName\":\"Lead Nurture Campaign\",\"triggerType\":\"form_submission\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/step/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-001\",\"stepId\":\"step-1\",\"stepName\":\"Send Welcome Email\",\"stepType\":\"send_email\"}" >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/step/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-001\",\"stepId\":\"step-1\",\"status\":\"completed\"}" >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-001\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 2 - Lead Nurture Success
echo [2/10] Creating successful Lead Nurture execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-002\",\"workflowId\":\"wf-lead-nurture\",\"workflowName\":\"Lead Nurture Campaign\",\"triggerType\":\"webhook\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-002\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 3 - Appointment Success
echo [3/10] Creating successful Appointment Reminder execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-003\",\"workflowId\":\"wf-appointment\",\"workflowName\":\"Appointment Reminder\",\"triggerType\":\"tag_added\"}" >nul
timeout /t 2 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-003\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 4 - Appointment Failed
echo [4/10] Creating failed Appointment execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-004\",\"workflowId\":\"wf-appointment\",\"workflowName\":\"Appointment Reminder\",\"triggerType\":\"webhook\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-004\",\"status\":\"failed\",\"error\":\"API rate limit exceeded\"}" >nul
echo   ✓ Completed

REM Test Execution 5 - Cart Recovery Success
echo [5/10] Creating successful Cart Recovery execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-005\",\"workflowId\":\"wf-abandoned-cart\",\"workflowName\":\"Abandoned Cart Recovery\",\"triggerType\":\"custom_event\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-005\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 6 - Lead Nurture Success
echo [6/10] Creating successful Lead Nurture execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-006\",\"workflowId\":\"wf-lead-nurture\",\"workflowName\":\"Lead Nurture Campaign\",\"triggerType\":\"form_submission\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-006\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 7 - Appointment Success
echo [7/10] Creating successful Appointment execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-007\",\"workflowId\":\"wf-appointment\",\"workflowName\":\"Appointment Reminder\",\"triggerType\":\"tag_added\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-007\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 8 - Cart Recovery Failed
echo [8/10] Creating failed Cart Recovery execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-008\",\"workflowId\":\"wf-abandoned-cart\",\"workflowName\":\"Abandoned Cart Recovery\",\"triggerType\":\"webhook\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-008\",\"status\":\"failed\",\"error\":\"Email delivery failed\"}" >nul
echo   ✓ Completed

REM Test Execution 9 - Lead Nurture Success
echo [9/10] Creating successful Lead Nurture execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-009\",\"workflowId\":\"wf-lead-nurture\",\"workflowName\":\"Lead Nurture Campaign\",\"triggerType\":\"webhook\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-009\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

REM Test Execution 10 - Appointment Success
echo [10/10] Creating successful Appointment execution...
curl -s -X POST http://localhost:8000/api/analytics/executions/start -H "Content-Type: application/json" -d "{\"executionId\":\"test-010\",\"workflowId\":\"wf-appointment\",\"workflowName\":\"Appointment Reminder\",\"triggerType\":\"tag_added\"}" >nul
timeout /t 1 /nobreak >nul
curl -s -X POST http://localhost:8000/api/analytics/executions/complete -H "Content-Type: application/json" -d "{\"executionId\":\"test-010\",\"status\":\"completed\"}" >nul
echo   ✓ Completed

echo.
echo ============================================
echo Test Data Generation Complete!
echo ============================================
echo.
echo Generated:
echo - 10 workflow executions
echo - 3 workflows (Lead Nurture, Appointment, Cart Recovery)
echo - 8 successful, 2 failed executions
echo - Multiple trigger types (form, webhook, tag, custom)
echo.
echo Now you can:
echo 1. Open http://localhost:3000
echo 2. Click on the "Analytics" tab
echo 3. Explore all 7 analytics views:
echo    - Dashboard (KPI cards)
echo    - Timeline (execution trends)
echo    - Performance (bottleneck analysis)
echo    - ROI Calculator
echo    - Compare (multi-workflow)
echo    - Alerts (notification center)
echo    - Reports (generate exports)
echo.
echo Press any key to exit...
pause >nul

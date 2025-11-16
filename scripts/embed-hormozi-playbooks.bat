@echo off
echo ============================================
echo Embedding Alex Hormozi Playbooks into BroBro
echo ============================================
echo.

cd /d "C:\Users\justi\BroBro"

echo [1/5] Embedding: 100M Playbook - Lead Nurture
python scripts\embed-business-book.py "kb\business-playbooks\100M-Playbook-Lead-Nurture.pdf" --title "100M Playbook: Lead Nurture" --author "Alex Hormozi" --category "lead-generation"
echo.

echo [2/5] Embedding: 100M Leads
python scripts\embed-business-book.py "kb\business-playbooks\100M-Leads.pdf" --title "100M Leads" --author "Alex Hormozi" --category "lead-generation"
echo.

echo [3/5] Embedding: 100M Offers
python scripts\embed-business-book.py "kb\business-playbooks\100M-Offers.pdf" --title "100M Offers" --author "Alex Hormozi" --category "offers"
echo.

echo [4/5] Embedding: 100M Money Models
python scripts\embed-business-book.py "kb\business-playbooks\100M-Money-Models.pdf" --title "100M Money Models" --author "Alex Hormozi" --category "business-models"
echo.

echo [5/5] Embedding: 100M Ads
python scripts\embed-business-book.py "kb\business-playbooks\100M-Ads.pdf" --title "100M Ads" --author "Alex Hormozi" --category "advertising"
echo.

echo ============================================
echo All Hormozi playbooks embedded successfully!
echo ============================================
pause

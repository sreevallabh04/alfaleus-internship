@echo off
echo Starting PricePulse Frontend Server...
cd frontend

echo Installing dependencies including CRACO...
call npm install
call npm install @craco/craco@7.1.0 --save --no-audit

echo Starting frontend development server...
npm start
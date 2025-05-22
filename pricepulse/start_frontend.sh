#!/bin/bash
echo "Starting PricePulse Frontend Server..."
cd frontend

echo "Installing dependencies including CRACO..."
npm install
npm install @craco/craco@7.1.0 --save --no-audit

echo "Starting frontend development server..."
npm start
#!/bin/bash

echo "========================================="
echo "PROBANDO URLS DE LOS MICROSERVICIOS"
echo "========================================="
echo ""

echo "1. Probando API Gateway (Health)..."
curl -s http://localhost:8000/ | jq '.' || echo "Error"
echo ""

echo "2. Probando Authentication Service (Login)..."
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}' | jq '.' || echo "Error"
echo ""

echo "3. Probando Data Management Service (Deportistas)..."
curl -s http://localhost:8000/api/v1/data/deportistas | jq '.' || echo "Error"
echo ""

echo "4. Probando Analytics Service (Métricas)..."
curl -s http://localhost:8000/api/v1/analytics/metricas | jq '.' || echo "Error"
echo ""

echo "5. Probando Notifications Service (Notificaciones)..."
curl -s http://localhost:8000/api/v1/notifications/notificaciones | jq '.' || echo "Error"
echo ""

echo "========================================="
echo "PROBANDO FRONTEND"
echo "========================================="
echo ""

echo "6. Probando Frontend (Página Principal)..."
curl -s http://localhost:5000/ | head -n 20
echo ""

echo "========================================="
echo "PRUEBAS COMPLETADAS"
echo "========================================="
echo ""
echo "URLs disponibles:"
echo "  - Frontend: http://localhost:5000"
echo "  - API Gateway: http://localhost:8000"
echo "  - API Gateway Docs: http://localhost:8000/docs"
echo "  - Auth Service: http://localhost:8001/docs"
echo "  - Data Service: http://localhost:8002/docs"
echo "  - Notifications Service: http://localhost:8003/docs"
echo "  - Analytics Service: http://localhost:8004/docs"


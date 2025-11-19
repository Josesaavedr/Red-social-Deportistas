#!/bin/bash

# Script para verificar que todos los servicios estén funcionando correctamente

echo "=========================================="
echo "Verificando servicios de microservicios"
echo "=========================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para verificar un servicio
check_service() {
    local service_name=$1
    local url=$2
    
    echo -n "Verificando $service_name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)
    
    if [ $? -eq 0 ] && [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response)"
        return 1
    fi
}

# Esperar un poco para que los servicios se inicien
echo -e "${YELLOW}Esperando 5 segundos para que los servicios se inicien...${NC}"
sleep 5
echo ""

# Contador de servicios
total=0
success=0

# Verificar API Gateway
echo "--- API Gateway ---"
check_service "API Gateway Health" "http://localhost:8000/health"
total=$((total + 1))
[ $? -eq 0 ] && success=$((success + 1))
echo ""

# Verificar Frontend
echo "--- Frontend ---"
check_service "Frontend" "http://localhost:5000"
total=$((total + 1))
[ $? -eq 0 ] && success=$((success + 1))
echo ""

# Verificar Microservicios
echo "--- Microservicios ---"

check_service "Authentication Service" "http://localhost:8001/health"
total=$((total + 1))
[ $? -eq 0 ] && success=$((success + 1))

check_service "Data Management Service" "http://localhost:8002/health"
total=$((total + 1))
[ $? -eq 0 ] && success=$((success + 1))

check_service "Notifications Service" "http://localhost:8003/health"
total=$((total + 1))
[ $? -eq 0 ] && success=$((success + 1))

check_service "Analytics Service" "http://localhost:8004/health"
total=$((total + 1))
[ $? -eq 0 ] && success=$((success + 1))

echo ""
echo "=========================================="
echo "Resumen: $success/$total servicios funcionando correctamente"
echo "=========================================="
echo ""

# Pruebas adicionales de endpoints
echo "--- Pruebas de Endpoints ---"
echo ""

echo "1. Probando endpoint raíz de Authentication Service:"
curl -s http://localhost:8001/ | python3 -m json.tool 2>/dev/null || echo "Error al obtener respuesta"
echo ""

echo "2. Probando endpoint raíz de Data Management Service:"
curl -s http://localhost:8002/ | python3 -m json.tool 2>/dev/null || echo "Error al obtener respuesta"
echo ""

echo "3. Probando endpoint de deportistas a través del API Gateway:"
curl -s http://localhost:8000/api/v1/data/api/v1/deportistas | python3 -m json.tool 2>/dev/null || echo "Error al obtener respuesta"
echo ""

echo "=========================================="
echo "Pruebas completadas"
echo "=========================================="

# Salir con código de error si no todos los servicios están funcionando
if [ $success -eq $total ]; then
    echo -e "${GREEN}✓ Todos los servicios están funcionando correctamente${NC}"
    exit 0
else
    echo -e "${RED}✗ Algunos servicios no están funcionando${NC}"
    exit 1
fi


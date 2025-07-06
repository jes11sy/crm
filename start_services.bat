@echo off
echo Starting CRM Microservices Architecture...
echo.

echo Starting User Service on port 8001...
start "User Service" cmd /k "cd user_service && python manage.py runserver 8001"

echo Starting Zayavki Service on port 8002...
start "Zayavki Service" cmd /k "cd zayavki_service && python manage.py runserver 8002"

echo Starting Finance Service on port 8003...
start "Finance Service" cmd /k "cd financesvc && python manage.py runserver 8003"

echo Starting API Gateway on port 8000...
start "API Gateway" cmd /k "cd api_gateway && python manage.py runserver 8000"

echo.
echo All services are starting...
echo.
echo API Gateway: http://localhost:8000
echo User Service: http://localhost:8001
echo Zayavki Service: http://localhost:8002
echo Finance Service: http://localhost:8003
echo.
echo Swagger Documentation: http://localhost:8000/swagger/
echo Health Check: http://localhost:8000/health/
echo.
pause 
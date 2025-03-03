@echo off

REM Verificar la existencia de la red clients
docker network inspect clients >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Network clients exists.
) else (
    docker network create clients --subnet 10.0.10.0/24
    echo Network clients created.
)

REM Verificar la existencia de la red servers
docker network inspect servers >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Network servers exists.
) else (
    docker network create servers --subnet 10.0.11.0/24
    echo Network servers created.
)

REM Verificar la existencia de la imagen router
docker image inspect router >nul 2>nul
if %ERRORLEVEL%==0 (
    echo Image router exists.
) else (
    docker build -t router -f router/router.Dockerfile .
    echo Image router created.
)

REM Verificar la existencia del contenedor router
docker container inspect router >nul 2>nul
if %ERRORLEVEL%==0 (
    docker container stop router
    docker container rm router
    echo Container router removed.
)

REM Ejecutar el contenedor router
docker run -d --rm --name router router

echo Container router executed.

REM Conectar el router a las redes clients y servers
docker network connect --ip 10.0.10.254 clients router
docker network connect --ip 10.0.11.254 servers router

echo Container router connected to client and server networks.



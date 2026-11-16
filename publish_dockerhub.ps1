# Script auxiliar para Build e Publicação no Docker Hub
param(
    [Parameter(Mandatory=$false)]
    [string]$DockerUser = ""
)

if (-not $DockerUser) {
    $DockerUser = Read-Host "Digite seu nome de usuário do Docker Hub"
}

if (-not $DockerUser) {
    Write-Host "Nome de usuário não informado. Cancelando." -ForegroundColor Red
    exit 1
}

$ImageTag = "$DockerUser/mineracao-student-api:v1"
$ImageLatest = "$DockerUser/mineracao-student-api:latest"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Iniciando Build da Imagem Docker..." -ForegroundColor Cyan
Write-Host "Tag: $ImageTag" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan

docker build -t $ImageTag -t $ImageLatest .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha no build da imagem Docker." -ForegroundColor Red
    exit 1
}

Write-Host "`nImagem construída com sucesso! Realizando login no Docker Hub..." -ForegroundColor Green
docker login

if ($LASTEXITCODE -ne 0) {
    Write-Host "Falha na autenticação do Docker Hub." -ForegroundColor Red
    exit 1
}

Write-Host "`nPublicando imagem no Docker Hub..." -ForegroundColor Cyan
docker push $ImageTag
docker push $ImageLatest

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host "SUCESSO: Imagem publicada no Docker Hub!" -ForegroundColor Green
Write-Host "Link da imagem: https://hub.docker.com/r/$DockerUser/mineracao-student-api" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green

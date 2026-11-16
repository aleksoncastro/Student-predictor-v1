# Imagem base oficial do Python (versão slim para manter a imagem leve e segura)
FROM python:3.10-slim

# Metadados da imagem
LABEL maintainer="Aluno UNITINS"
LABEL description="Container com modelo de Mineração de Dados para predição de desempenho acadêmico"

# Definir variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Definir diretório de trabalho dentro do container
WORKDIR /app

# Instalar dependências de sistema essenciais (caso necessárias para compilação)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependências do backend primeiro (para otimizar o cache de camadas do Docker)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o modelo treinado, backend e interface frontend
COPY model/ ./model/
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Expor a porta padrão da aplicação web e API
EXPOSE 8000

# Comando para inicializar o servidor ASGI Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

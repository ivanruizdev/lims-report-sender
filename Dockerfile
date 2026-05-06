# ==========================================
# ETAPA 1: Construir el Frontend (Vue.js)
# ==========================================
FROM node:20-alpine AS frontend-builder

# Establecer directorio de trabajo para Vue
WORKDIR /app/dashboard

# Copiar archivos de dependencias
COPY dashboard/package*.json ./

# Instalar dependencias de Node
RUN npm ci

# Copiar el resto del código fuente del frontend
COPY dashboard/ .

# Compilar la aplicación Vue para producción
RUN npm run build


# ==========================================
# ETAPA 2: Construir el Backend (Python)
# ==========================================
FROM python:3.12-slim

# Evitar que Python escriba archivos .pyc y forzar logs inmediatos
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias (ej. para psycopg2 si lo usas)
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente del backend
COPY src/ ./src/

# Copiar los archivos estáticos compilados de Vue desde la Etapa 1
# Los colocamos en una carpeta 'static' para que FastAPI los sirva
COPY --from=frontend-builder /app/dashboard/dist ./src/web/static

# Crear directorios temporales que pueda necesitar el bot
RUN mkdir -p /app/tmp/pdfs

# Exponer el puerto donde correrá Uvicorn (FastAPI)
EXPOSE 8000

# Comando para iniciar la aplicación (Uvicorn sirviendo a FastAPI)
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
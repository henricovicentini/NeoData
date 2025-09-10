FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /code

# Copia dependências e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .

# Variáveis de ambiente do Flask
ENV FLASK_APP=app.main:create_app
ENV FLASK_ENV=development
ENV PYTHONUNBUFFERED=1

# Expõe a porta
EXPOSE 5000

# Comando default
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

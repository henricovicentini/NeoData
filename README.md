# NeoData – Upload e Limpeza de Dados

## Organize, limpe, reutilize

O NeoData é uma aplicação Flask que permite:

Fazer upload de arquivos (.csv, .xlsx, .json ou .zip).

Inserir os dados no banco de dados SQLite.

Executar pipeline de limpeza automática (remoção de duplicados, imputação de nulos, detecção de outliers).

Baixar os dados tratados em CSV, XLSX ou JSON.

Visualizar dashboards interativos com filtros.

# 🚀 Tecnologias

Flask
 (backend web)

Flask-Login
 (autenticação)

Flask-Migrate
 (migrações de banco)

SQLAlchemy
 (ORM)

Pandas
 + Scikit-Learn
 (limpeza e tratamento)

Bootstrap 5
 (frontend responsivo)

Chart.js
 (dashboards interativos)

# 📂 Estrutura do Projeto

NeoData/
│── app/
│   ├── __init__.py
│   ├── main.py              # app principal Flask (factory)
│   ├── db.py                # inicialização SQLAlchemy
│   ├── models.py            # tabelas do banco
│   ├── cleaning.py          # funções de análise e limpeza
│   ├── blueprints/          # rotas organizadas
│   │   ├── auth/            # login/cadastro
│   │   ├── user/            # perfil do usuário
│   │   └── predicao/        # upload e visualização
│   ├── templates/           # HTMLs
│   └── static/              # CSS, JS, uploads
│── requirements.txt
│── Dockerfile
│── docker-compose.yml
│── README.md

# ⚙️ Instalação e Uso

🔹 Rodando localmente

git clone https://github.com/seu-usuario/neodata.git
cd neodata
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
flask --app app.main run


🔹 Rodando com Docker

docker-compose up --build

# 🔄 Fluxo de Uso

Faça login/cadastro.

Vá em Upload e envie um arquivo (CSV, XLSX, JSON ou ZIP).

Os dados são salvos na tabela RawRecord.

Clique em Executar Limpeza → dados tratados vão para CleanRecord.

Baixe os dados em CSV, XLSX ou JSON.

Explore os dashboards com filtros por empresa/ano.

# 🛠️ Desenvolvimento

Banco de dados SQLite (pode ser trocado por PostgreSQL facilmente).

Migrações com Alembic:

flask --app app.main db init
flask --app app.main db migrate -m "init"
flask --app app.main db upgrade


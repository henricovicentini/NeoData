# NeoData

**“Organize, limpe, reutilize”**

## 🚀 Objetivo Geral
Criar um sistema capaz de ingerir dados estruturados (CSV, SQL), detectar inconsistências, limpar automaticamente e disponibilizar os dados tratados para reutilização em outros sistemas, relatórios ou modelos.

---

## 🔄 Fluxo de Funcionamento

1. **Ingestão de Dados**
   - Upload de arquivos (CSV/Excel).
   - Conexão via API a bancos de dados (MySQL, PostgreSQL, SQL Server).
   - Extração para DataFrames (pandas).

2. **Análise Automática**
   - Estatísticas descritivas para identificar:
     - Valores ausentes (NaN)
     - Linhas duplicadas
     - Outliers
     - Tipos de dados inconsistentes

3. **Limpeza Inteligente (IA + Regras)**
   - Preenchimento automático (média, mediana, imputação por KNN/Random Forest).
   - Conversão de formatos (datas, moedas, strings).
   - Remoção/correção de duplicatas.

4. **Reutilização**
   - Exportação dos dados tratados em CSV/JSON.
   - Inserção dos dados limpos em outro banco de dados.
   - Integração com dashboards (Power BI, Metabase).

---

## 🛠️ Ferramentas Sugeridas
- **Python + pandas** → manipulação de dados  
- **SQLAlchemy** → conexão a bancos SQL  
- **scikit-learn** → detecção de outliers e imputação inteligente  
- **Great Expectations** → validação de qualidade de dados  
- **FastAPI ou Flask** → API  
- **Streamlit/Django/Flask + HTML/CSS** → interface web  

---

## 📊 Complexidade por Etapa
| Etapa | Descrição | Grau |
|-------|-----------|------|
| 1 | Site (upload CSV → limpeza → download CSV) | **5/10** |
| 2 | Site + API (upload → consumo por sistemas externos) | **6/10** |
| 3 | API + Banco de Dados (consulta → limpeza → retorno) | **7/10** |

---

## 🌐 Recursos da Demonstração
- Visualização dos **dados brutos** (com destaques para ausentes, duplicatas e outliers).  
- Botão **“Limpar Dados”** → executa modelo de limpeza.  
- Comparação **antes x depois** da limpeza.  
- **Download dos dados tratados** (CSV ou Excel).  
- **Estatísticas e gráficos** sobre valores imputados, duplicatas removidas e outliers tratados.  

---

## 📥 Como Popular o Banco de Dados
- **Gerar dados sintéticos** (pandas + numpy) com erros intencionais.  
- **Usar datasets públicos** (Kaggle, UCI, etc.).  
- **Atualização automática** com inserção periódica de registros.  

---

## ⚙️ Tecnologias da Demo
- **Frontend:** HTML + CSS + Bootstrap/Tailwind  
- **Backend:** Flask ou FastAPI  
- **Banco de dados:** SQLite (protótipo) ou PostgreSQL  
- **Python:** pandas, scikit-learn, SQLAlchemy  
- **Visualização:** Plotly, Matplotlib, Dash  

---

## 🔮 Observações
- Para protótipo: apenas **upload CSV + limpeza + download**.  
- Próxima etapa: adicionar banco e API para escalabilidade.  
- Continuous Learning não é necessário neste estágio.  

---

## 👨‍💻 Contribuindo
Contribuições são bem-vindas!  
Abra uma **issue** ou envie um **pull request**.  

---

## 📜 Licença
Este projeto está sob a licença **MIT**.

---

## 📭 Contato
vicentinihenrico@gmail.com


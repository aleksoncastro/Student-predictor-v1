# Sistema de Predição Acadêmica com Container Docker e Backend FastAPI

Projeto prático desenvolvido para a disciplina de **Mineração de Dados** do curso de **Sistemas de Informação** da **UNITINS (Universidade Estadual do Tocantins)**.

O objetivo desta aplicação é carregar um modelo de Machine Learning treinado com o dataset *Predict Students' Dropout and Academic Success* (UCI ID: 697), disponibilizá-lo através de uma API REST (FastAPI), fornecer uma interface web responsiva para consultas com validação e aviso obrigatório, e empacotar a solução em um container Docker para publicação no Docker Hub.

---

## 📁 Estrutura do Projeto

```text
atv13/
├── model/
│   ├── train_model.py          # Script de treinamento e exportação do modelo
│   ├── student_model.pkl       # Modelo serializado com joblib
│   ├── model_metadata.json     # Metadados: ordem dos atributos, acurácia e defaults
│   └── dataset_sample.csv      # Amostra com exemplos para referência
├── backend/
│   ├── main.py                 # API REST FastAPI + Servidor de arquivos estáticos
│   └── requirements.txt        # Dependências Python (FastAPI, uvicorn, scikit-learn, etc.)
├── frontend/
│   ├── index.html              # Interface web com formulário e aviso obrigatório
│   ├── style.css               # Folha de estilos moderna e responsiva
│   └── app.js                  # Validação client-side, carregamento de perfis e chamadas API
├── Dockerfile                  # Empacotamento Docker unificado (Python 3.10-slim)
├── .dockerignore               # Arquivos ignorados no build
├── docker-compose.yml          # Orquestração local simplificada
├── test_api.py                 # Suíte de testes automatizados com FastAPI TestClient
├── publish_dockerhub.ps1       # Script PowerShell para publicar a imagem no Docker Hub
├── run_local.bat               # Atalho para executar a aplicação localmente
└── README.md                   # Documentação detalhada
```

---

## 🧠 Modelo de Machine Learning

- **Dataset**: *Predict Students' Dropout and Academic Success* (UCI Machine Learning Repository #697).
- **Algoritmo**: `RandomForestClassifier` (200 árvores, profundidade balanceada).
- **Classes de Saída**:
  - `0`: **Abandono** (*Dropout*)
  - `1`: **Matriculado** (*Enrolled*)
  - `2`: **Concluinte** (*Graduate*)
- **Acurácia**: ~**77.1%** no conjunto de teste estratificado (80/20).
- **Garantia de Pré-processamento**: Os atributos recebidos na API são validados via Pydantic e reordenados rigorosamente na mesma ordem em que o modelo foi treinado (`feature_order`), preenchendo automaticamente quaisquer atributos não enviados com as medianas calculadas no treinamento.

---

## 🌐 Funcionalidades da Interface Web

1. **Formulário Organizado por Categorias**:
   - Desempenho acadêmico (disciplinas aprovadas, médias e avaliações no 1º e 2º semestres).
   - Situação financeira (mensalidades em dia, status de bolsista, pendências financeiras).
   - Perfil demográfico (idade de matrícula, gênero, deslocamento territorial).
   - Parâmetros complementares colapsáveis (notas de vestibular, qualificações anteriores e dados socioeconômicos).
2. **Perfis Rápidos de Exemplo**:
   - Botões de um clique para carregar cenários reais: *Concluinte*, *Risco de Abandono* e *Matriculado*.
3. **Validação Client-Side**:
   - Impede submissão de notas fora da escala (0 a 20), idades inconsistentes ou unidades aprovadas superiores ao número de disciplinas matriculadas.
4. **Apresentação Clara do Resultado**:
   - Badge destacado com a classe prevista.
   - Barras com a distribuição percentual de probabilidades de cada classe.
5. **Aviso Institucional Obrigatório**:
   - Exibido com destaque conforme exigência da atividade:
   > *"Aviso: Esta previsão é um apoio à análise, e não uma decisão definitiva sobre a trajetória de um estudante."*

---

## 🚀 Execução Local (Sem Docker)

Caso queira executar diretamente no ambiente Python:

1. **Instalar dependências**:
   ```bash
   pip install -r backend/requirements.txt
   ```

2. **Treinar o modelo (se necessário gerar novamente)**:
   ```bash
   py model/train_model.py
   ```

3. **Executar os testes automatizados**:
   ```bash
   py test_api.py
   ```

4. **Iniciar o servidor**:
   ```bash
   py -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   Acesse a aplicação no navegador em: **`http://localhost:8000`**  
   Documentação interativa Swagger em: **`http://localhost:8000/docs`**

---

## 🐳 Containerização com Docker

### 1. Construir a Imagem Docker
No diretório raiz do projeto:
```bash
docker build -t seu-usuario-dockerhub/mineracao-student-api:v1 .
```
*(Substitua `seu-usuario-dockerhub` pelo seu usuário no Docker Hub).*

### 2. Executar o Container Localmente
```bash
docker run -d -p 8000:8000 --name test-container seu-usuario-dockerhub/mineracao-student-api:v1
```
Acesse `http://localhost:8000` para a interface web e `http://localhost:8000/docs` para a API.

Para encerrar o container de teste:
```bash
docker stop test-container && docker rm test-container
```

### 3. Publicar no Docker Hub
Faça o login e envie a imagem:
```bash
docker login
docker push seu-usuario-dockerhub/mineracao-student-api:v1
```

*(Ou utilize o script automatizado `.\publish_dockerhub.ps1`).*

---

## 📡 Endpoints da API REST

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Retorna a interface web estática (`index.html`) |
| `POST` | `/predict` | Recebe dados do estudante e retorna a classe prevista e probabilidades |
| `GET` | `/health` | Checagem de disponibilidade do serviço e carregamento do modelo |
| `GET` | `/info` | Metadados do modelo, classes e acurácia |
| `GET` | `/example/{tipo}` | Retorna exemplo preenchido (`concluinte`, `abandono`, `matriculado`) |
| `GET` | `/docs` | Documentação interativa Swagger UI |

### Exemplo de Requisição (`POST /predict`):
```json
{
  "Curricular_units_1st_sem_approved": 5,
  "Curricular_units_1st_sem_grade": 14.5,
  "Curricular_units_2nd_sem_approved": 5,
  "Curricular_units_2nd_sem_grade": 15.0,
  "Tuition_fees_up_to_date": 1,
  "Scholarship_holder": 1,
  "Debtor": 0,
  "Age_at_enrollment": 19
}
```

### Exemplo de Resposta:
```json
{
  "prediction": "Concluinte",
  "prediction_code": 2,
  "probabilities": {
    "Abandono": 5.24,
    "Matriculado": 2.27,
    "Concluinte": 92.49
  },
  "disclaimer": "Aviso: Esta previsão é um apoio à análise, e não uma decisão definitiva sobre a trajetória de um estudante."
}
```

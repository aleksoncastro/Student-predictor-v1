"""
API de Predição de Desempenho Acadêmico (Mineração de Dados - UNITINS)
Empacotamento Backend com Modelo de Machine Learning e Interface Web
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

# Configuração de caminhos do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "model" / "student_model.pkl"
METADATA_PATH = BASE_DIR / "model" / "model_metadata.json"
FRONTEND_DIR = BASE_DIR / "frontend"

# Inicialização da aplicação FastAPI
app = FastAPI(
    title="API de Predição de Desempenho Acadêmico",
    description="API para prever Abandono, Matrícula ou Conclusão de estudantes universitários.",
    version="1.0.0"
)

# Liberação de CORS para permitir acesso do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Carregamento do modelo treinado e metadados
if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Modelo não encontrado em: {MODEL_PATH}. Execute 'py model/train_model.py' primeiro.")

model = joblib.load(MODEL_PATH)

metadata = {}
if METADATA_PATH.exists():
    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)

FEATURE_ORDER = metadata.get("feature_order", [])
CLASSES_MAP = {
    0: "Abandono",
    1: "Matriculado",
    2: "Concluinte"
}
DISCLAIMER_TEXT = "Aviso: Esta previsão é um apoio à análise, e não uma decisão definitiva sobre a trajetória de um estudante."


class StudentInput(BaseModel):
    """
    Estrutura de dados de entrada do estudante com valores padrão
    e validações rigorosas dos limites acadêmicos e demográficos.
    """
    # 1. Atributos Acadêmicos Principais (Semestres 1 e 2)
    Curricular_units_1st_sem_approved: int = Field(5, ge=0, le=30, description="Disciplinas aprovadas no 1º semestre")
    Curricular_units_1st_sem_grade: float = Field(12.29, ge=0.0, le=20.0, description="Média das notas no 1º semestre (0 a 20)")
    Curricular_units_1st_sem_enrolled: int = Field(6, ge=0, le=30, description="Disciplinas matriculadas no 1º semestre")
    Curricular_units_1st_sem_evaluations: int = Field(8, ge=0, le=40, description="Avaliações realizadas no 1º semestre")
    Curricular_units_1st_sem_credited: int = Field(0, ge=0, le=30, description="Disciplinas com equivalência creditada no 1º sem")
    Curricular_units_1st_sem_without_evaluations: int = Field(0, ge=0, le=30, description="Disciplinas sem avaliação no 1º sem")

    Curricular_units_2nd_sem_approved: int = Field(5, ge=0, le=30, description="Disciplinas aprovadas no 2º semestre")
    Curricular_units_2nd_sem_grade: float = Field(12.20, ge=0.0, le=20.0, description="Média das notas no 2º semestre (0 a 20)")
    Curricular_units_2nd_sem_enrolled: int = Field(6, ge=0, le=30, description="Disciplinas matriculadas no 2º semestre")
    Curricular_units_2nd_sem_evaluations: int = Field(8, ge=0, le=40, description="Avaliações realizadas no 2º semestre")
    Curricular_units_2nd_sem_credited: int = Field(0, ge=0, le=30, description="Disciplinas com equivalência creditada no 2º sem")
    Curricular_units_2nd_sem_without_evaluations: int = Field(0, ge=0, le=30, description="Disciplinas sem avaliação no 2º sem")

    # 2. Atributos Financeiros e Socioeconômicos
    Tuition_fees_up_to_date: int = Field(1, ge=0, le=1, description="Mensalidades em dia (1 = Sim, 0 = Não)")
    Scholarship_holder: int = Field(0, ge=0, le=1, description="Bolsista (1 = Sim, 0 = Não)")
    Debtor: int = Field(0, ge=0, le=1, description="Estudante inadimplente/devedor (1 = Sim, 0 = Não)")

    # 3. Atributos Demográficos e Pessoais
    Age_at_enrollment: int = Field(20, ge=15, le=100, description="Idade do estudante no momento da matrícula")
    Gender: int = Field(0, ge=0, le=1, description="Gênero (1 = Masculino, 0 = Feminino)")
    Marital_Status: int = Field(1, ge=1, le=6, description="Estado civil (1 = Solteiro, 2 = Casado, etc.)")
    Displaced: int = Field(1, ge=0, le=1, description="Estudante deslocado de sua cidade/região (1 = Sim, 0 = Não)")
    Educational_special_needs: int = Field(0, ge=0, le=1, description="Necessidades educacionais especiais (1 = Sim, 0 = Não)")
    International: int = Field(0, ge=0, le=1, description="Estudante internacional (1 = Sim, 0 = Não)")
    Nacionality: int = Field(1, ge=1, le=100, description="Nacionalidade do estudante")

    # 4. Atributos de Ingresso e Curso
    Course: int = Field(9238, ge=1, description="Código do curso de graduação")
    Application_mode: int = Field(17, ge=1, description="Modo/fase de candidatura")
    Application_order: int = Field(1, ge=0, le=9, description="Ordem de preferência da opção")
    Daytime_evening_attendance: int = Field(1, ge=0, le=1, description="Turno (1 = Diurno, 0 = Noturno)")
    Previous_qualification: int = Field(1, ge=1, description="Qualificação anterior")
    Previous_qualification_grade: float = Field(133.1, ge=0.0, le=200.0, description="Nota da qualificação prévia (0 a 200)")
    Admission_grade: float = Field(126.1, ge=0.0, le=200.0, description="Nota no processo seletivo de admissão (0 a 200)")

    # 5. Informações Familiares e Contexto Econômico
    Mothers_qualification: int = Field(19, ge=1, description="Nível de escolaridade da mãe")
    Fathers_qualification: int = Field(19, ge=1, description="Nível de escolaridade do pai")
    Mothers_occupation: int = Field(5, ge=0, description="Código da ocupação da mãe")
    Fathers_occupation: int = Field(7, ge=0, description="Código da ocupação do pai")
    Unemployment_rate: float = Field(11.1, ge=0.0, le=50.0, description="Taxa de desemprego regional (%)")
    Inflation_rate: float = Field(1.4, ge=-10.0, le=50.0, description="Taxa de inflação (%)")
    GDP: float = Field(0.32, ge=-20.0, le=20.0, description="Variação do PIB (%)")

    @field_validator("Curricular_units_1st_sem_grade", "Curricular_units_2nd_sem_grade")
    @classmethod
    def validate_grades(cls, v: float) -> float:
        if v < 0.0 or v > 20.0:
            raise ValueError("As notas semestrais devem estar na escala de 0.0 a 20.0.")
        return round(v, 2)


@app.get("/health")
def health_check():
    """Verifica se o backend e o modelo estão ativos."""
    return {
        "status": "online",
        "model_loaded": model is not None,
        "features_count": len(FEATURE_ORDER),
        "classes": list(CLASSES_MAP.values())
    }


@app.get("/info")
def model_info():
    """Retorna detalhes sobre o modelo treinado e métricas."""
    return {
        "model_type": metadata.get("model_type", "RandomForestClassifier"),
        "accuracy": metadata.get("accuracy", 0.77),
        "classes": CLASSES_MAP,
        "feature_order": FEATURE_ORDER,
        "classification_report": metadata.get("classification_report", {})
    }


@app.get("/example/{profile_type}")
def get_example_profile(profile_type: str):
    """
    Retorna perfis de exemplo para facilitar os testes rápidos da interface.
    Tipos disponíveis: 'concluinte', 'abandono', 'matriculado'.
    """
    p = profile_type.lower()
    if p in ["concluinte", "graduate"]:
        return {
            "Curricular_units_1st_sem_approved": 6,
            "Curricular_units_1st_sem_grade": 15.5,
            "Curricular_units_1st_sem_enrolled": 6,
            "Curricular_units_1st_sem_evaluations": 7,
            "Curricular_units_1st_sem_credited": 0,
            "Curricular_units_1st_sem_without_evaluations": 0,
            "Curricular_units_2nd_sem_approved": 6,
            "Curricular_units_2nd_sem_grade": 16.0,
            "Curricular_units_2nd_sem_enrolled": 6,
            "Curricular_units_2nd_sem_evaluations": 7,
            "Curricular_units_2nd_sem_credited": 0,
            "Curricular_units_2nd_sem_without_evaluations": 0,
            "Tuition_fees_up_to_date": 1,
            "Scholarship_holder": 1,
            "Debtor": 0,
            "Age_at_enrollment": 19,
            "Gender": 0,
            "Marital_Status": 1,
            "Displaced": 1,
            "Educational_special_needs": 0,
            "International": 0,
            "Nacionality": 1,
            "Course": 9238,
            "Application_mode": 1,
            "Application_order": 1,
            "Daytime_evening_attendance": 1,
            "Previous_qualification": 1,
            "Previous_qualification_grade": 150.0,
            "Admission_grade": 145.0,
            "Mothers_qualification": 1,
            "Fathers_qualification": 1,
            "Mothers_occupation": 3,
            "Fathers_occupation": 3,
            "Unemployment_rate": 10.8,
            "Inflation_rate": 1.4,
            "GDP": 1.74
        }
    elif p in ["abandono", "dropout", "risco"]:
        return {
            "Curricular_units_1st_sem_approved": 0,
            "Curricular_units_1st_sem_grade": 0.0,
            "Curricular_units_1st_sem_enrolled": 6,
            "Curricular_units_1st_sem_evaluations": 4,
            "Curricular_units_1st_sem_credited": 0,
            "Curricular_units_1st_sem_without_evaluations": 2,
            "Curricular_units_2nd_sem_approved": 0,
            "Curricular_units_2nd_sem_grade": 0.0,
            "Curricular_units_2nd_sem_enrolled": 6,
            "Curricular_units_2nd_sem_evaluations": 2,
            "Curricular_units_2nd_sem_credited": 0,
            "Curricular_units_2nd_sem_without_evaluations": 4,
            "Tuition_fees_up_to_date": 0,
            "Scholarship_holder": 0,
            "Debtor": 1,
            "Age_at_enrollment": 28,
            "Gender": 1,
            "Marital_Status": 1,
            "Displaced": 0,
            "Educational_special_needs": 0,
            "International": 0,
            "Nacionality": 1,
            "Course": 9147,
            "Application_mode": 39,
            "Application_order": 2,
            "Daytime_evening_attendance": 0,
            "Previous_qualification": 1,
            "Previous_qualification_grade": 115.0,
            "Admission_grade": 110.0,
            "Mothers_qualification": 19,
            "Fathers_qualification": 19,
            "Mothers_occupation": 9,
            "Fathers_occupation": 9,
            "Unemployment_rate": 13.9,
            "Inflation_rate": -0.3,
            "GDP": -1.7
        }
    else:  # matriculado / enrolled
        return {
            "Curricular_units_1st_sem_approved": 3,
            "Curricular_units_1st_sem_grade": 11.0,
            "Curricular_units_1st_sem_enrolled": 6,
            "Curricular_units_1st_sem_evaluations": 6,
            "Curricular_units_1st_sem_credited": 0,
            "Curricular_units_1st_sem_without_evaluations": 0,
            "Curricular_units_2nd_sem_approved": 3,
            "Curricular_units_2nd_sem_grade": 11.5,
            "Curricular_units_2nd_sem_enrolled": 6,
            "Curricular_units_2nd_sem_evaluations": 7,
            "Curricular_units_2nd_sem_credited": 0,
            "Curricular_units_2nd_sem_without_evaluations": 0,
            "Tuition_fees_up_to_date": 1,
            "Scholarship_holder": 0,
            "Debtor": 0,
            "Age_at_enrollment": 21,
            "Gender": 1,
            "Marital_Status": 1,
            "Displaced": 1,
            "Educational_special_needs": 0,
            "International": 0,
            "Nacionality": 1,
            "Course": 9238,
            "Application_mode": 17,
            "Application_order": 1,
            "Daytime_evening_attendance": 1,
            "Previous_qualification": 1,
            "Previous_qualification_grade": 130.0,
            "Admission_grade": 125.0,
            "Mothers_qualification": 19,
            "Fathers_qualification": 19,
            "Mothers_occupation": 5,
            "Fathers_occupation": 7,
            "Unemployment_rate": 11.1,
            "Inflation_rate": 1.4,
            "GDP": 0.32
        }


@app.post("/predict")
def predict_student(data: StudentInput):
    """
    Recebe os dados do estudante, ordena os atributos conforme o treinamento
    e retorna a previsão com probabilidades e o aviso institucional obrigatório.
    """
    try:
        # Converter para dicionário e garantir a ordem exata das features
        data_dict = data.model_dump()
        
        # Montar DataFrame respeitando a lista FEATURE_ORDER
        if FEATURE_ORDER:
            # Preencher eventuais features faltantes com seus valores padrão
            ordered_data = {feat: data_dict.get(feat, metadata.get("feature_defaults", {}).get(feat, 0)) for feat in FEATURE_ORDER}
            input_df = pd.DataFrame([ordered_data])
        else:
            input_df = pd.DataFrame([data_dict])

        # Realizar a predição da classe
        prediction_code = int(model.predict(input_df)[0])
        result_class = CLASSES_MAP.get(prediction_code, str(prediction_code))

        # Obter probabilidades de cada classe
        probabilities = {}
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_df)[0]
            # model.classes_ corresponde às classes codificadas [0, 1, 2]
            for idx, prob in zip(model.classes_, probs):
                class_name = CLASSES_MAP.get(int(idx), str(idx))
                probabilities[class_name] = round(float(prob) * 100, 2)

        return {
            "prediction": result_class,
            "prediction_code": prediction_code,
            "probabilities": probabilities,
            "disclaimer": DISCLAIMER_TEXT
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro no processamento da predição: {str(e)}")


# Servir Frontend Estático
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def serve_index():
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        return {"message": "API de Predição ativa. Interface web em desenvolvimento."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

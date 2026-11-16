"""
Script de Treinamento do Modelo de Predição de Desempenho Acadêmico
Dataset: Predict Students' Dropout and Academic Success (UCI ID: 697)
Curso: Sistemas de Informação - UNITINS
Disciplina: Mineração de Dados
"""

import os
import json
import re
import joblib
import pandas as pd
import numpy as np
from ucimlrepo import fetch_ucirepo
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

def clean_column_name(col: str) -> str:
    """Padroniza nomes de colunas para snake_case sem caracteres especiais."""
    c = col.replace("'", "").replace("/", "_").replace("-", "_")
    c = re.sub(r"[\(\)]", "", c)
    c = re.sub(r"\s+", "_", c)
    return c

def main():
    print("=" * 60)
    print("Iniciando treinamento do modelo de Mineração de Dados...")
    print("=" * 60)

    # 1. Carregar dataset do repositório UCI
    print("\n[1/6] Baixando dataset UCI ID 697 (Predict Students' Dropout and Academic Success)...")
    dataset = fetch_ucirepo(id=697)
    X_raw = dataset.data.features
    y_raw = dataset.data.targets.squeeze()

    print(f"Dataset carregado com sucesso!")
    print(f"Total de registros: {X_raw.shape[0]}")
    print(f"Total de atributos (features): {X_raw.shape[1]}")

    # 2. Pré-processamento e padronização dos atributos
    print("\n[2/6] Pré-processando atributos e mapeando classes...")
    rename_dict = {col: clean_column_name(col) for col in X_raw.columns}
    X = X_raw.rename(columns=rename_dict)
    feature_order = list(X.columns)

    # Mapeamento do alvo: 0: Abandono (Dropout), 1: Matriculado (Enrolled), 2: Concluinte (Graduate)
    target_encoding = {
        "Dropout": 0,
        "Enrolled": 1,
        "Graduate": 2
    }
    classes_map = {
        0: "Abandono",
        1: "Matriculado",
        2: "Concluinte"
    }

    y = y_raw.map(target_encoding)

    # Calcular valores padrão (medianas) para cada atributo
    defaults = {}
    for col in X.columns:
        if X[col].dtype == "int64":
            defaults[col] = int(X[col].median())
        else:
            defaults[col] = round(float(X[col].median()), 2)

    # 3. Divisão Treino e Teste (80% / 20% estratificado)
    print("\n[3/6] Dividindo base de dados em Treino (80%) e Teste (20%)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"Exemplos de Treino: {X_train.shape[0]} | Exemplos de Teste: {X_test.shape[0]}")

    # 4. Treinamento do Modelo (Random Forest Classifier)
    print("\n[4/6] Treinando classificador Random Forest (200 estimadores, balanceamento de classes)...")
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=16,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    # 5. Avaliação do Modelo
    print("\n[5/6] Avaliando métricas do modelo...")
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    target_names = ["Abandono", "Matriculado", "Concluinte"]
    report = classification_report(y_test, y_pred, target_names=target_names, output_dict=True)
    report_text = classification_report(y_test, y_pred, target_names=target_names)
    matrix = confusion_matrix(y_test, y_pred).tolist()

    print(f"\nAcurácia do modelo: {acc * 100:.2f}%\n")
    print(report_text)

    # 6. Salvar artefatos
    print("\n[6/6] Salvando modelo e metadados...")
    os.makedirs("model", exist_ok=True)
    model_path = os.path.join("model", "student_model.pkl")
    metadata_path = os.path.join("model", "model_metadata.json")
    sample_path = os.path.join("model", "dataset_sample.csv")

    joblib.dump(model, model_path)
    print(f"-> Modelo serializado em: {model_path}")

    # Metadados completos
    metadata = {
        "model_type": "RandomForestClassifier",
        "n_estimators": 200,
        "accuracy": round(acc, 4),
        "classes_map": classes_map,
        "target_encoding": target_encoding,
        "feature_order": feature_order,
        "feature_defaults": defaults,
        "confusion_matrix": matrix,
        "classification_report": report
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"-> Metadados salvos em: {metadata_path}")

    # Salvar amostra do dataset para consulta rápida
    sample_df = X.copy()
    sample_df["Target_Class"] = y.map(classes_map)
    sample_df.head(20).to_csv(sample_path, index=False)
    print(f"-> Amostra do dataset salva em: {sample_path}")

    print("\n" + "=" * 60)
    print("Treinamento finalizado com sucesso!")
    print("=" * 60)

if __name__ == "__main__":
    main()

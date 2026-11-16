/**
 * Script Frontend - Sistema de Predição Acadêmica
 * Mineração de Dados - UNITINS
 */

const API_BASE = window.location.origin;

// Elementos da Interface
const form = document.getElementById("predictionForm");
const btnSubmit = document.getElementById("btnSubmit");
const placeholderState = document.getElementById("placeholderState");
const resultDisplay = document.getElementById("resultDisplay");
const predictionBadge = document.getElementById("predictionBadge");
const predictionDescription = document.getElementById("predictionDescription");
const barGraduate = document.getElementById("bar-graduate");
const barEnrolled = document.getElementById("bar-enrolled");
const barDropout = document.getElementById("bar-dropout");
const probGraduate = document.getElementById("prob-graduate");
const probEnrolled = document.getElementById("prob-enrolled");
const probDropout = document.getElementById("prob-dropout");
const resultDisclaimerText = document.getElementById("resultDisclaimerText");
const apiStatusBadge = document.getElementById("apiStatusBadge");
const apiStatusText = document.getElementById("apiStatusText");
const toast = document.getElementById("toast");

// Inicialização
document.addEventListener("DOMContentLoaded", () => {
  checkBackendHealth();
  setupValidationListeners();
});

// Checagem de Saúde do Backend
async function checkBackendHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    if (res.ok) {
      const data = await res.json();
      apiStatusBadge.classList.add("status-online");
      apiStatusText.textContent = `Online • ${data.features_count} atributos`;
    } else {
      apiStatusText.textContent = "Serviço com instabilidade";
    }
  } catch (err) {
    apiStatusText.textContent = "Offline (Tentando reconectar)";
  }
}

// Carregar Perfis Predefinidos de Exemplo
async function loadProfile(type) {
  try {
    showToast(`Carregando perfil de exemplo: ${type.toUpperCase()}...`);
    const res = await fetch(`${API_BASE}/example/${type}`);
    if (!res.ok) throw new Error("Falha ao buscar exemplo da API.");
    
    const profile = await res.json();

    // Preencher campos do formulário
    for (const [key, val] of Object.entries(profile)) {
      const input = document.getElementById(key);
      if (input) {
        input.value = val;
        clearError(input);
      }
    }

    // Submeter automaticamente para exibir o resultado imediatamente
    submitPrediction();
  } catch (err) {
    showToast("Erro ao carregar perfil: " + err.message, true);
  }
}

// Limpar Formulário
function resetForm() {
  form.reset();
  clearAllErrors();
  placeholderState.style.display = "block";
  resultDisplay.style.display = "none";
  showToast("Formulário redefinido com valores padrão.");
}

// Configuração de Listeners de Validação em Tempo Real
function setupValidationListeners() {
  const inputs = form.querySelectorAll("input, select");
  inputs.forEach(input => {
    input.addEventListener("input", () => clearError(input));
  });

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    submitPrediction();
  });
}

// Validação dos Campos no Client-Side
function validateForm() {
  let isValid = true;
  clearAllErrors();

  const sem1Grade = parseFloat(document.getElementById("Curricular_units_1st_sem_grade").value);
  const sem2Grade = parseFloat(document.getElementById("Curricular_units_2nd_sem_grade").value);
  const age = parseInt(document.getElementById("Age_at_enrollment").value, 10);
  const sem1Approved = parseInt(document.getElementById("Curricular_units_1st_sem_approved").value, 10);
  const sem1Enrolled = parseInt(document.getElementById("Curricular_units_1st_sem_enrolled").value, 10);

  if (isNaN(sem1Grade) || sem1Grade < 0 || sem1Grade > 20) {
    showError("Curricular_units_1st_sem_grade", "A nota do 1º semestre deve estar entre 0.0 e 20.0.");
    isValid = false;
  }

  if (isNaN(sem2Grade) || sem2Grade < 0 || sem2Grade > 20) {
    showError("Curricular_units_2nd_sem_grade", "A nota do 2º semestre deve estar entre 0.0 e 20.0.");
    isValid = false;
  }

  if (isNaN(age) || age < 15 || age > 100) {
    showError("Age_at_enrollment", "A idade de ingresso deve ser entre 15 e 100 anos.");
    isValid = false;
  }

  if (sem1Approved > sem1Enrolled) {
    showError("Curricular_units_1st_sem_approved", "Disciplinas aprovadas não podem exceder o total matriculado.");
    isValid = false;
  }

  return isValid;
}

function showError(fieldId, message) {
  const input = document.getElementById(fieldId);
  const errorSpan = document.getElementById(`err-${fieldId}`);
  if (input) input.classList.add("invalid");
  if (errorSpan) errorSpan.textContent = message;
}

function clearError(input) {
  input.classList.remove("invalid");
  const errorSpan = document.getElementById(`err-${input.id}`);
  if (errorSpan) errorSpan.textContent = "";
}

function clearAllErrors() {
  const invalidInputs = form.querySelectorAll(".invalid");
  invalidInputs.forEach(i => i.classList.remove("invalid"));
  const errorSpans = form.querySelectorAll(".error-msg");
  errorSpans.forEach(s => s.textContent = "");
}

// Submissão dos Dados e Predição
async function submitPrediction() {
  if (!validateForm()) {
    showToast("Por favor, corrija os campos com erros antes de continuar.", true);
    return;
  }

  // Coletar dados de todos os inputs do formulário
  const formData = new FormData(form);
  const payload = {};

  formData.forEach((value, key) => {
    // Converter tipos apropriados
    if (key.includes("grade") || key.includes("rate") || key === "GDP" || key.includes("grade")) {
      payload[key] = parseFloat(value);
    } else {
      payload[key] = parseInt(value, 10);
    }
  });

  // Estado de carregamento
  btnSubmit.disabled = true;
  btnSubmit.querySelector(".btn-text").textContent = "Processando pelo modelo...";

  try {
    const response = await fetch(`${API_BASE}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || "Falha na comunicação com a API.");
    }

    const result = await response.json();
    renderResult(result);
    showToast("Predição concluída com sucesso!");

  } catch (error) {
    showToast("Erro: " + error.message, true);
  } finally {
    btnSubmit.disabled = false;
    btnSubmit.querySelector(".btn-text").textContent = "🔍 Realizar Predição";
  }
}

// Exibir Resultado na Interface
function renderResult(data) {
  placeholderState.style.display = "none";
  resultDisplay.style.display = "block";

  const pred = data.prediction;
  predictionBadge.textContent = pred;
  predictionBadge.className = "prediction-badge";

  // Estilização conforme a classe
  if (pred === "Concluinte") {
    predictionBadge.classList.add("badge-concluinte");
    predictionDescription.innerHTML = "<strong>Forte probabilidade de graduação.</strong> O estudante mantém rendimento acadêmico regular, aprovações consistentes e situação financeira em conformidade.";
  } else if (pred === "Abandono") {
    predictionBadge.classList.add("badge-abandono");
    predictionDescription.innerHTML = "<strong>Alerta de evasão/abandono detectado.</strong> O modelo identificou padrões de risco (baixa taxa de aprovação, notas insuficientes ou inadimplência). Recomenda-se acompanhamento psicopedagógico.";
  } else {
    predictionBadge.classList.add("badge-matriculado");
    predictionDescription.innerHTML = "<strong>Estudante com status ativo/matriculado.</strong> Desempenho acadêmico intermediário, demandando monitoramento contínuo das disciplinas em curso.";
  }

  // Atualizar barras de probabilidades
  const probs = data.probabilities || {};
  const grad = probs["Concluinte"] || 0;
  const enrol = probs["Matriculado"] || 0;
  const drop = probs["Abandono"] || 0;

  probGraduate.textContent = `${grad}%`;
  barGraduate.style.width = `${grad}%`;

  probEnrolled.textContent = `${enrol}%`;
  barEnrolled.style.width = `${enrol}%`;

  probDropout.textContent = `${drop}%`;
  barDropout.style.width = `${drop}%`;

  // Aviso obrigatório
  if (data.disclaimer) {
    resultDisclaimerText.textContent = data.disclaimer;
  }
}

// Exibir Notificação Toast
function showToast(message, isError = false) {
  toast.textContent = message;
  toast.className = "toast" + (isError ? " error" : "") + " show";
  setTimeout(() => {
    toast.className = "toast";
  }, 3500);
}

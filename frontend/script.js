// script.js

// Backend API Base URL
const API_BASE_URL = "http://localhost:8000";

// Global Session States
let activeModel = "loan"; // default model
let totalPredictions = 0;
let predictionHistory = [];

// DOM Elements
const apiPulse = document.getElementById("api-pulse");
const apiStatusText = document.getElementById("api-status-text");
const healthApiStatus = document.getElementById("health-api-status");
const healthSystemStatus = document.getElementById("health-system-status");
const statsTotalPredictions = document.getElementById("stats-total-predictions");
const statsAvgLatency = document.getElementById("stats-avg-latency");

const modelCards = document.querySelectorAll(".model-select-card");
const dynamicFieldsContainer = document.getElementById("dynamic-fields-container");
const predictionForm = document.getElementById("prediction-form");
const btnPredict = document.getElementById("btn-predict");
const predictSpinner = document.getElementById("predict-spinner");
const btnText = document.getElementById("btn-text");

const resultPanel = document.getElementById("prediction-result-panel");
const outputModelBadge = document.getElementById("output-model-badge");
const outputValue = document.getElementById("output-value");
const outputLatency = document.getElementById("output-latency");
const outputVersion = document.getElementById("output-version");
const outputTime = document.getElementById("output-time");

const errorPanel = document.getElementById("prediction-error-panel");
const errorTitle = document.getElementById("error-title");
const errorDesc = document.getElementById("error-desc");

// Chaos Trigger Elements
const btnChaosLatency = document.getElementById("btn-chaos-latency");
const latencySpinner = document.getElementById("latency-spinner");
const btnChaosError = document.getElementById("btn-chaos-error");
const errorSpinner = document.getElementById("error-spinner");

const toggleModelLoan = document.getElementById("toggle-model-loan");
const toggleModelHouse = document.getElementById("toggle-model-house");
const toggleModelChurn = document.getElementById("toggle-model-churn");

const historyLogBody = document.getElementById("history-log-body");
const btnClearHistory = document.getElementById("btn-clear-history");

// Dynamic forms templates based on selected model
const modelFields = {
    loan: `
        <div class="form-row-grid">
            <div class="form-group">
                <label for="input-income"><i class="fa-solid fa-wallet"></i> Annual Income ($)</label>
                <input type="number" id="input-income" class="form-control" value="65000" min="0" placeholder="e.g. 50000" required>
            </div>
            <div class="form-group">
                <label for="input-credit-score"><i class="fa-solid fa-star-half-stroke"></i> Credit Score (300-850)</label>
                <input type="number" id="input-credit-score" class="form-control" value="710" min="300" max="850" placeholder="e.g. 700" required>
            </div>
            <div class="form-group">
                <label for="input-loan-amount"><i class="fa-solid fa-hand-holding-dollar"></i> Loan Amount ($)</label>
                <input type="number" id="input-loan-amount" class="form-control" value="150000" min="0" placeholder="e.g. 100000" required>
            </div>
        </div>
    `,
    house: `
        <div class="form-row-grid">
            <div class="form-group">
                <label for="input-area"><i class="fa-solid fa-ruler-combined"></i> House Area (Sq Ft)</label>
                <input type="number" id="input-area" class="form-control" value="1800" min="100" placeholder="e.g. 1500" required>
            </div>
            <div class="form-group">
                <label for="input-bedrooms"><i class="fa-solid fa-bed"></i> Bedrooms</label>
                <input type="number" id="input-bedrooms" class="form-control" value="3" min="0" placeholder="e.g. 3" required>
            </div>
            <div class="form-group">
                <label for="input-bathrooms"><i class="fa-solid fa-bath"></i> Bathrooms</label>
                <input type="number" id="input-bathrooms" class="form-control" value="2.5" min="0" step="0.5" placeholder="e.g. 2" required>
            </div>
        </div>
    `,
    churn: `
        <div class="form-row-grid">
            <div class="form-group">
                <label for="input-tenure"><i class="fa-solid fa-calendar-check"></i> Account Tenure (Months)</label>
                <input type="number" id="input-tenure" class="form-control" value="18" min="0" placeholder="e.g. 12" required>
            </div>
            <div class="form-group">
                <label for="input-charges"><i class="fa-solid fa-file-invoice-dollar"></i> Monthly Charges ($)</label>
                <input type="number" id="input-charges" class="form-control" value="85" min="0" placeholder="e.g. 60" required>
            </div>
            <div class="form-group">
                <label for="input-contract"><i class="fa-solid fa-file-signature"></i> Contract Strategy</label>
                <select id="input-contract" class="form-control" required>
                    <option value="0">Month-to-Month Connection</option>
                    <option value="1">One Year Contract Terms</option>
                    <option value="2">Two Year Contract Terms</option>
                </select>
            </div>
        </div>
    `
};

// Initialize app
function init() {
    setupModelSelector();
    loadDynamicFields();
    loadSessionHistory();
    checkBackendHealth();
    
    // Periodically poll backend health
    setInterval(checkBackendHealth, 5000);
}

// Bind Model Cards Grid click events
function setupModelSelector() {
    modelCards.forEach(card => {
        card.addEventListener("click", () => {
            // Remove active style from all cards
            modelCards.forEach(c => c.classList.remove("active"));
            
            // Activate selected card
            card.classList.add("active");
            activeModel = card.getAttribute("data-model");
            
            // Load dynamic form
            loadDynamicFields();
        });
    });
}

// Load dynamic inputs
function loadDynamicFields() {
    dynamicFieldsContainer.innerHTML = modelFields[activeModel] || "";
    
    // Clear status views on change
    resultPanel.classList.add("hidden");
    errorPanel.classList.add("hidden");
}

// Fetch backend health and updates status badges
async function checkBackendHealth() {
    try {
        const start = performance.now();
        const response = await fetch(`${API_BASE_URL}/health`);
        const latency = Math.round(performance.now() - start);
        
        if (response.ok) {
            const data = await response.json();
            
            // Update Connection Pulses
            apiPulse.className = "pulse-indicator status-green";
            apiStatusText.innerText = "Secure Gateway Connected";
            
            healthApiStatus.innerText = "ONLINE";
            healthApiStatus.className = "metric-value text-blue";
            
            if (data.status === "healthy") {
                healthSystemStatus.innerText = "HEALTHY";
                healthSystemStatus.className = "metric-value text-green";
            } else {
                healthSystemStatus.innerText = "DEGRADED";
                healthSystemStatus.className = "metric-value text-amber";
            }
            
            // Sync Outage toggles state with actual API status in backend
            if (data.models) {
                syncToggleState(toggleModelLoan, data.models.loan);
                syncToggleState(toggleModelHouse, data.models.house);
                syncToggleState(toggleModelChurn, data.models.churn);
                
                // Update Model cards status visual states
                updateModelCardOnlineStatus("loan", data.models.loan);
                updateModelCardOnlineStatus("house", data.models.house);
                updateModelCardOnlineStatus("churn", data.models.churn);
            }
            
        } else {
            handleOfflineState();
        }
    } catch (e) {
        handleOfflineState();
    }
}

function handleOfflineState() {
    apiPulse.className = "pulse-indicator status-red";
    apiStatusText.innerText = "Gateway Connection Timeout";
    
    healthApiStatus.innerText = "OFFLINE";
    healthApiStatus.className = "metric-value text-red";
    
    healthSystemStatus.innerText = "CRITICAL";
    healthSystemStatus.className = "metric-value text-red";
    
    // Grey out model cards status
    updateModelCardOnlineStatus("loan", false);
    updateModelCardOnlineStatus("house", false);
    updateModelCardOnlineStatus("churn", false);
}

function syncToggleState(toggleElement, isEnabled) {
    if (toggleElement.checked !== isEnabled) {
        toggleElement.checked = isEnabled;
    }
}

function updateModelCardOnlineStatus(modelName, isOnline) {
    const card = document.getElementById(`card-model-${modelName}`);
    if (card) {
        const badge = card.querySelector(".model-card-badge");
        if (isOnline) {
            card.style.opacity = "1";
            card.style.pointerEvents = "auto";
            if (badge) {
                badge.className = "model-card-badge active-tag";
                badge.innerText = modelName === "house" ? "Regression" : "Classification";
            }
        } else {
            card.style.opacity = "0.55";
            if (badge) {
                badge.className = "model-card-badge";
                badge.style.backgroundColor = "rgba(239, 68, 68, 0.15)";
                badge.style.color = "var(--color-red)";
                badge.style.border = "1px solid rgba(239, 68, 68, 0.25)";
                badge.innerText = "OFFLINE";
            }
        }
    }
}

// Handle Inference Form Submission
async function handleInferenceSubmit(e) {
    e.preventDefault();
    
    // Extract input parameters
    let payload = {};
    if (activeModel === "loan") {
        payload = {
            income: parseFloat(document.getElementById("input-income").value),
            credit_score: parseInt(document.getElementById("input-credit-score").value),
            loan_amount: parseFloat(document.getElementById("input-loan-amount").value)
        };
    } else if (activeModel === "house") {
        payload = {
            area: parseFloat(document.getElementById("input-area").value),
            bedrooms: parseInt(document.getElementById("input-bedrooms").value),
            bathrooms: parseFloat(document.getElementById("input-bathrooms").value)
        };
    } else if (activeModel === "churn") {
        payload = {
            tenure: parseInt(document.getElementById("input-tenure").value),
            monthly_charges: parseFloat(document.getElementById("input-charges").value),
            contract_type: parseInt(document.getElementById("input-contract").value)
        };
    }

    // Set UI Loading State
    setLoadingState(true);
    resultPanel.classList.add("hidden");
    errorPanel.classList.add("hidden");

    const startTime = performance.now();
    let duration = 0;
    
    try {
        const response = await fetch(`${API_BASE_URL}/predict/${activeModel}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });
        
        duration = Math.round(performance.now() - startTime);
        
        if (response.ok) {
            const data = await response.json();
            
            // Format Prediction Output
            let displayVal = data.prediction;
            if (typeof displayVal === "number") {
                displayVal = `$${displayVal.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
            }
            
            // Update Dashboard metrics and response Card
            totalPredictions++;
            statsTotalPredictions.innerText = totalPredictions;
            statsAvgLatency.innerText = `${duration} ms`;
            
            outputModelBadge.innerText = `${activeModel.toUpperCase()} MODEL`;
            outputValue.innerText = displayVal;
            outputLatency.innerText = `${duration} ms`;
            outputVersion.innerText = data.model_version;
            outputTime.innerText = new Date(data.timestamp).toLocaleTimeString();
            
            resultPanel.classList.remove("hidden");
            
            // Save to Session Audit Logs
            addHistoryRecord(activeModel, payload, displayVal, 200, duration);
        } else {
            const errData = await response.json().catch(() => ({detail: "Unknown server error."}));
            displayInferenceError(response.status, errData.detail);
            addHistoryRecord(activeModel, payload, "Failed", response.status, duration);
        }
    } catch (e) {
        duration = Math.round(performance.now() - startTime);
        displayInferenceError(500, "Could not contact API server. Connection timed out or server offline.");
        addHistoryRecord(activeModel, payload, "Failed", 500, duration);
    } finally {
        setLoadingState(false);
        checkBackendHealth(); // Quick health poll to synchronize model outage checkboxes
    }
}

function setLoadingState(isLoading) {
    if (isLoading) {
        btnPredict.disabled = true;
        predictSpinner.classList.remove("hidden");
        btnText.innerText = "Executing Core Inference Model...";
    } else {
        btnPredict.disabled = false;
        predictSpinner.classList.add("hidden");
        btnText.innerText = "Execute Model Inference";
    }
}

function displayInferenceError(status, message) {
    errorTitle.innerText = `Inference Gateway Failure (HTTP ${status})`;
    errorDesc.innerText = message;
    errorPanel.classList.remove("hidden");
}

// DevOps Simulation Trigger Handlers
async function triggerLatencyChaos() {
    btnChaosLatency.disabled = true;
    latencySpinner.classList.remove("hidden");
    
    try {
        const start = performance.now();
        const response = await fetch(`${API_BASE_URL}/simulate/high-latency`, { method: "POST" });
        const latency = Math.round(performance.now() - start);
        
        if (response.ok) {
            alert(`Latency Spike simulated successfully! Latency observed on frontend: ${latency}ms.`);
        } else {
            alert(`Failed to simulate latency: HTTP ${response.status}`);
        }
    } catch (e) {
        alert("Latency Simulation failed: Connection error.");
    } finally {
        btnChaosLatency.disabled = false;
        latencySpinner.classList.add("hidden");
        checkBackendHealth();
    }
}

async function triggerCrashChaos() {
    btnChaosError.disabled = true;
    errorSpinner.classList.remove("hidden");
    
    try {
        const response = await fetch(`${API_BASE_URL}/simulate/error`, { method: "POST" });
        if (response.status === 500) {
            alert("API node forced shutdown simulated! (Returned HTTP 500 as designed). Prometheus will catch this anomaly.");
        } else {
            alert(`Unexpected simulation response status: HTTP ${response.status}`);
        }
    } catch (e) {
        alert("Failed to reach server (Server node is offline).");
    } finally {
        btnChaosError.disabled = false;
        errorSpinner.classList.add("hidden");
        checkBackendHealth();
    }
}

async function handleModelToggle(modelName, checkbox) {
    const action = checkbox.checked ? "enable" : "disable";
    try {
        const response = await fetch(`${API_BASE_URL}/simulate/model-failure?model=${modelName}&action=${action}`, {
            method: "POST"
        });
        
        if (!response.ok) {
            alert(`Failed to toggle model state: HTTP ${response.status}`);
            checkbox.checked = !checkbox.checked;
        }
    } catch (e) {
        alert("Failed to communicate model toggle state changes to server.");
        checkbox.checked = !checkbox.checked;
    } finally {
        checkBackendHealth();
    }
}

// History Audit Logs Handling
function addHistoryRecord(modelName, inputs, result, statusCode, latencyMs) {
    const record = {
        timestamp: new Date().toISOString(),
        model: modelName,
        inputs: JSON.stringify(inputs),
        result: result,
        status: statusCode,
        latency: latencyMs
    };
    
    predictionHistory.unshift(record); // Prepend so new items are at top
    // Limit to last 50 entries
    if (predictionHistory.length > 50) {
        predictionHistory.pop();
    }
    
    localStorage.setItem("quantum_history", JSON.stringify(predictionHistory));
    renderHistoryTable();
}

// Render history audits onto DOM
function renderHistoryTable() {
    if (predictionHistory.length === 0) {
        historyLogBody.innerHTML = `
            <tr>
                <td colspan="6" class="no-records">No predictions submitted in this session.</td>
            </tr>
        `;
        return;
    }
    
    historyLogBody.innerHTML = predictionHistory.map(record => {
        const timeStr = new Date(record.timestamp).toLocaleTimeString();
        let statusClass = "badge-200";
        if (record.status >= 500) {
            statusClass = record.status === 503 ? "badge-53" : "badge-500";
        }
        
        const badgeName = record.status === 503 ? "badge-503" : statusClass;
        
        // Pretty labels
        const modelLabels = {
            loan: "Loan Approval",
            house: "House Valuation",
            churn: "Churn Risk"
        };
        
        return `
            <tr>
                <td>${timeStr}</td>
                <td style="font-weight: 700; color: var(--color-purple);"><i class="fa-solid fa-square-poll-vertical"></i> ${modelLabels[record.model] || record.model}</td>
                <td><span class="code-style">${record.inputs}</span></td>
                <td><strong>${record.result}</strong></td>
                <td><span class="status-badge ${badgeName}">${record.status}</span></td>
                <td><i class="fa-regular fa-clock" style="font-size: 11px;"></i> ${record.latency} ms</td>
            </tr>
        `;
    }).join("");
}

function loadSessionHistory() {
    const saved = localStorage.getItem("quantum_history");
    if (saved) {
        predictionHistory = JSON.parse(saved);
        totalPredictions = predictionHistory.filter(r => r.status === 200).length;
        statsTotalPredictions.innerText = totalPredictions;
        renderHistoryTable();
    }
}

function clearSessionHistory() {
    predictionHistory = [];
    totalPredictions = 0;
    statsTotalPredictions.innerText = 0;
    statsAvgLatency.innerText = "0 ms";
    localStorage.removeItem("quantum_history");
    renderHistoryTable();
}

// Event Listeners Configuration
predictionForm.addEventListener("submit", handleInferenceSubmit);

btnChaosLatency.addEventListener("click", triggerLatencyChaos);
btnChaosError.addEventListener("click", triggerCrashChaos);

toggleModelLoan.addEventListener("change", () => handleModelToggle("loan", toggleModelLoan));
toggleModelHouse.addEventListener("change", () => handleModelToggle("house", toggleModelHouse));
toggleModelChurn.addEventListener("change", () => handleModelToggle("churn", toggleModelChurn));

btnClearHistory.addEventListener("click", clearSessionHistory);

// Start app
init();

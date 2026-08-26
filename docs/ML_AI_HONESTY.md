# ML/AI Honesty Report

This file records what the running code actually does as of this repository state.

| Claim area | Decision | Runtime evidence |
|---|---|---|
| Supplier risk scoring | Kept, renamed as heuristic/composite scoring | `backend/app/engines/analyzer.py` computes weighted delay, cost, quality, and confidence factors. It is not a trained risk model. |
| IsolationForest anomalies | Kept | `AnomalyDetector` runs scikit-learn `IsolationForest` when enough numeric columns exist, plus z-score and IQR checks. |
| Holt-Winters / Holt forecasting | Kept with data guards | `TimeSeriesForecaster` uses Holt-Winters only with enough monthly points, Holt linear trend with fewer points, and returns an insufficient-data reason otherwise. |
| Monte Carlo simulation | Kept | `MonteCarloEngine` fits supplier delay/cost distributions and runs bounded stochastic trials for disruptions. |
| Temporal Graph Neural Network / TGNN | Renamed | The code tracks temporal graph trends using memory vectors, linear regression, and Holt smoothing. It has no trainable neural network, gradients, or temporal attention. `TGNNEngine` remains only as a compatibility alias. |
| Causal / Bayesian / PyMC engine | Renamed | `backend/app/causal/__init__.py` is graph-based risk propagation. It does not perform do-calculus, Bayesian inference, PC/FCI/LiNGAM, or confounder adjustment. |
| XAI | Kept with narrower wording | `XAIEngine` uses Random Forest feature importance, permutation importance, and operational counterfactual suggestions. It explains predictive associations, not causal effects. |
| RAG retriever/reranker | Removed from shipped claims | Retrieval code exists under `backend/rag`, but the RAG router is not registered in `backend/app/main.py`, so it is not a shipped API surface. |
| AI Copilot | Kept with offline caveat | `AICopilot` calls Groq/Bedrock when configured and falls back to deterministic heuristic summaries when no provider response is available. |
| Agent graph | Kept with fallback caveat | `backend/agent/agent_graph.py` uses LangGraph when installed and falls back to sequential node execution. |

Public docs should use "risk propagation", "temporal trend engine", and "predictive feature importance" unless a future implementation adds true causal inference, a trained temporal graph neural network, or a registered RAG API.

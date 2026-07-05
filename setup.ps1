# ============================
# AI Tax Advisor Project Setup
# Root Folder: CAAI
# ============================

Write-Host "Creating AI Tax Advisor Project Structure..."

# ---------- Directories ----------
$directories = @(
"static/css",
"static/js",
"static/images",

"templates",

"uploads/form16",
"uploads/salary_slips",
"uploads/bank_statements",
"uploads/investment_proofs",
"uploads/temp",

"extracted_data/ocr_text",
"extracted_data/cleaned_data",
"extracted_data/structured_json",

"database",

"routes",

"services/ocr",
"services/nlp",
"services/tax_engine",
"services/recommendation",
"services/anomaly_detection",
"services/forecasting",
"services/explainability",
"services/chatbot",

"models",

"training/datasets",

"utils",

"reports/exported_reports",

"knowledge_base/embeddings",

"tests"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# ---------- Files ----------
$files = @(

"app.py",
"requirements.txt",
"README.md",
"config.py",
".env",

"static/css/style.css",
"static/js/dashboard.js",

"templates/index.html",
"templates/dashboard.html",
"templates/upload.html",
"templates/chatbot.html",
"templates/login.html",

"database/schema.sql",
"database/taxadvisor.db",
"database/models.py",

"routes/upload_routes.py",
"routes/dashboard_routes.py",
"routes/chatbot_routes.py",
"routes/prediction_routes.py",
"routes/auth_routes.py",

"services/ocr/ocr_engine.py",
"services/ocr/image_preprocessing.py",

"services/nlp/transaction_classifier.py",
"services/nlp/entity_extraction.py",
"services/nlp/text_cleaner.py",
"services/nlp/deduction_identifier.py",

"services/tax_engine/old_regime.py",
"services/tax_engine/new_regime.py",
"services/tax_engine/deduction_rules.py",
"services/tax_engine/tax_comparator.py",

"services/recommendation/investment_recommender.py",
"services/recommendation/persona_clustering.py",

"services/anomaly_detection/isolation_forest.py",

"services/forecasting/prophet_model.py",

"services/explainability/shap_explainer.py",

"services/chatbot/rag_pipeline.py",
"services/chatbot/vector_store.py",
"services/chatbot/llm_interface.py",

"models/transaction_classifier.pkl",
"models/anomaly_model.pkl",
"models/clustering_model.pkl",
"models/forecasting_model.pkl",
"models/tfidf_vectorizer.pkl",

"training/datasets/transactions.csv",
"training/datasets/synthetic_tax_data.csv",

"training/train_classifier.py",
"training/train_clustering.py",
"training/train_forecasting.py",
"training/train_anomaly.py",
"training/train_embeddings.py",

"utils/helpers.py",
"utils/pdf_reader.py",
"utils/excel_reader.py",
"utils/validations.py",
"utils/logger.py",
"utils/charts.py",

"reports/generate_pdf.py",
"reports/report_template.html",

"knowledge_base/Income_Tax_Act.pdf",
"knowledge_base/CBDT_FAQ.pdf",
"knowledge_base/deduction_rules.txt",

"tests/test_ocr.py",
"tests/test_tax_engine.py",
"tests/test_classifier.py",
"tests/test_chatbot.py",
"tests/test_api.py"
)

foreach ($file in $files) {
    if (!(Test-Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
    }
}

Write-Host ""
Write-Host "=========================================="
Write-Host " AI Tax Advisor Project Ready!"
Write-Host "=========================================="
Write-Host ""
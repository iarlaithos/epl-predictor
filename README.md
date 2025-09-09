# EPL Predictor (Python + ML Learning Project)

A personal sandbox for me to learn **Python** and **machine learning** by predicting **English Premier League** match outcomes (1X2). The focus is on writing clean, minimal Python, pulling real data, and iterating from simple baselines to something decent.

## What this is
- A hands-on way to learn Python tooling, packaging, and scripting.
- An end-to-end mini ML project: data → features → model → evaluation.
- Uses the **FBR API** for football data. The client **auto-generates API keys** at runtime (no `.env` required).

Learning plan (roadmap)

✅ Set up repo, venv, VS Code, thin FBR client.

⏭️ Build a downloader for one season of EPL matches.

⏭️ Create basic features (recent form, goals for/against, points).

⏭️ Train a multinomial logistic regression baseline; evaluate with log loss & Brier.

⏭️ Upgrade to a goals model (Poisson) and then tree ensembles (XGBoost/LightGBM).

⏭️ Add calibration & simple backtesting (time-series splits).
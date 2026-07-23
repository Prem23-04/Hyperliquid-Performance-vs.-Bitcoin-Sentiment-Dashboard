# ⚡ Hyperliquid Performance vs. Bitcoin Sentiment Analysis

[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg?logo=flask)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?logo=python)](https://www.python.org/)
[![Bootstrap 5](https://img.shields.io/badge/Bootstrap-5.3.0-purple.svg?logo=bootstrap)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An interactive, dynamic web application built with **Flask**, **Chart.js**, and **AOS (Animate On Scroll)**. This project investigates the impact of market sentiment—measured by the **Bitcoin Fear & Greed Index**—on trader performance and execution strategies using historical execution data from **Hyperliquid**.

---

## 📌 Features

- **📊 Dynamic KPI Dashboard**: Instantly inspect overall net PnL, overall win rate, total executions, volume (USD), and cumulative fees paid.
- **📂 Interactive Dataset Previews**: Searchable and paginated data viewer for both raw execution logs and daily sentiment scores.
- **📈 Multi-Chart Behavioral Analytics**:
  - Net PnL ($) breakdown across market sentiment categories (*Extreme Fear* to *Extreme Greed*).
  - Win Rate (%) trends relative to sentiment transitions.
  - Trading volume distribution by sentiment regime.
  - Directional bias analysis (Long/Buy vs. Short/Sell volume ratio).
  - Dual-axis time-series visualization tracking cumulative trader PnL against Fear & Greed Index values over time.
- **🤖 Behavioral Machine Learning**: K-Means clustering algorithm applied to trader accounts to identify distinct trader archetypes (*Contrarian/Smart Money* vs. *Herd Mentality*).
- **✨ Animated UI**: Responsive dark-themed dashboard enhanced with dynamic animations powered by AOS.js.

---

## 📂 Project Architecture

```text
crypto_sentiment_app/
│
├── data/
│   ├── historical_data.csv        # Hyperliquid execution logs
│   └── fear_greed_index.csv       # Bitcoin Fear & Greed daily index
├── static/
│   ├── css/
│   │   └── style.css              # Custom styling overrides
│   └── js/
│       └── dashboard.js           # Chart.js, AOS & table pagination logic
├── templates/
│   └── index.html                 # Main dashboard UI template
├── app.py                         # Flask backend & REST API endpoints
├── requirements.txt               # Dependencies
└── README.md                      # Project documentation

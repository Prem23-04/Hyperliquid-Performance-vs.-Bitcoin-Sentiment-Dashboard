from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

app = Flask(__name__)

def process_data():
    trades_path = os.path.join('data', 'historical_data.csv')
    sentiment_path = os.path.join('data', 'fear_greed_index.csv')

    df_trades = pd.read_csv(trades_path)
    df_sentiment = pd.read_csv(sentiment_path)

    df_trades.columns = df_trades.columns.str.strip()
    df_sentiment.columns = df_sentiment.columns.str.strip()

    df_trades['Timestamp_Clean'] = pd.to_datetime(df_trades['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    df_trades['Date'] = df_trades['Timestamp_Clean'].dt.strftime('%Y-%m-%d')
    df_sentiment['Date'] = pd.to_datetime(df_sentiment['date']).dt.strftime('%Y-%m-%d')

    df = pd.merge(df_trades, df_sentiment[['Date', 'value', 'classification']], on='Date', how='inner')
    df.rename(columns={'value': 'sentiment_score', 'classification': 'sentiment_class'}, inplace=True)

    numeric_cols = ['Execution Price', 'Size Tokens', 'Size USD', 'Closed PnL', 'Fee']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    return df

@app.route('/')
def index():
    return render_template('index.html')

# -------------------------------------------------------------
# New API: Paginated & Searchable Preview for Historical Trades
# -------------------------------------------------------------
@app.route('/api/preview/trades')
def preview_trades():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search', '').lower()

    trades_path = os.path.join('data', 'historical_data.csv')
    df_trades = pd.read_csv(trades_path)
    df_trades.columns = df_trades.columns.str.strip()

    if search:
        mask = df_trades.astype(str).apply(lambda row: row.str.lower().str.contains(search).any(), axis=1)
        df_trades = df_trades[mask]

    total_records = len(df_trades)
    start = (page - 1) * limit
    end = start + limit
    
    paginated_data = df_trades.iloc[start:end].fillna('').to_dict(orient='records')

    return jsonify({
        "total": total_records,
        "page": page,
        "limit": limit,
        "columns": list(df_trades.columns),
        "data": paginated_data
    })

# -------------------------------------------------------------
# New API: Paginated & Searchable Preview for Fear & Greed Index
# -------------------------------------------------------------
@app.route('/api/preview/sentiment')
def preview_sentiment():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    search = request.args.get('search', '').lower()

    sentiment_path = os.path.join('data', 'fear_greed_index.csv')
    df_sentiment = pd.read_csv(sentiment_path)
    df_sentiment.columns = df_sentiment.columns.str.strip()

    if search:
        mask = df_sentiment.astype(str).apply(lambda row: row.str.lower().str.contains(search).any(), axis=1)
        df_sentiment = df_sentiment[mask]

    total_records = len(df_sentiment)
    start = (page - 1) * limit
    end = start + limit
    
    paginated_data = df_sentiment.iloc[start:end].fillna('').to_dict(orient='records')

    return jsonify({
        "total": total_records,
        "page": page,
        "limit": limit,
        "columns": list(df_sentiment.columns),
        "data": paginated_data
    })

@app.route('/api/metrics')
def get_metrics():
    df = process_data()
    
    total_pnl = float(df['Closed PnL'].sum())
    total_volume = float(df['Size USD'].sum())
    total_trades = int(len(df))
    win_rate = float((df['Closed PnL'] > 0).mean() * 100)
    total_fees = float(df['Fee'].sum())

    order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
    
    sentiment_perf = df.groupby('sentiment_class').agg(
        Total_PnL=('Closed PnL', 'sum'),
        Avg_PnL=('Closed PnL', 'mean'),
        Win_Rate=('Closed PnL', lambda x: (x > 0).mean() * 100),
        Trade_Count=('Closed PnL', 'count'),
        Total_Volume=('Size USD', 'sum'),
        Total_Fees=('Fee', 'sum')
    ).reindex(order).dropna().reset_index()

    side_dist = df.groupby(['sentiment_class', 'Side'])['Size USD'].sum().unstack(fill_value=0).reindex(order).fillna(0)
    
    time_series = df.sort_values('Timestamp_Clean').groupby('Date').agg(
        Daily_PnL=('Closed PnL', 'sum'),
        Sentiment=('sentiment_score', 'mean')
    ).reset_index()
    time_series['Cumulative_PnL'] = time_series['Daily_PnL'].cumsum()

    return jsonify({
        "summary": {
            "total_pnl": round(total_pnl, 2),
            "total_volume": round(total_volume, 2),
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "total_fees": round(total_fees, 2)
        },
        "sentiment_breakdown": {
            "categories": sentiment_perf['sentiment_class'].tolist(),
            "pnl": sentiment_perf['Total_PnL'].round(2).tolist(),
            "win_rates": sentiment_perf['Win_Rate'].round(2).tolist(),
            "volume": sentiment_perf['Total_Volume'].round(2).tolist(),
            "fees": sentiment_perf['Total_Fees'].round(2).tolist()
        },
        "side_distribution": {
            "categories": side_dist.index.tolist(),
            "buy_volume": side_dist['BUY'].round(2).tolist() if 'BUY' in side_dist.columns else [],
            "sell_volume": side_dist['SELL'].round(2).tolist() if 'SELL' in side_dist.columns else []
        },
        "time_series": {
            "dates": time_series['Date'].tolist(),
            "cumulative_pnl": time_series['Cumulative_PnL'].round(2).tolist(),
            "sentiment_score": time_series['Sentiment'].round(1).tolist()
        }
    })

@app.route('/api/clusters')
def get_clusters():
    df = process_data()
    
    account_stats = df.groupby('Account').agg(
        Total_PnL=('Closed PnL', 'sum'),
        Win_Rate=('Closed PnL', lambda x: (x > 0).mean() * 100),
        Trade_Count=('Closed PnL', 'count'),
        Avg_Position_USD=('Size USD', 'mean'),
        Fear_Trade_Ratio=('sentiment_class', lambda x: (x.isin(['Fear', 'Extreme Fear'])).mean())
    ).reset_index()

    active_accounts = account_stats[account_stats['Trade_Count'] >= 5].copy()

    features = ['Total_PnL', 'Win_Rate', 'Avg_Position_USD', 'Fear_Trade_Ratio']
    X = active_accounts[features].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=3, random_state=42)
    active_accounts['Cluster'] = kmeans.fit_predict(X_scaled)

    scatter_data = []
    for _, row in active_accounts.iterrows():
        scatter_data.append({
            "account": row['Account'][:8] + "...",
            "x": round(float(row['Fear_Trade_Ratio'] * 100), 2),
            "y": round(float(row['Win_Rate']), 2),
            "cluster": int(row['Cluster']),
            "pnl": round(float(row['Total_PnL']), 2)
        })

    return jsonify(scatter_data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
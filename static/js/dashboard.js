let pageState = {
    trades: { page: 1, limit: 10, total: 0 },
    sentiment: { page: 1, limit: 10, total: 0 }
};

document.addEventListener("DOMContentLoaded", function () {
    AOS.init({ duration: 800, once: true, easing: 'ease-in-out' });

    fetchMetrics();
    fetchClusters();
    loadTablePreview('trades');
    loadTablePreview('sentiment');

    // Real-time dataset search listener
    document.getElementById('datasetSearch').addEventListener('input', function (e) {
        const query = e.target.value;
        pageState.trades.page = 1;
        pageState.sentiment.page = 1;
        loadTablePreview('trades', query);
        loadTablePreview('sentiment', query);
    });
});

function loadTablePreview(type, search = '') {
    const state = pageState[type];
    const url = `/api/preview/${type}?page=${state.page}&limit=${state.limit}&search=${encodeURIComponent(search)}`;

    fetch(url)
        .then(res => res.json())
        .then(res => {
            state.total = res.total;

            const head = document.getElementById(`${type}Head`);
            const body = document.getElementById(`${type}Body`);
            const info = document.getElementById(`${type}Info`);

            // Build Headers
            head.innerHTML = res.columns.map(col => `<th>${col}</th>`).join('');

            // Build Rows
            if (res.data.length === 0) {
                body.innerHTML = `<tr><td colspan="${res.columns.length}" class="text-center text-secondary">No records found</td></tr>`;
            } else {
                body.innerHTML = res.data.map(row => {
                    const cells = res.columns.map(col => `<td>${row[col]}</td>`).join('');
                    return `<tr>${cells}</tr>`;
                }).join('');
            }

            // Update Pagination Text
            const startRecord = (state.page - 1) * state.limit + 1;
            const endRecord = Math.min(state.page * state.limit, res.total);
            info.innerText = `Showing ${res.total > 0 ? startRecord : 0} to ${endRecord} of ${res.total.toLocaleString()} records`;

            // Enable/Disable Pagination Buttons
            document.getElementById(`prev${capitalize(type)}Btn`).disabled = state.page === 1;
            document.getElementById(`next${capitalize(type)}Btn`).disabled = endRecord >= res.total;
        });
}

function changePage(type, direction) {
    pageState[type].page += direction;
    const searchVal = document.getElementById('datasetSearch').value;
    loadTablePreview(type, searchVal);
}

function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}

function fetchMetrics() {
    fetch('/api/metrics')
        .then(response => response.json())
        .then(data => {
            document.getElementById('kpi-pnl').innerText = `$${data.summary.total_pnl.toLocaleString()}`;
            document.getElementById('kpi-winrate').innerText = `${data.summary.win_rate}%`;
            document.getElementById('kpi-trades').innerText = data.summary.total_trades.toLocaleString();
            document.getElementById('kpi-volume').innerText = `$${data.summary.total_volume.toLocaleString()}`;
            document.getElementById('kpi-fees').innerText = `$${data.summary.total_fees.toLocaleString()}`;

            new Chart(document.getElementById('pnlChart'), {
                type: 'bar',
                data: {
                    labels: data.sentiment_breakdown.categories,
                    datasets: [{ label: 'Total PnL ($)', data: data.sentiment_breakdown.pnl, backgroundColor: '#238636', borderRadius: 6 }]
                },
                options: { responsive: true }
            });

            new Chart(document.getElementById('winrateChart'), {
                type: 'line',
                data: {
                    labels: data.sentiment_breakdown.categories,
                    datasets: [{ label: 'Win Rate (%)', data: data.sentiment_breakdown.win_rates, borderColor: '#f0883e', backgroundColor: 'rgba(240, 136, 62, 0.2)', fill: true, tension: 0.3 }]
                },
                options: { responsive: true, scales: { y: { min: 0, max: 100 } } }
            });

            new Chart(document.getElementById('volumeChart'), {
                type: 'bar',
                data: {
                    labels: data.sentiment_breakdown.categories,
                    datasets: [{ label: 'Total Volume ($)', data: data.sentiment_breakdown.volume, backgroundColor: '#1f6beb', borderRadius: 6 }]
                },
                options: { responsive: true }
            });

            new Chart(document.getElementById('sideChart'), {
                type: 'bar',
                data: {
                    labels: data.side_distribution.categories,
                    datasets: [
                        { label: 'Buy Volume ($)', data: data.side_distribution.buy_volume, backgroundColor: '#2ea44f' },
                        { label: 'Sell Volume ($)', data: data.side_distribution.sell_volume, backgroundColor: '#da3633' }
                    ]
                },
                options: { responsive: true, scales: { x: { stacked: true }, y: { stacked: true } } }
            });

            new Chart(document.getElementById('timeSeriesChart'), {
                type: 'line',
                data: {
                    labels: data.time_series.dates,
                    datasets: [
                        { label: 'Cumulative PnL ($)', data: data.time_series.cumulative_pnl, borderColor: '#38d430', yAxisID: 'y' },
                        { label: 'Fear & Greed Index Score', data: data.time_series.sentiment_score, borderColor: '#a371f7', borderDash: [5, 5], yAxisID: 'y1' }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: { type: 'linear', position: 'left', title: { display: true, text: 'PnL ($)' } },
                        y1: { type: 'linear', position: 'right', min: 0, max: 100, title: { display: true, text: 'Sentiment Index' } }
                    }
                }
            });
        });
}

function fetchClusters() {
    fetch('/api/clusters')
        .then(response => response.json())
        .then(data => {
            const clusterColors = ['#58a6ff', '#3fb950', '#f85149'];
            
            const datasets = [0, 1, 2].map(clusterId => ({
                label: `Cluster ${clusterId}`,
                data: data.filter(d => d.cluster === clusterId),
                backgroundColor: clusterColors[clusterId],
                pointRadius: 6
            }));

            new Chart(document.getElementById('clusterChart'), {
                type: 'scatter',
                data: { datasets: datasets },
                options: {
                    responsive: true,
                    scales: {
                        x: { title: { display: true, text: 'Fear Trading Ratio (%)' } },
                        y: { title: { display: true, text: 'Win Rate (%)' } }
                    }
                }
            });
        });
}
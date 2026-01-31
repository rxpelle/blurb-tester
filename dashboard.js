const strategies = [
    {
        name: "High-Yield Savings (Safe)",
        apy: 0.045, // 4.5%
        note: "FDIC Insured. Max liquidity.",
        color: "#238636"
    },
    {
        name: "6-Month CD (Fixed)",
        apy: 0.048,
        note: "Locked for 6 months. Guaranteed return.",
        color: "#0066ff"
    },
    {
        name: "Bonus + Savings (Strategic)",
        apy: 0.05, // Effective 4% + $500 bonus
        bonus: 500,
        note: "E*TRADE / CIT Bank Promo. High immediate ROI.",
        color: "#f29100"
    },
    {
        name: "DeFi Yield (Aggressive)",
        apy: 0.10, // 10%
        note: "Stablecoin lending (Aave). Smart contract risk.",
        color: "#da3633"
    }
];

let growthChart, yieldChart;

function updateDashboard() {
    const checking = parseFloat(document.getElementById('checking').value) || 0;
    const venmo = parseFloat(document.getElementById('venmo').value) || 0;
    const years = parseInt(document.getElementById('duration').value) || 1;
    const totalCash = checking + venmo;

    const cardsContainer = document.getElementById('cards-container');
    cardsContainer.innerHTML = '';

    const results = strategies.map(strat => {
        const bonus = strat.bonus || 0;
        // Simple compounding: A = P(1 + r)^t + Bonus
        const finalAmount = totalCash * Math.pow(1 + strat.apy, years) + bonus;
        const totalEarnings = finalAmount - totalCash;
        
        const card = document.createElement('div');
        card.className = 'card';
        card.innerHTML = `
            <div class="card-title">
                ${strat.name}
                <span class="apy">${(strat.apy * 100).toFixed(1)}% APY</span>
            </div>
            <div class="earnings">$${totalEarnings.toLocaleString(undefined, {minimumFractionDigits: 0, maximumFractionDigits: 0})}</div>
            <div class="meta">${strat.note}</div>
        `;
        cardsContainer.appendChild(card);
        
        return {
            name: strat.name,
            final: finalAmount,
            earnings: totalEarnings,
            color: strat.color
        };
    });

    renderCharts(results, years);
}

function renderCharts(results, years) {
    const ctxGrowth = document.getElementById('growthChart').getContext('2d');
    const ctxYield = document.getElementById('yieldChart').getContext('2d');

    if (growthChart) growthChart.destroy();
    if (yieldChart) yieldChart.destroy();

    growthChart = new Chart(ctxGrowth, {
        type: 'bar',
        data: {
            labels: results.map(r => r.name),
            datasets: [{
                label: `Total Value after ${years} Year(s)`,
                data: results.map(r => r.final),
                backgroundColor: results.map(r => r.color),
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: { display: true, text: 'Wealth Accumulation ($)', color: '#fff' }
            },
            scales: {
                y: { beginAtZero: false, grid: { color: '#30363d' }, ticks: { color: '#8b949e' } },
                x: { ticks: { color: '#8b949e' } }
            }
        }
    });

    yieldChart = new Chart(ctxYield, {
        type: 'doughnut',
        data: {
            labels: results.map(r => r.name),
            datasets: [{
                data: results.map(r => r.earnings),
                backgroundColor: results.map(r => r.color),
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { position: 'bottom', labels: { color: '#8b949e' } },
                title: { display: true, text: 'Total Earnings Comparison', color: '#fff' }
            }
        }
    });
}

document.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', updateDashboard);
});

// Initial load
updateDashboard();

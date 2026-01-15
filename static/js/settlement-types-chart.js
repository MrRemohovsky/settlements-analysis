function initSettlementTypesChart(canvasId, data) {
    const labels = data.map(item => item.type);
    const populations = data.map(item => item.population);
    const maxValue = Math.max(...populations);

    const colors = [
        '#3498db', '#2980b9', '#1abc9c', '#16a085', '#27ae60',
        '#2ecc71', '#f39c12', '#e67e22', '#e74c3c', '#c0392b',
        '#9b59b6', '#8e44ad', '#34495e', '#2c3e50', '#95a5a6'
    ];

    const ctx = document.getElementById(canvasId).getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Население',
                data: populations,
                backgroundColor: colors.slice(0, labels.length),
                borderColor: colors.slice(0, labels.length),
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    max: maxValue * 1.05,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('ru-RU');
                        }
                    },
                    grid: {
                        drawBorder: false,
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    grid: {
                        drawBorder: false,
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(44, 62, 80, 0.9)',
                    padding: 12,
                    titleFont: { size: 13, weight: 'bold' },
                    bodyFont: { size: 12 },
                    borderColor: 'transparent',
                    displayColors: false,
                    callbacks: {
                        label: function(context) {
                            return 'Население: ' + context.parsed.x.toLocaleString('ru-RU');
                        }
                    }
                }
            }
        },
        plugins: [
            {
                id: 'textOnBars',
                afterDatasetsDraw(chart) {
                    const ctx = chart.ctx;
                    chart.data.datasets.forEach((dataset, datasetIndex) => {
                        const meta = chart.getDatasetMeta(datasetIndex);
                        meta.data.forEach((bar, index) => {
                            const value = dataset.data[index];
                            const x = bar.x + 8;
                            const y = bar.y;

                            const text = value.toLocaleString('ru-RU');

                            ctx.font = 'bold 12px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
                            ctx.fillStyle = '#2c3e50';
                            ctx.textAlign = 'left';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(text, x, y);
                        });
                    });
                }
            }
        ]
    });
}
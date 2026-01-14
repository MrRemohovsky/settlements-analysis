function initPopulationDistributionChart(canvasId, populationData, step = 1) {
    const container = document.getElementById(canvasId);
    if (!container || !populationData || populationData.length === 0) {
        return;
    }

    const data = populationData
        .filter(item => item.population > 0)
        .filter((_, i) => i % step === 0);

    const xValues = data.map(() => Math.random());
    const yValues = data.map(item => item.population);

    const trace = {
        x: xValues,
        y: yValues,
        mode: 'markers',
        type: 'scatter',
        marker: {
            size: 8,
            color: '#3498db',
            opacity: 0.6
        }
    };

    const layout = {
        title: 'Плотность населения поселений',
        xaxis: {
            visible: false
        },
        yaxis: {
            title: 'Население (человек)'
        },
        height: 500,
        showlegend: false
    };

    Plotly.newPlot(canvasId, [trace], layout, {responsive: true});
}

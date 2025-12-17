const chartColors = {
    primary: '#2563eb',
    secondary: '#10b981',
    danger: '#ef4444',
    warning: '#f59e0b',
    info: '#06b6d4',
    purple: '#8b5cf6',
    pink: '#ec4899'
};

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'bottom',
            labels: {
                padding: 15,
                font: {
                    size: 12,
                    family: "'Inter', sans-serif"
                }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            padding: 12,
            titleFont: {
                size: 14,
                weight: 'bold'
            },
            bodyFont: {
                size: 13
            },
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1
        }
    }
};

document.addEventListener('DOMContentLoaded', function() {
    if (typeof chartData === 'undefined') return;

    createChurnDistributionChart();
    createAgeChurnChart();
    createUsageChurnChart();
    createSatisfactionChurnChart();
    createTicketsChurnChart();
});

function createChurnDistributionChart() {
    const ctx = document.getElementById('churnDistributionChart');
    if (!ctx) return;

    const data = chartData.churnDistribution;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Retained', 'Churned'],
            datasets: [{
                data: [data[0] || 0, data[1] || 0],
                backgroundColor: [chartColors.secondary, chartColors.danger],
                borderWidth: 3,
                borderColor: '#fff'
            }]
        },
        options: {
            ...chartOptions,
            cutout: '65%',
            plugins: {
                ...chartOptions.plugins,
                legend: {
                    ...chartOptions.plugins.legend,
                    position: 'bottom'
                }
            }
        }
    });
}

function createAgeChurnChart() {
    const ctx = document.getElementById('ageChurnChart');
    if (!ctx) return;

    const data = chartData.ageChurn;
    const labels = Object.keys(data);
    const retained = labels.map(label => data[label].Retained || 0);
    const churned = labels.map(label => data[label].Churned || 0);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Retained',
                    data: retained,
                    backgroundColor: chartColors.secondary,
                    borderRadius: 6
                },
                {
                    label: 'Churned',
                    data: churned,
                    backgroundColor: chartColors.danger,
                    borderRadius: 6
                }
            ]
        },
        options: {
            ...chartOptions,
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function createUsageChurnChart() {
    const ctx = document.getElementById('usageChurnChart');
    if (!ctx) return;

    const data = chartData.usageChurn;
    const labels = data.map(item => {
        const freq = item.usage_frequency;
        return freq === 1 ? 'Low' : freq === 2 ? 'Medium' : 'High';
    });
    const churnRates = data.map(item => (item.churn * 100).toFixed(1));

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Churn Rate (%)',
                data: churnRates,
                borderColor: chartColors.primary,
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointHoverRadius: 8,
                pointBackgroundColor: chartColors.primary,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

function createSatisfactionChurnChart() {
    const ctx = document.getElementById('satisfactionChurnChart');
    if (!ctx) return;

    const data = chartData.satisfactionChurn;
    const labels = Object.keys(data).sort();
    const retained = labels.map(label => data[label].Retained || 0);
    const churned = labels.map(label => data[label].Churned || 0);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => `${l} ⭐`),
            datasets: [
                {
                    label: 'Retained',
                    data: retained,
                    backgroundColor: chartColors.secondary,
                    borderRadius: 6
                },
                {
                    label: 'Churned',
                    data: churned,
                    backgroundColor: chartColors.danger,
                    borderRadius: 6
                }
            ]
        },
        options: {
            ...chartOptions,
            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }
        }
    });
}

function createTicketsChurnChart() {
    const ctx = document.getElementById('ticketsChurnChart');
    if (!ctx) return;

    const data = chartData.ticketsChurn;
    const labels = Object.keys(data).sort((a, b) => {
        if (a === '4+') return 1;
        if (b === '4+') return -1;
        return parseFloat(a) - parseFloat(b);
    });
    const retained = labels.map(label => data[label].Retained || 0);
    const churned = labels.map(label => data[label].Churned || 0);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels.map(l => `${l} tickets`),
            datasets: [
                {
                    label: 'Retained',
                    data: retained,
                    backgroundColor: chartColors.secondary,
                    borderRadius: 6
                },
                {
                    label: 'Churned',
                    data: churned,
                    backgroundColor: chartColors.danger,
                    borderRadius: 6
                }
            ]
        },
        options: {
            ...chartOptions,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

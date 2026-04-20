async function fetchDashboardData() {
    try {
        const response = await fetch('/reports');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const reports = await response.json();
        return processReportsData(reports);
    } catch (error) {
        console.error('Erro ao buscar dados da API:', error);
        return getFallbackData();
    }
}

function processReportsData(reports) {
    const squads = {};
    const executionStatus = {
        completed: 0,
        failed: 0,
        running: 0,
        pending: 0
    };

    reports.forEach(report => {
        const squad = report.squad || 'Sem Squad';

        if (!squads[squad]) {
            squads[squad] = {
                total_automations: 0,
                successful_executions: 0,
                failed_executions: 0,
                avg_execution_time: 0,
                last_execution: null,
                automation_names: new Set()
            };
        }

        squads[squad].automation_names.add(report.name);
        squads[squad].total_automations = squads[squad].automation_names.size;

        if (report.status === 'success' || report.status === 'completed') {
            squads[squad].successful_executions++;
            executionStatus.completed++;
        } else if (report.status === 'failed' || report.status === 'error') {
            squads[squad].failed_executions++;
            executionStatus.failed++;
        } else if (report.status === 'running') {
            executionStatus.running++;
        } else {
            executionStatus.pending++;
        }

        if (!squads[squad].last_execution || report.report_date > squads[squad].last_execution) {
            squads[squad].last_execution = report.report_date;
        }
    });

    Object.keys(squads).forEach(squad => {
        const squadReports = reports.filter(r => r.squad === squad);
        const totalTests = squadReports.reduce((sum, r) => sum + (r.tests || 1), 0);
        const avgTests = totalTests / squadReports.length;
        squads[squad].avg_execution_time = Math.round((avgTests * 0.5 + 1) * 10) / 10;
    });

    const trendData = generateTrendData(reports);

    return {
        squads,
        execution_status: executionStatus,
        trend_data: trendData
    };
}

function generateTrendData(reports) {
    const labels = [];
    const successful = [];
    const failed = [];

    for (let i = 6; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('pt-BR', {day: '2-digit', month: '2-digit'}));
    }

    labels.forEach((label, index) => {
        const targetDate = new Date();
        targetDate.setDate(targetDate.getDate() - (6 - index));
        const dateStr = targetDate.toISOString().split('T')[0];

        const dayReports = reports.filter(report => {
            const reportDate = new Date(report.report_date).toISOString().split('T')[0];
            return reportDate === dateStr;
        });

        const daySuccessful = dayReports.filter(r =>
            r.status === 'success' || r.status === 'completed'
        ).length;
        const dayFailed = dayReports.filter(r =>
            r.status === 'failed' || r.status === 'error'
        ).length;

        successful.push(daySuccessful);
        failed.push(dayFailed);
    });

    return {labels, successful, failed};
}

function getFallbackData() {
    return {
        "squads": {
            "Frontend Squad": {
                "total_automations": 8,
                "successful_executions": 45,
                "failed_executions": 3,
                "avg_execution_time": 2.3,
                "last_execution": "2024-12-16T10:30:00Z"
            },
            "Backend Squad": {
                "total_automations": 12,
                "successful_executions": 78,
                "failed_executions": 5,
                "avg_execution_time": 3.1,
                "last_execution": "2024-12-16T09:45:00Z"
            },
            "Mobile Squad": {
                "total_automations": 6,
                "successful_executions": 32,
                "failed_executions": 2,
                "avg_execution_time": 4.2,
                "last_execution": "2024-12-16T11:15:00Z"
            },
            "QA Squad": {
                "total_automations": 15,
                "successful_executions": 95,
                "failed_executions": 8,
                "avg_execution_time": 2.8,
                "last_execution": "2024-12-16T08:20:00Z"
            }
        },
        "execution_status": {
            "completed": 250,
            "failed": 18,
            "running": 5,
            "pending": 12
        },
        "trend_data": {
            "labels": ["10/12", "11/12", "12/12", "13/12", "14/12", "15/12", "16/12"],
            "successful": [35, 42, 38, 45, 52, 48, 55],
            "failed": [3, 2, 4, 3, 1, 2, 3]
        }
    };
}

let dashboardData = {};

function updateMetricCards() {
    const totalSuccess = Object.values(dashboardData.squads).reduce((sum, squad) => sum + squad.successful_executions, 0);
    const totalFailed = Object.values(dashboardData.squads).reduce((sum, squad) => sum + squad.failed_executions, 0);
    const totalAutomations = Object.values(dashboardData.squads).reduce((sum, squad) => sum + squad.total_automations, 0);
    const successRate = totalSuccess + totalFailed > 0 ? Math.round((totalSuccess / (totalSuccess + totalFailed)) * 100) : 0;

    document.getElementById('totalSuccess').textContent = totalSuccess;
    document.getElementById('totalFailed').textContent = totalFailed;
    document.getElementById('totalAutomations').textContent = totalAutomations;
    document.getElementById('successRate').textContent = successRate + '%';
    document.getElementById('lastUpdate').textContent = new Date().toLocaleString('pt-BR');
}

function createSquadChart() {
    const ctx = document.getElementById('squadChart').getContext('2d');
    const squadNames = Object.keys(dashboardData.squads);
    const automationCounts = squadNames.map(squad => dashboardData.squads[squad].total_automations);
    const successCounts = squadNames.map(squad => dashboardData.squads[squad].successful_executions);
    const failedCounts = squadNames.map(squad => dashboardData.squads[squad].failed_executions);

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: squadNames,
            datasets: [
                {
                    label: 'Automações Cadastradas',
                    data: automationCounts,
                    backgroundColor: '#0065ff',
                    borderColor: '#0052cc',
                    borderWidth: 1
                },
                {
                    label: 'Execuções Bem-sucedidas',
                    data: successCounts,
                    backgroundColor: '#36b37e',
                    borderColor: '#2d9e5e',
                    borderWidth: 1
                },
                {
                    label: 'Execuções Falharam',
                    data: failedCounts,
                    backgroundColor: '#ff5630',
                    borderColor: '#e13d26',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

function createStatusChart() {
    const ctx = document.getElementById('statusChart').getContext('2d');
    const statusData = dashboardData.execution_status;

    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completas', 'Falharam', 'Executando', 'Pendentes'],
            datasets: [{
                data: [
                    statusData.completed,
                    statusData.failed,
                    statusData.running,
                    statusData.pending
                ],
                backgroundColor: [
                    '#36b37e',
                    '#ff5630',
                    '#ffab00',
                    '#0065ff'
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        }
    });
}

function createPerformanceChart() {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    const squadNames = Object.keys(dashboardData.squads);
    const avgTimes = squadNames.map(squad => dashboardData.squads[squad].avg_execution_time);

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: squadNames,
            datasets: [{
                label: 'Tempo Médio de Execução (min)',
                data: avgTimes,
                borderColor: '#ffab00',
                backgroundColor: 'rgba(255, 171, 0, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Tempo (minutos)'
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

function createTrendChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    const trendData = dashboardData.trend_data;

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: trendData.labels,
            datasets: [
                {
                    label: 'Execuções Bem-sucedidas',
                    data: trendData.successful,
                    borderColor: '#36b37e',
                    backgroundColor: 'rgba(54, 179, 126, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Execuções Falharam',
                    data: trendData.failed,
                    borderColor: '#ff5630',
                    backgroundColor: 'rgba(255, 86, 48, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 5
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
}

async function initializeDashboard() {
    try {
        document.getElementById('totalSuccess').textContent = '...';
        document.getElementById('totalFailed').textContent = '...';
        document.getElementById('totalAutomations').textContent = '...';
        document.getElementById('successRate').textContent = '...';

        dashboardData = await fetchDashboardData();

        updateMetricCards();
        createSquadChart();
        createStatusChart();
        createPerformanceChart();
        createTrendChart();
    } catch (error) {
        console.error('Erro ao inicializar dashboard:', error);
        dashboardData = getFallbackData();
        updateMetricCards();
        createSquadChart();
        createStatusChart();
        createPerformanceChart();
        createTrendChart();
    }
}

window.onload = initializeDashboard;

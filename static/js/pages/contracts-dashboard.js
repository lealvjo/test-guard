async function fetchContractsData() {
    try {
        console.log('=== INÍCIO fetchContractsData ===');
        const response = await fetch('/contracts');
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Dados recebidos da API:', data);
        console.log('Tipo dos dados:', typeof data);
        console.log('Estrutura dos dados:', Object.keys(data));

        const contracts = data.contracts || [];
        console.log('Contratos extraídos:', contracts);
        console.log('Quantidade de contratos:', contracts.length);

        const processedData = processContractsData(contracts);
        console.log('Dados processados retornados:', processedData);
        console.log('=== FIM fetchContractsData ===');

        return processedData;
    } catch (error) {
        console.error('❌ Erro ao buscar dados da API:', error);
        throw error;
    }
}

function processContractsData(contracts) {
    console.log('=== INÍCIO processContractsData ===');
    console.log('Contratos recebidos:', contracts);
    console.log('Tipo dos contratos:', typeof contracts);
    console.log('É array?', Array.isArray(contracts));
    console.log('Quantidade:', contracts ? contracts.length : 'undefined');

    if (!contracts || !Array.isArray(contracts)) {
        console.error('❌ Contratos inválidos:', contracts);
        return {
            squads: {},
            total_collections: 0,
            total_schemas: 0,
            total_squads: 0,
            avg_schemas_per_collection: 0,
            http_methods: {},
            growth_data: {labels: [], collections: [], schemas: []}
        };
    }

    if (contracts.length === 0) {
        console.warn('⚠️ Array de contratos vazio');
        return {
            squads: {},
            total_collections: 0,
            total_schemas: 0,
            total_squads: 0,
            avg_schemas_per_collection: 0,
            http_methods: {},
            growth_data: {labels: [], collections: [], schemas: []}
        };
    }

    const squads = {};
    let totalCollections = 0;
    let totalSchemas = 0;
    const squadNames = new Set();

    contracts.forEach((contract, index) => {
        console.log(`--- Processando contrato ${index + 1} ---`);
        console.log('Contrato:', contract);

        const squad = contract.squad || 'Sem Squad';
        console.log('Squad extraído:', squad);
        squadNames.add(squad);

        if (!squads[squad]) {
            console.log(`Inicializando squad: ${squad}`);
            squads[squad] = {
                collections: 0,
                total_schemas: 0,
                avg_schemas: 0,
                last_update: null,
                collection_names: []
            };
        }

        squads[squad].collections++;

        let schemasCount = 0;
        console.log('Schemas do contrato:', contract.schemas);
        console.log('Tipo dos schemas:', typeof contract.schemas);

        if (contract.schemas) {
            if (Array.isArray(contract.schemas)) {
                schemasCount = contract.schemas.length;
                console.log(`Schemas é array com ${schemasCount} itens`);
            } else if (typeof contract.schemas === 'string') {
                try {
                    const parsedSchemas = JSON.parse(contract.schemas);
                    schemasCount = Array.isArray(parsedSchemas) ? parsedSchemas.length : 0;
                    console.log(`Schemas é string JSON com ${schemasCount} itens`);
                } catch (e) {
                    console.warn('Erro ao fazer parse dos schemas:', e);
                    schemasCount = 0;
                }
            }
        } else {
            console.log('Contrato sem schemas');
        }

        console.log(`Schemas count para ${contract.name}: ${schemasCount}`);

        squads[squad].total_schemas += schemasCount;
        squads[squad].collection_names.push(contract.name);

        totalCollections++;
        totalSchemas += schemasCount;

        const updateDate = contract.created_at || contract.updated_at;
        if (!squads[squad].last_update || updateDate > squads[squad].last_update) {
            squads[squad].last_update = updateDate;
        }
    });

    Object.keys(squads).forEach(squad => {
        squads[squad].avg_schemas = squads[squad].collections > 0
            ? Math.round((squads[squad].total_schemas / squads[squad].collections) * 10) / 10
            : 0;
    });

    const growthData = generateGrowthData(contracts);
    console.log('Dados de crescimento gerados:', growthData);

    const httpMethods = {
        'GET': 0,
        'POST': 0,
        'PUT': 0,
        'DELETE': 0,
        'PATCH': 0,
        'HEAD': 0,
        'OPTIONS': 0,
        'N/A': 0
    };

    contracts.forEach(contract => {
        if (contract.schemas) {
            let schemas = contract.schemas;
            if (typeof schemas === 'string') {
                try {
                    schemas = JSON.parse(schemas);
                } catch (e) {
                    return;
                }
            }

            if (Array.isArray(schemas)) {
                schemas.forEach(schema => {
                    const method = schema.method || 'N/A';
                    if (httpMethods.hasOwnProperty(method)) {
                        httpMethods[method]++;
                    } else {
                        httpMethods['N/A']++;
                    }
                });
            }
        }
    });

    const result = {
        squads,
        total_collections: totalCollections,
        total_schemas: totalSchemas,
        total_squads: squadNames.size,
        avg_schemas_per_collection: totalCollections > 0 ? Math.round((totalSchemas / totalCollections) * 10) / 10 : 0,
        http_methods: httpMethods,
        growth_data: growthData
    };

    console.log('=== RESULTADO FINAL ===');
    console.log('Squads processados:', squads);
    console.log('Total collections:', totalCollections);
    console.log('Total schemas:', totalSchemas);
    console.log('Total squads:', squadNames.size);
    console.log('HTTP methods:', httpMethods);
    console.log('Growth data:', growthData);
    console.log('Resultado completo:', result);
    console.log('=== FIM processContractsData ===');

    return result;
}

function generateGrowthData(contracts) {
    try {
        console.log('=== INÍCIO generateGrowthData ===');
        console.log('Gerando dados de crescimento para:', contracts);
        console.log('Tipo dos contratos:', typeof contracts);
        console.log('É array?', Array.isArray(contracts));
        console.log('Quantidade:', contracts ? contracts.length : 'undefined');

        if (!contracts || !Array.isArray(contracts)) {
            console.warn('Contratos inválidos para gerar dados de crescimento');
            return {labels: [], collections: [], schemas: []};
        }

        if (contracts.length === 0) {
            console.warn('Array de contratos vazio para crescimento');
            return {labels: [], collections: [], schemas: []};
        }

        const labels = [];
        const collections = [];
        const schemas = [];

        for (let i = 6; i >= 0; i--) {
            const date = new Date();
            date.setDate(date.getDate() - i);
            labels.push(date.toLocaleDateString('pt-BR', {day: '2-digit', month: '2-digit'}));
        }

        console.log('Labels gerados:', labels);

        labels.forEach((label, index) => {
            const targetDate = new Date();
            targetDate.setDate(targetDate.getDate() - (6 - index));
            const dateStr = targetDate.toISOString().split('T')[0];

            console.log(`Processando dia ${label} (${dateStr})`);

            let dayContractsCount = 0;
            let daySchemasCount = 0;

            contracts.forEach((contract, contractIndex) => {
                try {
                    console.log(`  Verificando contrato ${contractIndex + 1}: ${contract.name}`);
                    console.log(`  Created_at: ${contract.created_at}`);

                    let contractDate = null;
                    if (contract.created_at) {
                        const date = new Date(contract.created_at);
                        contractDate = date.toISOString().split('T')[0];
                    }
                    console.log(`  Data do contrato: ${contractDate}`);

                    if (contractDate === dateStr) {
                        console.log(`  ✅ Contrato ${contract.name} criado neste dia!`);
                        dayContractsCount++;

                        let schemasCount = 0;
                        if (contract.schemas) {
                            if (Array.isArray(contract.schemas)) {
                                schemasCount = contract.schemas.length;
                                console.log(`  Schemas é array com ${schemasCount} itens`);
                            } else if (typeof contract.schemas === 'string') {
                                try {
                                    const parsedSchemas = JSON.parse(contract.schemas);
                                    schemasCount = Array.isArray(parsedSchemas) ? parsedSchemas.length : 0;
                                    console.log(`  Schemas é string JSON com ${schemasCount} itens`);
                                } catch (e) {
                                    console.warn(`  Erro ao fazer parse dos schemas: ${e}`);
                                    schemasCount = 0;
                                }
                            }
                        } else {
                            console.log('  Contrato sem schemas');
                        }
                        daySchemasCount += schemasCount;
                        console.log(`  Schemas count para ${contract.name}: ${schemasCount}`);
                    } else {
                        console.log(`  ❌ Contrato ${contract.name} não foi criado neste dia`);
                    }
                } catch (e) {
                    console.warn(`Erro ao processar contrato ${contractIndex + 1}:`, contract, e);
                }
            });

            console.log(`Dia ${label}: ${dayContractsCount} contratos, ${daySchemasCount} schemas`);
            collections.push(dayContractsCount);
            schemas.push(daySchemasCount);
        });

        const result = {labels, collections, schemas};
        console.log('=== RESULTADO generateGrowthData ===');
        console.log('Labels:', labels);
        console.log('Collections:', collections);
        console.log('Schemas:', schemas);
        console.log('Resultado final:', result);
        console.log('=== FIM generateGrowthData ===');

        return result;
    } catch (error) {
        console.error('❌ Erro ao gerar dados de crescimento:', error);
        return {labels: [], collections: [], schemas: []};
    }
}

let contractsData = {};

function updateMetricCards() {
    try {
        const totalCollectionsEl = document.getElementById('totalCollections');
        const totalSchemasEl = document.getElementById('totalSchemas');
        const totalSquadsEl = document.getElementById('totalSquads');
        const avgSchemasEl = document.getElementById('avgSchemasPerCollection');
        const lastUpdateEl = document.getElementById('lastUpdate');

        if (totalCollectionsEl) totalCollectionsEl.textContent = contractsData.total_collections || 0;
        if (totalSchemasEl) totalSchemasEl.textContent = contractsData.total_schemas || 0;
        if (totalSquadsEl) totalSquadsEl.textContent = contractsData.total_squads || 0;
        if (avgSchemasEl) avgSchemasEl.textContent = contractsData.avg_schemas_per_collection || 0;
        if (lastUpdateEl) lastUpdateEl.textContent = new Date().toLocaleString('pt-BR');

        console.log('✅ Cards de métricas atualizados');
    } catch (error) {
        console.error('❌ Erro ao atualizar cards de métricas:', error);
    }
}

function createSquadChart() {
    try {
        const canvas = document.getElementById('squadChart');
        if (!canvas) {
            console.error('❌ Canvas squadChart não encontrado');
            return;
        }

        const ctx = canvas.getContext('2d');
        const squadNames = Object.keys(contractsData.squads || {});
        const collectionsCount = squadNames.map(squad => contractsData.squads[squad].collections);
        const schemasCount = squadNames.map(squad => contractsData.squads[squad].total_schemas);

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: squadNames,
                datasets: [
                    {
                        label: 'Coleções',
                        data: collectionsCount,
                        backgroundColor: '#0065ff',
                        borderColor: '#0052cc',
                        borderWidth: 1
                    },
                    {
                        label: 'Total de Schemas',
                        data: schemasCount,
                        backgroundColor: '#36b37e',
                        borderColor: '#2d9e5e',
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
                            stepSize: 1
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

        console.log('✅ Gráfico de squad criado com sucesso');
    } catch (error) {
        console.error('❌ Erro ao criar gráfico de squad:', error);
    }
}

function createSchemasChart() {
    try {
        const canvas = document.getElementById('schemasChart');
        if (!canvas) {
            console.error('❌ Canvas schemasChart não encontrado');
            return;
        }

        const ctx = canvas.getContext('2d');
        const squadNames = Object.keys(contractsData.squads || {});
        const avgSchemas = squadNames.map(squad => contractsData.squads[squad].avg_schemas);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: squadNames,
                datasets: [{
                    label: 'Schemas Médios por Coleção',
                    data: avgSchemas,
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
                            text: 'Quantidade de Schemas'
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

        console.log('✅ Gráfico de schemas criado com sucesso');
    } catch (error) {
        console.error('❌ Erro ao criar gráfico de schemas:', error);
    }
}

function createDistributionChart() {
    try {
        const canvas = document.getElementById('distributionChart');
        if (!canvas) {
            console.error('❌ Canvas distributionChart não encontrado');
            return;
        }

        const ctx = canvas.getContext('2d');
        const squadNames = Object.keys(contractsData.squads || {});
        const collectionsData = squadNames.map(squad => contractsData.squads[squad].collections);

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: squadNames,
                datasets: [{
                    data: collectionsData,
                    backgroundColor: [
                        '#0065ff',
                        '#36b37e',
                        '#ffab00',
                        '#ff5630',
                        '#8b5cf6'
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

        console.log('✅ Gráfico de distribuição criado com sucesso');
    } catch (error) {
        console.error('❌ Erro ao criar gráfico de distribuição:', error);
    }
}

function createMethodsChart() {
    try {
        const canvas = document.getElementById('methodsChart');
        if (!canvas) {
            console.error('❌ Canvas methodsChart não encontrado');
            return;
        }

        const ctx = canvas.getContext('2d');
        const httpMethods = contractsData.http_methods || {};

        const methods = Object.keys(httpMethods).filter(method => httpMethods[method] > 0);
        const values = methods.map(method => httpMethods[method]);
        const total = values.reduce((a, b) => a + b, 0);

        const methodColors = {
            'GET': '#36b37e',
            'POST': '#0065ff',
            'PUT': '#ffab00',
            'DELETE': '#ff5630',
            'PATCH': '#8b5cf6',
            'HEAD': '#00b8d9',
            'OPTIONS': '#ff8b00',
            'N/A': '#5e6c84'
        };

        const colors = methods.map(method => methodColors[method] || '#5e6c84');

        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: methods,
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 3,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '60%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} contratos (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        console.log('✅ Gráfico de métodos HTTP criado com sucesso');
    } catch (error) {
        console.error('❌ Erro ao criar gráfico de métodos HTTP:', error);
    }
}

function createGrowthChart() {
    console.log('Criando gráfico de crescimento...');

    try {
        const ctx = document.getElementById('growthChart');
        if (!ctx) {
            console.error('Canvas growthChart não encontrado');
            return;
        }

        const growthData = contractsData.growth_data || {labels: [], collections: [], schemas: []};

        if (growthData.labels.length === 0) {
            console.warn('⚠️ Nenhum dado de crescimento disponível');
            return;
        }

        console.log('Dados do gráfico:', growthData);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: growthData.labels,
                datasets: [
                    {
                        label: 'Novas Coleções',
                        data: growthData.collections,
                        borderColor: '#0065ff',
                        backgroundColor: 'rgba(0, 101, 255, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Novos Schemas',
                        data: growthData.schemas,
                        borderColor: '#36b37e',
                        backgroundColor: 'rgba(54, 179, 126, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });

        console.log('✅ Gráfico de crescimento criado com sucesso!');
    } catch (error) {
        console.error('❌ Erro ao criar gráfico de crescimento:', error);
    }
}

function updateDetailsTable() {
    console.log('Atualizando tabela de detalhes...');

    try {
        const tbody = document.getElementById('detailsTableBody');
        if (!tbody) {
            console.error('Tbody não encontrado');
            return;
        }

        const squads = contractsData.squads || {};
        const squadNames = Object.keys(squads);

        if (squadNames.length === 0) {
            console.warn('⚠️ Nenhum squad encontrado');
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #5e6c84;">Nenhum squad encontrado</td></tr>';
            return;
        }

        console.log('Dados dos squads:', squads);

        tbody.innerHTML = '';

        squadNames.forEach(squad => {
            const squadData = squads[squad];
            const lastUpdate = squadData.last_update ?
                new Date(squadData.last_update).toLocaleDateString('pt-BR') :
                'N/A';

            const row = document.createElement('tr');
            row.innerHTML = `
                <td><strong>${squad}</strong></td>
                <td style="text-align: center;">${squadData.collections}</td>
                <td style="text-align: center;">${squadData.total_schemas}</td>
                <td style="text-align: center;">${squadData.avg_schemas}</td>
                <td style="text-align: center;">${lastUpdate}</td>
            `;
            tbody.appendChild(row);
        });

        console.log('✅ Tabela de detalhes atualizada com sucesso!');
        console.log('Linhas na tabela:', tbody.children.length);
    } catch (error) {
        console.error('❌ Erro ao atualizar tabela:', error);
    }
}

async function initializeContractsDashboard() {
    console.log('🚀 Inicializando dashboard de contratos...');

    try {
        const loadingElements = [
            'totalCollections', 'totalSchemas', 'totalSquads', 'avgSchemasPerCollection'
        ];

        loadingElements.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = '...';
        });

        console.log('📡 Buscando dados da API...');
        contractsData = await fetchContractsData();
        console.log('✅ Dados da API carregados:', contractsData);

        console.log('📊 Atualizando interface com dados:', contractsData);

        try {
            updateMetricCards();
            console.log('✅ Cards de métricas atualizados');
        } catch (error) {
            console.error('❌ Erro ao atualizar cards:', error);
        }

        try {
            createSquadChart();
            console.log('✅ Gráfico de squad criado');
        } catch (error) {
            console.error('❌ Erro ao criar gráfico de squad:', error);
        }

        try {
            createSchemasChart();
            console.log('✅ Gráfico de schemas criado');
        } catch (error) {
            console.error('❌ Erro ao criar gráfico de schemas:', error);
        }

        try {
            createDistributionChart();
            console.log('✅ Gráfico de distribuição criado');
        } catch (error) {
            console.error('❌ Erro ao criar gráfico de distribuição:', error);
        }

        try {
            createMethodsChart();
            console.log('✅ Gráfico de métodos HTTP criado');
        } catch (error) {
            console.error('❌ Erro ao criar gráfico de métodos HTTP:', error);
        }

        try {
            createGrowthChart();
            console.log('✅ Gráfico de crescimento criado');
        } catch (error) {
            console.error('❌ Erro ao criar gráfico de crescimento:', error);
        }

        try {
            updateDetailsTable();
            console.log('✅ Tabela de detalhes atualizada');
        } catch (error) {
            console.error('❌ Erro ao atualizar tabela:', error);
        }

        console.log('🎉 Dashboard inicializado com sucesso!');
    } catch (error) {
        console.error('💥 Erro ao inicializar dashboard:', error);

        const errorElements = [
            'totalCollections', 'totalSchemas', 'totalSquads', 'avgSchemasPerCollection'
        ];

        errorElements.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.textContent = 'Erro';
        });

        console.error('❌ Dashboard não pôde ser inicializado devido a erro na API');
    }
}

window.onload = initializeContractsDashboard;

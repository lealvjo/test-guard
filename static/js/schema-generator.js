// ===== SCHEMA GENERATOR - JavaScript específico =====

/**
 * Formata os editores JSON e Schema
 */
function formatEditors() {
    const json = tryParseJSON(document.getElementById('jsonInput').value);
    if (json) {
        document.getElementById('jsonInput').value = formatJSON(json);
    }
    
    const schema = tryParseJSON(document.getElementById('schemaInput').value);
    if (schema) {
        document.getElementById('schemaInput').value = formatJSON(schema);
    }
}

/**
 * Formata automaticamente o JSON
 */
function autoFormatJSON() {
    const jsonInput = document.getElementById('jsonInput');
    const json = tryParseJSON(jsonInput.value);
    if (json) {
        jsonInput.value = formatJSON(json);
    }
}

/**
 * Formata automaticamente o Schema
 */
function autoFormatSchema() {
    const schemaInput = document.getElementById('schemaInput');
    const schema = tryParseJSON(schemaInput.value);
    if (schema) {
        schemaInput.value = formatJSON(schema);
    }
}

/**
 * Limpa os editores
 */
function clearEditors() {
    document.getElementById('jsonInput').value = '';
    document.getElementById('schemaInput').value = '';
    hideAlert();
}

/**
 * Gera schema a partir do JSON
 */
function generateSchemaFromJson() {
    const json = tryParseJSON(document.getElementById('jsonInput').value);
    if (!json) { 
        showAlert('JSON inválido. Verifique a sintaxe.', true); 
        return; 
    }
    
    try {
        let schema;
        
        // Tenta biblioteca externa se existir
        if (window.GenerateSchema && typeof window.GenerateSchema.json === 'function') {
            schema = window.GenerateSchema.json('Root', json);
        } else {
            schema = buildSchemaFromJson(json);
        }
        
        // Garante metadados básicos
        schema.$schema = schema.$schema || 'http://json-schema.org/draft-07/schema#';
        schema.title = schema.title || 'Root';

        // Aplica opções
        const wantRequired = document.getElementById('optRequired').checked;
        const wantExample = document.getElementById('optExample').checked;

        if (!wantRequired) {
            removeRequired(schema);
        }
        if (wantExample) {
            addExamples(schema, json);
        }

        document.getElementById('schemaInput').value = formatJSON(schema);
        showAlert('Schema gerado com sucesso!', false);
        
    } catch (e) { 
        showAlert('Erro ao gerar schema: ' + e.message, true); 
    }
}

/**
 * Constrói schema a partir de JSON (fallback)
 * @param {*} data - Dados para gerar schema
 * @returns {object} - Schema gerado
 */
function buildSchemaFromJson(data) {
    const type = inferType(data);
    
    if (type === 'object') {
        const properties = {};
        const required = [];
        
        for (const key of Object.keys(data)) {
            properties[key] = buildSchemaFromJson(data[key]);
            required.push(key);
        }
        
        return { type: 'object', properties, required };
    }
    
    if (type === 'array') {
        const itemsSchema = data.length > 0 ? buildSchemaFromJson(data[0]) : {};
        return { type: 'array', items: itemsSchema };
    }
    
    return { type: type };
}

/**
 * Infere o tipo de um valor
 * @param {*} value - Valor para inferir tipo
 * @returns {string} - Tipo inferido
 */
function inferType(value) {
    if (value === null) return 'null';
    if (Array.isArray(value)) return 'array';
    
    switch (typeof value) {
        case 'string': return 'string';
        case 'boolean': return 'boolean';
        case 'number': return Number.isInteger(value) ? 'integer' : 'number';
        case 'object': return 'object';
        default: return 'string';
    }
}

/**
 * Remove campos required do schema
 * @param {object} schema - Schema para modificar
 */
function removeRequired(schema) {
    if (!schema || typeof schema !== 'object') return;
    
    if (schema.required) {
        delete schema.required;
    }
    
    if (schema.properties) {
        Object.values(schema.properties).forEach(child => removeRequired(child));
    }
    
    if (schema.items) {
        removeRequired(schema.items);
    }
}

/**
 * Adiciona exemplos ao schema
 * @param {object} schema - Schema para modificar
 * @param {*} data - Dados para extrair exemplos
 */
function addExamples(schema, data) {
    if (!schema || typeof schema !== 'object') return;
    
    const type = schema.type;
    
    if (type === 'object' && schema.properties && data && typeof data === 'object' && !Array.isArray(data)) {
        Object.keys(schema.properties).forEach(key => {
            addExamples(schema.properties[key], data[key]);
        });
    } else if (type === 'array' && schema.items && Array.isArray(data) && data.length) {
        addExamples(schema.items, data[0]);
    } else if (type && type !== 'object' && type !== 'array') {
        schema.example = data;
    }
}

// ===== INICIALIZAÇÃO =====

/**
 * Inicializa a página do schema generator
 */
function initializeSchemaGenerator() {
    const jsonInput = document.getElementById('jsonInput');
    const schemaInput = document.getElementById('schemaInput');
    
    if (!jsonInput || !schemaInput) {
        console.error('Elementos do schema generator não encontrados');
        return;
    }
    
    // Formatar quando o usuário colar conteúdo
    jsonInput.addEventListener('paste', function() {
        setTimeout(autoFormatJSON, 100);
    });
    
    schemaInput.addEventListener('paste', function() {
        setTimeout(autoFormatSchema, 100);
    });
    
    // Formatar quando o usuário sair do campo (blur)
    jsonInput.addEventListener('blur', autoFormatJSON);
    schemaInput.addEventListener('blur', autoFormatSchema);
    
    // Formatar quando o usuário pressionar Ctrl+Shift+F
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.shiftKey && e.key === 'F') {
            e.preventDefault();
            formatEditors();
        }
    });
}

// Executa inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initializeSchemaGenerator);

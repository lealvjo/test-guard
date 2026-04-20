function showAlert(message, isError) {
    const box = document.getElementById('alertBox');
    const icon = isError ? '❌' : '✅';
    box.innerHTML = `${icon} ${message}`;
    box.className = 'alert ' + (isError ? 'alert-error' : 'alert-success');
    box.style.display = 'block';
}

function tryParseJSON(text) {
    try {
        return JSON.parse(text);
    } catch {
        return null;
    }
}

function formatEditors() {
    const json = tryParseJSON(document.getElementById('jsonInput').value);
    if (json) document.getElementById('jsonInput').value = JSON.stringify(json, null, 2);
    const schema = tryParseJSON(document.getElementById('schemaInput').value);
    if (schema) document.getElementById('schemaInput').value = JSON.stringify(schema, null, 2);
}

function autoFormatJSON() {
    const jsonInput = document.getElementById('jsonInput');
    const json = tryParseJSON(jsonInput.value);
    if (json) {
        jsonInput.value = JSON.stringify(json, null, 2);
    }
}

function autoFormatSchema() {
    const schemaInput = document.getElementById('schemaInput');
    const schema = tryParseJSON(schemaInput.value);
    if (schema) {
        schemaInput.value = JSON.stringify(schema, null, 2);
    }
}

function clearEditors() {
    document.getElementById('jsonInput').value = '';
    document.getElementById('schemaInput').value = '';
    document.getElementById('alertBox').style.display = 'none';
}

function generateSchemaFromJson() {
    const json = tryParseJSON(document.getElementById('jsonInput').value);
    if (!json) {
        showAlert('JSON inválido. Verifique a sintaxe.', true);
        return;
    }

    try {
        let schema;
        if (window.GenerateSchema && typeof window.GenerateSchema.json === 'function') {
            schema = window.GenerateSchema.json('Root', json);
        } else {
            schema = buildSchemaFromJson(json);
        }

        schema.$schema = schema.$schema || 'http://json-schema.org/draft-07/schema#';
        schema.title = schema.title || 'Root';

        const wantRequired = document.getElementById('optRequired').checked;
        const wantExample = document.getElementById('optExample').checked;

        if (!wantRequired) removeRequired(schema);
        if (wantExample) addExamples(schema, json);

        document.getElementById('schemaInput').value = JSON.stringify(schema, null, 2);
        showAlert('Schema gerado com sucesso!', false);
    } catch (e) {
        showAlert('Erro ao gerar schema: ' + e.message, true);
    }
}

function buildSchemaFromJson(data) {
    const t = inferType(data);
    if (t === 'object') {
        const properties = {};
        const required = [];
        for (const key of Object.keys(data)) {
            properties[key] = buildSchemaFromJson(data[key]);
            required.push(key);
        }
        return {type: 'object', properties, required};
    }
    if (t === 'array') {
        const itemsSchema = data.length > 0 ? buildSchemaFromJson(data[0]) : {};
        return {type: 'array', items: itemsSchema};
    }
    return {type: t};
}

function inferType(value) {
    if (value === null) return 'null';
    if (Array.isArray(value)) return 'array';
    switch (typeof value) {
        case 'string':
            return 'string';
        case 'boolean':
            return 'boolean';
        case 'number':
            return Number.isInteger(value) ? 'integer' : 'number';
        case 'object':
            return 'object';
        default:
            return 'string';
    }
}

function removeRequired(schema) {
    if (!schema || typeof schema !== 'object') return;
    if (schema.required) delete schema.required;
    if (schema.properties) {
        Object.values(schema.properties).forEach(child => removeRequired(child));
    }
    if (schema.items) removeRequired(schema.items);
}

function addExamples(schema, data) {
    if (!schema || typeof schema !== 'object') return;
    const t = schema.type;
    if (t === 'object' && schema.properties && data && typeof data === 'object' && !Array.isArray(data)) {
        Object.keys(schema.properties).forEach(key => {
            addExamples(schema.properties[key], data[key]);
        });
    } else if (t === 'array' && schema.items && Array.isArray(data) && data.length) {
        addExamples(schema.items, data[0]);
    } else if (t && t !== 'object' && t !== 'array') {
        schema.example = data;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const jsonInput = document.getElementById('jsonInput');
    const schemaInput = document.getElementById('schemaInput');

    jsonInput.addEventListener('paste', function() {
        setTimeout(autoFormatJSON, 100);
    });

    schemaInput.addEventListener('paste', function() {
        setTimeout(autoFormatSchema, 100);
    });

    jsonInput.addEventListener('blur', autoFormatJSON);
    schemaInput.addEventListener('blur', autoFormatSchema);
});

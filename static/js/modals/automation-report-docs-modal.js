let currentAutomationApiDoc = null;
let currentAutomationApiLanguage = 'python';

function openAutomationApiDocsModal(automation) {
    currentAutomationApiDoc = automation || null;
    const modal = document.getElementById('automationApiDocsModal');
    if (!modal) return;

    const idEl = document.getElementById('automationApiDocsId');
    const nameEl = document.getElementById('automationApiDocsName');
    const squadEl = document.getElementById('automationApiDocsSquad');
    const typeEl = document.getElementById('automationApiDocsType');

    if (idEl) idEl.textContent = currentAutomationApiDoc?.id ?? '-';
    if (nameEl) nameEl.textContent = currentAutomationApiDoc?.name ?? '-';
    if (squadEl) squadEl.textContent = currentAutomationApiDoc?.squad ?? '-';
    if (typeEl) typeEl.textContent = currentAutomationApiDoc?.type ?? '-';

    modal.style.display = 'block';
    renderAutomationApiDocExample(currentAutomationApiLanguage);
}

function closeAutomationApiDocsModal() {
    const modal = document.getElementById('automationApiDocsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function renderAutomationApiDocExample(language) {
    currentAutomationApiLanguage = language;
    const automationId = currentAutomationApiDoc?.id ?? 123;
    const automationName = currentAutomationApiDoc?.name ?? 'MinhaAutomacao';

    let code = '';
    if (language === 'python') {
        code = `import requests

url = "http://localhost:5000/report"
payload = {
    "automation_id": ${automationId},
    "status": "PASSED",
    "url_report": "https://ci.exemplo.com/reports/${automationName.toString().toLowerCase()}",
    "tests": 42,
    "junit": {
        "testsuite": {
            "name": "${automationName}",
            "tests": 42,
            "failures": 0,
            "errors": 0
        }
    }
}

response = requests.post(url, json=payload, timeout=30)
print(response.status_code)
print(response.json())`;
    } else if (language === 'javascript') {
        code = `const url = "http://localhost:5000/report";
const payload = {
  automation_id: ${automationId},
  status: "PASSED",
  url_report: "https://ci.exemplo.com/reports/${automationName.toString().toLowerCase()}",
  tests: 42,
  junit: {
    testsuite: {
      name: "${automationName}",
      tests: 42,
      failures: 0,
      errors: 0
    }
  }
};

const response = await fetch(url, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});

const result = await response.json();
console.log(response.status, result);`;
    } else if (language === 'typescript') {
        code = `type ReportPayload = {
  automation_id: number;
  status: string;
  url_report: string;
  tests: number;
  junit?: Record<string, unknown> | null;
};

const payload: ReportPayload = {
  automation_id: ${automationId},
  status: "PASSED",
  url_report: "https://ci.exemplo.com/reports/${automationName.toString().toLowerCase()}",
  tests: 42,
  junit: null
};

const response = await fetch("http://localhost:5000/report", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload)
});

const result = await response.json();
console.log(response.status, result);`;
    } else if (language === 'java') {
        code = `import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ReportGenerationExample {
    public static void main(String[] args) throws Exception {
        String json = """
{
  "automation_id": ${automationId},
  "status": "PASSED",
  "url_report": "https://ci.exemplo.com/reports/${automationName.toString().toLowerCase()}",
  "tests": 42,
  "junit": null
}
""";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:5000/report"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(json))
                .build();

        HttpResponse<String> response = HttpClient.newHttpClient()
                .send(request, HttpResponse.BodyHandlers.ofString());

        System.out.println(response.statusCode());
        System.out.println(response.body());
    }
}`;
    } else if (language === 'dotnet') {
        code = `using System.Net.Http;
using System.Text;
using System.Text.Json;

var client = new HttpClient();
var payload = new
{
    automation_id = ${automationId},
    status = "PASSED",
    url_report = "https://ci.exemplo.com/reports/${automationName.toString().toLowerCase()}",
    tests = 42,
    junit = (object?)null
};

var json = JsonSerializer.Serialize(payload);
var response = await client.PostAsync(
    "http://localhost:5000/report",
    new StringContent(json, Encoding.UTF8, "application/json")
);

Console.WriteLine((int)response.StatusCode);
Console.WriteLine(await response.Content.ReadAsStringAsync());`;
    } else if (language === 'curl') {
        code = `curl -X POST "http://localhost:5000/report" \\
  -H "Content-Type: application/json" \\
  -d '{
    "automation_id": ${automationId},
    "status": "PASSED",
    "url_report": "https://ci.exemplo.com/reports/${automationName.toString().toLowerCase()}",
    "tests": 42,
    "junit": null
  }'`;
    }

    const codeEl = document.getElementById('automationApiDocCode');
    if (codeEl) codeEl.textContent = code;

    renderAutomationApiResponseExamples();

    const selectedKeyMap = {
        javascript: 'js',
        typescript: 'ts',
        dotnet: 'dotnet',
        curl: 'curl',
        python: 'python',
        java: 'java'
    };
    const selectedKey = selectedKeyMap[language] || language;
    ['python', 'js', 'ts', 'java', 'dotnet', 'curl'].forEach((langKey) => {
        const btn = document.getElementById(`automation-api-doc-lang-${langKey}`);
        if (btn) btn.classList.toggle('active', langKey === selectedKey);
    });
}

function renderAutomationApiResponseExamples() {
    const automationId = currentAutomationApiDoc?.id ?? 123;

    const successExample = {
        message: 'Relatorio gerado com sucesso!',
        received_data: {
            automation_id: automationId,
            status: 'PASSED',
            url_report: 'https://ci.exemplo.com/reports/exemplo',
            tests: 42,
            junit: null
        }
    };

    const validationErrorExample = {
        message: "Campo 'junit' deve ser um objeto JSON ou null"
    };

    const notFoundExample = {
        message: 'Automation not found'
    };

    const successEl = document.getElementById('automationApiDocResponseSuccess');
    const validationEl = document.getElementById('automationApiDocResponseValidation');
    const notFoundEl = document.getElementById('automationApiDocResponseNotFound');

    if (successEl) successEl.textContent = JSON.stringify(successExample, null, 2);
    if (validationEl) validationEl.textContent = JSON.stringify(validationErrorExample, null, 2);
    if (notFoundEl) notFoundEl.textContent = JSON.stringify(notFoundExample, null, 2);
}

async function copyAutomationApiDocExample() {
    const codeEl = document.getElementById('automationApiDocCode');
    if (!codeEl || !codeEl.textContent) return;

    try {
        await navigator.clipboard.writeText(codeEl.textContent);
    } catch (error) {
        console.error('Não foi possível copiar exemplo de request.', error);
    }
}

async function copyAutomationApiResponse(responseType) {
    const targetMap = {
        success: 'automationApiDocResponseSuccess',
        validation: 'automationApiDocResponseValidation',
        not_found: 'automationApiDocResponseNotFound'
    };
    const targetId = targetMap[responseType];
    const target = document.getElementById(targetId);
    if (!target || !target.textContent) return;

    try {
        await navigator.clipboard.writeText(target.textContent);
    } catch (error) {
        console.error('Não foi possível copiar exemplo de retorno.', error);
    }
}

document.addEventListener('click', function(event) {
    const modal = document.getElementById('automationApiDocsModal');
    if (modal && event.target === modal) {
        closeAutomationApiDocsModal();
    }
});

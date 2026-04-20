function parseJsonText(jsonText, options = {}) {
    const allowComments = !!options.allowComments;
    const text = String(jsonText ?? '');

    try {
        let normalizedText = text;
        if (allowComments) {
            if (typeof window.cleanJsonFromComments === 'function') {
                normalizedText = window.cleanJsonFromComments(normalizedText);
            } else {
                normalizedText = normalizedText
                    .replace(/\/\/.*$/gm, '')
                    .replace(/\/\*[\s\S]*?\*\//g, '')
                    .trim();
            }
        }

        return {
            ok: true,
            data: JSON.parse(normalizedText),
            text: normalizedText
        };
    } catch (error) {
        return {
            ok: false,
            error: error
        };
    }
}

function formatJsonText(jsonText, options = {}) {
    const spaces = Number.isInteger(options.spaces) ? options.spaces : 2;
    const parsed = parseJsonText(jsonText, options);

    if (!parsed.ok) {
        return parsed;
    }

    return {
        ok: true,
        data: parsed.data,
        text: JSON.stringify(parsed.data, null, spaces)
    };
}

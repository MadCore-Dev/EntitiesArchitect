const vscode = require('vscode');

const ENGINE_URL = 'http://localhost:8000/index.html';

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
    console.log('[MadCore] Engine Launcher activated');

    // Command: opens Simple Browser panel directly inside Antigravity
    const launchCmd = vscode.commands.registerCommand('madcore.launchEditor', async () => {
        try {
            await vscode.commands.executeCommand('simpleBrowser.show', ENGINE_URL);
        } catch (err) {
            vscode.window.showErrorMessage(
                `[MadCore] Could not open Simple Browser: ${err.message}`
            );
        }
    });

    context.subscriptions.push(launchCmd);

    // Activity Bar sidebar panel
    const provider = {
        resolveWebviewView(webviewView) {
            webviewView.webview.options = { enableScripts: true };
            webviewView.webview.html = getWebviewContent();

            // Handle the "launch" button click from the webview
            webviewView.webview.onDidReceiveMessage(msg => {
                if (msg.command === 'launch') {
                    vscode.commands.executeCommand('madcore.launchEditor');
                }
            }, undefined, context.subscriptions);
        }
    };

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('madcore.engineView', provider)
    );
}

function getWebviewContent() {
    return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            margin: 0;
            padding: 16px;
            font-family: var(--vscode-font-family);
            color: var(--vscode-foreground);
            background: var(--vscode-sideBar-background);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            box-sizing: border-box;
        }
        .logo {
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 3px;
            color: var(--vscode-textLink-foreground);
            margin-top: 20px;
        }
        .sub {
            font-size: 10px;
            opacity: 0.55;
            text-align: center;
            line-height: 1.5;
        }
        button {
            margin-top: 16px;
            padding: 10px 20px;
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            width: 100%;
            transition: background 0.15s;
        }
        button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .shortcut {
            font-size: 10px;
            opacity: 0.4;
        }
        hr {
            width: 100%;
            border: none;
            border-top: 1px solid var(--vscode-panel-border);
            margin: 8px 0;
        }
        .tip {
            font-size: 10px;
            opacity: 0.4;
            text-align: center;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="logo">MADCORE</div>
    <div class="sub">RPG Game Engine Editor<br>v0.0.1</div>
    <button onclick="launch()">🎮 Open Editor View</button>
    <div class="shortcut">or press ⌘⇧G</div>
    <hr>
    <div class="tip">
        After opening, drag the<br>
        Simple Browser tab to the<br>
        right editor group for<br>
        split-screen mode.
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        function launch() {
            vscode.postMessage({ command: 'launch' });
        }
    </script>
</body>
</html>`;
}

function deactivate() {}

module.exports = { activate, deactivate };

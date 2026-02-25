const vscode = require('vscode');
const os = require('os');
const net = require('net');
const { exec } = require('child_process');

const ENGINE_PORT = 8000;
const ENGINE_PATH = '/index.html';
const LOCALHOST_URL = `http://localhost:${ENGINE_PORT}${ENGINE_PATH}`;

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function getLocalIp() {
    const ifaces = os.networkInterfaces();
    for (const name of Object.keys(ifaces)) {
        for (const iface of ifaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    return 'localhost';
}

function checkServerRunning() {
    return new Promise((resolve) => {
        const socket = net.createConnection({ port: ENGINE_PORT, host: '127.0.0.1' });
        socket.setTimeout(600);
        socket.on('connect', () => { socket.destroy(); resolve(true); });
        socket.on('error', () => resolve(false));
        socket.on('timeout', () => { socket.destroy(); resolve(false); });
    });
}

function stopServer() {
    return new Promise((resolve) => {
        exec(`lsof -ti:${ENGINE_PORT} | xargs kill -9`, (err) => resolve(!err));
    });
}

function startServer(workspaceRoot) {
    return new Promise((resolve, reject) => {
        const { spawn } = require('child_process');
        // shell:true ensures the full user PATH is available (Homebrew, pyenv, etc.)
        const proc = spawn('python3 tools/serve_engine.py', [], {
            cwd: workspaceRoot,
            detached: true,
            shell: true,
            stdio: 'ignore'
        });

        // If the process fails to launch at all, reject early
        proc.on('error', (err) => reject(new Error(`Could not launch python3: ${err.message}`)));

        proc.unref(); // let it outlive the extension host

        // Poll until port is open (max 8s)
        let attempts = 0;
        const poll = setInterval(async () => {
            attempts++;
            const up = await checkServerRunning();
            if (up) {
                clearInterval(poll);
                resolve();
            } else if (attempts >= 16) {
                clearInterval(poll);
                reject(new Error('Server did not start within 8 seconds'));
            }
        }, 500);
    });
}

// ---------------------------------------------------------------------------
// Webview HTML
// ---------------------------------------------------------------------------

function getWebviewContent(localIp) {
    const networkUrl = `http://${localIp}:${ENGINE_PORT}${ENGINE_PATH}`;

    return /* html */ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background: #0f0f0f;
            color: #e5e5e5;
            font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px 14px 24px;
            gap: 18px;
            min-height: 100vh;
        }

        /* ---- Header ---- */
        .header {
            text-align: center;
        }
        .logo {
            font-size: 1.4rem;
            font-weight: 900;
            letter-spacing: 0.15em;
            color: #3b82f6;
        }
        .subtitle {
            font-size: 0.7rem;
            color: #525252;
            margin-top: 2px;
            letter-spacing: 0.05em;
        }

        /* ---- Status badge ---- */
        .status-bar {
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 8px 12px;
        }
        .status-left {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            background: #3f3f3f;
            flex-shrink: 0;
            transition: background 0.3s;
        }
        .dot.running { background: #22c55e; box-shadow: 0 0 6px #22c55e88; }
        .dot.stopped { background: #ef4444; }
        .dot.checking { background: #f59e0b; animation: pulse 1s infinite; }
        @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

        .status-text {
            font-size: 0.72rem;
            font-weight: 600;
            color: #a3a3a3;
        }
        .status-text.running { color: #22c55e; }
        .status-text.stopped { color: #ef4444; }

        .stop-btn {
            font-size: 0.65rem;
            font-weight: 700;
            color: #ef4444;
            background: transparent;
            border: 1px solid #ef444440;
            border-radius: 5px;
            padding: 3px 8px;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s, color 0.2s;
            letter-spacing: 0.03em;
        }
        .stop-btn:hover { background: #ef444420; border-color: #ef4444; }
        .stop-btn:disabled { opacity: 0.3; cursor: default; }
        .stop-btn.is-start { color: #22c55e; border-color: #22c55e40; }
        .stop-btn.is-start:hover { background: #22c55e20; border-color: #22c55e; }

        /* ---- QR section ---- */
        .qr-section {
            width: 100%;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 10px;
            background: #141414;
            border: 1px solid #2a2a2a;
            border-radius: 10px;
            padding: 14px 10px;
            transition: opacity 0.3s;
        }
        .qr-section.hidden { display: none; }
        .qr-label {
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #525252;
            font-weight: 600;
        }
        #qr-canvas {
            border-radius: 6px;
            overflow: hidden;
            line-height: 0;
        }
        #qr-canvas img, #qr-canvas canvas { border-radius: 6px; display: block; }
        .network-url {
            font-size: 0.68rem;
            color: #00d4aa;
            word-break: break-all;
            text-align: center;
            letter-spacing: 0.02em;
        }

        /* ---- Open button ---- */
        hr { width: 100%; border: none; border-top: 1px solid #222; }

        .open-btn {
            width: 100%;
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 11px 14px;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: filter 0.2s, transform 0.1s;
            letter-spacing: 0.02em;
        }
        .open-btn:hover { filter: brightness(1.15); transform: translateY(-1px); }
        .open-btn:active { transform: translateY(0); }

        .hint {
            font-size: 0.64rem;
            color: #3f3f3f;
            text-align: center;
        }

        .footer {
            font-size: 0.62rem;
            color: #2a2a2a;
            text-align: center;
            line-height: 1.5;
        }

        /* ---- Firewall tip ---- */
        .firewall-tip {
            font-size: 0.6rem;
            color: #3f3f3f;
            text-align: center;
            line-height: 1.5;
            max-width: 90%;
        }
        .firewall-tip span { color: #525252; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">⚡ MADCORE</div>
        <div class="subtitle">RPG Game Engine Editor &nbsp;·&nbsp; v0.0.1</div>
    </div>

    <!-- Server status -->
    <div class="status-bar">
        <div class="status-left">
            <div class="dot checking" id="dot"></div>
            <span class="status-text checking" id="status-text">Checking...</span>
        </div>
        <button class="stop-btn" id="stop-btn" disabled>■ Stop</button>
    </div>

    <!-- QR code (shown when server is running) -->
    <div class="qr-section hidden" id="qr-section">
        <span class="qr-label">📱 Scan to open on phone</span>
        <div id="qr-canvas"></div>
        <span class="network-url" id="network-url">${networkUrl}</span>
        <p class="firewall-tip">Phone won't connect? Look for a macOS popup asking to allow <span>'python3'</span> to accept incoming connections and click <span>Allow</span>. If you missed it: System Settings → Network → Firewall.</p>
    </div>

    <hr>

    <button class="open-btn" id="open-btn">
        🎮 Open Editor View
    </button>
    <div class="hint">or press ⌘⇧G</div>

    <div class="footer">
        After opening, drag the Simple Browser<br>tab to the right editor group for split-screen.
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        let currentNetworkUrl = ${JSON.stringify(networkUrl)};
        let serverRunning = false;

        // Build / rebuild QR code
        function buildQr(url) {
            const el = document.getElementById('qr-canvas');
            el.innerHTML = '';
            new QRCode(el, {
                text: url,
                width: 160,
                height: 160,
                colorDark: '#00d4aa',
                colorLight: '#1a1a1a',
                correctLevel: QRCode.CorrectLevel.M
            });
            document.getElementById('network-url').textContent = url;
        }

        function updateStatus(running, newNetworkUrl) {
            serverRunning = running;
            const dot = document.getElementById('dot');
            const txt = document.getElementById('status-text');
            const qrSection = document.getElementById('qr-section');
            const stopBtn = document.getElementById('stop-btn');

            dot.className = 'dot ' + (running ? 'running' : 'stopped');
            txt.className = 'status-text ' + (running ? 'running' : 'stopped');
            txt.textContent = running ? 'Server running' : 'Server stopped';

            // Toggle Start / Stop button
            stopBtn.disabled = false;
            if (running) {
                stopBtn.textContent = '\u25a0 Stop';
                stopBtn.classList.remove('is-start');
            } else {
                stopBtn.textContent = '\u25b6 Start';
                stopBtn.classList.add('is-start');
            }

            if (running) {
                // Rebuild QR if URL changed
                if (newNetworkUrl && newNetworkUrl !== currentNetworkUrl) {
                    currentNetworkUrl = newNetworkUrl;
                    buildQr(currentNetworkUrl);
                } else if (qrSection.classList.contains('hidden')) {
                    buildQr(currentNetworkUrl);
                }
                qrSection.classList.remove('hidden');
            } else {
                qrSection.classList.add('hidden');
            }
        }

        // Messages from extension
        window.addEventListener('message', event => {
            const msg = event.data;
            if (msg.type === 'statusUpdate') {
                updateStatus(msg.running, msg.networkUrl);
            }
        });

        // Open editor
        document.getElementById('open-btn').addEventListener('click', () => {
            vscode.postMessage({ command: 'launch' });
        });

        // Start / Stop toggle
        document.getElementById('stop-btn').addEventListener('click', () => {
            const btn = document.getElementById('stop-btn');
            btn.disabled = true;
            document.getElementById('dot').className = 'dot checking';
            if (serverRunning) {
                vscode.postMessage({ command: 'stopServer' });
            } else {
                vscode.postMessage({ command: 'startServer' });
            }
        });
    </script>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Extension entry points
// ---------------------------------------------------------------------------

function activate(context) {
    const localIp = getLocalIp();

    // Command: launch editor view (auto-starts server if needed)
    const launchCmd = vscode.commands.registerCommand('madcore.launchEditor', async () => {
        const isUp = await checkServerRunning();

        if (!isUp) {
            const folders = vscode.workspace.workspaceFolders;
            if (!folders || folders.length === 0) {
                vscode.window.showErrorMessage('[MadCore] No workspace folder found — cannot start server.');
                return;
            }
            const workspaceRoot = folders[0].uri.fsPath;

            await vscode.window.withProgress({
                location: vscode.ProgressLocation.Notification,
                title: '⚡ MadCore',
                cancellable: false
            }, async (progress) => {
                progress.report({ message: 'Starting engine server…' });
                try {
                    await startServer(workspaceRoot);
                    progress.report({ message: 'Server ready!' });
                } catch (err) {
                    vscode.window.showErrorMessage(`[MadCore] Could not start server: ${err.message}`);
                    return;
                }
            });
        }

        try {
            await vscode.commands.executeCommand('simpleBrowser.show', LOCALHOST_URL);
        } catch (err) {
            vscode.window.showErrorMessage(`[MadCore] Could not open Simple Browser: ${err.message}`);
        }
    });
    context.subscriptions.push(launchCmd);

    // Sidebar panel
    let currentView = null;
    let pollTimer = null;

    let lastKnownIp = localIp;

    async function sendStatus() {
        if (!currentView) return;

        // Detect network change
        const currentIp = getLocalIp();
        let networkUrl;
        if (currentIp !== lastKnownIp) {
            lastKnownIp = currentIp;
            networkUrl = `http://${currentIp}:${ENGINE_PORT}${ENGINE_PATH}`;

            // If server is running, restart it for the new interface
            const wasRunning = await checkServerRunning();
            if (wasRunning) {
                await stopServer();
                const folders = vscode.workspace.workspaceFolders;
                if (folders && folders.length > 0) {
                    try { await startServer(folders[0].uri.fsPath); } catch (_) {}
                }
            }
        }

        const running = await checkServerRunning();
        currentView.webview.postMessage({
            type: 'statusUpdate',
            running,
            ...(networkUrl ? { networkUrl } : {})
        });
    }

    const provider = {
        resolveWebviewView(webviewView) {
            currentView = webviewView;
            webviewView.webview.options = {
                enableScripts: true,
                localResourceRoots: []
            };
            webviewView.webview.html = getWebviewContent(localIp);

            // Initial probe + recurring poll every 3s
            sendStatus();
            pollTimer = setInterval(sendStatus, 3000);

            webviewView.onDidDispose(() => {
                currentView = null;
                if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
            });

            webviewView.webview.onDidReceiveMessage(async (msg) => {
                if (msg.command === 'launch') {
                    vscode.commands.executeCommand('madcore.launchEditor');
                } else if (msg.command === 'stopServer') {
                    const ok = await stopServer();
                    if (ok) vscode.window.showInformationMessage('[MadCore] Engine server stopped.');
                    setTimeout(sendStatus, 400);
                } else if (msg.command === 'startServer') {
                    const folders = vscode.workspace.workspaceFolders;
                    if (!folders || folders.length === 0) {
                        vscode.window.showErrorMessage('[MadCore] No workspace folder found.');
                        return;
                    }
                    try {
                        await startServer(folders[0].uri.fsPath);
                        vscode.window.showInformationMessage('[MadCore] Engine server started.');
                    } catch (err) {
                        vscode.window.showErrorMessage(`[MadCore] Failed to start: ${err.message}`);
                    }
                    setTimeout(sendStatus, 400);
                }
            });
        }
    };

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('madcore.engineView', provider, {
            webviewOptions: { retainContextWhenHidden: true }
        })
    );
}

function deactivate() {}

module.exports = { activate, deactivate };

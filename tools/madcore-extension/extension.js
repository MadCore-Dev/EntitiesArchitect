const vscode = require('vscode');
const os = require('os');
const net = require('net');
const http = require('http');
const path = require('path');
const fs = require('fs');

// ---------------------------------------------------------------------------
// State Management
// ---------------------------------------------------------------------------

const servers = new Map(); // Map<string, { server: http.Server, port: number }>

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

function getAvailablePort() {
    return new Promise((resolve) => {
        const srv = net.createServer();
        srv.listen(0, () => {
            const port = srv.address().port;
            srv.close(() => resolve(port));
        });
    });
}

function startNodeServer(filePath) {
    return new Promise(async (resolve, reject) => {
        const port = await getAvailablePort();
        const rootDir = path.dirname(filePath);
        const fileName = path.basename(filePath);

        const server = http.createServer((req, res) => {
            // Very simple file server for development
            let reqPath = req.url === '/' ? fileName : req.url;
            // Remove query strings
            reqPath = reqPath.split('?')[0];
            const fullPath = path.join(rootDir, reqPath);

            fs.readFile(fullPath, (err, data) => {
                if (err) {
                    res.writeHead(404);
                    res.end('File not found');
                    return;
                }
                const ext = path.extname(fullPath).toLowerCase();
                const mimeTypes = {
                    '.html': 'text/html',
                    '.js': 'text/javascript',
                    '.css': 'text/css',
                    '.json': 'application/json',
                    '.png': 'image/png',
                    '.jpg': 'image/jpg',
                    '.gif': 'image/gif',
                    '.svg': 'image/svg+xml',
                    '.wav': 'audio/wav',
                    '.mp4': 'video/mp4',
                    '.woff': 'application/font-woff',
                    '.ttf': 'application/font-ttf'
                };
                res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
                res.end(data);
            });
        });

        server.listen(port, '0.0.0.0', () => {
            servers.set(filePath, { server, port });
            resolve(port);
        });

        server.on('error', (err) => {
            reject(err);
        });
    });
}

function stopNodeServer(filePath) {
    const entry = servers.get(filePath);
    if (entry) {
        entry.server.close();
        servers.delete(filePath);
    }
}

async function getProjectConfig(workspaceRoot) {
    const configPath = path.join(workspaceRoot, '.madcore-server.json');
    if (fs.existsSync(configPath)) {
        try {
            const content = fs.readFileSync(configPath, 'utf8');
            return JSON.parse(content);
        } catch (e) {
            console.error('Error parsing config:', e);
        }
    }
    const config = vscode.workspace.getConfiguration('madcore');
    return {
        title: config.get('defaultTitle') || 'Dev Server',
        themeColor: config.get('defaultThemeColor') || '#3b82f6'
    };
}

// ---------------------------------------------------------------------------
// Webview HTML
// ---------------------------------------------------------------------------

function getWebviewContent(localIp, config) {
    return /* html */ `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        :root { --brand: ${config.themeColor || '#3b82f6'}; }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #0f0f0f;
            color: #d4d4d4;
            font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
            padding: 20px 12px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .header { text-align: center; }
        .logo { font-size: 1.2rem; font-weight: 900; letter-spacing: 0.1em; color: var(--brand); text-transform: uppercase; }
        .subtitle { font-size: 0.7rem; color: #525252; margin-top: 4px; }
        
        .server-list { display: flex; flex-direction: column; gap: 12px; }
        .server-card {
            background: #1a1a1a;
            border: 1px solid #2a2a2a;
            border-radius: 8px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .card-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 10px; }
        .file-info { display: flex; flex-direction: column; flex: 1; min-width: 0; }
        .file-name { font-size: 0.85rem; font-weight: 600; color: #e5e5e5; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
        .file-path { font-size: 0.65rem; color: #525252; overflow: hidden; text-overflow: ellipsis; }
        
        .status-badge {
            font-size: 0.65rem;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }
        .status-badge.off { background: #262626; color: #737373; }
        .status-badge.on { background: #064e3b; color: #34d399; }
        
        .card-actions { display: flex; gap: 8px; margin-top: 4px; }
        button {
            background: #262626;
            color: #d4d4d4;
            border: 1px solid #404040;
            border-radius: 6px;
            padding: 6px 10px;
            font-size: 0.72rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s;
        }
        button:hover { background: #404040; border-color: #525252; }
        button.primary { background: var(--brand); border-color: transparent; color: white; }
        button.primary:hover { filter: brightness(1.1); }
        button.stop { color: #f87171; border-color: #ef444440; }
        button.stop:hover { background: #451a1a; border-color: #ef4444; }

        .qr-section {
            background: #121212;
            border: 1px dashed #333;
            border-radius: 6px;
            padding: 12px;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        .qr-section.hidden { display: none; }
        .network-url { font-size: 0.65rem; color: #00d4aa; text-align: center; word-break: break-all; }
        
        .empty-state { text-align: center; color: #525252; font-size: 0.8rem; margin-top: 40px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">${config.title || 'Dev Server'}</div>
        <div class="subtitle">${config.subtitle || 'Workspace Utility'}</div>
    </div>

    <div id="server-list" class="server-list">
        <!-- Servers populated here -->
    </div>

    <div id="empty-state" class="empty-state hidden">
        No HTML files found in workspace.<br>Create an index.html to get started.
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const localIp = '${localIp}';
        let serverStates = {};

        function updateUI(files) {
            const list = document.getElementById('server-list');
            const empty = document.getElementById('empty-state');
            list.innerHTML = '';
            
            if (files.length === 0) {
                empty.classList.remove('hidden');
                return;
            }
            empty.classList.add('hidden');

            files.forEach(file => {
                const state = serverStates[file.path] || { running: false, port: 0, qr: false };
                const card = document.createElement('div');
                card.className = 'server-card';
                
                const relativePath = file.path.split('/').pop();
                const networkUrl = state.running ? "http://" + localIp + ":" + state.port + "/" + relativePath : "";

                card.innerHTML = \`
                    <div class="card-top">
                        <div class="file-info">
                            <span class="file-name">\${relativePath}</span>
                            <span class="file-path">\${file.path}</span>
                        </div>
                        <span class="status-badge \${state.running ? 'on' : 'off'}">\${state.running ? 'Online' : 'Offline'}</span>
                    </div>
                    <div class="card-actions">
                        \${!state.running 
                            ? '<button class="primary" onclick="startServer(\\''+file.path+'\\')">▶ Start</button>'
                            : '<button class="stop" onclick="stopServer(\\''+file.path+'\\')">■ Stop</button>'
                        }
                        \${state.running ? '<button onclick="openLink(\\''+networkUrl+'\\')">🌐 Open</button>' : ''}
                        \${state.running ? '<button onclick="toggleQR(\\''+file.path+'\\')">📱 QR</button>' : ''}
                    </div>
                    <div id="qr-\${btoa(file.path)}" class="qr-section \${state.qr ? '' : 'hidden'}">
                        <div class="qr-container" id="canvas-\${btoa(file.path)}"></div>
                        <span class="network-url">\${networkUrl}</span>
                    </div>
                \`;
                list.appendChild(card);
                
                if (state.qr && state.running) {
                    setTimeout(() => {
                        const container = document.getElementById("canvas-" + btoa(file.path));
                        container.innerHTML = '';
                        new QRCode(container, {
                            text: networkUrl,
                            width: 140,
                            height: 140,
                            colorDark: '#00d4aa',
                            colorLight: '#121212',
                            correctLevel: QRCode.CorrectLevel.M
                        });
                    }, 0);
                }
            });
        }

        window.addEventListener('message', event => {
            const msg = event.data;
            if (msg.type === 'stateUpdate') {
                serverStates = msg.states;
                updateUI(msg.files);
            }
        });

        function startServer(path) { vscode.postMessage({ command: 'start', path }); }
        function stopServer(path) { vscode.postMessage({ command: 'stop', path }); }
        function toggleQR(path) { vscode.postMessage({ command: 'toggleQR', path }); }
        function openLink(url) { vscode.postMessage({ command: 'open', url }); }

        // Initial scan request
        vscode.postMessage({ command: 'refresh' });
    </script>
</body>
</html>`;
}

// ---------------------------------------------------------------------------
// Extension Activation
// ---------------------------------------------------------------------------

function activate(context) {
    const localIp = getLocalIp();
    let detectedFiles = [];
    let serverStates = {}; // Map of path -> { running, port, qrEnabled }

    async function refreshWorkspace() {
        const uris = await vscode.workspace.findFiles('**/*.html', '**/node_modules/**');
        detectedFiles = uris.map(u => ({ path: u.fsPath }));
        sendState();
    }

    function sendState() {
        // Build state object for the webview
        const states = {};
        detectedFiles.forEach(f => {
            const entry = servers.get(f.path);
            states[f.path] = {
                running: !!entry,
                port: entry ? entry.port : 0,
                qr: !!serverStates[f.path]?.qrEnabled
            };
        });
        
        if (activeWebview) {
            activeWebview.webview.postMessage({
                type: 'stateUpdate',
                files: detectedFiles,
                states
            });
        }
    }

    let activeWebview = null;

    const provider = {
        async resolveWebviewView(webviewView) {
            activeWebview = webviewView;
            
            const folders = vscode.workspace.workspaceFolders;
            const config = folders ? await getProjectConfig(folders[0].uri.fsPath) : {};

            webviewView.webview.options = { enableScripts: true };
            webviewView.webview.html = getWebviewContent(localIp, config);

            webviewView.webview.onDidReceiveMessage(async (msg) => {
                switch (msg.command) {
                    case 'refresh':
                        await refreshWorkspace();
                        break;
                    case 'start':
                        try {
                            await startNodeServer(msg.path);
                            if (!serverStates[msg.path]) serverStates[msg.path] = {};
                            serverStates[msg.path].running = true;
                            sendState();
                        } catch (e) {
                            vscode.window.showErrorMessage(`Failed to start server: ${e.message}`);
                        }
                        break;
                    case 'stop':
                        stopNodeServer(msg.path);
                        if (serverStates[msg.path]) serverStates[msg.path].running = false;
                        sendState();
                        break;
                    case 'toggleQR':
                        if (!serverStates[msg.path]) serverStates[msg.path] = {};
                        serverStates[msg.path].qrEnabled = !serverStates[msg.path].qrEnabled;
                        sendState();
                        break;
                    case 'open':
                        vscode.commands.executeCommand('simpleBrowser.show', msg.url);
                        break;
                }
            });

            webviewView.onDidDispose(() => {
                activeWebview = null;
            });
        }
    };

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider('madcore.serverView', provider, {
            webviewOptions: { retainContextWhenHidden: true }
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('madcore.launchServer', () => {
             vscode.commands.executeCommand('workbench.view.extension.madcore-dev-server');
        })
    );

    // Watch for file changes
    const watcher = vscode.workspace.createFileSystemWatcher('**/*.html');
    watcher.onDidCreate(() => refreshWorkspace());
    watcher.onDidDelete(() => refreshWorkspace());
    context.subscriptions.push(watcher);
}

function deactivate() {
    for (const [path, entry] of servers) {
        entry.server.close();
    }
}

module.exports = { activate, deactivate };

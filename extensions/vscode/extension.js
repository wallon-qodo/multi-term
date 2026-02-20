// VSCode extension for Claude Multi-Terminal integration
const vscode = require('vscode');
const WebSocket = require('ws');
const path = require('path');

let ws = null;
let wss = null;
let statusBarItem = null;
let outputChannel = null;

/**
 * Extension activation
 */
function activate(context) {
    console.log('Claude Multi-Terminal extension is now active');

    // Create output channel
    outputChannel = vscode.window.createOutputChannel('Claude Multi-Terminal');

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.text = '$(circle-slash) Claude: Disconnected';
    statusBarItem.tooltip = 'Claude Multi-Terminal Integration';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('claude-multi-terminal.openFile', openFile)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('claude-multi-terminal.applyChanges', applyChanges)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('claude-multi-terminal.syncContext', syncContext)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('claude-multi-terminal.jumpToLine', jumpToLine)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('claude-multi-terminal.startServer', startServer)
    );
    context.subscriptions.push(
        vscode.commands.registerCommand('claude-multi-terminal.stopServer', stopServer)
    );

    // Auto-start server if configured
    const config = vscode.workspace.getConfiguration('claude-multi-terminal');
    if (config.get('autoStartServer')) {
        startServer();
    }

    // Watch for file changes
    if (config.get('autoSync')) {
        setupFileWatcher(context);
    }

    log('Extension activated');
}

/**
 * Extension deactivation
 */
function deactivate() {
    stopServer();
    if (outputChannel) {
        outputChannel.dispose();
    }
}

/**
 * Start WebSocket server for bidirectional communication
 */
function startServer() {
    const config = vscode.workspace.getConfiguration('claude-multi-terminal');
    const port = config.get('serverPort', 8765);

    if (wss) {
        vscode.window.showWarningMessage('Integration server already running');
        return;
    }

    try {
        wss = new WebSocket.Server({ port });

        wss.on('connection', (socket) => {
            ws = socket;
            log('Claude Multi-Terminal connected');
            updateStatusBar(true);

            socket.on('message', (data) => {
                handleMessage(JSON.parse(data.toString()));
            });

            socket.on('close', () => {
                ws = null;
                log('Claude Multi-Terminal disconnected');
                updateStatusBar(false);
            });

            socket.on('error', (error) => {
                log(`WebSocket error: ${error.message}`);
            });

            // Send welcome message
            sendMessage({ type: 'connected', version: '0.1.0' });
        });

        wss.on('error', (error) => {
            log(`Server error: ${error.message}`);
            vscode.window.showErrorMessage(`Failed to start server: ${error.message}`);
            wss = null;
        });

        log(`Integration server started on port ${port}`);
        vscode.window.showInformationMessage(`Claude integration server started on port ${port}`);
    } catch (error) {
        log(`Failed to start server: ${error.message}`);
        vscode.window.showErrorMessage(`Failed to start server: ${error.message}`);
    }
}

/**
 * Stop WebSocket server
 */
function stopServer() {
    if (wss) {
        wss.close();
        wss = null;
        ws = null;
        updateStatusBar(false);
        log('Integration server stopped');
        vscode.window.showInformationMessage('Claude integration server stopped');
    }
}

/**
 * Handle incoming messages from Claude Multi-Terminal
 */
async function handleMessage(message) {
    log(`Received message: ${message.type}`);

    try {
        switch (message.type) {
            case 'openFile':
                await handleOpenFile(message);
                break;
            case 'applyChanges':
                await handleApplyChanges(message);
                break;
            case 'jumpToLine':
                await handleJumpToLine(message);
                break;
            case 'getContext':
                await handleGetContext(message);
                break;
            case 'ping':
                sendMessage({ type: 'pong', timestamp: Date.now() });
                break;
            default:
                log(`Unknown message type: ${message.type}`);
        }
    } catch (error) {
        log(`Error handling message: ${error.message}`);
        sendMessage({ type: 'error', error: error.message, messageId: message.id });
    }
}

/**
 * Handle openFile message
 */
async function handleOpenFile(message) {
    const { filePath, line, column } = message;

    try {
        const uri = vscode.Uri.file(filePath);
        const document = await vscode.workspace.openTextDocument(uri);
        const editor = await vscode.window.showTextDocument(document);

        if (line !== undefined) {
            const position = new vscode.Position(line - 1, column || 0);
            editor.selection = new vscode.Selection(position, position);
            editor.revealRange(new vscode.Range(position, position), vscode.TextEditorRevealType.InCenter);
        }

        sendMessage({
            type: 'fileOpened',
            filePath,
            success: true,
            messageId: message.id
        });

        log(`Opened file: ${filePath}${line ? ` at line ${line}` : ''}`);
    } catch (error) {
        sendMessage({
            type: 'fileOpened',
            filePath,
            success: false,
            error: error.message,
            messageId: message.id
        });
        log(`Failed to open file: ${error.message}`);
    }
}

/**
 * Handle applyChanges message
 */
async function handleApplyChanges(message) {
    const { filePath, changes, description } = message;

    try {
        const uri = vscode.Uri.file(filePath);
        const document = await vscode.workspace.openTextDocument(uri);
        const editor = await vscode.window.showTextDocument(document);

        const edit = new vscode.WorkspaceEdit();

        // Apply each change
        for (const change of changes) {
            const startPos = new vscode.Position(change.startLine - 1, change.startColumn || 0);
            const endPos = new vscode.Position(change.endLine - 1, change.endColumn || 0);
            const range = new vscode.Range(startPos, endPos);

            edit.replace(uri, range, change.newText);
        }

        const success = await vscode.workspace.applyEdit(edit);

        if (success) {
            // Highlight changes if configured
            const config = vscode.workspace.getConfiguration('claude-multi-terminal');
            if (config.get('highlightChanges')) {
                highlightChanges(editor, changes);
            }

            // Save document
            await document.save();

            sendMessage({
                type: 'changesApplied',
                filePath,
                success: true,
                changesCount: changes.length,
                messageId: message.id
            });

            vscode.window.showInformationMessage(
                `Applied ${changes.length} change(s) to ${path.basename(filePath)}`
            );
            log(`Applied changes to: ${filePath}`);
        } else {
            throw new Error('Failed to apply edit');
        }
    } catch (error) {
        sendMessage({
            type: 'changesApplied',
            filePath,
            success: false,
            error: error.message,
            messageId: message.id
        });
        log(`Failed to apply changes: ${error.message}`);
    }
}

/**
 * Handle jumpToLine message
 */
async function handleJumpToLine(message) {
    const { filePath, line, column } = message;

    try {
        const uri = vscode.Uri.file(filePath);
        const document = await vscode.workspace.openTextDocument(uri);
        const editor = await vscode.window.showTextDocument(document);

        const position = new vscode.Position(line - 1, column - 1 || 0);
        editor.selection = new vscode.Selection(position, position);
        editor.revealRange(
            new vscode.Range(position, position),
            vscode.TextEditorRevealType.InCenter
        );

        sendMessage({
            type: 'jumpedToLine',
            filePath,
            line,
            success: true,
            messageId: message.id
        });

        log(`Jumped to ${filePath}:${line}`);
    } catch (error) {
        sendMessage({
            type: 'jumpedToLine',
            filePath,
            line,
            success: false,
            error: error.message,
            messageId: message.id
        });
        log(`Failed to jump to line: ${error.message}`);
    }
}

/**
 * Handle getContext message
 */
async function handleGetContext(message) {
    try {
        const editor = vscode.window.activeTextEditor;
        const context = {
            activeFile: editor?.document.fileName,
            workspaceRoot: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
            openFiles: vscode.workspace.textDocuments.map(doc => doc.fileName),
            selection: null
        };

        if (editor) {
            const selection = editor.selection;
            context.selection = {
                start: { line: selection.start.line + 1, column: selection.start.character },
                end: { line: selection.end.line + 1, column: selection.end.character },
                text: editor.document.getText(selection)
            };
        }

        sendMessage({
            type: 'context',
            context,
            messageId: message.id
        });

        log('Sent context to Claude');
    } catch (error) {
        sendMessage({
            type: 'context',
            context: null,
            error: error.message,
            messageId: message.id
        });
        log(`Failed to get context: ${error.message}`);
    }
}

/**
 * Command: Open file from conversation
 */
async function openFile() {
    const input = await vscode.window.showInputBox({
        prompt: 'Enter file path',
        placeHolder: '/path/to/file.py:123'
    });

    if (!input) return;

    const parts = input.split(':');
    const filePath = parts[0];
    const line = parts[1] ? parseInt(parts[1]) : undefined;

    await handleOpenFile({ filePath, line });
}

/**
 * Command: Apply changes to file
 */
async function applyChanges() {
    vscode.window.showInformationMessage('Apply changes from Claude Multi-Terminal');
    // This is typically triggered from Claude Multi-Terminal, not manually
}

/**
 * Command: Sync context to Claude
 */
async function syncContext() {
    if (!ws) {
        vscode.window.showWarningMessage('Not connected to Claude Multi-Terminal');
        return;
    }

    await handleGetContext({ type: 'getContext', id: Date.now() });
    vscode.window.showInformationMessage('Context synced to Claude Multi-Terminal');
}

/**
 * Command: Jump to line
 */
async function jumpToLine() {
    const input = await vscode.window.showInputBox({
        prompt: 'Enter file path and line number',
        placeHolder: '/path/to/file.py:123'
    });

    if (!input) return;

    const parts = input.split(':');
    const filePath = parts[0];
    const line = parts[1] ? parseInt(parts[1]) : 1;

    await handleJumpToLine({ filePath, line });
}

/**
 * Setup file watcher for auto-sync
 */
function setupFileWatcher(context) {
    const watcher = vscode.workspace.createFileSystemWatcher('**/*');

    watcher.onDidChange((uri) => {
        if (ws) {
            sendMessage({
                type: 'fileChanged',
                filePath: uri.fsPath,
                timestamp: Date.now()
            });
        }
    });

    watcher.onDidCreate((uri) => {
        if (ws) {
            sendMessage({
                type: 'fileCreated',
                filePath: uri.fsPath,
                timestamp: Date.now()
            });
        }
    });

    watcher.onDidDelete((uri) => {
        if (ws) {
            sendMessage({
                type: 'fileDeleted',
                filePath: uri.fsPath,
                timestamp: Date.now()
            });
        }
    });

    context.subscriptions.push(watcher);
}

/**
 * Highlight applied changes in editor
 */
function highlightChanges(editor, changes) {
    const decorationType = vscode.window.createTextEditorDecorationType({
        backgroundColor: 'rgba(100, 200, 100, 0.3)',
        border: '1px solid rgba(100, 200, 100, 0.8)'
    });

    const ranges = changes.map(change => {
        const startPos = new vscode.Position(change.startLine - 1, change.startColumn || 0);
        const endPos = new vscode.Position(change.endLine - 1, change.endColumn || Number.MAX_SAFE_INTEGER);
        return new vscode.Range(startPos, endPos);
    });

    editor.setDecorations(decorationType, ranges);

    // Clear highlight after 3 seconds
    setTimeout(() => {
        decorationType.dispose();
    }, 3000);
}

/**
 * Send message to Claude Multi-Terminal
 */
function sendMessage(message) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(message));
    }
}

/**
 * Update status bar
 */
function updateStatusBar(connected) {
    if (connected) {
        statusBarItem.text = '$(check) Claude: Connected';
        statusBarItem.backgroundColor = undefined;
    } else {
        statusBarItem.text = '$(circle-slash) Claude: Disconnected';
        statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
    }
}

/**
 * Log message to output channel
 */
function log(message) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] ${message}`;
    console.log(logMessage);
    if (outputChannel) {
        outputChannel.appendLine(logMessage);
    }
}

module.exports = {
    activate,
    deactivate
};

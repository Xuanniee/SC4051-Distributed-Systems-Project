const { CLIENT_BUFFER_SIZE, DEFAULT_TIMEOUT_MS, DEFAULT_RETRIES } = require('./constants');
const { STATUS_CODE } = require('./constants');
const { BufferReader } = require('../protocols/marshaller');

const serverHost = process.env.SERVER_HOST || '127.0.0.1';
const serverPort = process.env.SERVER_PORT || 2222;

function isNormalResponse(msg) {
    try {
        const reader = new BufferReader(msg);
        const statusCode = reader.readU8();
        if (!Object.values(STATUS_CODE).includes(statusCode)) {
            return false;
        }

        reader.readString();
        return true;
    } catch {
        return false;
    }
}

function socketSend(socket, packet, timeoutMs) {
    return new Promise((resolve, reject) => {
        let settled = false; // Checks if this request has already been completed

        const onMessage = (msg) => {
            if (settled) {
                return;
            }

            if (msg.length > CLIENT_BUFFER_SIZE) {
                settled = true;
                cleanup();
                reject(new Error(`Message exceeds buffer size: ${msg.length} > ${CLIENT_BUFFER_SIZE}`));
                return;
            }

            // This function intercepts both normal responses and monitor callbacks, so we ignore callbacks here
            if (!isNormalResponse(msg)) {
                return;
            }

            settled = true;
            cleanup();
            resolve(msg);
        };

        const cleanup = () => {
            socket.off('message', onMessage);
            clearTimeout(timer);
        };

        const timer = setTimeout(() => {
            if (settled) {
                return;
            }
            settled = true;
            cleanup();
            reject(new Error('Request timeout'));
        }, timeoutMs);

        socket.once('message', onMessage);

        socket.send(packet, serverPort, serverHost, (err) => {
            if (err) {
                if (settled) {
                    return;
                }
                settled = true;
                cleanup();
                reject(err);
            }
        });
    });
}

module.exports = async function sendWithRetries(socket, packet, {
    timeoutMs = DEFAULT_TIMEOUT_MS,
    maxRetries = DEFAULT_RETRIES,
} = {}) {
    let lastError;
    let currentTimeoutMs = timeoutMs;

    for (let attempt = 0; attempt < maxRetries + 1; attempt++) {
        try {
            if (attempt > 0) {
                console.log(`Retry attempt ${attempt}`);
            }
            return await socketSend(socket, packet, currentTimeoutMs);
        } catch (err) {
            lastError = err;

            if (!String(err.message).includes('Request timeout')) {
                throw err;
            }

            if (attempt < maxRetries) {
                console.error(`Request timeout (${currentTimeoutMs}ms). Will retry...`);
            }

            currentTimeoutMs = Math.min(currentTimeoutMs * 2, 30000);
        }
    }

    throw new Error(`Failed after ${maxRetries + 1} attempts: ${lastError.message}`);
}
const { CLIENT_BUFFER_SIZE } = require('./constants');
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

module.exports = function socketSend(socket, packet, timeoutMs = 5000) {
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

        socket.on('message', onMessage);

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
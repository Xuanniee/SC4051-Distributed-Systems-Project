const { CLIENT_BUFFER_SIZE } = require('./constants');

module.exports = function socketSend(socket, packet, timeoutMs = 5000) {
    const serverHost = process.env.SERVER_HOST || '127.0.0.1';
    const serverPort = process.env.SERVER_PORT || 2222;

    return new Promise((resolve, reject) => {
        const timer = setTimeout(() => {
            reject(new Error('Request timeout'));
        }, timeoutMs);

        socket.once('message', (msg) => {
            if (msg.length > CLIENT_BUFFER_SIZE) {
                reject(new Error(`Message exceeds buffer size: ${msg.length} > ${CLIENT_BUFFER_SIZE}`));
                return;
            }
            clearTimeout(timer);
            try {
                resolve(msg);
            } catch (err) {
                reject(err);
            }
        });

        socket.send(packet, serverPort, serverHost, (err) => {
            if (err) {
                clearTimeout(timer);
                reject(err);
            }
        });
    });
}
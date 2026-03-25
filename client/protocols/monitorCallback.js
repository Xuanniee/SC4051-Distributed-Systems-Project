const { decodeCallbackResponse } = require('./codecs');

module.exports = function monitorCallback(socket) {
    socket.on('message', (msg) => {
        try {
            const update = decodeCallbackResponse(msg);
            if (!update || !update.eventName) {
                return;
            }

            console.log(`\n[MONITOR CALLBACK] ${update.eventName}\n`, update);
        } catch (err) {
            // console.error('Failed to decode monitor callback message:', err);
        }
    });
}
const { decodeStandardResponse, encodeMonitorRequest } = require('../protocols/codecs');
const { buildPacket, sendWithRetries } = require('../helpers');
const { OP_CODE } = require('../helpers/constants');

module.exports = async function monitor({ socket, clientId, requestId, timeoutMs, maxRetries }, durationSecs = 300) {
    if (durationSecs <= 0) {
        throw new Error('Monitoring duration must be a positive integer');
    }

    const bodyBuffer = encodeMonitorRequest(durationSecs);
    const packet = buildPacket(OP_CODE.MONITOR_REGISTER, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeStandardResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send monitor request:', err);
    }
}
const { decodeStandardResponse, encodeMonitorRequest } = require('../protocols/codecs');
const { buildPacket, socketSend } = require('../helpers');
const { OP_CODE } = require('../helpers/constants');

module.exports = async function monitor({ socket, clientId, requestId }, durationSecs = 300) {
    if (durationSecs <= 0) {
        throw new Error('Monitoring duration must be a positive integer');
    }

    const bodyBuffer = encodeMonitorRequest(durationSecs);
    const packet = buildPacket(OP_CODE.MONITOR_REGISTER, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await socketSend(socket, packet);
        return decodeStandardResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send monitor request:', err);
    }
}
const { OP_CODE } = require('../helpers/constants.js');
const { buildPacket, sendWithRetries } = require('../helpers');
const { encodeBalanceInquiryRequest, decodeBalanceInquiryResponse } = require('../protocols/codecs.js');

module.exports = async function balanceInquiry({ socket, clientId, requestId, timeoutMs, maxRetries },
    { name, accountNo, password }) {
    if (!accountNo || accountNo < 1000 || !name || !password || password.length !== 8) {
        throw new Error('Invalid account details');
    }

    const bodyBuffer = encodeBalanceInquiryRequest({ name, password, accountNo });
    const packet = buildPacket(OP_CODE.BALANCE_INQUIRY, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeBalanceInquiryResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send balance inquiry request', err);
    }
}
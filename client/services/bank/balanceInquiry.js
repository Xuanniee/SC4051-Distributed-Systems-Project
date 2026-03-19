const { OP_CODE } = require('../../helpers/constants.js');
const { buildPacket, socketSend } = require('../../helpers');
const { encodeBalanceInquiryRequest, decodeBalanceInquiryResponse } = require('../../protocols/codecs.js');

module.exports = async function balanceInquiry({ socket, clientId, requestId },
    { name, accountNo, password }) {
    const bodyBuffer = encodeBalanceInquiryRequest({ name, password, accountNo });
    const packet = buildPacket(OP_CODE.BALANCE_INQUIRY, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await socketSend(socket, packet);
        const reply = decodeBalanceInquiryResponse(encodedReply);
        console.log("\nResponse:", reply);
    } catch (err) {
        console.error('Failed to send balance inquiry request:', err);
    }
}
const { encodeCloseAccountRequest, decodeStandardResponse } = require("../protocols/codecs");
const { OP_CODE } = require("../helpers/constants");
const { buildPacket, sendWithRetries } = require("../helpers");

module.exports = async function closeAccount({ socket, clientId, requestId, timeoutMs, maxRetries },
    { name, password, accountNo }) {
    if (isNaN(accountNo)) {
        throw new Error('Account number must be a valid number');
    }
    accountNo = parseInt(accountNo) || -1;

    if (!accountNo || accountNo < 1000 || !name || !password || password.length !== 8) {
        throw new Error('Invalid account details');
    }

    const bodyBuffer = encodeCloseAccountRequest({ name, password, accountNo });
    const packet = buildPacket(OP_CODE.CLOSE_ACCOUNT, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeStandardResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send close account request', err);
    }
}
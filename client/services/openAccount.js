const { buildPacket, sendWithRetries } = require("../helpers");
const { OP_CODE, CURRENCY } = require("../helpers/constants");
const { encodeOpenAccountRequest, decodeOpenAccountResponse } = require("../protocols/codecs");

async function openAccount({ socket, clientId, requestId, timeoutMs, maxRetries },
    { name, password, initialBalance = 0, currency = 1 }) {
    if (!name || !password || password.length !== 8) {
        throw new Error('Please enter a name and password with exactly 8 characters');
    }

    if (currency < 1 || currency > Object.keys(CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (initialBalance < 0) {
        throw new Error('Initial balance cannot be negative');
    }

    const bodyBuffer = encodeOpenAccountRequest({ name, password, initialBalance, currency });
    const packet = buildPacket(OP_CODE.OPEN_ACCOUNT, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeOpenAccountResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send open account request:', err);
    }
}

module.exports = openAccount;
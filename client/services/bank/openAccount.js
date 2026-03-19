const { buildPacket, socketSend } = require("../../helpers");
const { OP_CODE, CURRENCY } = require("../../helpers/constants");
const { encodeOpenAccountRequest, decodeOpenAccountResponse } = require("../../protocols/codecs");

async function openAccount({ socket, clientId, requestId },
    { name, password, initialBalance = 0, currency = 1 }) {
    if (currency < 1 || currency > Object.keys(CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (initialBalance < 0) {
        throw new Error('Initial balance cannot be negative');
    }

    const bodyBuffer = encodeOpenAccountRequest({ name, password, initialBalance, currency });
    const packet = buildPacket(OP_CODE.OPEN_ACCOUNT, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await socketSend(socket, packet);
        const reply = decodeOpenAccountResponse(encodedReply);
        console.log("\nResponse:", reply);
    } catch (err) {
        console.error('Failed to send open account request:', err);
    }
}

module.exports = openAccount;
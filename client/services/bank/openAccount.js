const { constants, buildPacket, socketSend } = require("../../helpers");
const { OP_CODE, STATUS_CODE } = require("../../helpers/constants");
const { encodeOpenAccountRequest, decodeStandardResponse } = require("../../protocols/codecs");

async function openAccount({ socket, clientId, requestId },
    { name, password, initialBalance = 0, currency = 1 }) {
    if (currency < 1 || currency > Object.keys(constants.CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (initialBalance < 0) {
        throw new Error('Initial balance cannot be negative');
    }

    const bodyBuffer = encodeOpenAccountRequest({ name, password, initialBalance, currency });
    const packet = buildPacket(OP_CODE.OPEN_ACCOUNT, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await socketSend(socket, packet);
        const reply = decodeStandardResponse(encodedReply);
        console.log("\nResponse:", { ...reply, status: Object.keys(STATUS_CODE).find(key => STATUS_CODE[key] === reply.statusCode) });
    } catch (err) {
        console.error('Failed to send open account request:', err);
    }
}

module.exports = openAccount;
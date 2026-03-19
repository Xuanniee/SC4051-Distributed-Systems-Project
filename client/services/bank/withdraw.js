const { OP_CODE, CURRENCY } = require('../../helpers/constants.js');
const { buildPacket, socketSend } = require('../../helpers');
const { encodeWithdrawDepositRequest, decodeWithdrawDepositResponse } = require('../../protocols/codecs.js');

module.exports = async function withdraw({ socket, clientId, requestId },
    { name, accountNo, password, currency = 1, amount }) {
    if (currency < 1 || currency > Object.keys(CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (amount <= 0) {
        throw new Error('Withdrawal amount must be more than 0');
    }

    const bodyBuffer = encodeWithdrawDepositRequest({ name, password, accountNo, currency, amount });
    const packet = buildPacket(OP_CODE.WITHDRAW, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await socketSend(socket, packet);
        const reply = decodeWithdrawDepositResponse(encodedReply);
        console.log("\nResponse:", reply);
    } catch (err) {
        console.error('Failed to send withdrawal request:', err);
    }
}
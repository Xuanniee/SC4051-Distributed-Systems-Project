const { OP_CODE, CURRENCY } = require('../helpers/constants.js');
const { buildPacket, socketSend } = require('../helpers');
const { encodeWithdrawDepositRequest, decodeWithdrawDepositResponse } = require('../protocols/codecs.js');

module.exports = async function deposit({ socket, clientId, requestId },
    { name, accountNo, password, currency = 1, amount = 0 }) {
    if (!accountNo || accountNo < 1000 || !name || !password || password.length !== 8) {
        throw new Error('Invalid account details');
    }

    if (currency < 1 || currency > Object.keys(CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (amount <= 0) {
        throw new Error('Deposit amount must be more than 0');
    }

    const bodyBuffer = encodeWithdrawDepositRequest({ name, password, accountNo, currency, amount });
    const packet = buildPacket(OP_CODE.DEPOSIT, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await socketSend(socket, packet);
        return decodeWithdrawDepositResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send deposit request:', err);
    }
}
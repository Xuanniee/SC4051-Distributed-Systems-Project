const { OP_CODE, CURRENCY } = require('../helpers/constants.js');
const { buildPacket, sendWithRetries } = require('../helpers');
const { encodeWithdrawDepositRequest, decodeWithdrawDepositResponse } = require('../protocols/codecs.js');

module.exports = async function deposit({ socket, clientId, requestId, timeoutMs, maxRetries },
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
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeWithdrawDepositResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send deposit request:', err);
    }
}
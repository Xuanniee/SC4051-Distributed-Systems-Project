const { OP_CODE, CURRENCY } = require('../helpers/constants.js');
const { buildPacket, sendWithRetries } = require('../helpers');
const { encodeWithdrawDepositRequest, decodeWithdrawDepositResponse } = require('../protocols/codecs.js');

module.exports = async function withdraw({ socket, clientId, requestId, timeoutMs, maxRetries },
    { name, accountNo, password, currency = 1, amount = 0 }) {
    if (isNaN(currency) || isNaN(amount) || isNaN(accountNo)) {
        throw new Error('Currency, amount, and account number must be valid numbers');
    }
    currency = parseInt(currency) || 1;
    amount = parseFloat(amount) || 0;
    accountNo = parseInt(accountNo) || -1;

    if (!accountNo || accountNo < 1000 || !name || !password || password.length !== 8) {
        throw new Error('Invalid account details');
    }

    if (currency < 1 || currency > Object.keys(CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (amount <= 0) {
        throw new Error('Withdrawal amount must be more than 0');
    }

    const bodyBuffer = encodeWithdrawDepositRequest({ name, password, accountNo, currency, amount });
    const packet = buildPacket(OP_CODE.WITHDRAW, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeWithdrawDepositResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send withdrawal request', err);
    }
}
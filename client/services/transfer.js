const { OP_CODE, CURRENCY } = require('../helpers/constants.js');
const { buildPacket, sendWithRetries } = require('../helpers');
const { encodeTransferRequest, decodeTransferResponse } = require('../protocols/codecs.js');

module.exports = async function transfer({ socket, clientId, requestId, timeoutMs, maxRetries },
    { fromName, fromAccountNo, password, toAccountNo, currency = 1, amount = 0 }) {
    if (isNaN(currency) || isNaN(amount) || isNaN(fromAccountNo) || isNaN(toAccountNo)) {
        throw new Error('Currency, amount, and account numbers must be valid numbers');
    }
    currency = parseInt(currency) || 1;
    amount = parseFloat(amount) || 0;
    fromAccountNo = parseInt(fromAccountNo) || -1;
    toAccountNo = parseInt(toAccountNo) || -1;

    if (!fromAccountNo || fromAccountNo < 1000 || !fromName || !password || password.length !== 8) {
        throw new Error('Invalid account details');
    }

    if (!toAccountNo || toAccountNo < 1000) {
        throw new Error('Invalid recipient account number');
    }

    if (currency < 1 || currency > Object.keys(CURRENCY).length) {
        throw new Error('Invalid currency');
    }

    if (amount <= 0) {
        throw new Error('Transfer amount must be more than 0');
    }

    const bodyBuffer = encodeTransferRequest({ fromName, fromAccountNo, password, toAccountNo, currency, amount });
    const packet = buildPacket(OP_CODE.TRANSFER, clientId, requestId, bodyBuffer);

    try {
        const encodedReply = await sendWithRetries(socket, packet, { timeoutMs, maxRetries });
        return decodeTransferResponse(encodedReply);
    } catch (err) {
        throw new Error('Failed to send transfer request', err);
    }
}
const { CURRENCY, STATUS_CODE } = require("../helpers/constants");
const { BufferWriter, BufferReader } = require("./marshaller");

module.exports = {
    decodeStandardResponse: (buffer) => {
        const reader = new BufferReader(buffer);
        const statusCode = reader.readU8();
        const status = Object.keys(STATUS_CODE).find(key => STATUS_CODE[key] === reply.statusCode);
        const message = reader.readString();
        return { statusCode, status, message };
    },
    encodeOpenAccountRequest: ({ name, password, initialBalance = 0, currency = 1 }) => {
        if (currency < 1 || currency > Object.keys(CURRENCY).length) {
            throw new Error('Invalid currency');
        }

        if (initialBalance < 0) {
            throw new Error('Initial balance cannot be negative');
        }

        const writer = new BufferWriter();
        writer.writeString(name);
        writer.writeString(password);
        writer.writeU8(currency);
        writer.writeF64(initialBalance);

        return writer.toBuffer();
    },
    decodeOpenAccountResponse: (buffer) => {
        const reader = new BufferReader(buffer);

        const statusCode = reader.readU8();
        const status = Object.keys(STATUS_CODE).find(key => STATUS_CODE[key] === statusCode);
        const message = reader.readString();
        if (statusCode !== STATUS_CODE.SUCCESS) {
            return { statusCode, status, message };
        }
        const accountNo = reader.readU32();

        return { statusCode, status, message, accountNo };
    },
    encodeDepositRequest: ({ accountId, amount, currency }) => {
        if (currency < 1 || currency > Object.keys(CURRENCY).length) {
            throw new Error('Invalid currency');
        }

        if (amount <= 0) {
            throw new Error('Deposit amount must be positive');
        }

        const writer = new BufferWriter();
        writer.writeU32(accountId);
        writer.writeU8(currency);
        writer.writeF64(amount);

        return writer.toBuffer();
    }
}
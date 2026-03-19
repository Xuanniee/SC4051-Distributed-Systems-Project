const { CURRENCY, STATUS_CODE } = require("../helpers/constants");
const { BufferWriter, BufferReader } = require("./marshaller");

module.exports = {
    decodeStandardResponse: (buffer) => {
        const reader = new BufferReader(buffer);
        const statusCode = reader.readU8();
        const status = Object.keys(STATUS_CODE).find(key => STATUS_CODE[key] === statusCode);
        const message = reader.readString();
        return { statusCode, status, message };
    },
    encodeOpenAccountRequest: ({ name, password, initialBalance = 0, currency = 1 }) => {
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
    encodeCloseAccountRequest: ({ name, password, accountNo }) => {
        const writer = new BufferWriter();

        writer.writeString(name);
        writer.writeU32(accountNo);
        writer.writeString(password);

        return writer.toBuffer();
    },
    encodeDepositRequest: ({ accountId, amount, currency }) => {
        const writer = new BufferWriter();

        writer.writeU32(accountId);
        writer.writeU8(currency);
        writer.writeF64(amount);

        return writer.toBuffer();
    }
}
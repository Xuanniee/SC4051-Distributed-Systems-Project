const { constants } = require("../helpers");
const { BufferWriter, BufferReader } = require("./marshaller");

module.exports = {
    decodeStandardResponse: (buffer) => {
        const reader = new BufferReader(buffer);
        const statusCode = reader.readU8();
        const message = reader.readString();
        return { statusCode, message };
    },
    encodeOpenAccountRequest: ({ name, password, initialBalance = 0, currency = 1 }) => {
        if (currency < 1 || currency > Object.keys(constants.CURRENCY).length) {
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
    }
}
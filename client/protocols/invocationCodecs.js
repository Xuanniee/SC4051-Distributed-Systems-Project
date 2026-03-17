const { BufferWriter, BufferReader } = require('./marshaller');

module.exports = {
    encodeInvocationHeader: (clientId, requestId) => {
        const writer = new BufferWriter();
        writer.writeString(clientId);
        writer.writeU32(requestId);
        return writer.toBuffer();
    },
    decodeInvocationHeader: (payload) => {
        const reader = new BufferReader(payload);
        const clientId = reader.readString();
        const requestId = reader.readU32();

        const remainingPayload = payload.slice(reader.offset);
        return { clientId, requestId, ...remainingPayload };
    }
} 
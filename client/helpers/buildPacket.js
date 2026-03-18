const { OP_CODE } = require("./constants");
const { encodeInvocationHeader } = require("../protocols/invocationCodecs");

module.exports = function buildPacket(opcode, clientId, requestId, bodyBuffer) {
    if (opcode < 1 || opcode > Object.keys(OP_CODE).length) {
        throw new Error('Invalid opcode');
    }

    const header = encodeInvocationHeader(clientId, requestId);
    return Buffer.concat([
        Buffer.from([opcode]),
        header,
        bodyBuffer,
    ]);
}
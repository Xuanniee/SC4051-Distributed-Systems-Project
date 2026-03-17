module.exports = {
    BufferReader: class BufferReader {
        constructor(data) {
            this.data = data;
            this.offset = 0;
        }

        read(size) {
            const end = this.offset + size;
            if (end > this.data.length) {
                throw new Error(`Not enough bytes to read ${size} byte(s).
                    Offset=${this.offset}, buffer_length=${this.data.length}`);
            }
            const chunk = this.data.slice(this.offset, end);
            this.offset = end;
            return chunk;
        }

        readU8() {
            const value = this.read(1).readUInt8(0);
            return value;
        }

        readU32() {
            const value = this.read(4).readUInt32BE(0);
            return value;
        }

        readF64() {
            const value = this.read(8).readDoubleBE(0);
            return value;
        }

        readString() {
            const length = this.readU32();
            const strBuf = this.read(length);
            return strBuf.toString('utf8');
        }

        readBytes() {
            const length = this.readU32();
            return this.read(length);
        }

        remaining() {
            return this.data.length - this.offset;
        }

        hasRemaining() {
            return this.remaining() > 0;
        }
    },
    BufferWriter: class BufferWriter {
        constructor() {
            this.parts = [];
        }

        writeU8(value) {
            const buf = Buffer.alloc(1);
            buf.writeUInt8(value, 0);
            this.parts.push(buf);
        }

        writeU32(value) {
            const buf = Buffer.alloc(4);
            buf.writeUInt32BE(value, 0);
            this.parts.push(buf);
        }

        writeF64(value) {
            const buf = Buffer.alloc(8);
            buf.writeDoubleBE(value, 0);
            this.parts.push(buf);
        }

        writeString(value) {
            const strBuf = Buffer.from(value, 'utf8');
            this.writeU32(strBuf.length);
            this.parts.push(strBuf);
        }

        writeBytes(value) {
            this.writeU32(value.length);
            this.parts.push(value);
        }

        toBuffer() {
            return Buffer.concat(this.parts);
        }
    }
}
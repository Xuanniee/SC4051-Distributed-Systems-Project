const crypto = require('crypto');
const os = require('os');

module.exports = function generateClientId(nodeTag = '') {
    const timestampPart = Date.now().toString(36);
    const hostPart = os.hostname().slice(0, 8).replace(/[^a-zA-Z0-9]/g, '').toLowerCase() || 'host';
    const pidPart = (process.pid || 0).toString(36);
    const randomPart = crypto.randomBytes(3).toString('hex');
    const safeNodeTag = (nodeTag || '').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 12);

    return safeNodeTag
        ? `${safeNodeTag}-${timestampPart}-${hostPart}-${pidPart}-${randomPart}`
        : `${timestampPart}-${hostPart}-${pidPart}-${randomPart}`;
}
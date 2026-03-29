const { DEFAULT_TIMEOUT_MS, DEFAULT_MONITOR_DURATION_SECONDS, DEFAULT_RETRIES } = require('./constants');

function parsePositiveInteger(rawValue, flagName, allowZero = false) {
    const parsed = Number.parseInt(rawValue, 10);
    if (!Number.isInteger(parsed) || (allowZero ? parsed < 0 : parsed <= 0)) {
        throw new Error(`${flagName} must be a positive integer`);
    }
    return parsed;
}

function readFlagValue(args, flagName) {
    const idx = args.indexOf(flagName);
    if (idx === -1) {
        return undefined;
    }

    const value = args[idx + 1];
    if (!value || value.startsWith('--')) {
        throw new Error(`Missing value for ${flagName}`);
    }

    return value;
}

module.exports = function getArgs() {
    const args = process.argv.slice(2);

    const timeoutRaw = readFlagValue(args, '--timeout');
    const timeoutMs = timeoutRaw
        ? parsePositiveInteger(timeoutRaw, '--timeout')
        : DEFAULT_TIMEOUT_MS;

    const monitorDurationRaw = readFlagValue(args, '--monitor-duration');
    const monitorDurationSeconds = monitorDurationRaw
        ? parsePositiveInteger(monitorDurationRaw, '--monitor-duration')
        : DEFAULT_MONITOR_DURATION_SECONDS;

    const retriesRaw = readFlagValue(args, '--retries');
    const maxRetries = retriesRaw
        ? parsePositiveInteger(retriesRaw, '--retries', true)
        : DEFAULT_RETRIES;

    return {
        timeoutMs,
        monitorDurationSeconds,
        maxRetries,
    };
}
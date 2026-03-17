module.exports = function createRequestIdGenerator() {
    let requestId = 0;
    return () => {
        requestId += 1;
        return requestId;
    };
}
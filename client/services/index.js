const monitor = require('./monitor');

module.exports = {
    openAccount: require('./openAccount'),
    closeAccount: require('./closeAccount'),
    deposit: require('./deposit'),
    withdraw: require('./withdraw'),
    balanceInquiry: require('./balanceInquiry'),
    transfer: require('./transfer'),
    monitor: require('./monitor')
}
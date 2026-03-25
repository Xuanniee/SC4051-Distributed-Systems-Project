const { generateClientId, createRequestIdGenerator } = require('./helpers');
const readline = require('node:readline/promises');
const { stdin: input, stdout: output } = require('node:process');
const { OP_CODE, CURRENCY } = require('./helpers/constants');
const BankServices = require('./services');
const dgram = require('node:dgram');
const monitorCallback = require('./protocols/monitorCallback');
const { getArgs } = require('./helpers');

async function client() {
    const socket = dgram.createSocket('udp4');
    let isMonitoring = false;
    let monitorExpiryTimer = null;
    const { timeoutMs, monitorDurationSeconds, maxRetries } = getArgs();

    const clientId = generateClientId(process.env.CLIENT_NODE_ID || 'client');
    const nextRequestId = createRequestIdGenerator();

    console.log(`
        App started with Client ID: ${clientId}\n
        Request timeout (ms): ${timeoutMs}\n
        Request retries: ${maxRetries}\n
        Monitor duration (s): ${monitorDurationSeconds}\n
    `);

    const rl = readline.createInterface({ input, output });
    while (true) {
        const option = await rl.question(`
            --- Bank Client ---
            1. Open Account
            2. Close Account
            3. Deposit
            4. Withdraw
            5. Monitor Register
            6. Balance Inquiry
            7. Transfer
            8. Exit

            Please select an option: `);

        switch (option.trim()) {
            case OP_CODE.OPEN_ACCOUNT.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const initialBalance = await rl.question('Enter initial balance (default 0): ');
                    const currency = await rl.question(`Select currency (${Object.keys(CURRENCY).map(k => `${CURRENCY[k]}: ${k}`).join(', ')}, default 1): `);
                    const reply = await BankServices.openAccount({ socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries }, {
                        name,
                        password,
                        initialBalance: parseFloat(initialBalance) || 0,
                        currency: parseInt(currency, 10) || 1,
                    });
                    console.log('\nAccount opened successfully!\n', reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.CLOSE_ACCOUNT.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const accountNo = await rl.question('Enter account number: ');
                    const reply = await BankServices.closeAccount({ socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo, 10) || -1,
                    });
                    console.log('\nAccount closed successfully!\n', reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.DEPOSIT.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const accountNo = await rl.question('Enter account number: ');
                    const currency = await rl.question(`Select currency (${Object.keys(CURRENCY).map(k => `${CURRENCY[k]}: ${k}`).join(', ')}, default 1): `);
                    const amount = await rl.question('Enter deposit amount: ');
                    const reply = await BankServices.deposit({ socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo, 10) || -1,
                        currency: parseInt(currency, 10) || 1,
                        amount: parseFloat(amount) || 0,
                    });
                    console.log('\nDeposit successful!\n', reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.WITHDRAW.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const accountNo = await rl.question('Enter account number: ');
                    const currency = await rl.question(`Select currency (${Object.keys(CURRENCY).map(k => `${CURRENCY[k]}: ${k}`).join(', ')}, default 1): `);
                    const amount = await rl.question('Enter withdrawal amount: ');
                    const reply = await BankServices.withdraw({ socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo, 10) || -1,
                        currency: parseInt(currency, 10) || 1,
                        amount: parseFloat(amount) || 0,
                    });
                    console.log('\nWithdrawal successful!\n', reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.MONITOR_REGISTER.toString():
                try {
                    if (isMonitoring) {
                        console.log('\nAlready registered for monitoring updates.\n');
                        break;
                    }

                    const durationSecs = await rl.question(`Enter monitoring duration in seconds (default ${monitorDurationSeconds}): `);
                    const parsedDurationSecs = parseInt(durationSecs) || monitorDurationSeconds;

                    monitorCallback(socket);
                    isMonitoring = true;

                    if (monitorExpiryTimer) {
                        clearTimeout(monitorExpiryTimer);
                    }
                    monitorExpiryTimer = setTimeout(() => {
                        isMonitoring = false;
                        monitorExpiryTimer = null;
                    }, parsedDurationSecs * 1000);

                    const reply = await BankServices.monitor(
                        { socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries },
                        parsedDurationSecs,
                    );
                    console.log(`\nMonitoring for ${parsedDurationSecs} seconds started successfully! (CTRL + C to exit)\n`, reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                    isMonitoring = false;
                }
                break;
            case OP_CODE.BALANCE_INQUIRY.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const accountNo = await rl.question('Enter account number: ');
                    const reply = await BankServices.balanceInquiry({ socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo, 10) || -1,
                    });
                    console.log(`\nYour balance: (${reply.currency || CURRENCY.SGD}) $${reply.balance || 0}\n`, reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.TRANSFER.toString():
                try {
                    const fromName = await rl.question('Enter your account name: ');
                    const password = await rl.question('Enter your account password: ');
                    const fromAccountNo = await rl.question('Enter your account number: ');
                    const toAccountNo = await rl.question('Enter the recipient\'s account number: ');
                    const currency = await rl.question(`Select currency (${Object.keys(CURRENCY).map(k => `${CURRENCY[k]}: ${k}`).join(', ')}, default 1): `);
                    const amount = await rl.question('Enter transfer amount: ');

                    const reply = await BankServices.transfer({ socket, clientId, requestId: nextRequestId(), timeoutMs, maxRetries }, {
                        fromName,
                        password,
                        fromAccountNo: parseInt(fromAccountNo, 10) || -1,
                        toAccountNo: parseInt(toAccountNo, 10) || -1,
                        currency: parseInt(currency, 10) || 1,
                        amount: parseFloat(amount) || 0,
                    });
                    console.log('\nTransfer successful!\n', reply);
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case '8':
                console.log('Exiting...');
                if (monitorExpiryTimer) {
                    clearTimeout(monitorExpiryTimer);
                }
                rl.close();
                socket.close();
                process.exit(0);
            default:
                console.log('\nInvalid option. Please try again.\n');
        }
    }
}

client();
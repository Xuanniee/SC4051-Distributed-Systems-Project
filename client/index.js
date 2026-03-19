const { generateClientId, createRequestIdGenerator } = require('./helpers');
const readline = require('node:readline/promises');
const { stdin: input, stdout: output } = require('node:process');
const { OP_CODE, CURRENCY } = require('./helpers/constants');
const { openAccount, closeAccount, deposit, withdraw } = require('./services/bank');
const dgram = require('node:dgram');

async function client() {
    const port = process.env.PORT || 5000;
    const host = process.env.HOST || 'localhost';

    const socket = dgram.createSocket('udp4');

    const clientId = generateClientId(process.env.CLIENT_NODE_ID || 'client');
    const nextRequestId = createRequestIdGenerator();

    console.log(`
        Client is running on http://${host}:${port}
        Client ID: ${clientId}
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

            Please select an option: `); // TODO: Check balance

        switch (option.trim()) {
            case OP_CODE.OPEN_ACCOUNT.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const initialBalance = await rl.question('Enter initial balance (default 0): ');
                    const currency = await rl.question(`Select currency (${Object.keys(CURRENCY).map(k => `${CURRENCY[k]}: ${k}`).join(', ')}, default 1): `);
                    await openAccount({ socket, clientId, requestId: nextRequestId() }, {
                        name,
                        password,
                        initialBalance: parseFloat(initialBalance) || 0,
                        currency: parseInt(currency) || 1
                    });
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.CLOSE_ACCOUNT.toString():
                try {
                    const name = await rl.question('Enter account name: ');
                    const password = await rl.question('Enter account password: ');
                    const accountNo = await rl.question('Enter account number: ');
                    await closeAccount({ socket, clientId, requestId: nextRequestId() }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo) || -1
                    });
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
                    await deposit({ socket, clientId, requestId: nextRequestId() }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo) || -1,
                        currency: parseInt(currency) || 1,
                        amount: parseFloat(amount) || 0
                    });
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
                    await withdraw({ socket, clientId, requestId: nextRequestId() }, {
                        name,
                        password,
                        accountNo: parseInt(accountNo) || -1,
                        currency: parseInt(currency) || 1,
                        amount: parseFloat(amount) || 0
                    });
                } catch (err) {
                    console.error(`\nError: ${err.message}`);
                }
                break;
            case OP_CODE.MONITOR_REGISTER.toString():
                console.log('Registering monitor... (not implemented)');
                break;
            case OP_CODE.BALANCE_INQUIRY.toString():
                console.log('Inquiring balance... (not implemented)');
                break;
            case OP_CODE.TRANSFER.toString():
                console.log('Transferring... (not implemented)');
                break;
            case '8':
                console.log('Exiting...');
                rl.close();
                socket.close();
                process.exit(0);
            default:
                console.log('\nInvalid option. Please try again.\n');
        }
    }
}

client();
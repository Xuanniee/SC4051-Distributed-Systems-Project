const { generateClientId } = require('./helpers');
const readline = require('node:readline/promises');
const { stdin: input, stdout: output } = require('node:process');

async function client() {
    const PORT = process.env.PORT || 5000;
    const HOST = process.env.HOST || 'localhost';

    const clientId = generateClientId(process.env.CLIENT_NODE_ID || 'client');

    console.log(`
        Client is running on http://${HOST}:${PORT}
        Client ID: ${clientId}
        `);

    const rl = readline.createInterface({ input, output });
    while (true) {
        const option = await rl.question(`
            --- Bank Client ---
            1. Check Balance
            2. Deposit
            3. Withdraw
            4. Exit

            Please select an option: `);

        switch (option.trim()) {
            case '1':
                console.log('Checking balance... (not implemented)');
                break;
            case '2':
                console.log('Depositing... (not implemented)');
                break;
            case '3':
                console.log('Withdrawing... (not implemented)');
                break;
            case '4':
                console.log('Exiting client. Goodbye!');
                rl.close();
                return;
            default:
                console.log('\nInvalid option. Please try again.\n');
        }
    }
}

client();
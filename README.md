# WARNING: THIS IS A 2 HOUR RUSHED SHITTY BOT

## Overview
this is simple ad posting bot for owner com, it has client logging + auto channel detection. please be advised that channel detection isn't 100% accurate and this is for education purposes only.

## Installation
please ensure you have the following installed:
- python 3.9+

### Setup
1. clone the repository:
   ```sh
   git clone https://github.com/kelvbun/adposter
   cd adposter
   ```
2. Install dependencies:
   - i highly suggest you use run this in a venv
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - create a `.env` file in the project root.
   - copy and paste the following:
     ```
     TOKEN=your-bot-token
     WEBHOOK=your-webhook-url
     PREFIX=your-prefix
     CLOCK=your-recurrent-task-in-minutes
     ```

## Commands
- `<prefix>send <file> <message>`: Sends a message to channels listed in the specified file.
- `<prefix>check <file>`: Checks the validity of channels in a file.  (NOT ADDED YET SOON)
- `<prefix>scan <file>`: Fetches and stores matching channels in the file. By default `<file>` is promo
- `<prefix>show <file>`: Displays stored channels.

## License
this project is licensed under [MIT License](LICENSE).

## Contact
for questions, suggestions, or contributing reach out via discord (@kelvbun) or open an issue in the repository.

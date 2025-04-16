## Overview
this is simple ad posting bot for owner com, it has client logging + auto channel detection. please be advised that channel detection isn't 100% accurate. the code is poorly written and for education purposes only. 

## Installation
please ensure you have the following installed:
```sh
python 3.9+
```

## Setup
1. clone the repository:
   ```sh
   git clone https://github.com/kelvbun/adposter
   cd adposter
   ```
2. install dependencies:
   - i highly suggest you use run this in a venv so
   ```sh
   python3 -m venv venv
   pip install -r requirements.txt
   ```
3. set up environment variables:
   - create a `.env` file in the project root.
   - copy and paste the following:
     ```
     TOKEN=your-bot-token
     WEBHOOK=your-webhook-url
     PREFIX=your-prefix
     CLOCK=your-recurrent-task-in-minutes
     ```

4. start the bot:
   - activate the venv
   - run the bot (macos): 
   ```sh
   source venv/bin/activate 
   python main.py
   ```

## Commands
- `<prefix>send <file> <message>`: sends a message to channels listed in the specified file.
- `<prefix>check <file>`: checks the validity of channels in a file. (NOT ADDED YET SOON)
- `<prefix>scan <file>`: fetches and stores matching channels in the file. by default `promo` is promo
- `<prefix>show <file>`: displays stored channels.

## Contact
for questions, suggestions, or contributing reach out via discord (@kelvbun) or open an issue in the repository. please note that this project is under the MIT license.

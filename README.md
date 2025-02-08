# WARNING: THIS IS A 2 HOUR RUSHED SHITTY BOT

# Discord Ad Poster Bot

## Overview
This project is a Discord bot designed to automate advertisement posting and moderation in Discord servers. It includes functionalities for sending promotional messages, checking and managing channels, and logging events related to bans and removals.

## Features
- **Automated Ad Posting**: Sends promotional messages to specified channels.
- **Channel Validation**: Checks and verifies channels before sending messages.
- **Event Logging**: Logs member bans and removals.
- **Channel Discovery**: Fetches and stores all channels matching predefined criteria.

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- `pip`

### Setup
1. Clone the repository:
   ```sh
   git clone <repository-url>
   cd <project-folder>
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the project root.
   - Add the following:
     ```
     TOKEN=your-bot-token
     WEBHOOK_URL=your-webhook-url
     ```

## Usage
1. Run the bot:
   ```sh
   python main.py
   ```
2. Use the command prefix `-v-` to interact with the bot.

## File Structure
- **main.py**: Initializes and runs the bot.
- **log.py**: Handles logging of user bans and removals.
- **macro.py**: Manages advertisement posting and channel checking.
- **requirements.txt**: Lists dependencies for installation.

## Commands
- `-v- send <file> <message>`: Sends a message to channels listed in the specified file.
- `-v- check <file>`: Checks the validity of channels in a file.
- `-v- fetch_all <file>`: Fetches and stores matching channels in the file.
- `-v- show <file>`: Displays stored channels.

## License
This project is licensed under [MIT License](LICENSE).

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Contact
For questions or suggestions, reach out via Discord or open an issue in the repository.

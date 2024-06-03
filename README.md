# EPITA Pegasus Discord Notifications

This project allows you to have notifications on Discord when you have new notes on pegasus, the EPITA notes system.

## Installation

To get started, ensure you have BeautifulSoup installed. Use the following command with pip:

```bash
pip install beautifulsoup4
```


To facilitate the initialization of the program you can install browser-cookie3 but this is not a mandatory.

```bash
pip install browser-cookie3
```

## Usage

1. First run "setup.py" to create the files (tokens.json / pegasus.html) necessary for "pegasus_update.py" to work.
    - The cookie has an expiration date, so you may need to relaunch setup.py every few months
2. Then try to run the pegasus_update.py script, you should receive "No new grade" with your Discord webhook.
3. If everything works correctly you can now place the repository files on your VPS to run it in a loop (every 30 minutes for example).

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.
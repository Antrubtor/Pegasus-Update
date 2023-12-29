# EPITA Pegasus Discord Notifications

This project allows you to have notifications on discord when you have new notes on pegasus, the EPITA notes system.

## Installation

To get started, ensure you have BeautifulSoup installed. Use the following command with pip:

```bash
pip install beautifulsoup4
```

## Usage

1. Begin by obtaining the URL for Pegasus using these steps:
   - Open your browser.
   - Access Pegasus.
   - Click on 'Logout' at the top right.
   - Press F12 (for the inspect tool).
   - Go to the 'Network' tab.
   - Click the button on the page: 'Sign in with Office 365.'
   - Once loaded, use the search function in the network tab and look for `gfront-controller.php`.
   - Find a request result starting with `https://prepa-epita.helvetius.net/pegasus/gfront-controller.php`.

2. If everything works correctly, you can execute the code using the Windows Task Scheduler every hour to stay updated (a .bat file is provided).

## Contributing

Contributions are welcome! Feel free to fork the repository and submit a pull request.
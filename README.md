### 〓 Instructions 〓
1. Please install python3 and run "prepare.bat" before running it for the first time.
    - Download URL: https://www.python.org/downloads/release/python-377/
    - Version 3.7.7 is recommended, otherwise the installation of the library may generate exceptions.
2. Modify the configuration file ".\Pixiv_Collection\config.json".
    - [chrome] the file path of the chrome browser.
3. Download the driver for your chrome version and place it in the current directory.
    - Please make sure the chrome driver version matches the chrome version as chrome has an auto-update problem.
    - Chrome driver URL: https://googlechromelabs.github.io/chrome-for-testing/
    - <2023-10-10> Backup: https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/117.0.5938.149/win64/chromedriver-win64.zip
4. Please log in to your pixiv account in the pop-up browser in a minute.
5. Just wait for the image to download.

### 〓 Command-line parameter 〓
- h/help
    - View command line prompts.
- debug/debug
    - Turn on debug mode. Do not start the simulator.
- sd/start_date
    - Start date.
    - Exmaple: -sd "20231010"
- ed/end_date
    - End date.
    - Example: -ed "20231011"

### 〓 Latest version 2.1 〓
1. Add customized date intervals.
2. Add history of date to avoid repeated crawling.
3. Add history of image to avoid repeated downloading.
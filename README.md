# gform2adafruitIO
Python script to automatically publish data from Google Form to Adafruit IO.

*Michael D'Argenio  
mjdargen@gmail.com  
https://dargen.io   
https://github.com/mjdargen  
Created: December 12, 2020  
Last Modified: December 12, 2020*  

## Overview

This program shows how to easily link a Google Form with Adafruit IO feeds. Instead of allowing just anyone to access your feeds directly, this program acts as a middleware between a public Google Form and a private feed. Anyone can complete your Google Form. This program will periodically check the form for new submissions, vet the submission data to confirm the data is valid, then push the data to your Adafruit IO feed.  

This example program uses the Adafruit Matrix Portal to make a Marquee Sign that anyone can submit text to. The Google Form asks the user for text and a color. The program ensures the color is valid and the text is profanity-free (as profanity-free as possible). The program then publishes the data to Adafruit IO. The Matrix Portal pulls this information down from Adafruit IO to scroll across the display.

You can follow the directions below or check out this Instructable for more info: https://www.instructables.com/Gform2adafruitIO-Automatic-Marquee-Driven-by-Googl/  
Or if Hackster is more your style, you can check out this tutorial here: https://www.hackster.io/mjdargen/gform2adafruitio-marquee-driven-by-google-form-adafruit-io-b31e81

## Installation/Set-Up/Execution Steps
* Clone repository:
  * `git clone https://github.com/mjdargen/gform2adafruitIO.git`
* Install packages:
  * Install packages by running this command in the cloned repository: `pip3 install -r requirements.txt`
  * Specifically tested with the following environment:
      * python == 3.7.7
      * requests == 2.24.0
      * webcolors == 1.11.1
      * adafruit-io == 2.4.0
      * python-dotenv == 0.14.0
* Setup Google Form
  * Create form. Here is my sample form: https://forms.gle/MUWWtGKMeH4RmXeq6
  * Publish form to Google Sheet: Click on "Responses" tab of your Form and
  click the Sheets icon. This will bring you to a linked spreadsheet.
  * Any new submission will automatically show up in the linked Sheet.
* Publish Linked Google Sheet as csv
  * Go to "File -> Publish to the web".
  * Once the window appears, select the "Link" tab.
  * Select the sheet that you want to publish: "Form Responses 1".
  * Then select to publish it as "Comma-separated values (.csv)".
  * Click Publish. A pop-up will appear asking if you are sure. Click "OK".
  * The window will now show the link to the .csv file.
  * You can open this link and it will download the .csv file.
  * Here is the csv published by my sample form: https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2AwUbx6lsZK-H0WjvcF1Bu2VUlsN4ir8kMD10xSEkl-JkxXKlqLZfnJ5pgyNhYIDYMEOK6Ys4cEYK/pub?gid=1198589603&single=true&output=csv
* Update the URL for the csv file
  * Modify the variable CSV_URL to point to your URL from previous step.
  * `CSV_URL = "..."`
* Set max number of quotes
  * This is the maximum number of values you want in your Adafruit IO feed.
  * `MAX_QUOTES = 10` -> will keep the 10 most recent quotes/colors
* Set up environment variables with Adafruit IO key & username
  * Create a file called ".env".
  * Enter your Adafruit IO information in the following format:
      * `ADAFRUIT_IO_KEY=<put_your_adafruit_io_key_here>`
      * `ADAFRUIT_IO_USERNAME=<put_your_adafruit_io_username_here>`
* Set up names for your Adafruit IO feeds.
  * In this case, I have 2 feeds: one for text and one for color.
  * I have grouped them together in the Adafruit IO portal.
  * When grouped, the name format for feeds is: group_name.feed_name
      * `TEXT_FEED = 'matrix-portal-quotes.signtext'`
      * `COLOR_FEED = 'matrix-portal-quotes.signcolor'`
* Determine how program will run by selecting which `if __name__ == "__main__":`
  * Do this at the very bottom of this file.
  * If you want the program to run once, select first option.
  * If you want the program to run repeatedly forever, select second option.
* Run: `python3 gform2adafruitIO.py`


## Program Description
Here is a description of the functionality per function of the program:
* `fetch_form_data()`
  * Uses requests library to download .csv file of Google Sheet.
  * Compares downloaded file with last retrieved file to see if there is new submission data.
  * If there is new data, to process it proceeds. Otherwise, the program ends.
* `processing()`
  * Organizes form data into dictionary structure.
  * Calls `color_check()` to process color data and see if it is valid.
  * Calls `profanity_check()` to process text data and see if it is free of profanity.
* `adafruitIOaccess()`
  * Connects with Adafruit IO using Rest API.
  * Pulls existing values from text & color feeds.
  * Adds the new values to those feeds.
  * Removes values from those feeds if they exceed the maximum limit of values.
* `update_files()`
  * After successfully completing all other tasks, overwrites previous downloaded .csv with current downloaded .csv for next execution.  

Here is a description of 2 different ways to run the code.
* 1st `if __name__ == "__main__":` option:
  * Program executes exactly once then exists. Great for scheduling script to run.
  * My script is running on a Raspberry Pi and scheduled using [cron](https://www.raspberrypi.org/documentation/linux/usage/cron.md). Use [this tool](https://crontab.guru/) to figure out scheduling.
  * Below I show how to add a task to cron to schedule the script to run every 30 minutes.
    * `sudo crontab -e`
    * `*/30 * * * * /usr/bin/python3 /home/pi/Documents/gform2adafruitIO/gform2adafruitIO.py`
* 2nd `if __name__ == "__main__":` option:
  * Program executes repeatedly in a loop forever. There is a sleep interval between executions.
  * Set sleep interval (in seconds) by modifying this line: `INTRVL = 1800`


## Adafruit Matrix Portal Info
If you want to run this specific Marquee Sign example with the Adafruit Matrix Portal, check out the links below. They will walk you through how to set up the Matrix Portal and how to set up the feeds in Adafruit IO.  
Adafruit Matrix Portal Product Page: https://www.adafruit.com/product/4745  
General Adafruit Matrix Portal Info: https://learn.adafruit.com/adafruit-matrixportal-m4  
Custom Scrolling Quote Tutorial: https://learn.adafruit.com/aio-quote-board-matrix-display  


## Credits
I took the profanity.txt file from snguyenthanh's project linked here: https://github.com/snguyenthanh/better_profanity/blob/master/better_profanity/profanity_wordlist.txt

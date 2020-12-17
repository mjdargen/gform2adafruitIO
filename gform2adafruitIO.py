# gform2adafruitIO: Automatic Marquee Driven by Google Form/Adafruit IO
#
# Michael D'Argenio
# mjdargen@gmail.com
# https://dargenio.dev
# https://github.com/mjdargen
# Created: December 12, 2020
# Last Modified: December 12, 2020
#
# This program shows how to easily link a Google Form with Adafruit IO feeds.
# Instead of allowing just anyone to access your feeds directly, this program
# acts as a middleware between a public Google Form and a private feed. Anyone
# can complete your Google Form. This program will periodically check the form
# for new submissions, vet the submission data to confirm the data is valid,
# then push the data to your Adafruit IO feed.
#
# This example program uses the Adafruit Matrix Portal to make a Marquee Sign
# that anyone can submit text to. The Google Form asks the user for text and
# a color. The program ensures the color is valid and the text is profanity-free
# (as profanity-free as possible). The program then publishes the data to
# Adafruit IO. The Matrix Portal pulls this information down from Adafruit IO
# to scroll across the display.
#
# Adafruit Matrix Portal: https://www.adafruit.com/product/4745
#
# Here is how to setup and run this program:
#   Clone repository:
#       git clone https://github.com/mjdargen/gform2adafruitIO.git
#   Install packages:
#       Install packages by running this command in the cloned repository:
#           pip3 install -r requirements.txt
#       Specifically tested with the following environment:
#           python == 3.7.7
#           requests == 2.24.0
#           webcolors == 1.11.1
#           adafruit-io == 2.4.0
#           python-dotenv == 0.14.0
#   Setup Google Form
#       Create form. Here is my sample form: https://forms.gle/MUWWtGKMeH4RmXeq6
#       Publish form to Google Sheet: Click on "Responses" tab of your Form and
#       click the Sheets icon. This will bring you to a linked spreadsheet.
#       Any new submission will automatically show up in the linked Sheet.
#   Publish Linked Google Sheet as csv
#       Go to "File -> Publish to the web".
#       Once the window appears, select the "Link" tab.
#       Select the sheet that you want to publish: "Form Responses 1".
#       Then select to publish it as "Comma-separated values (.csv)".
#       Click Publish. A pop-up will appear asking if you are sure. Click "OK".
#       The window will now show the link to the .csv file.
#       You can open this link and it will download the .csv file.
#       Here is the csv published by my sample form:
#       https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2AwUbx6lsZK-H0WjvcF1Bu2VUlsN4ir8kMD10xSEkl-JkxXKlqLZfnJ5pgyNhYIDYMEOK6Ys4cEYK/pub?gid=1198589603&single=true&output=csv
#   Update the URL for the csv file
#       Modify the variable CSV_URL to point to your URL from previous step.
#       CSV_URL = "..."
#   Set max number of quotes
#       This is the maximum number of values you want in your Adafruit IO feed.
#       MAX_QUOTES = 10 -> will keep the 10 most recent quotes/colors
#   Set up environment variables with Adafruit IO key & username
#       Create a file called ".env".
#       Enter your Adafruit IO information in the following format:
#           ADAFRUIT_IO_KEY=<put_your_adafruit_io_key_here>
#           ADAFRUIT_IO_USERNAME=<put_your_adafruit_io_username_here>
#   Set up names for your feeds.
#       In this case, I have 2 feeds: one for text and one for color.
#       I have grouped them together in the Adafruit IO portal.
#       When grouped, the name format for feeds is: group_name.feed_name
#           TEXT_FEED = 'matrix-portal-quotes.signtext'
#           COLOR_FEED = 'matrix-portal-quotes.signcolor'
#   Determine how program will run by selecting which if __name__ == "__main__":
#       Do this at the very bottom of this file.
#       If you want the program to run once, select first option.
#       If you want the program to run repeatedly forever, select second option.
#   Run: python3 gform2adafruitIO.py
#
#   Credits:
#       I took the profanity.txt file from snguyenthanh's project linked below:
#       https://github.com/snguyenthanh/better_profanity/blob/master/better_profanity/profanity_wordlist.txt

import filecmp
import time
import os
import requests
import webcolors
from Adafruit_IO import Client, RequestError, Feed
from dotenv import load_dotenv

#####################################
# THIS SECTION IS FOR YOU TO UPDATE #
#####################################
# published csv of form data
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQ2AwUbx6lsZK-H0WjvcF1Bu2VUlsN4ir8kMD10xSEkl-JkxXKlqLZfnJ5pgyNhYIDYMEOK6Ys4cEYK/pub?gid=1198589603&single=true&output=csv"
# maximum number of quotes to keep in adafruit IO feed
MAX_QUOTES = 10
# set to your Adafruit IO feed names (format ->  group_name.feed_name)
TEXT_FEED = 'matrix-portal-quotes.signtext'
COLOR_FEED = 'matrix-portal-quotes.signcolor'
#####################################
#          END OF SECTION           #
#####################################


# main processing
def main():
    print("Fetching form data...")
    new = fetch_form_data()
    if new:
        print("Processing new data...")
        quotes = processing()
        print("Updating Adafruit IO feeds...")
        adafruitIOaccess(quotes)
        print("Updating local files for comparison...")
        update_files()
    print("Done!")


# retrieve Google Form data as CSV
def fetch_form_data():
    # request and download csv
    r = requests.get(CSV_URL)
    decoded_content = r.content.decode('utf-8')

    # requests downloads the content, create a new file to store the data
    f = open("new.csv", "w")
    f.write(decoded_content)
    f.close()

    # see if files match
    try:
        filecmp.cmp("old.csv", "new.csv")
    except IOError:
        # old file doesn't exist yet, create empty file
        f = open("old.csv", "w")
        f.close()

    # files match, no new forms submitted
    if filecmp.cmp("old.csv", "new.csv"):
        print("\tNo new forms submitted. Exiting...")
        return False
    # files don't match, so process new data
    else:
        print("\tNew form submitted! Proceeding... ")
        return True

# process form data, organizes into dictionary, checks if valid
def processing():

    # read in new data
    with open("new.csv") as input_file:
        # why is it double new lines??
        raw_data = input_file.read().split('\n\n')

    # remove header line
    raw_data = raw_data[1:]

    # create dictionary structure for text and color
    quotes = []
    for data in raw_data:
        data = data.split(",")
        quotes.append({'text': data[1], 'color': data[2]})

    # process color info
    for i, q in enumerate(quotes):
        # try converting to hex value
        success, color = color_check(q['color'])
        # successful
        if success:
            q['color'] = color
        # unsuccesful, so remove entire quote/color from list
        else:
            quotes.pop(i)

    # process text info for profanity
    for i, q in enumerate(quotes):
        # if profanity detected, remove entire quote/color from list
        if profanity_check(q['text']):
            print(f"\tProfanity detected. Ignoring: {q['text']}")
            quotes.pop(i)

    return quotes


# converts form color to hex value if valid
def color_check(data):

    data = data.strip()
    # if it's a text color like "green"
    if data.isalpha():
        try:
            HEX = webcolors.name_to_hex(data)
        except (ValueError):
            print(f"\tNot a valid text color: {data}")
            return False, ""
    # if it's a hex number, assume it is if it starts with # and length 7
    elif (data[1:].isalnum() and data[0] == '#' and len(data) == 7):
        try:
            HEX = webcolors.hex_to_rgb(data)  # just to test
            HEX = data
        except (ValueError):
            print(f"\tNot a valid text color: {data}")
            return False, ""
    # else assume it's invalid
    else:
        print(f"\tNot a valid text color: {data}")
        return False, ""

    # convert to integers and make it valid
    return True, HEX


# process text info for profanity
def profanity_check(quote):
    # open profanity check file
    with open("./profanity.txt") as input_file:
        profanity = input_file.read().splitlines()
    temp = quote
    # remove all punctuation
    for c in ",.?!/\'\";:-<>(){}[]|\\_@#$%^&*+=":
        temp = temp.replace(c, "")
    # check for profanity for each word in quote
    for word in temp.split(" "):
        # for each word in profanity list
        for prof in profanity:
            # if exact match, remove from quote list and break
            if word.lower() == prof.lower():
                return True
    return False


# access Adafruit IO and publishes to color/text feeds
def adafruitIOaccess(quotes):

    # load adafruit IO key and username as environment variables
    load_dotenv()
    ADAFRUIT_IO_KEY = os.getenv('ADAFRUIT_IO_KEY')
    ADAFRUIT_IO_USERNAME = os.getenv('ADAFRUIT_IO_USERNAME')

    # create an instance of the REST client.
    aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

    # assign feeds
    text_feed = aio.feeds(TEXT_FEED)
    color_feed = aio.feeds(COLOR_FEED)

    # retrieve all current quotes on Adafruit IO
    published = aio.data(text_feed.key)

    # get just the text values from published quotes
    for i, p in enumerate(published):
        published[i] = p.value

    # for every quote, check if it's already published
    for q in quotes:
        # if already there, don't publish
        if q['text'] in published:
            continue
        # send new text value
        print(f"\tAdded data to text feed: {q['text']}.")
        aio.send_data(text_feed.key, q['text'])
        # send corresponding color value
        print(f"\tAdded data to color feed: {q['color']}.")
        aio.send_data(color_feed.key, q['color'])

    # retrieve all current quotes on Adafruit IO
    published = aio.data(text_feed.key)

    # keep only the most recent MAX_QUOTES, remove all others
    for i, p in enumerate(published):
        if i > MAX_QUOTES-1:
            # delete a data value from text feed
            print(f"\tRemoved data from text feed: {p.value}.")
            data = aio.delete(text_feed.key, p.id)

    # retrieve all current colors on Adafruit IO
    published = aio.data(color_feed.key)

    # keep the most recent MAX_QUOTES, remove all others
    for i, p in enumerate(published):
        if i > MAX_QUOTES-1:
            # delete a data value from color feed
            print(f"\tRemoved data from color feed: {p.value}.")
            data = aio.delete(color_feed.key, p.id)


# updates local csv file for easy comparison
def update_files():
    f_old = open("old.csv", "w", newline='')
    f_new = open("new.csv", "r", newline='')
    content = f_new.read()
    f_old.write(content)
    f_old.close()
    f_new.close()


# if you want to schedule as cron job, use this
# runs once per program call
if __name__ == "__main__":
    main()


# if you want to run script forever, use this
# loops repeatedly forever when program is called. has a sleep interval
# if __name__ == "__main__":
#     INTRVL = 1800  # set sleep interval in seconds
#     while True:
#         main()
#         print(f"Sleeping for {INTRVL//60} minutes...\n\n\n")
#         time.sleep(INTRVL)

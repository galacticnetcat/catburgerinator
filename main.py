# CatBurgerinatorT100
# Credits to Netcat
# - https://spacehey.com/netcat04
# SPACEHEY BRING BACK EARLY WEB!!

# main.py
# Note: only scrapes from mcdonald's and lol

import os
import platform
import time
import random
import subprocess
import requests
from bs4 import BeautifulSoup

# mcdonald's url to find all of the deals
URL = "https://www.mcdonalds.com/us/en-us/deals.html"
# file to log all the found deals so they are not repeated again when running
DEALS_FILE = "fatso.txt"
# set time to check the sites again
CHECK_INTERVAL = 60
# folder that stores all of the notification audio sound files
AUDIO_FOLDER = os.path.join(os.path.dirname(__file__), "audios")

# method to scrape all of the deals from the site
def scrape_deals():
    res = requests.get(URL)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    deals = []

    teasers = soup.select("div.cmp-teaser")
    for teaser in teasers:
        title_tag = teaser.select_one(".cmp-teaser__title h3")
        desc_tag = teaser.select_one(".cmp-teaser__description p")
        link_tag = teaser.select_one(".cmp-teaser__action-link")

        title = title_tag.text.strip() if title_tag else "No title"
        description = ""
        if desc_tag:
            description = ' '.join(desc_tag.stripped_strings)

        link = link_tag['href'] if link_tag else "No link"

        deals.append({
            'title': title,
            'description': description,
            'link': link
        })

    return deals

# create a file to save all of the already loaded deals
def load_seen_deals():
    if not os.path.exists(DEALS_FILE):
        return set()
    with open(DEALS_FILE, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

# save any deals found to fatso.txt
def save_seen_deal(deal_id):
    with open(DEALS_FILE, 'a', encoding='utf-8') as f:
        f.write(deal_id + '\n')

# play a random audio file in /audios
def play_random_audio():
    if not os.path.exists(AUDIO_FOLDER):
        print("Audio folder does not exist.")
        return

    audio_files = [f for f in os.listdir(AUDIO_FOLDER) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aiff', '.aac'))]

    if not audio_files:
        print("No audio files found in the folder.")
        return

    selected_file = random.choice(audio_files)
    file_path = os.path.join(AUDIO_FOLDER, selected_file)

    try:
        subprocess.Popen(['afplay', file_path])
    except Exception as e:
        print(f"Error playing audio: {e}")

# use macos built in system notifications to notify all the new deals at mcdonald's
def notify_new_deal(deal, suppress_audio=False):
    title = deal['title']
    message = deal['description']
    link = deal['link']

    subprocess.run([
        "terminal-notifier",
        "-title", title,
        "-message", message,
        "-open", link,
        "-appIcon", "/imgs/icon1.png"
    ])

    if not suppress_audio:
        play_random_audio()

# use all built modules and like do some shit lol
def main_loop():
    print("Starting McDonald's Deals Scraper...")
    seen_deals = load_seen_deals()
    last_audio_time = 0 

    while True:
        try:
            deals = scrape_deals()
            new_found = False
            current_time = time.time()
            new_deals_to_notify = []

            for deal in deals:
                deal_id = deal['title'] + " | " + deal['link']

                if deal_id not in seen_deals:
                    new_deals_to_notify.append(deal)
                    save_seen_deal(deal_id)
                    seen_deals.add(deal_id)
                    new_found = True

            if new_found:
                print(f"{len(new_deals_to_notify)} new deal(s) found!")

                for i, deal in enumerate(new_deals_to_notify):
                    print("New Deal Found!")
                    print(f"Title: {deal['title']}")
                    print(f"Description: {deal['description']}")
                    print(f"Link: {deal['link']}")
                    print("-" * 40)

                    suppress_audio = i > 0 and current_time - last_audio_time < 10
                    notify_new_deal(deal, suppress_audio=suppress_audio)

                    if not suppress_audio:
                        last_audio_time = current_time

            else:
                print("No new deals at this time.")

        except Exception as e:
            print(f"Error during scraping: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
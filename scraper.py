# -----------------------
# Imports Libraries
# -----------------------

import feedparser                # Fetches RSS feeds and interprets the XML structure
import requests                  # Makes HTTP requests to fetch web pages/APIs
from bs4 import BeautifulSoup    # Parses HTML and XML documents
import csv                       # Handles CSV file operations
import time                      # Adds delays to avoid overwhelming the server
import tkinter as tk             # Manages GUI elements
from tkinter import messagebox

# -----------------------
# CONFIGURATION
# -----------------------
RSS_FEEDS = {
    "world": "https://www.cnn.com/world",
    "us": "https://rss.cnn.com/rss/edition_us.rss",
    "business": "https://rss.cnn.com/rss/money_news_international.rss",
    "tech": "https://rss.cnn.com/rss/edition_technology.rss"
}

CSV_FILE = "cnn_articles.csv"

# Sets user-agent to reduce chance of being blocked
HEADERS = {"User-Agent": "Mozilla/5.0"}

# -----------------------
# SAVE TO CSV
# -----------------------
def save_to_csv(articles, file_path):
    with open(file_path, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for article in articles:
            writer.writerow(article)

# -----------------------
# RSS SCRAPER
# -----------------------
def scrape_rss(feed_url):
    articles = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        articles.append([entry.title, entry.link, entry.published])
    return articles

# -----------------------
# HTML FALLBACK SCRAPER
# -----------------------
def scrape_html(section_url):
    articles = []
    try:
        response = requests.get(section_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        for headline in soup.select("h3 a"):
            title = headline.get_text(strip=True)
            link = headline.get("href")
            if link and link.startswith("/"):
                link = "https://edition.cnn.com" + link
            if title and link:
                articles.append([title, link, ""])
    except Exception as e:
        print(f"Error scraping HTML: {e}")
    return articles

# -----------------------
# POP-UP MESSAGE
# -----------------------
def show_popup(message):
    root = tk.Tk()
    root.withdraw()  # hide main window
    messagebox.showinfo("CNN Scraper", message)
    root.destroy()

# -----------------------
# MAIN SCRAPER
# -----------------------
def main():
    all_articles = []

    for section, rss_url in RSS_FEEDS.items():
        print(f"Scraping {section.upper()} via RSS...")
        rss_articles = scrape_rss(rss_url)
        if rss_articles:
            all_articles.extend(rss_articles)
        else:
            print(f"No RSS data for {section}, falling back to HTML scraping...")
            section_url = f"https://edition.cnn.com/{section}"
            html_articles = scrape_html(section_url)
            all_articles.extend(html_articles)

        time.sleep(1)  # polite delay

    save_to_csv(all_articles, CSV_FILE)
    show_popup(f"✅ Scraping complete!\nSaved {len(all_articles)} articles to {CSV_FILE}")

if __name__ == "__main__":
    try:
        open(CSV_FILE, "x").write("Title,URL,Published\n")
    except FileExistsError:
        pass
    main()

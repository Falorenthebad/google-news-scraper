# Google News Scraper

A Python script to scrape the latest news articles from **Google News** based on a search query.
It fetches article titles, publishers, publication times, and direct links.

## Features

* Search news articles from Google News using custom queries.
* Retrieve:
  * **Title**
  * **Publisher**
  * **Publication date/time (UTC)**
  * **Direct link to the article**
* Configurable number of results (up to 100).
* Automatic retries for network errors.
* Clean and readable CLI output.

## Requirements

* Python 3.8+
* `requests`
* `beautifulsoup4`
* `urllib3`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Clone this repository:

   ```bash
   git clone https://github.com/Falorenthebad/google-news-scraper.git
   cd google-news-scraper
   ```

2. Run the script:

   ```bash
   python google_news_scraper.py
   ```

3. Example input:

   ```
   Search term: Github
   How many results? (press Enter for 5, max 100): 1
   ```

4. Example output:

   ```
   Google News search: https://news.google.com/search?q=Github&hl=en-US&gl=US&ceid=US%3Aen

   1. GPT-5 is now generally available in GitHub Models
      Source    : The GitHub Blog
      Published : 08 August 2025 00:15:05 UTC
      Link      : https://news.google.com/read/CBMilgFBVV95cUxNcmlBVzlhbG5KZDVJUHVnekM4eVFBUW5hUEVDcnp1Znh5b2tUb3VKcGw2dmtEVWY1aUs4cF9yMUt1RnJKbzZQUVNTaDNBXzh2eHZWVWRyMmZQTmlKTHcweDFqY2ZPTnU0ZGFRVFo4aEoxVlFMTXlVSGh0eU1rOENod1hGVDVJWm9uR1ZjS1N3YVZTb0ZmVUE?hl=en-US&gl=US&ceid=US%3Aen
   --------------------------------------------------------------------------------
   ```
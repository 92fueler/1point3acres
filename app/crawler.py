import requests
from bs4 import BeautifulSoup
from colorama import Fore
import time  # Add this at the top with other imports
import random
from time import sleep
from requests.exceptions import RequestException

from db import get_collection
from config import BASE_URL, HEADERS


def fetch_thread(thread_id, reply_page=1, retry_count=0):
    """Fetch a specific thread page with retry logic."""
    url = f"{BASE_URL}/thread-{thread_id}-{reply_page}-1.html"
    print(Fore.BLUE + f"Fetching URL: {url}")

    # Enhanced headers with more browser-like properties
    enhanced_headers = {
        **HEADERS,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        response = requests.get(url, headers=enhanced_headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
        elif response.status_code == 403 and retry_count < 3:
            # Implement exponential backoff
            wait_time = (2 ** retry_count) * 5 + random.uniform(1, 3)
            print(Fore.YELLOW + f"Rate limited. Waiting {wait_time:.2f} seconds before retry...")
            sleep(wait_time)
            return fetch_thread(thread_id, reply_page, retry_count + 1)
        else:
            print(Fore.RED + f"Failed to fetch {url} with status code {response.status_code}")
            return None
    except RequestException as e:
        print(Fore.RED + f"Request failed: {e}")
        return None


def parse_thread(soup):
    """Parse thread title and posts from the HTML."""
    try:
        # Extract all posts (original post + replies)
        posts = soup.find_all(
            "div", id=lambda x: x and x.startswith("post_")
        )  # Matches 'post_*'

        parsed_posts = []

        for post in posts:
            # Find the post content by looking for td with postmessage_* id
            content_td = post.find("td", id=lambda x: x and x.startswith("postmessage_"))
            if not content_td:
                continue

            # Get the raw text content
            post_content = content_td.text.strip()

            # Remove the registration/login prompts
            unwanted_texts = [
                "注册一亩三分地论坛，查看更多干货！",
                "您需要 登录 才可以下载或查看附件。没有帐号？注册账号",
            ]

            for text in unwanted_texts:
                post_content = post_content.replace(text, "")

            # Clean up extra whitespace and newlines
            lines = [line.strip() for line in post_content.splitlines() if line.strip()]
            post_content = "  ".join(lines)  # Join with double spaces instead of newlines

            if post_content:  # Only add non-empty posts
                parsed_posts.append(post_content)

        return parsed_posts
    except AttributeError as e:
        print(Fore.RED + f"Error parsing posts: {e}")
        return []


def get_thread_title(soup):
    """Extract thread title from the HTML."""
    try:
        thread_title = soup.find("span", id="thread_subject").text.strip()
        print(Fore.BLUE + f"thread title: {thread_title}")
        return thread_title
    except AttributeError as e:
        print(f"Error parsing thread title: {e}")
        return None


def get_total_pages(soup):
    """Extract total number of pages from the thread."""
    try:
        # Find the span element that contains the total page count
        page_info = soup.find("span", title=lambda x: x and x.startswith("共"))
        if page_info:
            # Extract just the number from the text (e.g., "41 页" -> "41")
            total_pages = int(page_info.text.strip(" /页"))
            print(Fore.BLUE + f"Total pages: {total_pages}")
            return total_pages
        return 1  # If no page info found, assume it's just one page
    except (AttributeError, ValueError) as e:
        print(Fore.RED + f"Error parsing page count: {e}")
        return 1


def crawl_thread(thread_id):
    """Crawl a thread including its replies across pages."""
    # Get the first page to extract title and total pages
    first_page = fetch_thread(thread_id, reply_page=1)
    if not first_page:
        return None, []

    # Get thread title
    thread_title = get_thread_title(first_page)

    # Get total number of pages
    total_pages = get_total_pages(first_page)

    all_replies = []

    # Iterate through all pages
    for page in range(1, total_pages + 1):
        if page == 1:
            soup = first_page  # Reuse the first page we already fetched
        else:
            # Random delay between 3 and 7 seconds
            wait_time = random.uniform(3, 7)
            print(Fore.YELLOW + f"Waiting {wait_time:.2f} seconds before next request...")
            sleep(wait_time)

            soup = fetch_thread(thread_id, reply_page=page)
            if not soup:
                print(Fore.YELLOW + "Taking a longer break before continuing...")
                sleep(random.uniform(10, 15))  # Longer break if request fails
                continue

        posts = parse_thread(soup)
        print(Fore.BLUE + f"Page {page}/{total_pages}: {len(posts)} posts")

        if len(posts) == 0:
            break  # Stop if no posts found on current page

        all_replies.extend(posts)

    print(Fore.BLUE + f"Crawled thread {thread_id} with {len(all_replies)} replies across {total_pages} pages.")

    return thread_title, all_replies


if __name__ == "__main__":
    # thread_ids = [1103788] # 1 page of replies
    thread_ids = [286214]
    for thread_id in thread_ids:
        crawl_thread(thread_id)

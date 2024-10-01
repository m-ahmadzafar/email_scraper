import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse
from collections import deque

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_domain(url):
    parsed = urlparse(url)
    return parsed.netloc

def get_all_website_links(url, domain):
    urls = set()
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return urls

        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.findAll("a"):
            href = a_tag.attrs.get("href")
            if href == "" or href is None:
                continue
            href = urljoin(url, href)
            parsed_href = urlparse(href)
            href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
            if is_valid(href) and domain in href:
                urls.add(href)
    except Exception as e:
        print(f"An error occurred: {e}")
    return urls

def scrape_emails(url):
    emails = set()
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return emails

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = ' '.join(element.get_text() for element in soup.find_all())
        email_regex = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}'
        emails.update(re.findall(email_regex, text_content))
    except Exception as e:
        print(f"An error occurred: {e}")
    return emails

def crawl_website(start_url):
    visited = set()
    queue = deque([start_url])
    all_emails = set()
    domain = get_domain(start_url)

    while queue:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        print(f"Crawling: {url}")
        emails = scrape_emails(url)
        all_emails.update(emails)

        links = get_all_website_links(url, domain)
        for link in links:
            if link not in visited:
                queue.append(link)

    return all_emails

def save_emails_to_file(emails, filename):
    try:
        with open(filename, 'w') as file:
            for email in emails:
                file.write(f"{email}\n")
        print(f"Emails saved to {filename}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

if __name__ == "__main__":
    domain = input("Enter the website domain (e.g., https://example.com): ")
    emails = crawl_website(domain)
    if emails:
        save_emails_to_file(emails, "emails.txt")
    else:
        print("No emails found or failed to scrape the website.")

# import requests
# from bs4 import BeautifulSoup
# import re

# def scrape_emails(url):
#     try:
#         response = requests.get(url)
#         if response.status_code != 200:
#             print(f"Failed to retrieve the webpage: {response.status_code}")
#             return []

#         soup = BeautifulSoup(response.text, 'html.parser')
#         emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', soup.text)
#         return emails
#     except Exception as e:
#         print(f"An error occurred: {e}")
#         return []

# def save_emails_to_file(emails, filename):
#     try:
#         with open(filename, 'w') as file:
#             for email in emails:
#                 file.write(f"{email}\n")
#         print(f"Emails saved to {filename}")
#     except Exception as e:
#         print(f"An error occurred while writing to the file: {e}")

# if __name__ == "__main__":
#     domain = input("Enter the website domain (e.g., https://example.com): ")
#     emails = scrape_emails(domain)
#     if emails:
#         save_emails_to_file(emails, "emails.txt")
#     else:
#         print("No emails found or failed to scrape the website.")

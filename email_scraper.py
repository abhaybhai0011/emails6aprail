import asyncio
import csv
import re

from playwright.async_api import async_playwright

# ScraperAPI Keys
SCRAPER_API_KEYS = [
    "07ec776ae12695df16fe4b68c7faa34c",
    "c9f3d4cd30f9152105ca4d292060d8ec"
]
SCRAPER_API_URL = "http://api.scraperapi.com?api_key={api_key}&url={url}"

EMAIL_SAVE_FILE = "emails.csv"
LINK_FILE = "link.txt"
found_emails_set = set()  # For duplicate filtering
api_index = 0  # Used for rotating API keys


def read_links():
    try:
        with open(LINK_FILE, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"⚠️ Link file '{LINK_FILE}' not found.")
        return []


def save_emails(emails):
    global found_emails_set
    new_emails = [email for email in emails if email not in found_emails_set]

    if new_emails:
        try:
            with open(EMAIL_SAVE_FILE, "a", newline="") as file:
                writer = csv.writer(file)
                for email in new_emails:
                    writer.writerow([email])
            found_emails_set.update(new_emails)
            print(f"💾 Saved {len(new_emails)} new emails: {new_emails}")
        except Exception as e:
            print(f"❌ Error saving emails: {e}")


def remove_link(link):
    try:
        links = read_links()
        if link in links:
            links.remove(link)
            with open(LINK_FILE, "w") as file:
                file.write("\n".join(links))
    except Exception as e:
        print(f"❌ Error removing link: {e}")


def extract_emails(text):
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    return list(set(re.findall(email_pattern, text)))


async def scrape_page(link, api_key):
    final_url = SCRAPER_API_URL.format(api_key=api_key, url=link)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print(f"🌐 Visiting: {link} via ScraperAPI (key: {api_key[-4:]})")
            await page.goto(final_url, timeout=30000)
            await page.wait_for_load_state("domcontentloaded")

            content = await page.content()
            emails = extract_emails(content)

            if emails:
                print(f"✅ Emails found: {emails}")
                save_emails(emails)
            else:
                print(f"ℹ️ No emails found on: {link}")

            await browser.close()
            return True
        except Exception as e:
            print(f"❌ Error scraping {link}: {e}")
            await browser.close()
            return False


async def main():
    global api_index

    links = read_links()
    if not links:
        print("⚠️ No links found. Exiting...")
        return

    for link in links:
        current_api_key = SCRAPER_API_KEYS[api_index % len(SCRAPER_API_KEYS)]
        success = await scrape_page(link, current_api_key)

        if success:
            remove_link(link)

        api_index += 1  # Rotate API key


if __name__ == "__main__":
    asyncio.run(main())

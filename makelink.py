# dynamic_link_generator.py

import os

# Generate links with fixed category list in the base URL
def generate_links(from_subs, to_subs, min_views_7_days):
    base_url = "https://playboard.co/en/search?country=IN&&category=20&category=28&category=26&category=23"
    links = []

    for start in range(from_subs, to_subs, 2000):
        end = min(start + 2000, to_subs)
        sub_range = f"{start}%3A{end}"
        view_range = f"{min_views_7_days}%3A"
        full_url = f"{base_url}&subscribers={sub_range}&play7={view_range}&sortTypeId=1"
        links.append(full_url)

    return links

# Save only unique links without removing old ones
def save_links(new_links, filename="link.txt"):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            existing_links = set(line.strip() for line in file if line.strip())
    else:
        existing_links = set()

    unique_links = [link for link in new_links if link not in existing_links]

    if unique_links:
        with open(filename, "a", encoding="utf-8") as file:
            for link in unique_links:
                file.write(link + "\n")

    print(f"{len(unique_links)} new unique link(s) added to {filename}.")

def main():
    from_subs = int(input("Enter the FROM subscriber base (e.g., 20000): "))
    to_subs = int(input("Enter the TO subscriber base (e.g., 30000): "))
    min_views_7_days = int(input("Enter the minimum views in 7 days (e.g., 80000): "))

    links = generate_links(from_subs, to_subs, min_views_7_days)
    save_links(links)

if __name__ == "__main__":
    main()

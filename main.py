import ru_local as RU
import csv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def parse_search(query):
    """
    Parses the search page for a given query and returns a list of products.

    Args:
        query (str): Search query.

    Returns:
        list[dict]: A list of dictionaries with product data.
        Each dictionary contains keys.:
            - name (str): product name
            - link (str): link to the product card
            - price (str): current price
            - old_price (str | None): old price (if any)
            - article (str | None): article number
            - vendor (str | None): manufacturer
            - image (str | None): image link
    """
    base_url = "https://obuv-tut2000.ru/magazin/search?gr_smart_search=1&search_text="
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page_num = 1
        while True:
            url = f"{base_url}{query}&page={page_num}"
            page.goto(url, wait_until="domcontentloaded", timeout=60000)

            try:
                page.wait_for_selector(".shop2-product-item.product-item", timeout=5000)
            except:
                break

            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.select(".shop2-product-item.product-item")

            if not cards:
                break

            for card in cards:
                name_tag = card.select_one(".gr-product-name a")
                price_tag = card.select_one(".product-price .price-current strong")
                old_price_tag = card.select_one(".product-price .price-old strong")
                article_tag = card.select_one(".product-article")
                vendor_tag = card.select_one(".gr-vendor-block")
                img_tag = card.select_one(".gr-product-image img")

                products.append({
                    "name": name_tag.get_text(strip=True) if name_tag else None,
                    "link": "https://obuv-tut2000.ru" + name_tag["href"] if name_tag else None,
                    "price": price_tag.get_text(strip=True) if price_tag else None,
                    "old_price": old_price_tag.get_text(strip=True) if old_price_tag else None,
                    "article": article_tag.get_text(strip=True).replace("Артикул:", "").strip() if article_tag else None,
                    "vendor": vendor_tag.get_text(strip=True) if vendor_tag else None,
                    "image": "https://obuv-tut2000.ru" + img_tag["src"] if img_tag else None
                })

            page_num += 1

        browser.close()

    return products


def save_to_csv(products, filename):
    """
    Saves a list of products to a CSV file.

    Args:
        products (list[dict]): List of dictionaries with product data.
        filename (str): Name of the file to save.
    """
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=products[0].keys())
        writer.writeheader()
        writer.writerows(products)


if __name__ == "__main__":
    query = input(f"{RU.SEARC_QUERY}").strip()
    products = parse_search(query)

    if not products:
        print(f"RU.NO_PRODUCTS")
    else:
        filename = f"{query}_products.csv"
        save_to_csv(products, filename)
        print(f"{RU.PRODCUTS_FOUND} {len(products)}")
        print(f"{RU.DATA_FILE} {filename}")

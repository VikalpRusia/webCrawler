"""Client for sending request to server"""
import argparse
import sys

import requests


def main(url):
    """sends request to server"""
    response = requests.post('http://localhost:8001/api/v1/crawl/', json={'url': url})
    if response.status_code == 200:
        print_sitemap(response.json(), url)
    elif response.status_code == 404:
        print_error(f"Error in the URL: {url}")
        sys.exit(1)
    elif response.status_code == 207:
        resp = response.json()
        print_sitemap(resp.get("sitemap"), url)
        print_error("----- ERROR ------")
        print_errors(resp.get("errors"))
        sys.exit(2)
    else:
        print_error("Something went wrong, check the server/client logs")
        sys.exit(3)


def print_sitemap(sitemap, root, indent=0):
    """recursively prints sitemap"""
    print(' ' * indent + root)
    for link in sitemap.get(root, []):
        print_sitemap(sitemap, link, indent + 2)


def print_errors(errors):
    """prints errors"""
    for error_url, error in errors.items():
        print_error(f"{error_url} caused due to {error}")


def print_error(message):
    "prints error to stderr"
    print(message, file=sys.stderr)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Crawler Client')
    parser.add_argument('url', type=str, help='The URL to start crawling from')
    args = parser.parse_args()

    main(args.url)

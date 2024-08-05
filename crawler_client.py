import aiohttp
import asyncio
import argparse


async def main(url):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://localhost:8000/api/v1/crawl/', json={'url': url}) as response:
            sitemap = await response.json()
            print_sitemap(sitemap, url)


def print_sitemap(sitemap, root, indent=0):
    print(' ' * indent + root)
    for link in sitemap.get(root, []):
        print_sitemap(sitemap, link, indent + 2)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Crawler Client')
    parser.add_argument('url', type=str, help='The URL to start crawling from')
    args = parser.parse_args()

    asyncio.run(main(args.url))

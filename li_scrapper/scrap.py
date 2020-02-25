from .modules.linked_in_scraper.linked_in_scraper import LinkedInScraper
import json


def main(cookie, profile_url):
    scraper = LinkedInScraper(cookie)

    scraper.init_driver()
    scraper.login()

    user_data = scraper.parse_profile(profile_url)

    f = open('user_data.json', 'w')
    f.write(json.dumps(user_data))
    f.close()

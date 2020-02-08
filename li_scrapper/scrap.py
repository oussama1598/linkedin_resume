from .modules.linked_in_scraper.linked_in_scraper import LinkedInScraper


def main():
    COOKIE = "AQEDASGcJcQCjGQfAAABbuaqNVgAAAFwIZOw6E0AUvdZfrkE0qInEqLsEJIUGgQESTVE1FhQIQjI2ReVi05CpwKVVReY3jtuWoS1-TxkH3flC8yY72bpDWnwOroZ1nF3qE_fdl-YZ5yS8Iic7UQf0yE2"

    scraper = LinkedInScraper(COOKIE)

    scraper.init_driver()
    scraper.login()

    print(scraper.parse_profile('https://www.linkedin.com/in/oussama-b-318a14138/'))

import os
import argparse
import logging
import json
from urllib.parse import urlparse
from app.modules.linked_in_scraper import LinkedInScraper

from dotenv import load_dotenv

from app.controllers.tex_generator import generate_tex_file_from_data


def main(args):
    logging.basicConfig(level=logging.INFO)

    parsed_url = urlparse(args.profile)

    if parsed_url.netloc != 'linkedin.com' and parsed_url.netloc != 'www.linkedin.com' or "/in/" not in args.profile:
        return logging.error("Not a valid linkedin url.")

    load_dotenv()

    if not args.skip:
        scraper = LinkedInScraper(os.getenv("COOKIE"))

        scraper.init_driver()
        scraper.login()

        user_data = scraper.parse_profile(args.profile)

        with open('user_data.json', 'w') as file:
            file.write(json.dumps(user_data, indent=3))

    generate_tex_file_from_data(
        "user_data.json",
        os.path.join(args.saveto, "resume.pdf"),
        "awesome-cv"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('profile', type=str, help='The link of a linkedin profile.')
    parser.add_argument('--template', '-t', default="awesome-cv",
                        help='The template to be used.')
    parser.add_argument('--saveto', '-s', default=os.getcwd(),
                        help='Where to save the ouputed pdf file.')
    parser.add_argument('--skip', '-sk', default=False, const=True, nargs='?',
                        help='Skip the scraping, note that the user_data.json has to exist.')

    arguments = parser.parse_args()

    main(arguments)

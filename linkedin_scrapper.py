from dotenv import load_dotenv
import os
from li_scrapper.scrap import main


if __name__ == "__main__":
    load_dotenv()

    main(os.getenv("COOKIE"), os.getenv("PROFILE_URL"))

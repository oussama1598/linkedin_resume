from dotenv import load_dotenv
import os
from li_scrapper.scrap import main

from app.modules.tex_generator import generate_tex_file_from_data

if __name__ == "__main__":
    # load_dotenv()
    #
    # main(os.getenv("COOKIE"), os.getenv("PROFILE_URL"))

    generate_tex_file_from_data(
        "jser_data.json",
        "resume.pdf",
        "awesome-cv"
    )

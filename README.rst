# LinkedIn Resume Generator
----

## Introduction

This sample python program, will enable anyone to build their own resume from everthing that is saved in their linkedin profile.
It's not the final version, it lacks the whole latex resume generation, at this stage it can only spit a json file containing the data.

# How to use

Clone this repo:
    
    - git clone https://github.com/oussama1598/linkedin_resume

Then install the necessary modules:
    
    - Install pipenv by following the instructions here: https://github.com/pypa/pipenv
    - Install the python packages by exceuting the command : 
        - pipenv install

Modify the cookie and the profile url in the .env file
    
    - Use your browser to signin into LinkedIn with the account you want to use for scraping.
    - After login, open your browser's Dev Tools and find the cookie with the name li_at. Remember the value of that cookie.
    - Set the PROFILE_URL variable with your profile's link

Run the script:
    
    - python shell
    - python linkedin_scrapper.py
    
This will generate your json's data

### NOTE: This is not the final version, and some errors may accure feel free to report any problem

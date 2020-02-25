import requests
import logging
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from .linked_in_constants import (LINKED_IN_URL, FULLNAME_XPATH, TITLE_XPATH, LOCATION_XPATH,
                                  PHOTO_XPATH, DESCRIPTION_XPATH, SKILLS_SHOW_MORE_BUTTON_XPATH, SKILLS_LIST_XPATH, EDUCATIONS_SHOW_MORE_BUTTON_XPATH, EDUCATIONS_LIST_XPATH)

logging.basicConfig(level=logging.INFO)


class LinkedInScraper:
    def __init__(self, _cookie):
        self.driver_options = webdriver.ChromeOptions()
        self.driver = None

        self.cookie = _cookie

    def init_driver(self):
        logging.info('Initializing the web driver')

        self.driver_options.add_argument('--log-level=3')
        self.driver_options.add_argument('--disable-logging')
        # self.driver_options.add_argument('--headless')

        # self.driver_options.add_experimental_option('prefs', {
        #     'profile.managed_default_content_settings.images': 2
        # })

        try:
            self.driver = webdriver.Chrome(chrome_options=self.driver_options)
        except:
            logging.error('Couldn\'t Initialize the web driver')

    def set_login_cookie(self):
        self.driver.add_cookie({'name': 'li_at', 'value': self.cookie})

    def login(self):
        self.driver.get(LINKED_IN_URL)
        self.set_login_cookie()
        self.driver.get(LINKED_IN_URL)

        input_field = self.driver.find_elements_by_class_name('input__field')

        if len(input_field) > 0:
            logging.error('Invalid cookie')

            self.driver.close()

    def wait_for_element_by_xpath(self, element_xpath):
        tries = 0
        element = self.driver.find_elements_by_xpath(element_xpath)

        while len(element) <= 0:
            element = self.driver.find_elements_by_xpath(element_xpath)
            tries += 1

            if tries > 2:
                print(f'Can\'t find {element_xpath}')

                return None

        return element[0]

    def get_skills(self):
        skills = {}

        skills_show_more_button = self.driver.find_elements_by_css_selector(
            SKILLS_SHOW_MORE_BUTTON_XPATH)

        while len(skills_show_more_button) <= 0:
            skills_show_more_button = self.driver.find_elements_by_css_selector(
                SKILLS_SHOW_MORE_BUTTON_XPATH)

        self.driver.execute_script(
            'arguments[0].click()', skills_show_more_button[0])

        skills_list = self.driver.find_elements_by_css_selector(
            '.pv-skill-category-list.pv-profile-section__section-info')

        for skills_category in skills_list:
            skill_title = skills_category.find_element_by_css_selector(
                '.pv-skill-categories-section__secondary-skill-heading').text

            skills[skill_title] = [
                el.text for el in skills_category.find_elements_by_class_name('pv-skill-category-entity__name-text')]

        return skills

    def get_educations(self):
        educations = []

        educations_list = self.driver.find_elements_by_css_selector(
            '#education-section ul > .ember-view')

        for education in educations_list:
            school_name_el = education.find_elements_by_class_name(
                'pv-entity__school-name')
            degree_name_el = education.find_elements_by_class_name(
                'pv-entity__degree-name')
            field_of_study_el = education.find_elements_by_class_name(
                'pv-entity__fos')
            dates_el = education.find_elements_by_css_selector(
                '.pv-entity__dates')

            school_name = None
            degree_name = None
            field_of_study = None
            start_date = None
            end_date = None

            if len(school_name_el) > 0:
                school_name = school_name_el[0].text

            if len(degree_name_el) > 0:
                degree_name = degree_name_el[0].find_element_by_class_name(
                    'pv-entity__comma-item').text

            if len(field_of_study_el) > 0:
                field_of_study = field_of_study_el[0].find_element_by_class_name(
                    'pv-entity__comma-item').text

            if len(dates_el) > 0:
                dates = dates_el[0].find_elements_by_css_selector('time')

                start_date = dates[0].text if len(dates) > 0 else None
                end_date = dates[1].text if len(dates) > 1 else None

            educations.append({
                "schoolName": school_name,
                "degreeName": degree_name,
                "fieldOfStudy": field_of_study,
                "startDate": start_date,
                "endDate": end_date
            })

        return educations

    def get_experiences(self):
        experiences = []

        experience_list = self.driver.find_elements_by_css_selector(
            '#experience-section ul > .ember-view')

        for experience in experience_list:
            title_el = experience.find_elements_by_css_selector('h3')
            company_el = experience.find_elements_by_css_selector(
                '.pv-entity__secondary-title')
            description_el = experience.find_elements_by_css_selector(
                '.pv-entity__description')
            location_el = experience.find_elements_by_css_selector(
                '.pv-entity__location span:nth-child(2)')
            date_range_el = experience.find_elements_by_css_selector(
                '.pv-entity__date-range span:nth-child(2)')

            title = None
            company = None
            description = None
            location = None
            start_date = None
            end_date = None

            if len(title_el) > 0:
                title = title_el[0].text

            if len(company_el) > 0:
                company = company_el[0].text

            if len(description_el) > 0:
                description = description_el[0].text

            if len(location_el) > 0:
                location = location_el[0].text

            if len(date_range_el) > 0:
                dates = date_range_el[0].text.split('–')

                start_date = dates[0] if len(dates) > 0 else None
                end_date = dates[1] if len(dates) > 1 else None

            experiences.append({
                "title": title,
                "company": company,
                "description": description,
                "location": location,
                "start_date": start_date,
                "end_date": end_date
            })

        return experiences

    def parse_profile(self, profile_url):
        user_data = {'userProfile': {}}

        logging.info(f'Parsing {profile_url}')

        self.driver.get(profile_url)

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        see_more_buttons = self.driver.find_elements_by_css_selector(
            'button.pv-profile-section__see-more-inline.pv-profile-section__text-truncate-toggle.link')

        for see_more_button in see_more_buttons:
            self.driver.execute_script('arguments[0].click()', see_more_button)

        fullname = self.driver.find_element_by_css_selector(
            FULLNAME_XPATH).text
        title = self.driver.find_element_by_css_selector(TITLE_XPATH).text
        location = self.driver.find_element_by_css_selector(
            LOCATION_XPATH).text
        photo = self.driver.find_element_by_css_selector(
            PHOTO_XPATH).get_attribute('src')
        description = self.driver.find_element_by_css_selector(
            DESCRIPTION_XPATH).text

        user_data['userProfile']['fullname'] = fullname
        user_data['userProfile']['title'] = title
        user_data['userProfile']['location'] = location
        user_data['userProfile']['photo'] = photo
        user_data['userProfile']['description'] = description

        user_data["educations"] = self.get_educations()
        user_data["skills"] = self.get_skills()
        user_data["experiences"] = self.get_experiences()

        return user_data

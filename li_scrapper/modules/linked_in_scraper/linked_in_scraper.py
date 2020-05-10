import logging
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .linked_in_constants import SKILLS_SHOW_MORE_BUTTON_XPATH

LINKED_IN_URL = 'https://www.linkedin.com/'

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

    def text_or_none(self, element):
        if element:
            return element.text

        return ""

    def wait_for(self, css_selector):
        try:
            return WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
            )
        except:
            return None

    def get_element(self, css_selector, parent=None):
        elements = []

        if parent:
            elements = parent.find_elements_by_css_selector(css_selector)
        else:
            elements = self.driver.find_element_by_css_selector(css_selector)

        if len(elements) > 0:
            return elements[0]

        return None

    def get_user_data(self):
        user_profile = {}

        user_profile['fullname'] = self.text_or_none(
            self.driver.find_element_by_css_selector('.pv-top-card--list > li'))
        user_profile['title'] = self.text_or_none(self.driver.find_element_by_css_selector('.ph5.pb5 .mt1'))
        user_profile['location'] = self.text_or_none(
            self.driver.find_element_by_css_selector('.pv-top-card--list.pv-top-card--list-bullet.mt1 > li'))
        user_profile['photo'] = self.driver.find_element_by_css_selector(
            '.profile-photo-edit__preview.ember-view').get_attribute('src')
        user_profile['about'] = self.text_or_none(
            self.driver.find_element_by_css_selector('.pv-about__summary-text.mt4.t-14.ember-view'))

        self.driver.find_element_by_css_selector("a[data-control-name='contact_see_more']").click()

        linkedin_url_element = self.wait_for('.ci-vanity-url a')
        linkedin_url = linkedin_url_element.get_attribute('href')

        user_profile['linkedin_username'] = linkedin_url.split('/')[-1]
        user_profile['linkedin_link'] = linkedin_url

        email_element = self.wait_for('.ci-email a')
        user_profile['email'] = self.text_or_none(email_element)

        websites_element = self.wait_for('.ci-websites')
        user_profile['websites'] = {}

        for website in websites_element.find_elements_by_css_selector('li'):
            website_link = website.find_element_by_css_selector('a').get_attribute('href')
            website_type = self.text_or_none(website.find_element_by_css_selector('span')) \
                .strip().replace('(', '').replace(')', '').lower()

            user_profile['websites'][website_type] = website_link

        numbers_element = self.wait_for('.ci-phone')
        user_profile['numbers'] = {}

        for phone in numbers_element.find_elements_by_css_selector('li'):
            phone_number = self.text_or_none(phone.find_elements_by_css_selector('span')[0])
            phone_type = self.text_or_none(phone.find_elements_by_css_selector('span')[1]) \
                .strip().replace('(', '').replace(')', '').lower()

            user_profile['numbers'][phone_type] = phone_number

        self.driver.find_element_by_css_selector("button.artdeco-modal__dismiss").click()

        return user_profile

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

            school_name = ""
            degree_name = ""
            field_of_study = ""
            start_date = ""
            end_date = ""

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

                start_date = dates[0].text if len(dates) > 0 else ""
                end_date = dates[1].text if len(dates) > 1 else ""

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

            title = ""
            company = ""
            description = ""
            location = ""
            start_date = ""
            end_date = ""

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

                start_date = dates[0] if len(dates) > 0 else ""
                end_date = dates[1] if len(dates) > 1 else ""

            experiences.append({
                "title": title,
                "company": company,
                "description": description,
                "location": location,
                "start_date": start_date,
                "end_date": end_date
            })

        return experiences

    def get_projects(self):
        projects = []

        expand_button = self.wait_for('button[aria-controls="projects-expandable-content"]')

        if not expand_button:
            return []

        self.driver.execute_script('arguments[0].click()', expand_button)

        projects_list = self.driver.find_elements_by_css_selector(
            '#projects-expandable-content ul > .ember-view')

        for project in projects_list:
            title = ""
            description = ""
            external_link = ""
            start_date = ""
            end_date = ""

            title_el = self.get_element('.pv-accomplishment-entity__title', project)

            if title_el:
                self.driver.execute_script('arguments[0].remove()', title_el.find_element_by_css_selector('span'))
                title = self.text_or_none(title_el)

            description_el = self.get_element('.pv-accomplishment-entity__description', project)

            if description_el:
                self.driver.execute_script('arguments[0].remove()', description_el.find_element_by_css_selector('div'))
                description = self.text_or_none(description_el)

            external_link_el = self.get_element('.pv-accomplishment-entity__external-source', project)

            if external_link_el:
                external_link = external_link_el.get_attribute('href')

            date_range_el = self.get_element('.pv-accomplishment-entity__date', project)

            if date_range_el:
                dates = self.text_or_none(date_range_el).split('–')

                start_date = dates[0] if len(dates) > 0 else ""
                end_date = dates[1] if len(dates) > 1 else ""

            projects.append({
                "title": title,
                "description": description,
                "external_link": external_link,
                "start_date": start_date.strip(),
                "end_data": end_date.strip()
            })

        return projects

    def parse_profile(self, profile_url):
        user_data = {}

        logging.info(f'Parsing {profile_url}')

        self.driver.get(profile_url)

        user_data['user_profile'] = self.get_user_data()

        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")

        see_more_buttons = self.driver.find_elements_by_css_selector(
            'button.pv-profile-section__see-more-inline.pv-profile-section__text-truncate-toggle.link')

        for see_more_button in see_more_buttons:
            self.driver.execute_script('arguments[0].click()', see_more_button)

        user_data["educations"] = self.get_educations()
        user_data["skills"] = self.get_skills()
        user_data["experiences"] = self.get_experiences()
        user_data["projects"] = self.get_projects()

        return user_data

from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxProfile


class scraper_base:
    def __init__(self):
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-background-networking")
        self.profile = FirefoxProfile()
        self.profile.set_preference("permission.default.image", 2)
        self.options.profile = self.profile




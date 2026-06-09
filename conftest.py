import pytest
import yaml
from appium import webdriver
from appium.options import AppiumOptions


def load_capabilities(platform: str) -> dict:
    with open(f"capabilities/{platform}.yaml", "r") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="session")
def android_driver():
    caps = load_capabilities("android")
    options = AppiumOptions()
    for k, v in caps.items():
        setattr(options, k, v)
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()


@pytest.fixture(scope="session")
def ios_driver():
    caps = load_capabilities("ios")
    options = AppiumOptions()
    for k, v in caps.items():
        setattr(options, k, v)
    driver = webdriver.Remote("http://127.0.0.1:4723", options=options)
    yield driver
    driver.quit()

def pytest_addoption(parser):
    parser.addoption("--skip-slow", action="store_true", help="skip slow tests")

*** Settings ***
Library       library/Log.py

*** Test Cases ***
Selenium Screenshot test
    Item Log  INFO  </td></tr><tr><td colspan="3"><a href="examples/res/selenium-screenshot-1.png"><img src="examples/res/selenium-screenshot-1.png" width="800px"></a>  None  True
Playwright Screenshot test
    Item Log  INFO  </td></tr><tr><td colspan="3"><a href="examples/res/Screenshot_test_FAILURE_SCREENSHOT_1.png" target="_blank"><img src="examples/res/Screenshot_test_FAILURE_SCREENSHOT_1.png" width="800px"/></a>  None  True

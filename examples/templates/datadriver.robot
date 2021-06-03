*** Settings ***
Documentation  Test templates defined through DataDriver and external CSV file
Library        DataDriver
Resource       test_keywords.robot
Test Template  Login invalid credentials

*** Test Cases ***
Login with user '${username}' and password '${password}'

*** Keywords ***
Login invalid credentials
    [Arguments]  ${username}                                 ${password}
    Run Keyword  Login with invalid credentials should fail  ${username}  ${password}

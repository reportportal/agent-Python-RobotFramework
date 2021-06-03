*** Settings ***
Documentation  Test templates defined through keyword
Resource       test_keywords.robot

*** Test Cases ***
Invalid Password
    [Template]     Login with invalid credentials should fail
    invalid        ${VALID PASSWORD}
    ${VALID USER}  invalid
    invalid        invalid
    ${EMPTY}       ${VALID PASSWORD}
    ${VALID USER}  ${EMPTY}
    ${EMPTY}       ${EMPTY}

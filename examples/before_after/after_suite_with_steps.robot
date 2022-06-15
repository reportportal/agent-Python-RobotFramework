*** Settings ***
Suite Teardown    Log suite tear down

*** Test Cases ***
My first test
    Log    My first test

*** Keywords ***
Log suite tear down
    Log    Suite tear down step

*** Settings ***
Suite Setup       Log suite setup

*** Test Cases ***
My first test
    Log    My first test

*** Keywords ***
Log suite setup
    Fail    Suite setup step

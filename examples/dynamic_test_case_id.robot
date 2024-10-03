*** Settings ***
Documentation  Example of setting Test Case ID in runtime
Library        library/TestCaseId.py

*** Test Cases ***
Test set dynamic Test Case ID
    Case Id   dynamic_tags.robot[{scope_var}]

*** Settings ***
Documentation  Example of 'Wait Until Keyword Succeeds' keyword reporting

*** Variables ***
${countval}  0

*** Test Cases ***
Wuks test
    Wait Until Keyword Succeeds     2x                  200ms               Fail on first try

*** Keywords ***
Fail on first try
    ${counter}                      Evaluate            ${countval} + 1
    Set Suite Variable              ${countval}         ${counter}
    IF                              ${countval} < 3
                                    Fail                To less executions
    END

*** Settings ***
Documentation  Example of failing 'Wait Until Keyword Succeeds' keyword reporting

*** Variables ***
${countval}  0

*** Test Cases ***
Wuks test
    Wait Until Keyword Succeeds     3x                  200ms               Fail on first try

*** Keywords ***
Fail on first try
    ${counter}                      Evaluate            ${countval} + 1
    Set Suite Variable              ${countval}         ${counter}
    IF                              ${countval} < 4
                                    Fail                To less executions
    END

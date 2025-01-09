*** Settings ***
Documentation  Example of 'Run Keyword And Ignore Error' keyword reporting

*** Variables ***
${countval}  0

*** Test Cases ***
Rkie test
    Run Keyword And Ignore Error    Fail on first try
    Fail on first try

*** Keywords ***
Fail on first try
    ${counter}                      Evaluate            ${countval} + 1
    Set Suite Variable              ${countval}         ${counter}
    IF                              ${countval} < 2
                                    Log                 To less executions error  ERROR
                                    Fail                To less executions
    END

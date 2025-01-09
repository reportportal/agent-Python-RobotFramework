*** Settings ***
Documentation  Example of logging on binary file read
Library        library/Log.py
Library        OperatingSystem

*** Variables ***
${PUG_IMAGE}        res/pug/lucky.jpg

*** Keywords ***
Read Binary File
    [Tags]          binary
    [Arguments]     ${file}
    ${data}         Get Binary File     ${file}
    Binary Log      INFO                image    pug.jpg  ${data}

*** Test Cases ***
Read Pug Image
    Read Binary File    ${PUG_IMAGE}

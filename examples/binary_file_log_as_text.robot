*** Settings ***
Documentation  Example of logging on binary file read
Library        OperatingSystem

*** Variables ***
${PUG_IMAGE}        res/pug/lucky.jpg

*** Keywords ***
Read Binary File
    [Tags]          binary
    [Arguments]     ${file}
    ${data}         Get Binary File   ${file}
    Log             ${data}

*** Test Cases ***
Read Pug Image
    Read Binary File    ${PUG_IMAGE}

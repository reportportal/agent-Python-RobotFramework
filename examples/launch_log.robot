*** Settings ***
Documentation  Example of launch level logs
Library        library/Log.py
Library        OperatingSystem
Library        String

*** Variables ***
${PASS_MESSAGE}       Hello, world!
${ERROR_MESSAGE}      Goodbye, world!
${PUG_MESSAGE}        Enjoy my pug!
${PUG_IMAGE}          res/pug/lucky.jpg

*** Keywords ***
Get image
    [Arguments]    ${image}
    ${data}        Get Binary File    ${image}
    ${name}        Fetch From Right   ${image}               /
    ${result}      Create Dictionary
    ...            mime               image/jpeg
    ...            name               ${name}
    ...            data               ${data}
    [return]       ${result}

*** Test Cases ***
Launch log test
    Launch Log        INFO               ${PASS_MESSAGE}
    Launch Log        ERROR              ${ERROR_MESSAGE}
    ${log_image}      Get image          ${PUG_IMAGE}
    Launch Log        INFO               ${PUG_MESSAGE}      ${log_image}

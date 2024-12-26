*** Settings ***
Documentation  Example of 'WHILE' keyword reporting

*** Variables ***
@{fruits}  apple   banana  cherry

*** Test Cases ***
For test
    ${iter} =    Get Length          ${fruits}
    WHILE        ${iter} > 0
        ${iter}  Evaluate            ${iter} - 1
        Log      ${fruits}[${iter}]
    END

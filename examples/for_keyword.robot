*** Settings ***
Documentation  Example of 'FOR' keyword reporting

*** Variables ***
@{fruits}  apple   banana  cherry

*** Test Cases ***
For test
    FOR    ${var}  IN      @{fruits}
        Log    ${var}
    END

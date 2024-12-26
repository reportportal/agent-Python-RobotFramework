*** Settings ***
Documentation  Example of failing 'FOR' keyword reporting

*** Variables ***
@{fruits}  apple   banana  cherry

*** Test Cases ***
For test
    FOR    ${var}  IN      @{fruits}
           Log     ${var}
           IF      "${var}" == "banana"
                   Fail  Banana is not a fruit
           END
    END

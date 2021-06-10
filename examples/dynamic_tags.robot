*** Settings ***
Documentation  Example of setting test tags in runtime
Library        library/Log.py

*** Test Cases ***
Test tag set
    Item Log  INFO               A test with a tag set in runtime
    Set Tags  dynamic_tag
Test no tag
    Item Log  INFO               A test with no tags set
Test set multiple tags
    Item Log  INFO               A test with multiple tags set in runtime
    Set Tags  multiple_tags_one  multiple_tags_two

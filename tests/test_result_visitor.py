import pytest

from robotframework_reportportal.result_visitor import RobotResultsVisitor


class TestResultVisitorTest:

    @pytest.fixture()
    def visitor(self):
        return RobotResultsVisitor()

    def test_parse_message_no_img_tag(self, visitor):
        with pytest.raises(AttributeError):
            visitor.parse_message('usual test comment without image')

    def test_parse_message_bad_img_tag(self, visitor):
        with pytest.raises(AttributeError):
            visitor.parse_message('<img src=\'bad.html.img>')

    def test_parse_message_contains_image(self, visitor):
        assert ['src="any.png"', 'any.png'] == visitor.parse_message(
            '<img alt="" src="any.png" />')

    def test_parse_message_contains_image_with_space(self, visitor):
        assert ['src="any%20image.png"', 'any image.png'] == \
               visitor.parse_message('<img alt="" src="any%20image.png" />')

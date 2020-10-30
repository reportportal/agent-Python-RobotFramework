import unittest

from robotframework_reportportal.result_visitor import RobotResultsVisitor


class ResultVisitorTest(unittest.TestCase):
    def test_parse_message_empty(self):
        o = RobotResultsVisitor()
        self.assertRaises(AttributeError, o.parse_message, 'usual test comment without image')
        self.assertRaises(AttributeError, o.parse_message, '<img src=\'bad.html.img>')

    def test_parse_message_contains_image(self):
        o = RobotResultsVisitor()
        self.assertEqual(['src="any.png"', 'any.png'], o.parse_message('<img alt="" src="any.png" />'))

    def test_parse_message_contains_image_with_space(self):
        o = RobotResultsVisitor()
        self.assertEqual(['src="any%20image.png"', 'any image.png'],
                         o.parse_message('<img alt="" src="any%20image.png" />'))


if __name__ == '__main__':
    unittest.main()

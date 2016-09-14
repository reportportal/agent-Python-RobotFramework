class RobotServiceException(Exception):
    def __init__(self, *args, **kwargs):
        super(RobotServiceException, self).__init__(*args, **kwargs)
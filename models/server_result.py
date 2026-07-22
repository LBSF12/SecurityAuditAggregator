class ServerResult:
    """
    Store server metadata and compliance results.
    """

    def __init__(
        self,
        hostname=None,
        ip_addresses=None,
        execution_time=None
    ):

        self.hostname = hostname
        self.ip_addresses = ip_addresses or []
        self.execution_time = execution_time

        self.requirements = {}

    def add_result(self, requirement, status):
        self.requirements[requirement] = status

    def to_dict(self):
        return {
            "hostname": self.hostname,
            "ip_addresses": self.ip_addresses,
            "execution_time": self.execution_time,
            "requirements": self.requirements
        }
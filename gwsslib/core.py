import pprint


class Core(object):
    def __init__(self, logger):
        self.log = logger

    def test(self):
        print("test called")

    def missing_command(self, payload):
        self.log.warn("payload missing 'request'.")
        return {"reason": "request missing from payload - no command executed"}

    def stub(self, payload):
        self.log.info("running stub processing")
        self.log.debug(pprint.pformat(payload))
        return {"success": True}

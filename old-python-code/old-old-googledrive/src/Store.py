class Store:
    def __init__(self):
        self.state = {}

    def setState(self, payload):
        self.state.update(payload)

    def getState(self):
        return self.state

class Reducers:
    @staticmethod
    def sample(payload):
        return {
            'bla': payload
        }
    # => store.setState(Reducers.sample({ 'some': 'payload' }))

store = Store()
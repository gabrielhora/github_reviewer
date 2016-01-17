from app import app
import unittest


class FlaskrTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_ping(self):
        resp = self.app.get('/ping')
        assert resp.status_code == 200
        assert 'pong' in str(resp.data)


if __name__ == '__main__':
    unittest.main()

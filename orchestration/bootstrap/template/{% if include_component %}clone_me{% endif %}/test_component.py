import copy
import unittest
from clone_me.component import run


class ComponentSmokeTests(unittest.TestCase):
    def test_request_result_and_repeat(self):
        request = {"request_id": "smoke-1", "payload": {}}
        original = copy.deepcopy(request)
        expected = {"request_id": "smoke-1", "status": "ok", "payload": {}}
        self.assertEqual(run(request), expected)
        self.assertEqual(run(request), expected)
        self.assertEqual(request, original)

    def test_invalid_requests_fail_closed(self):
        for request in [None, {}, {"request_id": " ", "payload": {}},
                        {"request_id": 1, "payload": {}},
                        {"request_id": "x", "payload": []},
                        {"request_id": "x", "payload": {"value": 1}},
                        {"request_id": "x", "payload": {}, "extra": True}]:
            with self.subTest(request=request), self.assertRaises(ValueError):
                run(request)


if __name__ == "__main__":
    unittest.main()

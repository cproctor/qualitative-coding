from tests.fixtures import QCTestCase

class TestMemo(QCTestCase):
    def test_memo_saves_memo(self):
        self.set_mock_editor(verbose=True)
        self.run_in_testpath("qc memo chris")
        memo_files = list((self.testpath / "memos").iterdir())
        self.assertEqual(len(memo_files), 1)

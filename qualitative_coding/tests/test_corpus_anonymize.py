from tests.fixtures import QCTestCase
from qualitative_coding.corpus import QCCorpus
import yaml

NEWS = """A "hefty sneeze" has caused a professional footballer to sustain a 
"nasty back injury". Victor Adeboyejo, a striker for Bolton Wanderers, 
had been due to take part in a Bristol Street Motors Trophy group game at 
Barrow on Tuesday. He was forced to pull out of the squad, however, 
because of discomfort in his back and ribcage. Manager Ian Evatt, who was 
already missing first team players because of injury and the international 
break, said the pain appeared to have been caused by a "pretty hefty sneeze."
"""

class TestCorpusAnonymize(QCTestCase):
    def setUp(self):
        super().setUp()
        (self.testpath / "news.txt").write_text(NEWS)
        self.run_in_testpath("qc corpus import news.txt")
        self.run_in_testpath("qc corpus anonymize")

    def test_creates_key_file_with_yaml(self):
        keyfile = self.testpath / "key.yaml"
        self.assertTrue(keyfile.exists())
        keys = yaml.safe_load(keyfile.read_text())
        self.assertTrue("Victor Adeboyejo" in keys)

    def test_creates_anonymized_corpus(self):
        self.run_in_testpath("qc corpus anonymize")
        anon_news = (self.testpath / "anonymized" / "news.txt").read_text()
        self.assertTrue("Victor Adeboyejo" not in anon_news)

    def test_reverses_anonymization(self):
        self.run_in_testpath("qc corpus anonymize")
        self.run_in_testpath("qc corpus anonymize -r -o recovered")
        news = (self.testpath / "recovered" / "news.txt").read_text()
        self.assertTrue("Victor Adeboyejo" in news)

    def test_replaces_longer_strings_first(self):
        keyfile = self.testpath / "key.yaml"
        keyfile.write_text(yaml.dump({
            "Victor": "X",
            "Victor Adeboyejo": "VA"
        }))
        self.run_in_testpath("qc corpus anonymize")
        anon_news = (self.testpath / "anonymized" / "news.txt").read_text()
        self.assertTrue("Adeboyejo" not in anon_news)




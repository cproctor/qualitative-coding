from unittest import TestCase
from qualitative_coding.tree_node import TreeNode
from tempfile import TemporaryDirectory
import yaml
from pathlib import Path

class TestTreeNode(TestCase):
    def test_read_write_are_isomorphic(self):
        with TemporaryDirectory() as tempdir:
            for case in [EMPTY_CODEBOOK, FLAT_CODEBOOK, NESTED_CODEBOOK]:
                infile = Path(tempdir) / "in.yaml"
                outfile = Path(tempdir) / "out.yaml"
                infile.write_text(case)
                tn = TreeNode.read_yaml(infile)
                TreeNode.write_yaml(outfile, tn)
                self.assertEqual(outfile.read_text(), case)

EMPTY_CODEBOOK = "[]\n"
FLAT_CODEBOOK = """- a one
- b two
- c three
"""
NESTED_CODEBOOK = """- one:
  - a
  - b
  - c
- two:
  - d
"""
CASES = [EMPTY_CODEBOOK, FLAT_CODEBOOK, NESTED_CODEBOOK]

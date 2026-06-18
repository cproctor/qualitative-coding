from unittest import TestCase
from qualitative_coding.optional_deps import import_ai_dependency
from qualitative_coding.exceptions import QCError

class TestOptionalDeps(TestCase):
    def test_import_ai_dependency_returns_module_when_installed(self):
        module = import_ai_dependency("json", "Some feature")
        self.assertEqual(module.dumps({"a": 1}), '{"a": 1}')

    def test_import_ai_dependency_raises_qc_error_when_missing(self):
        with self.assertRaises(QCError) as ctx:
            import_ai_dependency("not_a_real_package", "Doing AI things")
        message = str(ctx.exception)
        self.assertIn("Doing AI things", message)
        self.assertIn("ai", message)
        self.assertIn("qualitative-coding[ai]", message)

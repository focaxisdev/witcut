"""Mutation tests for the repository validator, using isolated copies."""
from pathlib import Path
import importlib.util
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('witcut_validate', ROOT / 'scripts/validate.py')
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class PackageValidation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / 'package'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        self.addCleanup(self.temp.cleanup)

    def append_readme(self, text):
        with (self.root / 'README.md').open('a', encoding='utf-8') as stream:
            stream.write(text)

    def test_current_package_passes(self):
        self.assertEqual(validator.validate(self.root), [])

    def test_deleted_reference_is_detected(self):
        (self.root / 'skills/witcut/references/qa.md').unlink()
        errors = validator.validate(self.root)
        self.assertTrue(any('Missing file:' in e for e in errors))
        self.assertTrue(any('missing link target:' in e for e in errors))

    def test_link_cannot_depend_on_parent_machine_file(self):
        (self.root.parent / 'private.md').write_text('private', encoding='utf-8')
        self.append_readme('\n[Outside](../private.md)\n')
        self.assertTrue(any('escapes package' in e for e in validator.validate(self.root)))

    def test_nested_relative_links_resolve_from_document(self):
        self.assertEqual(validator.validate(self.root), [])
        self.append_readme('\n[Missing](references/qa.md)\n')
        self.assertTrue(any('missing link target' in e for e in validator.validate(self.root)))

    def test_skill_name_must_match_folder(self):
        entry = self.root / 'skills/witcut/SKILL.md'
        entry.write_text(entry.read_text().replace('name: witcut', 'name: wrong'), encoding='utf-8')
        self.assertTrue(any('name must match' in e for e in validator.validate(self.root)))

    def test_duplicate_frontmatter_fails(self):
        entry = self.root / 'skills/witcut/SKILL.md'
        entry.write_text(entry.read_text().replace('name: witcut', 'name: witcut\nname: witcut'), encoding='utf-8')
        self.assertTrue(any('duplicate field' in e for e in validator.validate(self.root)))

    def test_external_and_fragment_only_links_are_not_local_files(self):
        self.append_readme('\n[Web](https://example.invalid/no-check) [Section](#example)\n')
        self.assertEqual(validator.validate(self.root), [])


if __name__ == '__main__':
    unittest.main()

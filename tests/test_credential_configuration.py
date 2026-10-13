"""Offline checks for credentials, with no live logins or publications."""

import ast
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import runpy
import tempfile
import types
import unittest
from unittest.mock import patch

import requests

# Legacy package imports try to download NLTK corpora; keep this suite offline.
with patch("nltk.download", return_value=False):
    from pypubpub import Pubshelper_v6


ROOT = Path(__file__).resolve().parents[1]
UTILITIES = (
    "check_dois.py",
    "fix_doi_now.py",
    "fix_trailing_punctuation.py",
    "restore_dois.py",
    "restore_dois_proper.py",
)


class CredentialConfigurationTests(unittest.TestCase):
    def test_client_accepts_explicit_credentials(self):
        with patch.dict(os.environ, {}, clear=True):
            client = Pubshelper_v6(email="reader@example.invalid", password="fake-login")
        self.assertEqual(client.email, "reader@example.invalid")
        self.assertEqual(client.password, "fake-login")

    def test_client_reads_environment_when_arguments_are_omitted(self):
        values = {"PUBPUB_EMAIL": "reader@example.invalid", "PUBPUB_PASSWORD": "fake-login"}
        with patch.dict(os.environ, values, clear=True):
            client = Pubshelper_v6()
        self.assertEqual(client.email, values["PUBPUB_EMAIL"])
        self.assertEqual(client.password, values["PUBPUB_PASSWORD"])

    def test_missing_or_blank_client_credentials_fail_before_session_creation(self):
        for values in ({}, {"PUBPUB_EMAIL": "reader@example.invalid"},
                       {"PUBPUB_EMAIL": "reader@example.invalid", "PUBPUB_PASSWORD": " "}):
            with self.subTest(values_present=sorted(values)):
                with patch.dict(os.environ, values, clear=True), patch("requests.Session") as session:
                    with self.assertRaisesRegex(ValueError, "PUBPUB_EMAIL.*PUBPUB_PASSWORD"):
                        Pubshelper_v6()
                    session.assert_not_called()

    def test_explicit_blank_does_not_fall_back_to_environment(self):
        values = {"PUBPUB_EMAIL": "reader@example.invalid", "PUBPUB_PASSWORD": "fake-login"}
        with patch.dict(os.environ, values, clear=True):
            with self.assertRaises(ValueError):
                Pubshelper_v6(email="", password="")

    def test_login_does_not_print_credentials(self):
        client = Pubshelper_v6(email="reader@example.invalid", password="fake-login")
        response = types.SimpleNamespace(cookies={"session": "fake-cookie"})
        output = io.StringIO()
        with patch.object(client.requests, "post", return_value=response):
            with contextlib.redirect_stdout(output):
                client.login()
        self.assertNotIn(client.email, output.getvalue())
        self.assertNotIn(client.password, output.getvalue())
        self.assertNotIn("..XX..", output.getvalue())

    def test_utilities_reject_missing_or_blank_credentials_before_network(self):
        cases = (({}, KeyError),
                 ({"PUBPUB_EMAIL": "reader@example.invalid"}, KeyError),
                 ({"PUBPUB_EMAIL": "", "PUBPUB_PASSWORD": "fake-login"}, RuntimeError),
                 ({"PUBPUB_EMAIL": "reader@example.invalid", "PUBPUB_PASSWORD": " "}, RuntimeError))
        for filename in UTILITIES:
            for values, error_type in cases:
                with self.subTest(filename=filename, values_present=sorted(values)):
                    with patch.dict(os.environ, values, clear=True):
                        with patch.object(requests, "post") as post, patch.object(requests, "get") as get:
                            with self.assertRaises(error_type):
                                runpy.run_path(str(ROOT / "scripts" / "utilities" / filename))
                            post.assert_not_called()
                            get.assert_not_called()

    def test_notebook_pair_requires_explicit_credentials(self):
        notebook = json.loads((ROOT / "notebooks" / "tryingpubpubapi.ipynb").read_text())
        cell_source = next("".join(cell["source"]) for cell in notebook["cells"]
                           if "class Pubshelper:" in "".join(cell.get("source", [])))
        export = (ROOT / "notebooks" / "tryingpubpubapi.py").read_text()
        export = "\n".join("" if line.startswith("!") else line for line in export.splitlines())
        for source in (cell_source, export):
            tree = ast.parse(source)
            helper = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                          and node.name == "Pubshelper")
            namespace = {}
            exec(compile(ast.Module(body=[helper], type_ignores=[]), "notebook-helper", "exec"), namespace)
            with self.assertRaises(TypeError):
                namespace["Pubshelper"]()
            client = namespace["Pubshelper"](email="reader@example.invalid", password="fake-login")
            self.assertEqual(client.email, "reader@example.invalid")

    def test_setup_writes_supplied_coda_key_and_blank_pubpub_fields(self):
        fake_codaio = types.ModuleType("codaio")
        fake_codaio.Coda = object
        spec = importlib.util.spec_from_file_location("setup_coda_test", ROOT / "scripts/coda_integration/setup_coda.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict("sys.modules", {"codaio": fake_codaio}):
            spec.loader.exec_module(module)
        previous_cwd = os.getcwd()
        output = io.StringIO()
        try:
            with tempfile.TemporaryDirectory() as folder:
                os.chdir(folder)
                with contextlib.redirect_stdout(output):
                    module.create_env_file("fake-coda-key", "fake-doc", "fake-table")
                generated = Path(".env").read_text()
        finally:
            os.chdir(previous_cwd)
        self.assertIn("CODA_API_KEY=fake-coda-key\n", generated)
        self.assertIn("PUBPUB_EMAIL=\n", generated)
        self.assertIn("PUBPUB_PASSWORD=\n", generated)
        self.assertNotIn("fake-coda-key", output.getvalue())


if __name__ == "__main__":
    unittest.main()

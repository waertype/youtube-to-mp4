#!/usr/bin/env python3

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
import downloader


class TestValidation(unittest.TestCase):

    def test_url_http_valide(self):
        self.assertTrue(downloader.valider_url("https://www.youtube.com/watch?v=test"))

    def test_url_http_simple(self):
        self.assertTrue(downloader.valider_url("http://example.com/video"))

    def test_url_sans_protocol(self):
        self.assertFalse(downloader.valider_url("www.youtube.com"))

    def test_url_vide(self):
        self.assertFalse(downloader.valider_url(""))

    def test_url_sans_domaine(self):
        self.assertFalse(downloader.valider_url("https://localhost"))


class TestDetectionErreurs(unittest.TestCase):

    def test_erreur_age(self):
        self.assertTrue(downloader.est_erreur_age(Exception("age-restricted video")))
        self.assertTrue(downloader.est_erreur_age(Exception("sign in to confirm")))

    def test_pas_erreur_age(self):
        self.assertFalse(downloader.est_erreur_age(Exception("video not found")))

    def test_erreur_format(self):
        self.assertTrue(downloader.est_erreur_format(Exception("no formats available")))
        self.assertTrue(downloader.est_erreur_format(Exception("requested format is not available")))

    def test_erreur_cookie_db(self):
        self.assertTrue(downloader.est_erreur_cookie_db(Exception("could not copy")))
        self.assertTrue(downloader.est_erreur_cookie_db(Exception("cookie database")))


class TestOptsBase(unittest.TestCase):

    def test_opts_dossier_courant(self):
        opts = downloader.opts_base()
        self.assertIn("outtmpl", opts)
        self.assertIn("quiet", opts)
        self.assertIn("no_warnings", opts)
        self.assertIn("progress_hooks", opts)
        self.assertFalse(opts["quiet"])

    def test_opts_dossier_custom(self):
        opts = downloader.opts_base("/custom/path")
        self.assertIn("/custom/path", opts["outtmpl"])

    def test_opts_progress_hooks(self):
        opts = downloader.opts_base()
        self.assertIsInstance(opts["progress_hooks"], list)
        self.assertEqual(len(opts["progress_hooks"]), 1)


class TestUtilitaires(unittest.TestCase):

    def test_nom_navigateur_chrome(self):
        opts = {"cookiesfrombrowser": ("chrome",)}
        self.assertEqual(downloader.nom_navigateur_depuis_opts(opts), "Google Chrome")

    def test_nom_navigateur_firefox(self):
        opts = {"cookiesfrombrowser": ("firefox",)}
        self.assertEqual(downloader.nom_navigateur_depuis_opts(opts), "Mozilla Firefox")

    def test_nom_navigateur_absent(self):
        self.assertEqual(downloader.nom_navigateur_depuis_opts({}), "le navigateur")


class TestProgressHook(unittest.TestCase):

    @patch("builtins.print")
    def test_hook_downloading(self, mock_print):
        downloader.hook_progression({
            "status": "downloading",
            "_percent_str": " 45.0%",
            "_speed_str": " 2.5MiB/s",
            "_eta_str": "00:15",
        })
        mock_print.assert_called()

    @patch("builtins.print")
    def test_hook_finished(self, mock_print):
        downloader.hook_progression({"status": "finished", "filename": "/tmp/video.mp4"})
        mock_print.assert_called()

    @patch("builtins.print")
    def test_hook_error(self, mock_print):
        downloader.hook_progression({"status": "error"})
        mock_print.assert_called()


class TestStrategies(unittest.TestCase):

    def test_strategies_non_vides(self):
        self.assertGreater(len(downloader.STRATEGIES), 0)

    def test_strategies_format(self):
        for s in downloader.STRATEGIES:
            self.assertEqual(len(s), 4)
            self.assertIsInstance(s[0], str)
            self.assertIsInstance(s[1], dict)
            self.assertIsInstance(s[2], str)
            self.assertIsInstance(s[3], str)


class TestNavigateurs(unittest.TestCase):

    def test_navigateurs_non_vides(self):
        self.assertGreater(len(downloader.NAVIGATEURS), 0)

    def test_navigateurs_format(self):
        for key, (slug, nom) in downloader.NAVIGATEURS.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(slug, str)
            self.assertIsInstance(nom, str)


class TestExtensionsCookies(unittest.TestCase):

    def test_extensions_non_vides(self):
        self.assertGreater(len(downloader.EXTENSIONS_COOKIES), 0)

    def test_extensions_urls(self):
        for nav, url in downloader.EXTENSIONS_COOKIES.items():
            self.assertIn("http", url)


class TestMotsCles(unittest.TestCase):

    def test_mots_age(self):
        self.assertGreater(len(downloader.MOTS_AGE), 0)

    def test_mots_format(self):
        self.assertGreater(len(downloader.MOTS_FORMAT), 0)

    def test_mots_cookie_db(self):
        self.assertGreater(len(downloader.MOTS_COOKIE_DB), 0)


class TestIntegration(unittest.TestCase):

    def test_import_yt_dlp(self):
        import yt_dlp
        self.assertTrue(hasattr(yt_dlp, "YoutubeDL"))

    @patch("downloader.yt_dlp.YoutubeDL")
    def test_obtenir_info(self, mock_ydl):
        mock_instance = MagicMock()
        mock_instance.extract_info.return_value = {
            "title": "Test Video",
            "extractor_key": "youtube",
        }
        mock_ydl.return_value.__enter__.return_value = mock_instance
        result = downloader.obtenir_info("https://www.youtube.com/watch?v=test", {})
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
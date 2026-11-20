"""Minimalne testy publikowanej strony, bez zależności zewnętrznych."""
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPO_PREFIX = "/MatPomGit/app-eeg-mne/blob/main/"


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.lang = None
        self.tags = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        self.tags.append(tag)
        if "id" in props:
            self.ids.add(props["id"])
        if tag == "html":
            self.lang = props.get("lang")
        if tag in ("a", "link") and (url := props.get("href")):
            self.links.append(url)


class SiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (SITE / "index.html").read_text(encoding="utf-8")
        cls.parser = SiteParser()
        cls.parser.feed(cls.page)

    def test_semantic_document(self):
        self.assertEqual(self.parser.lang, "pl")
        for tag in ("main", "nav", "h1", "footer", "article"):
            self.assertIn(tag, self.parser.tags)
        self.assertIn("P3", self.page)
        self.assertIn("CSP", self.page)
        self.assertIn("LDA", self.page)

    def test_no_patronizing_disclaimers(self):
        for phrase in (
            "diagnozą kliniczną",
            "odczytywania myśli",
            "Nie należy utożsamiać",
            "<strong>Ważne:</strong>",
            'class="study-disclaimer"',
            'class="method-note"',
            'class="signal-footnote"',
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, self.page)

    def test_internal_anchors_and_assets(self):
        for href in self.parser.links:
            if href.startswith("#"):
                self.assertIn(href[1:], self.parser.ids, href)
            elif href == "./":
                continue
            elif not urlparse(href).scheme:
                self.assertTrue((SITE / href).is_file(), href)

    def test_repository_links_point_to_existing_files(self):
        for href in self.parser.links:
            parsed = urlparse(href)
            self.assertIn(parsed.scheme, ("", "https"), href)
            if parsed.netloc == "github.com" and parsed.path.startswith(REPO_PREFIX):
                path = ROOT / unquote(parsed.path[len(REPO_PREFIX):])
                self.assertTrue(path.is_file(), href)

    def test_no_executable_or_tracking_dependencies(self):
        self.assertNotIn("<script", self.page.lower())
        self.assertNotIn("http://", self.page.lower())
        self.assertTrue((SITE / "styles.css").is_file())
        self.assertTrue((SITE / ".nojekyll").is_file())


if __name__ == "__main__":
    unittest.main()

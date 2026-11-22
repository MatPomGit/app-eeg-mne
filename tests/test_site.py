"""Minimalne testy publikowanej strony, bez zależności zewnętrznych."""
import posixpath
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REPO_PREFIX = "/MatPomGit/app-eeg-mne/blob/main/"


def invalid_ids(parser):
    """HTML id must have a nonempty string value."""
    return {value for value in parser.ids if not isinstance(value, str) or not value.strip()}


def link_errors(href, ids):
    """Validate URL policy; only local same-document fragments resolve against our IDs."""
    if not isinstance(href, str) or not href.strip():
        return ["empty href"]
    parsed = urlparse(href)
    errors = []
    if parsed.scheme.lower() not in ("", "https"):
        errors.append("unsafe scheme")
    elif parsed.scheme and not parsed.netloc:
        errors.append("missing HTTPS host")
    elif not parsed.scheme and parsed.netloc:
        errors.append("scheme-relative URL")
    if "#" in href and not parsed.fragment:
        errors.append("empty fragment")
    if (parsed.fragment and not parsed.scheme and not parsed.netloc
            and posixpath.normpath(parsed.path) in (".", "index.html")
            and unquote(parsed.fragment) not in ids):
        errors.append("missing local fragment")
    return errors


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicate_ids = set()
        self.links = []
        self.lang = None
        self.tags = []

    def handle_starttag(self, tag, attrs):
        props = dict(attrs)
        self.tags.append(tag)
        if "id" in props:
            if props["id"] in self.ids:
                self.duplicate_ids.add(props["id"])
            self.ids.add(props["id"])
        if tag == "html":
            self.lang = props.get("lang")
        if tag in ("a", "link") and "href" in props:
            self.links.append(props["href"])


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
            if not isinstance(href, str):
                continue  # Rejected by test_links_reject_unsafe_schemes_and_empty_fragments.
            parsed = urlparse(href)
            if parsed.scheme or parsed.netloc or parsed.path in ("", "./"):
                continue
            self.assertTrue((SITE / unquote(parsed.path)).is_file(), href)

    def test_unique_nonempty_ids(self):
        self.assertFalse(invalid_ids(self.parser), invalid_ids(self.parser))
        self.assertFalse(self.parser.duplicate_ids, self.parser.duplicate_ids)

    def test_links_reject_unsafe_schemes_and_empty_fragments(self):
        for href in self.parser.links:
            with self.subTest(href=href):
                self.assertFalse(link_errors(href, self.parser.ids), href)

    def test_repository_links_point_to_existing_files(self):
        for href in self.parser.links:
            if not isinstance(href, str):
                continue
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


class SiteValidationRegressionTests(unittest.TestCase):
    def test_duplicate_ids_are_detected(self):
        parser = SiteParser()
        parser.feed('<main id="same"></main><aside id="same"></aside>')
        self.assertEqual(parser.duplicate_ids, {"same"})

    def test_empty_and_whitespace_ids_are_detected(self):
        for markup in ('<p id></p>', '<p id=""></p>', '<p id="  "></p>'):
            with self.subTest(markup=markup):
                parser = SiteParser()
                parser.feed(markup)
                self.assertTrue(invalid_ids(parser))

    def test_href_validation_positive_and_negative_cases(self):
        ids = {"section"}
        cases = (
            ("#section", []),
            ("./index.html#section", []),
            ("?view=1#section", []),
            ("https://example.org/page#external-section", []),
            ("https://example.org/page", []),
            ("#", ["empty fragment"]),
            ("index.html#", ["empty fragment"]),
            ("#unknown", ["missing local fragment"]),
            ("./index.html#unknown", ["missing local fragment"]),
            ("javascript:alert(1)", ["unsafe scheme"]),
            ("//example.org/page", ["scheme-relative URL"]),
            ("https:relative", ["missing HTTPS host"]),
            ("", ["empty href"]),
            (None, ["empty href"]),
        )
        for href, errors in cases:
            with self.subTest(href=href):
                self.assertEqual(link_errors(href, ids), errors)

    def test_blank_href_attributes_are_collected(self):
        parser = SiteParser()
        parser.feed('<a href=""></a><a href></a>')
        self.assertEqual(parser.links, ["", None])


if __name__ == "__main__":
    unittest.main()

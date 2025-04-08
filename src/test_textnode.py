import unittest

from textnode import TextNode, TextType


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "abc")
        node2 = TextNode("This is a text node", TextType.BOLD, "abc")
        self.assertEqual(node, node2)

    def test_neq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_neq_different_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, "foobar")

    def test_to_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = node.to_leaf_node()
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_to_bold(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html_node = node.to_leaf_node()
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a text node")

    def test_to_img(self):
        node = TextNode("This is a text node", TextType.IMAGE, "http://a.b")
        html_node = node.to_leaf_node()
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, None)
        self.assertTrue("src" in html_node.props)
        self.assertEqual("http://a.b", html_node.props["src"])
        self.assertTrue("alt" in html_node.props)
        self.assertEqual("This is a text node", html_node.props["alt"])

    def text_to_href(self):
        node = TextNode("This is a text node", TextType.LINK, "http://a.b")
        html_node = node.to_leaf_node()
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "This is a text node")
        self.assertTrue("href" in html_node.props)
        self.assertEqual("http://a.b", html_node.props["href"])


if __name__ == "__main__":
    unittest.main()
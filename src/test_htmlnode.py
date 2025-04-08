import unittest

from src.HTMLNode import HTMLNode, LeafNode, ParentNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_none(self):
        node = HTMLNode("test", "test")
        self.assertEqual("", node.props_to_html())

    def test_props_to_html(self):
        node = HTMLNode("test", "test")
        node.props = {"a": "b"}
        self.assertEqual(" a=\"b\"", node.props_to_html())

    def test_props_to_html_multi(self):
        node = HTMLNode("test", "test")
        node.props = {"a": "b", "1": "2"}
        self.assertEqual(" a=\"b\" 1=\"2\"", node.props_to_html())

    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_leaf_to_html_p_with_properties(self):
        node = LeafNode("p", "Hello, world!",{ "test": "test" })
        self.assertEqual(node.to_html(), "<p test=\"test\">Hello, world!</p>")

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
import unittest

from markdown_processor import _markdown_to_blocks, BlockType, block_to_blocktype, markdown_to_html_node, \
    extract_title
from textnode import TextNode, TextType, _split_nodes_delimiter, _split_nodes_image, _split_nodes_link, \
    _extract_markdown_images, _extract_markdown_links, text_to_textnodes


class TestNodeSplitter(unittest.TestCase):
    def test_simple_split(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = _split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(3, len(new_nodes))

        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        for i in range(0,3):
            self.assertEqual(expected[i], new_nodes[i])

    def test_extract_markdown_image(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        extracted = _extract_markdown_images(text)
        self.assertEqual(2, len(extracted))
        self.assertEqual("rick roll", extracted[0][0])
        self.assertEqual("https://i.imgur.com/aKaOqIh.gif", extracted[0][1])

    def test_extract_markdown_image_with_link(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        extracted = _extract_markdown_images(text)
        self.assertEqual(0, len(extracted))

    def test_extract_markdown_link(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        extracted = _extract_markdown_links(text)
        self.assertEqual(2, len(extracted))
        self.assertEqual("to boot dev", extracted[0][0])
        self.assertEqual("https://www.boot.dev", extracted[0][1])

    def test_extract_markdown_link_with_image(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        extracted = _extract_markdown_links(text)
        self.assertEqual(0, len(extracted))

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = _split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode(
                    "second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"
                ),
            ],
            new_nodes,
        )

    def test_split_link(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = _split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_process_text(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        self.assertListEqual([
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ], nodes)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = _markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_multiple_newline(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line





- This is a list
- with items
"""
        blocks = _markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_block_to_blocktype_ordered_list(self):
        text = """
1. test
2. bla
"""
        self.assertEqual(BlockType.ORDERED_LIST, block_to_blocktype(text.strip()))

    def test_block_to_blocktype_unordered_list(self):
        text = """
- test
- bla
"""
        self.assertEqual(BlockType.UNORDERED_LIST, block_to_blocktype(text.strip()))

    def test_block_to_blocktype_quote(self):
        text = """
> test
> bla
"""
        self.assertEqual(BlockType.QUOTE, block_to_blocktype(text.strip()))

    def test_block_to_blocktype_heading(self):
        text = "## test"
        self.assertEqual(BlockType.HEADING, block_to_blocktype(text.strip()))

    def test_block_to_blocktype_code(self):
        text = "```test```"
        self.assertEqual(BlockType.CODE, block_to_blocktype(text.strip()))

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_unordered_list(self):
        md = """
- item1
- item2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>item1</li><li>item2</li></ul></div>",
        )

    def test_ordered_list(self):
        md = """
1. item1 **bold**
2. item2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>item1 <b>bold</b></li><li>item2</li></ol></div>",
        )

    def test_quote(self):
        md = """
> line1
> line2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote> line1 line2</blockquote></div>",
        )

    def test_heading(self):
        md = """
### heading
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h3>heading</h3></div>",
        )

    def test_extract_title(self):
        md = """
## test
# title
### test2
"""
        title = extract_title(md)
        self.assertEqual(title, "title")

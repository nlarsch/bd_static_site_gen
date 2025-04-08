import re
from enum import Enum
from typing import Callable

from HTMLNode import LeafNode


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other: any) -> bool:
        if isinstance(other, TextNode):
            if self.text == other.text and self.text_type == other.text_type and self.url == other.url:
                return True
        return False

    def __repr__(self) -> str:
        return f"TextNode(\"{self.text}\", {self.text_type}, {self.url})"

    def to_leaf_node(self) -> LeafNode:
        match self.text_type:
            case TextType.TEXT:
                return LeafNode(None, self.text)
            case TextType.BOLD:
                return LeafNode("b", self.text)
            case TextType.ITALIC:
                return LeafNode("i", self.text)
            case TextType.CODE:
                return LeafNode("code", self.text)
            case TextType.LINK:
                return LeafNode("a", self.text, {"href": self.url})
            case TextType.IMAGE:
                return LeafNode("img", None, {"src": self.url, "alt": self.text})
        raise ValueError("unknown text type")


def _split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    result = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue
        fragments = old_node.text.split(delimiter)
        mode = False
        for fragment in fragments:
            result.append(TextNode(fragment, text_type if mode else old_node.text_type))
            mode = not mode
    return result


def _split_bolt(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_delimiter(old_nodes, "**", TextType.BOLD)


def _split_italic(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_delimiter(old_nodes, "_", TextType.ITALIC)


def _split_code(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_nodes_delimiter(old_nodes, "`", TextType.CODE)


def _split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_iternal(old_nodes, _extract_markdown_images, TextType.IMAGE)


def _split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    return _split_iternal(old_nodes, _extract_markdown_links, TextType.LINK)


def _extract_markdown_images(text: str) -> list[tuple[str, str]]:
    return re.findall(r"!\[([^]]*)\]\(([^\)]*)\)", text)


def _extract_markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"(?<!\!)\[([^]]*)\]\(([^\)]*)\)", text)


_splitters: list[Callable[[list[TextNode]], list[TextNode]]] = [
    _split_bolt,
    _split_italic,
    _split_code,
    _split_nodes_image,
    _split_nodes_link,
]


def _split_iternal(old_nodes: list[TextNode], func: Callable[[str], list[tuple[str, str]]], type: TextType) -> list[TextNode]:
    result = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            result.append(old_node)
            continue
        current_idx = 0
        text = old_node.text
        img_data = func(text)
        while len(img_data) > 0:
            image = img_data.pop(0)
            prefix_idx = text.find(image[0], current_idx) - (1 if type == TextType.LINK else 2)
            suffix_idx = text.find(image[1], current_idx) + len(image[1]) + 1
            result.append(TextNode(text[current_idx:prefix_idx], old_node.text_type))
            result.append(TextNode(image[0], type, image[1]))
            current_idx = suffix_idx
        if current_idx < len(text):
            result.append(TextNode(text[current_idx:], old_node.text_type))
    return result


def text_to_textnodes(text: str) -> list[TextNode]:
    result = [TextNode(text, TextType.TEXT)]
    for splitter in _splitters:
        result = splitter(result)
    return result

import logging
import os
from enum import Enum

from HTMLNode import ParentNode, LeafNode, HTMLNode
from textnode import text_to_textnodes
import re

logger = logging.getLogger(__name__)

class BlockType(Enum):
    PARAGRAPH = 0
    HEADING = 1
    CODE = 2
    QUOTE = 3
    UNORDERED_LIST = 4
    ORDERED_LIST = 5


def _markdown_to_blocks(markdown: str) -> list[str]:
    result = []
    for block in markdown.split("\n\n"):
        stripped_block = block.strip()
        if len(stripped_block) != 0:
            result.append(stripped_block)
    return result

def block_to_blocktype(block: str) -> BlockType:
    if re.match(r"^#{1,6} .*$", block):
        return BlockType.HEADING
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    split_blocks = block.split("\n")
    if all(s.startswith(">") for s in split_blocks):
        return BlockType.QUOTE
    if all(s.startswith("- ") for s in split_blocks):
        return BlockType.UNORDERED_LIST
    if all(s.startswith(f"{i+1}. ") for i, s in enumerate(split_blocks)):
        return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH

def markdown_to_html_node(markdown: str) -> HTMLNode:
    children = []
    blocks = _markdown_to_blocks(markdown)
    for block in blocks:
        type = block_to_blocktype(block)
        match type:
            case BlockType.HEADING:
                children.append(block_to_heading(block))
            case BlockType.QUOTE:
                children.append(block_to_quote(block))
            case BlockType.UNORDERED_LIST:
                children.append(block_unordered_list(block))
            case BlockType.ORDERED_LIST:
                children.append(block_ordered_list(block))
            case BlockType.PARAGRAPH:
                children.append(block_to_paragraph(block))
            case BlockType.CODE:
                children.append(block_to_code(block))
            case _:
                raise ValueError(f"unknown block type {type}")

    return ParentNode("div", children)

def parse_children(text: str) -> list[HTMLNode]:
    textnodes = text_to_textnodes(text)
    children = []
    for text_node in textnodes:
        children.append(text_node.to_leaf_node())
    return children

def block_to_quote(markdown: str) -> HTMLNode:
    lines = markdown.split("\n")
    result = ""
    for line in lines:
        result += line[1:]
    children = parse_children(result)
    return ParentNode("blockquote", children)

def block_to_paragraph(markdown: str) -> HTMLNode:
    children = parse_children(" ".join(markdown.split("\n")))
    return ParentNode("p", children)

def block_to_code(markdown: str) -> HTMLNode:
    children = [LeafNode("code", "\n".join(markdown[:-3].split("\n")[1:]))]
    return ParentNode("pre", children)

def block_ordered_list(markdown: str) -> HTMLNode:
    items = markdown.split("\n")
    children = []
    for item in items:
        children.append(ParentNode("li", parse_children(re.sub(r"^\d+\. ", "", item))))
    return ParentNode("ol", children)

def block_unordered_list(markdown: str) -> HTMLNode:
    items = markdown.split("\n")
    children = []
    for item in items:
        children.append(ParentNode("li", parse_children(item[2:])))
    return ParentNode("ul", children)

def block_to_heading(markdown: str) -> HTMLNode:
    level = len(re.findall(r"(#+) .*", markdown)[0])
    children = parse_children(re.sub(r"#+ ", "", markdown))
    return ParentNode("h" + str(level), children)

def extract_title(markdown: str) -> str:
    lines = markdown.split("\n")
    for line in lines:
        if re.match(r"^#[^#]+$", line) is not None:
            return line.lstrip("#").strip()
    raise ValueError("no title found")

def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str) -> None:
    logger.info(f"Generating page from {from_path} to {dest_path} using {template_path}")
    md_string = ""
    with open(from_path, "r", encoding="utf-8") as f:
        logger.debug(f"Reading from file {from_path}")
        md_string = f.read()
    template_string = ""
    with open(template_path, "r", encoding="utf-8") as f:
        logger.debug(f"Reading from file {template_path}")
        template_string = f.read()

    html = markdown_to_html_node(md_string).to_html()
    title = extract_title(md_string)
    result = template_string.replace("{{ Title }}", title).replace("{{ Content }}", html)
    result = result.replace("href=\"/", f"href=\"{basepath}")
    result = result.replace("src\"/", f"src=\"{basepath}")

    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path))
    with open(dest_path, "w", encoding="utf-8") as f:
        logger.debug(f"Writing to file {dest_path}")
        f.write(result)

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str) -> None:
    for file in os.listdir(dir_path_content):
        if os.path.isfile(os.path.join(dir_path_content, file)):
            if file.endswith(".md"):
                generate_page(os.path.join(dir_path_content, file), template_path, os.path.join(dest_dir_path, re.sub(r".md$", ".html", file)), basepath)
        else:
            generate_pages_recursive(os.path.join(dir_path_content, file), template_path, os.path.join(dest_dir_path, file), basepath)
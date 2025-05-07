"""Collect information on document sections and Pygame API objects

The following persistent Pygame specific environment structures are built:

pyg_sections: [{'docname': <docname>,
                'fullname': <fullname>,
                'refid': <ref>},
               ...]
    all Pygame api sections in the documents in order processed.
pyg_descinfo_tbl: {<id>: {'fullname': <fullname>,
                          'desctype': <type>,
                          'summary': <summary>,
                          'signatures': <sigs>,
                          'children': <toc>,
                          'refid': <ref>,
                          'docname': <docname>},
                   ...}
    object specific information, including a list of direct children, if any.

<docname>: (str) the simple document name without path or extension.
<fullname>: (str) a fully qualified object name. It is a unique identifier.
<ref>: (str) an id usable as local uri reference.
<id>: (str) unique desc id, the first entry in the ids attribute list.
<type>: (str) an object's type: the desctype attribute.
<summary>: (str) a summary line as identified by a :summaryline: role.
           This corresponds to the first line of a docstring.
<sigs>: (list of str) an object's signatures, in document order.
<toc>: (list of str) refids of an object's children, in document order.

"""

from ext.utils import Visitor, get_fullname, get_refid, GetError

from collections import deque
import os.path

MODULE_ID_PREFIX = "module-"


def setup(app):
    app.connect("env-purge-doc", prep_document_info)
    app.connect("doctree-read", collect_document_info)


def prep_document_info(app, env, docname):
    try:
        env.pyg_sections = [e for e in env.pyg_sections if e["docname"] != docname]
    except AttributeError:
        pass
    except KeyError:
        pass
    try:
        descinfo_tbl = env.pyg_descinfo_tbl
    except AttributeError:
        pass
    else:
        to_remove = [k for k, v in descinfo_tbl.items() if v["docname"] == docname]
        for k in to_remove:
            del descinfo_tbl[k]


def collect_document_info(app, doctree):
    doctree.walkabout(RemoveComments(app, doctree))
    doctree.walkabout(CollectInfo(app, doctree))


class RemoveComments(Visitor):
    def __init__(self, app, document_node):
        super().__init__(app, document_node)

    def visit_comment(self, node):
        node.parent.remove(node)

class CollectInfo(Visitor):
    """Records the information for a document"""

    desctypes = {
        "data",
        "function",
        "exception",
        "class",
        "attribute",
        "property",
        "method",
        "staticmethod",
        "classmethod",
        "type",
    }

    def __init__(self, app, document_node):
        super().__init__(app, document_node)
        self.docname = self.env.docname
        self.desc_stack: deque[str] = deque()
        self.children_stack: deque[list[str]] = deque()
        self.summary_stack: deque[str] = deque()
        try:
            self.env.pyg_sections
        except AttributeError:
            self.env.pyg_sections = []
        try:
            self.env.pyg_descinfo_tbl
        except AttributeError:
            self.env.pyg_descinfo_tbl = {}

    def push(self, node):
        if len(self.desc_stack) >= 1:
            to_remove = node.child_text_separator + node.astext()
            parent_desc = self.desc_stack[-1]
            if to_remove + node.child_text_separator in parent_desc:
                to_remove += node.child_text_separator

            self.desc_stack[-1] = self.desc_stack[-1].replace(to_remove, "")

        self.desc_stack.append(node.astext())
        self.children_stack.append([])
        self.summary_stack.append("")

    def _add_descinfo_entry(self, node, entry):
        key = get_refid(node)
        if key.startswith(MODULE_ID_PREFIX):
            key = key[len(MODULE_ID_PREFIX) :]
        self.env.pyg_descinfo_tbl[key] = entry

        if len(self.children_stack) >= 1:
            self.children_stack[-1].append(get_refid(node))

    def visit_document(self, node):
        # Only index pygame Python API documents, found in the docs/reST/ref
        # subdirectory. Thus the tutorials and the C API documents are skipped.
        source = node["source"]
        head, file_name = os.path.split(source)
        if not file_name:
            raise self.skip_node
        head, dir_name = os.path.split(head)
        if dir_name != "ref":
            raise self.skip_node
        head, dir_name = os.path.split(head)
        if dir_name != "reST":
            raise self.skip_node
        head, dir_name = os.path.split(head)
        if dir_name != "docs":
            raise self.skip_node

    def visit_inline(self, node):
        """Collect a summary or signature"""

        if "summaryline" in node["classes"]:
            self.summary_stack[-1] = node.astext()

    def visit_section(self, node):
        if not node["names"]:
            raise self.skip_node
        self.push(node)

    def depart_section(self, node):
        """Record section info"""

        if not node.children:
            return
        if node["ids"][0].startswith(MODULE_ID_PREFIX):
            docs = self.desc_stack.pop().strip()
            entry = {
                "fullname": get_fullname(node),
                "desctype": node.get("desctype", "module"),
                "refid": get_refid(node),
                "docname": self.docname,
                "full_docs": docs,
                "children": self.children_stack.pop(),
                "summary": self.summary_stack.pop(),
            }
            self._add_descinfo_entry(node, entry)

            entry = {
                "docname": self.docname,
                "fullname": get_fullname(node),
                "refid": get_refid(node),
            }
            self.env.pyg_sections.append(entry)
        elif self.children_stack[-1]:
            # No section level introduction: use the first toplevel directive
            # instead
            docs = self.desc_stack.pop().strip()
            children = self.children_stack.pop()
            entry = self.env.pyg_descinfo_tbl[children[0]].copy()
            entry["refid"] = get_refid(node)
            self._add_descinfo_entry(node, entry)

            desc_node = get_descinfo_refid(children[0], self.env)
            entry = {
                "docname": self.docname,
                "fullname": desc_node["fullname"],
                "refid": desc_node["refid"],
            }
            self.env.pyg_sections.append(entry)

    def visit_desc(self, node):
        if node.get("desctype", "") not in self.desctypes:
            raise self.skip_node
        self.push(node)

    def depart_desc_content(self, node):
        if self.summary_stack[-1] == "":
            self.summary_stack[-1] = node.astext().split("\n", 1)[0]

    def depart_desc(self, node):
        entry = {
            "fullname": get_fullname(node),
            "desctype": node.get("desctype", "module"),
            "refid": get_refid(node),
            "docname": self.docname,
            "full_docs": self.desc_stack.pop(),
            "children": self.children_stack.pop(),
            "summary": self.summary_stack.pop(),
        }

        self._add_descinfo_entry(node, entry)


def tour_descinfo(fn, node, env):
    try:
        descinfo = get_descinfo(node, env)
    except GetError:
        return
    fn(descinfo)
    for refid in descinfo["children"]:
        tour_descinfo_refid(fn, refid, env)


def tour_descinfo_refid(fn, refid, env):
    descinfo = env.pyg_descinfo_tbl[refid]  # A KeyError would mean a bug.
    fn(descinfo)
    for refid in descinfo["children"]:
        tour_descinfo_refid(fn, refid, env)


def get_descinfo(node, env):
    return get_descinfo_refid(get_refid(node), env)


def get_descinfo_refid(refid, env):
    if refid.startswith(MODULE_ID_PREFIX):
        refid = refid[len(MODULE_ID_PREFIX) :]
    try:
        return env.pyg_descinfo_tbl[refid]
    except KeyError:
        raise GetError("Not found")

# An idiosyncratic implementation of nodes in a tree structure.
# Could use refactoring

import yaml
from functools import total_ordering

@total_ordering
class TreeNode:
    """
    A node in a tree, represented as either a string (terminal)
    or a dict (with children).
    """
    root = "$ROOT$"
    indent = "    "
    list_marker = "- "

    @classmethod
    def read_yaml(cls, filename):
        with open(filename) as f:
            return TreeNode({cls.root: yaml.safe_load(f)})

    @classmethod
    def write_yaml(cls, filename, tree_node):
        with open(filename, 'w') as f:
            f.write(yaml.dump(tree_node.to_json(), default_flow_style=False))

    def __init__(self, representation, parent=None):
        self.parent = parent
        if isinstance(representation, str):
            self.name = representation
            self.children = []
        elif isinstance(representation, dict) and len(representation) == 1:
            ((self.name, children),) = representation.items()
            self.children = [TreeNode(child, parent=self) for child in children or []]
        else:
            raise ValueError("Illegal node representation: {}".format(representation))

    def add_child(self, representation):
        self.children.append(TreeNode(representation, parent=self))

    def remove_children_by_name(self, name):
        for child in self.children: 
            child.remove_children_by_name(name)
            if child.name == name:
                for c in child.children:
                    self.children.append(c)
                    c.parent = self
        self.children = [c for c in self.children if c.name != name]

    def rename(self, old_name, new_name):
        "Renames all children"
        if self.name == old_name:
            self.name = new_name
        for child in self.children:
            child.rename(old_name, new_name)

    def ancestors(self):
        "Returns a list of ancestors, ending with self"
        if self.is_root() or self.is_root():
            return []
        else:
            return self.parent.ancestors() + [self]

    def depth(self):
        return len(self.ancestors())

    def backtrack_to(self, target_nodes):
        "Returns a list of ancestors traversed to reach one of target_nodes"
        traversed = []
        for a in reversed(self.ancestors()):
            if a in target_nodes:
                return list(reversed(traversed))
            else:
                traversed.append(a)
        return None

    def flatten(self, names=False, expanded=False, sep=":", depth=None):
        """
        Returns the node and its children as a depth-first list.
        If names, return strings of node names.
        If expanded, return expanded name, like 'fruits:apples:pippin'
        If depth is not None, limits the depth of recursion
        """
        result = [self] if not self.is_root() else []
        if depth is None or depth > 0:
            for child in self.children: 
                result += child.flatten(depth=depth if depth is None else depth - 1)
        if names:
            if expanded:
                result = [n.expanded_name(sep=sep) for n in result]
            else:
                result = [n.name for n in result]
        return sorted(result)

    def expanded_name(self, sep=":"):
        "Returns expanded name, like 'fruits:apples:pippin'"
        if self.parent and not self.parent.is_root():
            return self.parent.expanded_name(sep=sep) + sep + self.name
        else:
            return self.name

    def indented_name(self, nodes, sep=":", indent_length=2, indent_start='.'):
        "Returns indented name, like '.    pippin'"
        ancestor_traversal = self.parent.backtrack_to(nodes)
        if ancestor_traversal is None: # This node goes all the way back to root
            return ":".join(n.name for n in self.ancestors())
        else: 
            ancestor_depth = self.depth() - len(ancestor_traversal) - 1
            return (
                indent_start + 
                ' ' * indent_length * ancestor_depth + 
                ":".join(a.name for a in ancestor_traversal+[self])
            )

    def find(self, name):
        "Returns all child nodes (including self) with matching name"
        result = [self] if self.name == name else []
        for child in self.children:
            result += child.find(name)
        return result

    def sum(self, prop):
        "Returns the sum of self plus all children's values for prop"
        val = getattr(self, prop) if hasattr(self, prop) else 0
        return val + sum(c.sum(prop) for c in self.children)

    def to_json(self):
        "Returns a str/list/dict representation. The root node is stored as a list."
        if any(self.children):
            if self.is_root():
                return [child.to_json() for child in sorted(self.children)]
            else:
                return {self.name: [child.to_json() for child in sorted(self.children)]}
        else:
            return self.name

    def __str__(self, max_depth=None, current_depth=0):
        "String representation of tree, limited to `max_depth` if provided. `current_depth` is used internally for recursion."
        if self.is_root():
            if max_depth is None or max_depth > 0:
                md = None if max_depth is None else max_depth - 1
                return "".join([c.__str__(max_depth=md, current_depth=current_depth) for c in sorted(self.children)])
            else:
                return ""
        else:
            string_rep = self.indent * current_depth + self.list_marker + self.name + "\n"
            if max_depth is None or current_depth < max_depth:
                string_rep += "".join([c.__str__(max_depth=max_depth, current_depth=current_depth+1) for c in sorted(self.children)])
            return string_rep
            
    def is_root(self):
        return self.name == self.root

    def __eq__(self, other):
        return self.expanded_name() == other.expanded_name()

    def __lt__(self, other):
        return self.expanded_name() < other.expanded_name()

    def __hash__(self):
        return hash(self.expanded_name())

    def __repr__(self):
        return "<{}>".format(self.name)


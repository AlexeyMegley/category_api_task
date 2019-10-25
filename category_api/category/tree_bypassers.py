def tree_relations_generator(tree: dict, name_field='name', children_field='children') -> (str, str):
    """ 
    Generate tuple (parent_name, child_name,) on every relation
    """
    name = tree.get(name_field)
    children = tree.get(children_field) or []
    for child_tree in children:
        yield (name, child_tree[name_field])
        yield from tree_relations_generator(child_tree)


def tree_names_generator(tree: dict, name_field='name', children_field='children') -> str:
    """
    Iterate through all category names
    """
    yield tree.get(name_field)
    children = tree.get(children_field) or []
    for child_tree in children:
        yield from tree_names_generator(child_tree)

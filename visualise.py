import os
import graphviz
import neat

def draw_net(config, genome, view=False, filename="network.gv", node_names=None, show_disabled=True, prune_unused=False, node_colors=None, fmt='png'):
    """ Receives a genome and draws a neural network with arbitrary topology. """
    from graphviz import Digraph

    if graphviz is None:
        raise ImportError("This function requires graphviz but it is not installed.")

    node_attrs = {
        'shape': 'circle',
        'fontsize': '9',
        'height': '0.2',
        'width': '0.2'}

    dot = Digraph(format=fmt, node_attr=node_attrs)

    inputs = set()
    outputs = set()

    for k in config.genome_config.input_keys:
        inputs.add(k)
        name = node_names.get(k, str(k)) if node_names else str(k)
        dot.node(name, _attributes={'style': 'filled', 'fillcolor': node_colors.get(k, 'lightgray') if node_colors else 'lightgray'})

    for k in config.genome_config.output_keys:
        outputs.add(k)
        name = node_names.get(k, str(k)) if node_names else str(k)
        dot.node(name, _attributes={'style': 'filled', 'fillcolor': node_colors.get(k, 'lightblue') if node_colors else 'lightblue'})

    used_nodes = set(genome.nodes.keys()) if not prune_unused else set()
    if prune_unused:
        connections = [cg for cg in genome.connections.values() if cg.enabled or show_disabled]
        visited = set()
        to_visit = list(outputs)

        while to_visit:
            node = to_visit.pop()
            if node in visited:
                continue
            visited.add(node)
            used_nodes.add(node)

            for k, cg in genome.connections.items():
                if cg.enabled or show_disabled:
                    if cg.key[1] == node:
                        to_visit.append(cg.key[0])

    for n in used_nodes:
        if n not in inputs and n not in outputs:
            name = node_names.get(n, str(n)) if node_names else str(n)
            dot.node(name, _attributes={'style': 'filled', 'fillcolor': node_colors.get(n, 'white') if node_colors else 'white'})

    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            input, output = cg.key
            if prune_unused and (input not in used_nodes or output not in used_nodes):
                continue
            input_name = node_names.get(input, str(input)) if node_names else str(input)
            output_name = node_names.get(output, str(output)) if node_names else str(output)
            style = 'solid' if cg.enabled else 'dotted'
            color = 'green' if cg.weight > 0 else 'red'
            width = str(0.1 + abs(cg.weight / 5.0))
            dot.edge(input_name, output_name, _attributes={'style': style, 'color': color, 'penwidth': width})

    filename = filename.replace(' ', '_')
    dot.render(filename, view=view)

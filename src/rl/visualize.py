import graphviz
from neat.graphs import feed_forward_layers

def draw_net(config, genome, filename='pretty_net.dot', node_names=None, show_disabled=True, prune_unused=False, node_colors=None):
    dot = graphviz.Digraph(format='dot')
    dot.attr(rankdir='LR')  # Left to right

    input_nodes = config.genome_config.input_keys
    output_nodes = config.genome_config.output_keys

    used_nodes = set()
    if prune_unused:
        for conn in genome.connections.values():
            if conn.enabled:
                used_nodes.add(conn.key[0])
                used_nodes.add(conn.key[1])

    layers = feed_forward_layers(input_nodes, output_nodes, genome.connections)

    def name(n):
        if node_names and n in node_names:
            return node_names[n]
        return f"n{n}"

    # Group input nodes
    with dot.subgraph() as s:
        s.attr(rank='same')
        for node in input_nodes:
            s.node(name(node), style='filled', fillcolor='lightgray')

    # Group output nodes
    with dot.subgraph() as s:
        s.attr(rank='same')
        for node in output_nodes:
            s.node(name(node), style='filled', fillcolor='lightblue')

    # Hidden layers
    for layer in layers:
        with dot.subgraph() as s:
            s.attr(rank='same')
            for node in layer:
                if node in input_nodes or node in output_nodes:
                    continue
                if prune_unused and node not in used_nodes:
                    continue
                s.node(name(node), style='filled', fillcolor='white')

    # Add connections
    for conn_key, conn in genome.connections.items():
        if not show_disabled and not conn.enabled:
            continue
        a, b = conn_key
        dot.edge(
            name(a),
            name(b),
            style='solid' if conn.enabled else 'dotted',
            color='green' if conn.weight > 0 else 'red',
            penwidth=str(0.1 + abs(conn.weight / 5.0))
        )

    with open(filename, 'w') as f:
        f.write(dot.source)
    print(f"[✅] Clean .dot file saved: {filename}")

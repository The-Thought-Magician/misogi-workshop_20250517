import os

# Create a GraphViz DOT file to visualize the graph
def create_visualization():
    dot_content = '''
digraph OutfitRecommender {
    // Graph styling
    bgcolor="transparent";
    rankdir=LR;
    node [shape=box, style="rounded,filled", fillcolor="#f0f8ff", color="#4682b4", fontname="Arial"];
    edge [color="#4682b4", fontname="Arial"];
    
    // Nodes
    start [label="START", shape=oval, fillcolor="#98fb98"];
    get_weather [label="get_weather\nFetches weather data"];
    generate_outfit [label="generate_outfit\nGenerates outfit with LLM"];
    check_rating [label="check_rating\nEvaluates user rating", shape=diamond, fillcolor="#fffacd"];
    generate_result [label="generate_result\nCreates final message"];
    end [label="END", shape=oval, fillcolor="#ffb6c1"];
    
    // Edges
    start -> get_weather;
    get_weather -> generate_outfit;
    generate_outfit -> check_rating;
    check_rating -> generate_outfit [label="rating < 7 AND\nattempts < max"];
    check_rating -> generate_result [label="rating >= 7 OR\nattempts >= max"];
    generate_result -> end;
}
'''

    # Write the DOT file
    with open('outfit_graph.dot', 'w') as f:
        f.write(dot_content)
    
    print("Created DOT file: outfit_graph.dot")
    print("To generate an image, run: dot -Tpng outfit_graph.dot -o outfit_graph.png")

if __name__ == "__main__":
    create_visualization() 
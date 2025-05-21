def create_ascii_visualization():
    """
    Create an ASCII art visualization of the LangGraph workflow
    for the outfit recommendation application.
    """
    
    ascii_graph = """
    Outfit Recommendation LangGraph Workflow
    ========================================

    +----------------+      +------------------+      +-------------------+
    |                |      |                  |      |                   |
    |   get_weather  |----->|  generate_outfit |----->|    check_rating   |
    |                |      |                  |      |                   |
    +----------------+      +------------------+      +--------+----------+
                                                               |
                                                               |
                     +------------------------------+          |
                     |                              |          |
                     |                              v          v
                     |                    +---------+----------+----+
                     |                    |                         |
                     +--------------------+    generate_outfit      |
                     |  rating < 7 AND    |                         |
                     |  attempts < max     +-------------------------+
                     |                     
                     |                     
                     |                     +-------------------------+
                     |  rating >= 7 OR     |                         |
                     +-------------------->|    generate_result      |------> END
                        attempts >= max    |                         |
                                           +-------------------------+

    """
    
    print(ascii_graph)
    
    # Save to file as well
    with open('outfit_graph_ascii.txt', 'w') as f:
        f.write(ascii_graph)
    
    print("ASCII graph saved to outfit_graph_ascii.txt")

if __name__ == "__main__":
    create_ascii_visualization() 
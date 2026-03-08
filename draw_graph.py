from graph import graph

def save_graph_image():
    try:
        png_bytes = graph.get_graph().draw_mermaid_png()
        
        with open("graph.png", "wb") as f:
            f.write(png_bytes)
        
        print("✅ Graf resmi başarıyla oluşturuldu: graph.png")
    except Exception as e:
        print(f"Graf resmi oluşturulurken bir hata oluştu: {e}")

if __name__ == "__main__":
    save_graph_image()

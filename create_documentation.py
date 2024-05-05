import ast


def extract_function_comments(file_path):
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    class_functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            class_functions[class_name] = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    function_name = item.name
                    docstring = ast.get_docstring(item)
                    class_functions[class_name].append((function_name, docstring))

    return class_functions


def generate_readme(name, class_functions):
    with open("documentation/classes/" + name + ".md", "w") as readme_file:
        for class_name, functions in class_functions.items():
            readme_file.write(f"# {class_name} Documentation\n\n")
            for function_name, docstring in functions:
                readme_file.write(f"## {function_name}()\n\n")
                readme_file.write(f"{docstring}\n\n")


def main():
    generate_readme("RuneLiteBot", extract_function_comments("src/model/runelite_bot.py"))
    generate_readme("Walker", extract_function_comments("src/utilities/walker.py"))
    generate_readme("Random", extract_function_comments("src/utilities/random_util.py"))
    generate_readme("Mouse", extract_function_comments("src/utilities/mouse.py"))
    generate_readme("Pathfinder", extract_function_comments("src/utilities/api/pathfinder.py"))
    generate_readme("Statis Socket", extract_function_comments("src/utilities/api/status_socket.py"))
    generate_readme("Morg_http_client", extract_function_comments("src/utilities/api/morg_http_client.py"))


if __name__ == "__main__":
    main()

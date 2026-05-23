with open("src/binance50/cli.py") as f:
    content = f.read()

# Since we appended commands to the end of the file, we might have added them AFTER `if __name__ == "__main__":`
# Let's check where they are
if 'if __name__ == "__main__":' in content:
    lines = content.split("\n")
    idx = -1
    for i, line in enumerate(lines):
        if line.startswith('if __name__ == "__main__":'):
            idx = i
            break

    if idx != -1:
        main_block = lines[idx:]
        rest_block = lines[:idx]

        # move all appended commands to before the main block
        new_content = "\n".join(rest_block) + "\n" + "\n".join(main_block)
        with open("src/binance50/cli.py", "w") as f:
            f.write(new_content)

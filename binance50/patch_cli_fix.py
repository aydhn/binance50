with open("src/binance50/cli.py") as f:
    content = f.read()

# The previous command didn't actually move the appended commands properly because they were already below main block
# Let's cleanly separate everything
import re

commands_pattern = re.compile(r"(@app\.command\(\)\ndef stream_config\(\):[\s\S]*)")
match = commands_pattern.search(content)

if match:
    cmds = match.group(1)

    # Check if cmds has the main block inside it or after it
    if 'if __name__ == "__main__":' in cmds:
        parts = cmds.split('if __name__ == "__main__":')
        actual_cmds = parts[0]
        main_block = 'if __name__ == "__main__":' + parts[1]

        # Remove from bottom
        content = content.replace(cmds, "")

        # Put actual_cmds before main_block
        content = content + "\n" + actual_cmds + "\n" + main_block
    else:
        # cmds is below main block. Find main block and put cmds before it.
        content = content.replace(cmds, "")
        main_match = re.search(r'(if __name__ == "__main__":[\s\S]*)', content)
        if main_match:
            main_block = main_match.group(1)
            content = content.replace(main_block, "")
            content = content + "\n" + cmds + "\n" + main_block

    with open("src/binance50/cli.py", "w") as f:
        f.write(content)

with open("src/binance50/core/exceptions.py") as f:
    content = f.read()

content = content.replace('"user_action_required": self.user_action_required,', '"user_action_required": self.user_action_required,\n            "exception_class": self.__class__.__name__,')

with open("src/binance50/core/exceptions.py", "w") as f:
    f.write(content)

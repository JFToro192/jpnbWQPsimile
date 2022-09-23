from IPython.core.display import HTML

def css_styling():
    styles = open("./src/styles/custom.css", "r").read()
    return HTML(styles)
from tater.core import parse

from ptar.tokenize import Ptar, Tokenizer
from ptar.ast import Sources


def main():
    with open('ptar/data/parallel_table.txt') as f:
        text = f.read()

    text = Ptar(text).raw()
    tokenizer = Tokenizer()
    items = tokenizer.tokenize(text)
    tree = parse(Sources, items)
    import pdb; pdb.set_trace()

if __name__ == '__main__':
    main()

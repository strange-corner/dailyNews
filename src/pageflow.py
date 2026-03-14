import abc
import os


class SeqElem:

    @abc.abstractmethod
    def ident(self) -> str:
        """ Representation in the page flow UI"""
        raise NotImplementedError


class Article(SeqElem):

    def __init__(self, filename):
        self.filename = filename

    def __eq__(self, other):
        return self.ident() == other.ident()

    def ident(self) -> str:
        return self.filename


class CategoryMarker(SeqElem):

    def __init__(self, name):
        self.name = name

    def ident(self) -> str:
        return self.name


class PageFlow:
    """ Represents the Sequence of Elements (SeqElems) in the newspaper. SeqElems can be Articles, Category markers, etc."""

    def __init__(self):
        self.seq = []

    def elements(self) -> list[SeqElem]:
        return self.seq

    def add(self, elem: SeqElem):
        if elem in self.seq:
            i = self.seq.index(elem)
            self.seq.remove(elem)
            self.seq.insert(i, elem)
        else:
            self.seq.append(elem)

    def refreshArticles(self, folder: str):
        self.removeAllArticles()
        if os.path.isdir(folder):
            for fname in os.listdir(folder):
                if fname.endswith(".tex") and fname.startswith("a_"):
                    self.seq.append(Article(fname))

    def removeAllArticles(self):
        self.seq = [ele for ele in self.seq if type(ele) != Article]

    def removeArticle(self, index: int):
        self.seq = self.seq[:index] + self.seq[index+1:]

    def move_up(self, eleset: list[int]):
        for idx in eleset:
            if idx > 0:
                self.seq.insert(idx - 1, self.seq.pop(idx))

    def move_dn(self, eleset: list[int]):
        eleset = list(eleset)
        eleset.reverse()
        for idx in eleset:
            if idx < len(self.seq):
                self.seq.insert(idx + 1, self.seq.pop(idx))

    def save_pageflow(self, folder):
        """ saves the order of elements of the pageflow in a file pageflow.txt """
        with open(f"{folder}/pageflow.txt", "w", encoding="utf-8") as f:
            for elem in self.seq:
                ident = elem.ident()
                print("saving " + ident)
                f.write(ident)
                f.write("\n")
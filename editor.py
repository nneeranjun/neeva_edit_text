from collections import deque
class SimpleEditor:
    def __init__(self, document):
        self.document = list(document)
        self.dictionary = set()
        # On windows, the dictionary can often be found at:
        # C:/Users/{username}/AppData/Roaming/Microsoft/Spelling/en-US/default.dic
        with open("/usr/share/dict/words") as input_dictionary:
            for line in input_dictionary:
                words = line.strip().split(" ")
                for word in words:
                    self.dictionary.add(word)
        self.paste_text = [""]
        self.history_size = 20
        self.undo_stack = deque()
        self.redo_stack = deque()

    def undo(self):
        if len(self.undo_stack) == 0:
            return
        old = self.undo_stack.pop()
        if old[0] == "paste":
            #remove pasted characters from document
            for x in reversed(range(old[1][0], old[1][1])):
                del self.document[x]
        else:
            #re-paste old characters
            self.document = self.document[:old[1][0]] + old[1][1] +  self.document[old[1][0]:]
        if len(self.redo_stack) == self.history_size:
            self.redo_stack.popleft()
        self.redo_stack.append(old)

    def redo(self):
        if len(self.redo_stack) == 0:
            return
        old = self.redo_stack.pop()
        if old[0] == "paste":
            self.paste(old[1][0])
        else:
            self.cut(old[1][0],old[1][0] + len(old[1][1]))

    """
    Cut [i, j - 1] from document
    """
    def cut(self, i, j):
        self.paste_text = self.document[i:j]
        for x in reversed(range(i, j)):
            del self.document[x]
        if len(self.undo_stack) == self.history_size:
            self.undo_stack.popleft()
        self.undo_stack.append(["cut", [i, self.paste_text]])

    """
    Copy [i, j - 1] from document
    """
    def copy(self, i, j):
        self.paste_text = self.document[i:j]

    """
    Paste into document right before index i
    """
    def paste(self, i):
        for x in reversed(self.paste_text):
            self.document.insert(i, x)
        if len(self.undo_stack) == self.history_size:
            self.undo_stack.popleft()
        self.undo_stack.append(["paste", [i, i + len(self.paste_text)]])

    def get_text(self):
        return "".join(self.document)

    def misspellings(self):
        result = 0
        i = 0
        while i < len(self.document):
            j = i + 1
            curr_word = "" + self.document[i]
            while j < len(self.document) and self.document[j] != " ":
                curr_word += self.document[j]
                j += 1
            if curr_word not in self.dictionary:
                result += 1
            i = j
        return result

import timeit

class EditorBenchmarker:
    new_editor_case = """
from __main__ import SimpleEditor
s = SimpleEditor("{}")"""

    editor_cut_paste = """
for n in range({}):
    if n%2 == 0:
        s.cut(1, 3)
    else:
        s.paste(2)"""

    editor_copy_paste = """
for n in range({}):
    if n%2 == 0:
        s.copy(1, 3)
    else:
        s.paste(2)"""

    editor_get_text = """
for n in range({}):
    s.get_text()"""

    editor_mispellings = """
for n in range({}):
    s.misspellings()"""

    def __init__(self, cases, N):
        self.cases = cases
        self.N = N
        self.editor_cut_paste = self.editor_cut_paste.format(N)
        self.editor_copy_paste = self.editor_copy_paste.format(N)
        self.editor_get_text = self.editor_get_text.format(N)
        self.editor_mispellings = self.editor_mispellings.format(N)

    def benchmark(self):
        for case in self.cases:
            print("Evaluating case: {}".format(case))
            new_editor = self.new_editor_case.format(case)
            cut_paste_time = timeit.timeit(stmt=self.editor_cut_paste,setup=new_editor,number=1)
            print("{} cut paste operations took {} s".format(self.N, cut_paste_time))
            copy_paste_time = timeit.timeit(stmt=self.editor_copy_paste,setup=new_editor,number=1)
            print("{} copy paste operations took {} s".format(self.N, copy_paste_time))
            get_text_time = timeit.timeit(stmt=self.editor_get_text,setup=new_editor,number=1)
            print("{} text retrieval operations took {} s".format(self.N, get_text_time))
            mispellings_time = timeit.timeit(stmt=self.editor_mispellings,setup=new_editor,number=1)
            print("{} mispelling operations took {} s".format(self.N, mispellings_time))
    def testFunctions(self):
        s = SimpleEditor("hello friendsmy")
        s.copy(13, 15)
        s.paste(6)
        assert(s.get_text() == "hello myfriendsmy")
        s.undo()
        assert(s.get_text() == "hello friendsmy")
        s.redo()
        assert(s.get_text() == "hello myfriendsmy")
        s.cut(0, 6)
        assert(s.get_text() == "myfriendsmy")
        s.paste(11)
        assert(s.get_text() == "myfriendsmyhello ")
        print("Test Passed")

if __name__ == "__main__":
    b = EditorBenchmarker(["hello friends"], 100)
    b.benchmark()
    b.testFunctions()

#Essa é a estrutura de dados que ficara salva na memoria, tem coisas aqui que eu não utilizei, mas que podem ser utilizadas no futuro.
from typing import Iterable

class Line:
    def __init__(self, line, times_changed):
        self.line = line
        self.times_changed = times_changed

class File:
    def __init__(self, file_name):
        self.file_name = file_name
        self.lines_changed: Iterable[Line] = []
        self.times_changed = 0
    
    def count_change(self, line=None):
        self.times_changed += 1
        if line is not None:
            self.update_line(line)
    
    def update_line(self, line):
        for line_changed in self.lines_changed:
            if line_changed.line == line:
                line_changed.times_changed += 1
                break
        else:
            self.lines_changed.append(Line(line, 1))
        self.times_changed += 1

class Folder:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.times_changed = 0
        self.files: Iterable[File] = []

    def add_file(self, file_name):
        file = File(file_name)
        file.count_change()
        self.files.append(file)
    
    def remove_file(self, file_name):
        for file in self.files:
            if file.file_name == file_name:
                self.files.remove(file)
                break
    
    def count_change(self):
        self.times_changed += 1
    
    def count_file_change(self, file_name, line=None):
        for file in self.files:
            if file.file_name == file_name:
                file.count_change(line)
                break


class AuthorHistoryChange:
    def __init__(self):
        self.lines_added = 0
        self.lines_removed = 0
        self.files_changed = 0
        self.total_lines_changed = 0
        self.date = None


class Author:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.times_changed = 0
        self.changes: Iterable[AuthorHistoryChange] = []
    
    def add_change(self, lines_added, lines_removed, files_changed, total_lines_changed, date):
        change = AuthorHistoryChange()
        change.lines_added = lines_added
        change.lines_removed = lines_removed
        change.date = date
        change.files_changed = files_changed
        change.total_lines_changed = total_lines_changed
        self.changes.append(change)
        self.times_changed += 1
        

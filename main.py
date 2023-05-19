import sys

from peewee import *
from PySide6.QtCore import QAbstractListModel, QFile, QIODevice, Qt
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow

db = SqliteDatabase("notes.db")

class Note(Model):
    title = CharField()
    active = BooleanField(default=False)

    class Meta:
        database = db

db.connect()
db.create_tables([Note])

class NoteModel(QAbstractListModel):
    def __init__(self, *args, notes=None, **kwargs):
        super(NoteModel, self).__init__(*args, **kwargs)
        self.notes = notes or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            status, text = self.notes[index.row()]
            return text

    def rowCount(self, index):
        return len(self.notes)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.load_ui()
        self.model = NoteModel()
        self.w.listView_Notes.setModel(self.model)
        self.load_data()

    def load_ui(self):
        loader = QUiLoader()
        ui_file_name = "window.ui"
        ui_file = QFile(ui_file_name)
        if not ui_file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_name}: {ui_file.errorString()}")
            sys.exit(-1)
        self.w = loader.load(ui_file)
        if not loader:
            print(loader.errorString())
            sys.exit(-1)
        ui_file.close()

        self.w.action_Quit.triggered.connect(self.close_app)
        self.w.action_Add.pressed.connect(self.add_note)
        self.w.action_Remove.triggered.connect(self.remove_note)

    def close_app(self):
        sys.exit(0)

    def load_data(self):
        notes = Note.select()
        for note in notes:
            self.model.notes.append((note.active, note.title))

    def add_note(self):
        note_text = self.w.plainText_Note.toPlainText()
        if note_text.strip():
            note = Note(title=note_text.strip())
            if note.save():
                self.model.notes.append((False, note_text))
                self.model.layoutChanged.emit()
                self.w.plainText_Note.setPlainText("")

    def remove_note(self):
        indexes = self.w.listView_Notes.selectedIndexes()
        if indexes:
            index = indexes[0]
            note = Note().get(title=index.data())
            if note.delete_instance():
                del self.model.notes[index.row()]
                self.model.layoutChanged.emit()
                self.w.listView_Notes.clearSelection()
            


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.w.show()
    sys.exit(app.exec())
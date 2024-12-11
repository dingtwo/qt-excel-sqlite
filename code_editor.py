from PyQt5.Qsci import QsciScintilla, QsciLexerPython
from PyQt5.QtWidgets import QVBoxLayout, QWidget


class CodeEditor(QsciScintilla):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Syntax highlighting
        lexer = QsciLexerPython()
        lexer.setDefaultFont(self.font())
        self.setLexer(lexer)

        # Editor settings
        self.setTabWidth(4)
        self.setIndentationsUseTabs(False)
        self.setUtf8(True)
        self.setFolding(QsciScintilla.PlainFoldStyle)
        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)
        self.setAutoIndent(True) 

        # Autocompletion
        self.setAutoCompletionThreshold(2)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)

from PyQt4 import QtGui, QtCore
from helpedwidget import *
from widgets.util import *

class AddRemoveWidget(QtGui.QWidget):
    """
    A simple class that provides to vertically positioned buttons for adding and removing something.
    The addFunction and removeFunction functions must be provided.
    """
    def __init__(self, parent=None, addFunction=None, removeFunction=None, horizontal=False):
        """Creates a two button widget"""
        QtGui.QWidget.__init__(self, parent)

        self.addButton = QtGui.QToolButton(self)
        self.addButton.setIcon(resourceIcon("add"))
        self.addButton.setIconSize(QtCore.QSize(16, 16))
        self.connect(self.addButton, QtCore.SIGNAL('clicked()'), addFunction)

        self.removeButton = QtGui.QToolButton(self)
        self.removeButton.setIcon(resourceIcon("remove"))
        self.removeButton.setIconSize(QtCore.QSize(16, 16))
        self.connect(self.removeButton, QtCore.SIGNAL('clicked()'), removeFunction)

        if horizontal:
            self.buttonLayout = QtGui.QHBoxLayout()
        else:
            self.buttonLayout = QtGui.QVBoxLayout()

        self.buttonLayout.setMargin(0)

        if horizontal:
            self.buttonLayout.addStretch(1)

        self.buttonLayout.addWidget(self.addButton)
        self.buttonLayout.addWidget(self.removeButton)

        if not horizontal:
            self.buttonLayout.addStretch(1)
        else:
            self.buttonLayout.addSpacing(2)

        self.setLayout(self.buttonLayout)

    def enableAddButton(self, state):
        """Enable or disable the add button"""
        self.addButton.setEnabled(state)

    def enableRemoveButton(self, state):
        """Enable or disable the remove button"""
        self.removeButton.setEnabled(state)


class KeywordList(HelpedWidget):
    """Shows a list of keywords. The data structure expected and sent to the getter and setter is an array of values."""
    def __init__(self, parent=None, listLabel="", help=""):
        """Construct a list for showing keywords"""
        HelpedWidget.__init__(self, parent, listLabel, help)

        self.list = QtGui.QListWidget(self)
        self.list.setMinimumHeight(50)
        self.list.setMaximumHeight(70)

        self.addWidget(self.list)

        self.addRemoveWidget = AddRemoveWidget(self, self.addItem, self.removeItem)
        self.addWidget(self.addRemoveWidget)

        #self.addStretch()
        self.addHelpButton()
        self.title = "New keyword"
        self.description = "Enter name of keyword:"

    def setPopupLabels(self, title, description):
        """Change the labels of the default popup."""
        self.title = title
        self.description = description

    def newKeywordPopup(self, list):
        """
        Pops up a message box asking for a new keyword.
        Override this and return a string to customize the input dialog - Empty string equals canceled.
        The provided list are the already defined keywords
        """
        newKeyword, ok = QtGui.QInputDialog.getText(self, self.tr(self.title), self.tr(self.description), QtGui.QLineEdit.Normal)

        if ok:
            return str(newKeyword).strip()
        else:
            return ""    

    def addItem(self):
        """Called by the add button to insert a new keyword"""
        newKeyword = self.newKeywordPopup(self.getList())
        if not newKeyword == "":
            self.list.addItem(newKeyword)
            self.contentsChanged()


    def removeItem(self):
        """Called by the remove button to remove a selected keyword"""
        if not self.list.currentItem() == None:
            self.list.takeItem(self.list.currentRow())
            self.contentsChanged()


    def getList(self):
        """Returns the keywrods available in the list"""
        keywordList = []
        for index in range(self.list.count()):
            keywordList.append(str(self.list.item(index).text()))
        return keywordList

    def contentsChanged(self):
        """Called whenever the contents of the list changes."""
        self.updateContent(self.getList())


    def fetchContent(self):
        """Retrieves data from the model and inserts it into the list"""
        keywords = self.getFromModel()

        self.list.clear()

        for keyword in keywords:
            self.list.addItem(keyword)



class KeywordTable(HelpedWidget):
    """Shows a table of key/value pairs. The data structure expected and sent to the getter and setter is a dictionary of values."""
    def __init__(self, parent=None, tableLabel="", help="", colHead1="Keyword", colHead2="Value"):
        """Construct a table for key/value pairs."""
        HelpedWidget.__init__(self, parent, tableLabel, help)

        self.table = QtGui.QTableWidget(self)
        self.table.setColumnCount(2)
        self.headers = [colHead1, colHead2]
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setColumnWidth(0, 150)
        #self.table.setColumnWidth(1, 250)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setMinimumHeight(110)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.addWidget(self.table)

        self.addWidget(AddRemoveWidget(self, self.addItem, self.removeItem))

        self.addHelpButton()

        #self.connect(self.spinner, QtCore.SIGNAL('valueChanged(int)'), self.updateContent)
        self.connect(self.table, QtCore.SIGNAL('cellChanged(int,int)'), self.contentsChanged)


    def addItem(self):
        """Called by the add button to insert a new keyword"""
        self.table.insertRow(self.table.currentRow() + 1)
        self.contentsChanged()


    def removeItem(self):
        """Called by the remove button to remove a selected keyword"""
        currentRow = self.table.currentRow()

        if currentRow >= 0:
            doDelete = QtGui.QMessageBox.question(self, "Delete row?", "Are you sure you want to delete the key/value pair?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )

            if doDelete:
                self.table.removeRow(currentRow)
                self.contentsChanged()


    def contentsChanged(self):
        """Called whenever the contents of a cell changes."""
        keyValueList = []

        for index in range(self.table.rowCount()):
            key = self.table.item(index, 0)
            if not key == None:
                key = str(key.text()).strip()
                value = self.table.item(index, 1)

                if not key == "" and not value == None:
                    keyValueList.append([key, str(value.text()).strip()])

        self.updateContent(keyValueList)


    def fetchContent(self):
        """Retrieves data from the model and inserts it into the table."""
        values = self.getFromModel()

        for row in reversed(range(self.table.rowCount())):
            self.table.removeRow(row)

        #for column in reversed(range(self.table.columnCount())):
        #    self.table.removeColumn(column)

        #self.table.clearContents()

        row = 0
        for value in values:
            keyItem = QtGui.QTableWidgetItem(value[0])
            valueItem = QtGui.QTableWidgetItem(value[1])
            self.table.insertRow(row)
            self.table.setItem(row, 0, keyItem)
            self.table.setItem(row, 1, valueItem)
            row+=1
            



class MultiColumnTable(HelpedWidget):
    """Shows a table of parameters. The data structure expected and sent to the getter and setter is an array of arrays."""
    def __init__(self, parent=None, tableLabel="", help="", colHeads=["c1", "c2", "c3", "c4", "c5"]):
        """Construct a table with arbitrary number of columns."""
        HelpedWidget.__init__(self, parent, tableLabel, help)

        self.table = QtGui.QTableWidget(self)
        self.table.setColumnCount(len(colHeads))
        self.headers = colHeads
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.setColumnWidth(0, 150)
        #self.table.setColumnWidth(1, 250)
        #self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        #self.table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Interactive)

        self.table.setMinimumHeight(110)
        self.table.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.addWidget(self.table)


        self.addWidget(AddRemoveWidget(self, self.addItem, self.removeItem))

        self.addHelpButton()

        #self.connect(self.spinner, QtCore.SIGNAL('valueChanged(int)'), self.updateContent)
        self.connect(self.table, QtCore.SIGNAL('cellChanged(int,int)'), self.contentsChanged)


    def addItem(self):
        """Called by the add button to insert a new keyword"""
        self.table.insertRow(self.table.currentRow() + 1)
        self.contentsChanged()


    def removeItem(self):
        """Called by the remove button to remove a selected keyword"""
        currentRow = self.table.currentRow()

        if currentRow >= 0:
            doDelete = QtGui.QMessageBox.question(self, "Delete row?", "Are you sure you want to delete the key/value pair?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No )

            if doDelete:
                self.table.removeRow(currentRow)
                self.contentsChanged()


    def contentsChanged(self):
        """Called whenever the contents of a cell changes."""
        rowValues = []

        for rowIndex in range(self.table.rowCount()):
            row = []
            for columnIndex in range(self.table.columnCount()):
                item = self.table.item(rowIndex, columnIndex)
                if not item == None:
                    row.append(str(item.text()))
                else:
                    row.append("")

            rowValues.append(row)


        self.updateContent(rowValues)


    def fetchContent(self):
        """Retrieves data from the model and inserts it into the table"""
        rows = self.getFromModel()

        self.table.clear()
        self.table.setHorizontalHeaderLabels(self.headers)

        rowIndex = 0
        for row in rows:
            self.table.insertRow(rowIndex)
            columnIndex = 0
            for value in row:
                item = QtGui.QTableWidgetItem(str(value))                
                self.table.setItem(rowIndex, columnIndex, item)
                columnIndex+=1

            rowIndex+=1

    def setDelegate(self, column, delegate):
        self.table.setItemDelegateForColumn(column, delegate)



class SpinBoxDelegate(QtGui.QItemDelegate):
    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    # QWidget *parent, const QStyleOptionViewItem &/* option */, const QModelIndex &/* index */
    def createEditor(self, parent, option, index):
        editor = QtGui.QSpinBox(parent)

        editor.setMinimum(0)
        editor.setMaximum(100)

        return editor

    #QWidget *editor, const QModelIndex &index
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole).toInt()
        editor.setValue(value[0])

    #QWidget *editor, QAbstractItemModel *model, const QModelIndex &index
    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()

        model.setData(index, value, QtCore.Qt.EditRole)

    #Widget *editor, const QStyleOptionViewItem &option, const QModelIndex &/* index */
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DoubleSpinBoxDelegate(QtGui.QItemDelegate):
    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    # QWidget *parent, const QStyleOptionViewItem &/* option */, const QModelIndex &/* index */
    def createEditor(self, parent, option, index):
        editor = QtGui.QDoubleSpinBox(parent)

        editor.setMinimum(0)
        editor.setMaximum(100)
        editor.setDecimals(2)
        editor.setSingleStep(0.01)

        return editor

    #QWidget *editor, const QModelIndex &index
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole).toDouble()
        editor.setValue(value[0])

    #QWidget *editor, QAbstractItemModel *model, const QModelIndex &index
    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()

        model.setData(index, value, QtCore.Qt.EditRole)

    #Widget *editor, const QStyleOptionViewItem &option, const QModelIndex &/* index */
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ComboBoxDelegate(QtGui.QItemDelegate):
    def __init__(self, parent):
        QtGui.QItemDelegate.__init__(self, parent)

    # QWidget *parent, const QStyleOptionViewItem &/* option */, const QModelIndex &/* index */
    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)

        editor.setMinimum(0)
        editor.setMaximum(100)
        editor.setDecimals(2)
        editor.setSingleStep(0.01)

        return editor

    #QWidget *editor, const QModelIndex &index
    def setEditorData(self, editor, index):
        value = index.model().data(index, QtCore.Qt.EditRole).toDouble()
        editor.setValue(value[0])

    #QWidget *editor, QAbstractItemModel *model, const QModelIndex &index
    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()

        model.setData(index, value, QtCore.Qt.EditRole)

    #Widget *editor, const QStyleOptionViewItem &option, const QModelIndex &/* index */
    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


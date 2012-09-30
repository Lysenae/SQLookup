#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
from database import *

TIMEOUT = 2000
MAX = 400

class PictureDialog(QtGui.QDialog):

    def __init__(self, img):
        '''
        Constructs dialog.
        '''
        
        super(PictureDialog, self).__init__()
        
        self.setModal(True)
        self.setWindowTitle("SQLookup Image Viewer")
        self.setWindowIcon(QtGui.QIcon('icons/app_icon.png'))
        
        self._layout = QtGui.QHBoxLayout(self)
        
        self._pixmap = QtGui.QPixmap()
        
        self._label = QtGui.QLabel(self)
        self._label.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.scale_image(img)
        
        self._layout.addWidget(self._label)
        self.setLayout(self._layout)
        
        self.show()
        
    def scale_image(self, img):
        '''
        Scales loaded image.
        '''
    
        self._pixmap.loadFromData(img)
        sizes = self._pixmap.size()
        pm = None
        
        if sizes.height() > MAX and sizes.width() > MAX:
            wx = float(sizes.width()) / float(MAX)
            hx = float(sizes.height()) / float(MAX)
            pm = self._pixmap.scaled(int(sizes.width() / wx),
             int(sizes.height() / hx), QtCore.Qt.KeepAspectRatio)
            
        elif sizes.height() > MAX and sizes.width() < MAX:
            hx = float(sizes.height()) / float(MAX)
            pm = self._pixmap.scaled(int(sizes.width() / hx),
             int(sizes.height() / hx), QtCore.Qt.KeepAspectRatio)
            
        elif sizes.height() < MAX and sizes.width() > MAX:
            wx = float(sizes.width()) / float(MAX)
            pm = self._pixmap.scaled(int(sizes.width() / wx),
             int(sizes.height() / wx), QtCore.Qt.KeepAspectRatio)
            
        else:
            pm = self._pixmap 
        
        self.setFixedSize(pm.size().width(), pm.size().height())
        self._label.setPixmap(pm)

class SQLookup(QtGui.QMainWindow):
    
    def __init__(self):
        '''
        Constructs GUI.
        '''
        
        super(SQLookup, self).__init__()
        self._build_ui()
        self._databases = []
        self._acive_table = None
        
    def _build_ui(self):
        '''
        Builds widgets.
        '''
        
        self.setGeometry(100, 100, 800, 350)
        self.setMinimumSize(400, 200)
        self.setWindowTitle('SQLookup')
        self.setWindowIcon(QtGui.QIcon('icons/app_icon.png'))
    
        self._toolbar = self.addToolBar('Tools')
        self._menubar = QtGui.QMenuBar(self)
        self._statusbar = QtGui.QStatusBar(self)
        self._create_actions()
        
        self._table_view = QtGui.QTreeView(self)
        self._table_view.setMinimumSize(150, 150)
        
        self._editor_view = QtGui.QTreeView(self)
        self._editor_view.setMinimumSize(250, 150)

        self._splitter = QtGui.QSplitter(QtCore.Qt.Horizontal)        
        self._splitter.addWidget(self._table_view)
        self._splitter.addWidget(self._editor_view)
        self._splitter.setChildrenCollapsible(False)
        self._splitter.moveSplitter(260, 0)
        
        self.setCentralWidget(self._splitter)
        self.setMenuBar(self._menubar)
        self.setStatusBar(self._statusbar)
        
        #Create table view and model:
        self._table_model = QtGui.QStandardItemModel(0, 4, self)
        self._table_model.setHorizontalHeaderLabels(['Name','Rows','Columns', 'Path'])
        self._table_view.setModel(self._table_model)
        self._table_view.setColumnWidth(0, 150)
        self._table_view.setColumnWidth(1, 45)
        self._table_view.setColumnWidth(2, 45)
        self._table_view.setColumnHidden(3, True)
        self._table_view.activated.connect(self.on_table_activated)
        
        self._editor_model = None
        
        #Empty model; used on startup or when table's database is closed:
        self._empty_model = QtGui.QStandardItemModel(0, 1, self)
        self._empty_model.setHorizontalHeaderLabels(['<Nothing>'])
        self._editor_view.setModel(self._empty_model)
        self._editor_view.activated.connect(self.on_row_item_activated)
        
        self.show()
        
    def _create_actions(self):
        '''
        Creates actions and connects them to slots
        '''
        
        self._open_db = QtGui.QAction(QtGui.QIcon('icons/db_open.png'), 'Open DB', self)
        self._open_db.setShortcut('Ctrl+O')
        self._open_db.triggered.connect(self._open_db_clicked)
        
        self._new_db = QtGui.QAction(QtGui.QIcon('icons/db_new.png'), 'New DB', self)
        #self._new_db.setShortcut('Ctrl+N')
        #self._new_db.triggered.connect() #TODO: Slot implementation
        
        self._close_db = QtGui.QAction(QtGui.QIcon('icons/db_close.png'), 'Close DB', self)
        self._close_db.setShortcut('Ctrl+Q')
        self._close_db.triggered.connect(self._close_db_clicked)
        
        self._commit_db = QtGui.QAction(QtGui.QIcon('icons/db_commit.png'), 'Commit', self)
        #self._commit_db.setShortcut('Ctrl+S')
        #self._commit_db.triggered.connect() #TODO: Slot implementation
        
        self._rollback_db = QtGui.QAction(QtGui.QIcon('icons/db_rollback.png'), 'Rollback', self)
        #self._rollback_db.setShortcut('Ctrl+Z')
        #self._rollback_db.triggered.connect() #TODO: Slot implementation
        
        self._quit = QtGui.QAction(QtGui.QIcon('icons/quit.png'), 'Quit', self)
        self._quit.setShortcut('Ctrl+X')
        self._quit.triggered.connect(self.close)
        
        self._build_toolbar()
        self._build_menubar()
        
    def _build_toolbar(self):
        '''
        Adds actions to toolbar.
        '''
        
        self._toolbar.addAction(self._open_db)
        self._toolbar.addAction(self._new_db)
        self._toolbar.addAction(self._close_db)
        self._toolbar.addAction(self._commit_db)
        self._toolbar.addAction(self._rollback_db)
        #self.tool_bar.addAction(self._quit)
        
    def _build_menubar(self):
        '''
        Adds actions to menubar.
        '''
        
        self._menu_application = self._menubar.addMenu('&Application')
        self._menu_application.addAction(self._quit)
        
        self._menu_database = self._menubar.addMenu('&Database')
        self._menu_database.addAction(self._open_db)
        self._menu_database.addAction(self._new_db)
        self._menu_database.addAction(self._close_db)
        self._menu_database.addAction(self._commit_db)
        self._menu_database.addAction(self._rollback_db)
        
    def db_count(self):
        '''
        Returns count of currently opened databases.
        '''
        
        return len(self._databases)
        
    def set_editable(self, items, editable):
        '''
        Sets <items>'s editable property to <editable>.
        
        @items -- list of items, list(QtGui.QStandardItem)
        @editable -- value to be set, bool
        '''
        
        for i in items:
            if type(i) == QtGui.QStandardItem:
                i.setEditable(editable)
            else:
                continue
                
    def remove_database(self, db_path):
        '''
        Disconnects and closes selected database.
        
        @db_path -- path to the database, str
        '''
        
        if self.db_count() == 0:
            return
        else:
            for i in range(self.db_count()):
                if self._databases[i].path() == db_path:
                    self._databases[i].disconnect()
                    del self._databases[i]
                    return
                    
    def get_database(self, db_path):
        '''
        Gets database with <db_path> from list of opened databases.
        
        @db_path -- path to the database, str
        '''
        
        if self.db_count() == 0:
            return None
        else:
            for db in self._databases:
                if db.path() == db_path:
                    return db
                    
    def remove_editor_view(self, db_path):
        '''
        Removes editor's view if database of shown table is closed.
        Does nothing if table does not belong to closed database.
        
        @db_path - path to the database, str
        '''

        if self._active_table.database_path() == db_path:
                self._editor_view.setModel(self._empty_model)
                
    def closeEvent(self, event):
        '''
        Reimplemented Qt's closeEvent.
        Disconnects all databases and cloces application.
        
        @event -- close event, QtGui.QCloseEvent
        '''
        
        if self.db_count() > 0:
            for db in self._databases:
                print("Disconnecting {0}...".format(db.name()))
                db.disconnect()
                print("Done")
                
        
    def _open_db_clicked(self):
        '''
        Opens and connects database. Lists all the table in database.
        '''
    
        fname, tmp = QtGui.QFileDialog.getOpenFileName(self, 'Open database', '/home/daniel/Dokumenty/Python/SQLite Lookup')

        cur = self.db_count()
        db_opened = False
        
        if fname == "":
            return
        
        if cur > 0:
            for db in self._databases:
                if fname == db.path():
                    db_opened = True

        if not db_opened:
            self._databases.append(Database())
            
            try:
                self._databases[cur].connect(fname)
            except ConnectionError as er:
                self._statusbar.showMesage(str(er), TIMEOUT)
                del self._databases[cur]
            else: 
                try:
                    tables = self._databases[cur].table_names()
                except InvalidFileError as er:
                    self._statusbar.showMessage(str(er), TIMEOUT)
                    del self._databases[cur]
                else:
                    item = QtGui.QStandardItem(self._databases[cur].name())
                    params = [item ,QtGui.QStandardItem(''),QtGui.QStandardItem(''), QtGui.QStandardItem(fname)]
                    self.set_editable(params, False)
                    self._table_model.appendRow(params)
                    tables = self._databases[cur].table_names()
                    
                    for t in tables:
                        tbl = self._databases[cur].get_table(t)
                        params = []
                        params.append(QtGui.QStandardItem(tbl.name()))
                        params.append(QtGui.QStandardItem(str(tbl.row_count())))
                        params.append(QtGui.QStandardItem(str(tbl.column_count())))
                        self.set_editable(params, False)
                        item.appendRow(params)
                    
                    #Set item as expanded when loaded:    
                    index = self._table_model.indexFromItem(item)
                    self._table_view.setExpanded(index, True)
        else:
            self._statusbar.showMessage("Database with same name already opened.", TIMEOUT)
        
    def _close_db_clicked(self):
        '''
        Closes selected database.
        '''
        
        if len(self._table_view.selectionModel().selection().indexes()) == 0:
            self._statusbar.showMessage("Can't close database. No database selected.", TIMEOUT)
        else:
            model = self._table_view.model()
            current = self._table_view.currentIndex()
            parent = model.parent(current)
            db_name = ""
            db_path = ""
            
            if parent.isValid():
                db_name = str(model.data(parent))
                #Get database path from 3rd column which stores path:
                db_path = str(model.data(parent.sibling(parent.row(), 3)))
                self.remove_database(db_path)
                model.removeRow(parent.row())
            else:
                db_name = str(model.data(current))
                #Get database path from 3rd column which stores path:
                db_path = str(model.data(current.sibling(current.row(), 3)))
                self.remove_database(db_path)
                model.removeRow(current.row())
                
            self.remove_editor_view(db_path)
                
            self._statusbar.showMessage("Database {0} sucessfully closed.".format(db_name), TIMEOUT)
            
    def on_table_activated(self, index):
        '''
        Activates table and show table's content in editor view.
        
        @index -- index of the table, QtGui.QModelIndex
        '''
        
        model = self._table_view.model()
        db_path = ""
        db = None
        
        #If user did not clicked 1st column:
        sibling = index.sibling(index.row(), 0)
        if sibling != index:
            index = sibling
            
        parent = model.parent(index)
        
        #Do something only if table is activated, do nothing otherwise:
        if parent.isValid():
            self._editor_model = None
            db_path = str(model.data(parent.sibling(parent.row(), 3)))
            db = self.get_database(db_path)
            table = db.get_table(str(model.data(index)))
            
            #Set up editor view and model:
            cols = table.column_count()
            if cols > 0:
                self._editor_model = QtGui.QStandardItemModel(0, cols, self)
                col_names = table.column_names()
                self._editor_model.setHorizontalHeaderLabels(col_names)
                self._editor_view.setModel(self._editor_model)
                self._active_table = table
                
                for i in range(cols):
                    self._editor_view.setColumnWidth(i, 125)
                
                #Load rows:
                rows = table.rows()
                for row in rows:
                    params = []
                    
                    for r in range(len(row)):
                        clmn = table.get_column_by_id(r)
                        if clmn.data_type() == "BLOB":
                            params.append(QtGui.QStandardItem("<BLOB>"))
                        else:
                            params.append(QtGui.QStandardItem(str(row[r])))
                        
                    self.set_editable(params, False)                        
                    self._editor_model.appendRow(params)
                    
    def on_row_item_activated(self, index):
        '''
        In view mode shows BLOB content, string datas are ignored.
        
        @index -- index of the table, QtGui.QModelIndex
        '''
        
        model = self._editor_view.model()
        table = self._active_table
        header = model.headerData(index.column(), QtCore.Qt.Horizontal)
        pks = table.primary_keys()
        img = None
        all_ok = True
        
        if model.data(index) == "<BLOB>":
            #Verify if it's really column of type BLOB:
            clmn = table.get_column_by_id(index.column())
            if clmn.data_type() == "BLOB":
                pk_vals = []
                
                for pk_id in table.primary_keys_ids():
                    sblng = index.sibling(index.row(), pk_id)
                    if sblng.isValid():
                        pk_vals.append(model.data(sblng))
                    else:
                        all_ok = False
                        break
                        
                if all_ok:                
                    img = table.show_image(index.column(), pk_vals)
                    dialog = PictureDialog(img) 
                    
                    result = dialog.exec()                   

#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sqlite3 as sl
from exceptions import *

class Database:

    def __init__(self):
        '''
        Initialize database object.
        '''
        
        self._connection = None
        self._connected = False
        self._db_name = ""
        self._full_path = ""
        
    def __str__(self):
        '''
        Returns database name.
        '''
        
        return self.name()
        
    def is_connected(self):
        '''
        Verifies if database is currently connected.
        Returns True if DB is connected, otherwise returns False.
        '''
        
        if self._connected == True:
            return True
        else:
            return False
            
    def connection(self):
        '''
        Returns connection object of the database.
        '''
        
        return self._connection
             
    def name(self):
        '''
        Returns database name.
        '''
        
        return self._db_name
        
    def path(self):
        '''
        Returns path to the database file.
        '''
        
        return self._full_path
        
    def connect(self, path):
        '''
        Connects the database or create a new SQLite3 database.
        
        @path -- path to database file, str
        '''
        
        try:
            self._connection = sl.connect(path)
        except sl.OperationalError as er:
            raise ConnectionError(str(er), path)
        self._connected = True
        self._db_name = self._get_db_name(path)
        self._full_path = path
            
    def disconnect(self):
        '''
        Disconnect currently connected database.
        Raises NotConnectedError if database is not connected.
        '''
        
        if self.is_connected():
            self._connection.close()
            self._connected = False
        else:
            raise NotConnectedError(self._db_name)

    def _get_db_name(self, path):
        '''
        Private: Gets the database name from <path>.
        Works only with UNIX interpretation of paths.
        
        @path -- path to database file, str
        '''
        
        last = -1
        slash = False        
        pos = None
        
        while slash == False:
            if path[last] == '/':
                pos = last
                slash = True
            else:
                if last == 0 - len(path):
                    break
                else:
                    last = last - 1
                
        if slash == False:
            return path
        else:
            return path[pos+1:]
        
    def version(self):
        '''
        Returns SQLite version.
        Raises NotConnectedError if database is not connected.
        '''
        
        if self.is_connected():
            cur = self._connection.execute('SELECT SQLITE_VERSION()')
            ver = cur.fetchone()
            return ver[0]
        else:
            raise NotConnectedError(self._db_name)
            
    def table_names(self):
        '''
        Gets the table names from Master.
        Raises NotConnectedError if database is not connected.
        '''
        
        if self.is_connected():
            try:
                cur = self._connection.execute('SELECT Name FROM sqlite_master')
            except sl.DatabaseError as er:
                raise InvalidFileError(str(er), self.name())
                
            tbls = cur.fetchall()
            tables = []
            for tbl in tbls:
                tables.append(tbl[0])
            return tables
        else:
            raise NotConnectedError(self._db_name)
                                    
    def get_table(self, table_name):
        '''
        Retrieves the table with given <table_name> and returns its
        object representation if <table_name> matches the name in
        Master, otherwise raises TableNotFoundError.
        
        @table_name -- Name of the table, str
        '''
        
        tables = self.table_names()
        
        for table in tables:
            if table == table_name:
                return Table(table_name, self)
                
        raise TableNotFoundError(table_name, self.name())
        
class Table:

    def __init__(self, table_name, database):
        '''
        Creates an object representation of table with
        <table_name> from <database>.
        
        @table_name -- name of the table, str
        @database -- database it belongs to, Database
        '''
        
        if type(database) != Database or type(table_name) != str:
            raise InstanceCreationError(table_name)
            
        self._name = table_name
        self._database = database
        
    def __str__(self):
        '''
        Returns name of the table.
        '''
        
        return self.name()
        
    def name(self):
        '''
        Returns name of the table.
        '''
        
        return self._name
        
    def database(self):
        '''
        Returns database in which table is present.
        '''
        
        return self._database
        
    def database_name(self):
        '''
        Returns name of the database the table belongs to
        '''
        
        return self.database().name()
        
    def database_path(self):
        '''
        Returns path to the database file.
        '''
        
        return self.database().path()

    def connection(self):
        '''
        Returns database connection object.
        '''

        return self._database.connection()
        
    def is_connected(self):
        '''
        Returns True if database is connected, otherwise returns False.
        '''
        
        return self._database.is_connected()
        
    def set_name(self, name):
        '''
        Sets table name to <name>.
        
        @name -- new table name, str
        '''
        
        self._name = name
        
    def exists(self):
        '''
        Checks if table with name of this table exists in the database.
        Returns True if exists, otherwise returns False.
        '''
        
        tables = self.database().table_names()
        
        for table in tables:
            if table == self._name:
                return True
                
        return False
            
    def metadata(self):
        '''
        Returns metadata of table. Metadata: [Column ID, Column name,
        Data type, Not null, Default value, Primary key]
        If table does not exist returns empty list.
        Raises NotConnectedError if database is not connected.
        '''
        
        if self.is_connected():
            cur = self.connection().execute('PRAGMA table_info(' + self.name() + ')')
            meta = cur.fetchall()
            return meta
        else:
            raise NotConnectedError(self._db_name)
        
    def column_names(self):
        '''
        Gets the column names from <table_name>.
        If table does not exist returns empty list.
        Raises NotConnectedError if database is not connected.
        '''
        
        meta = self.metadata()
        columns = []
        for col_n in meta:
            columns.append(col_n[1])
        return columns
        
    def rows(self):
        '''
        Get rows from table.
        If table does not exists returns empty list.
        Raises NotConnectedError if database is not connected.
        '''
        
        if self.is_connected():
            try:
                cur = self.connection().execute('SELECT * FROM ' + self.name())
            except sl.OperationalError:
                raise TableNotFoundError(self.name(), self.db_name())
                
            rows = []
            
            while True:
                row = cur.fetchone()
                
                if row == None:
                    break
                    
                rows.append(row)
                    
            return rows
        else:
            raise NotConnectedError(self.database().name())
        
    def column_count(self):
        '''
        Returns number of columns.
        '''
        
        return len(self.column_names())
        
    def row_count(self):
        '''
        Returns number of rows.
        '''
        
        return len(self.rows())
        
    def primary_keys(self):
        '''
        Returns list of primary keys.
        '''
        
        meta = self.metadata()
        pks = []
        
        for m in meta:
            if m[5] == 1:
                pks.append(m[1])
                
        return pks
            
    def primary_keys_ids(self):
        '''
        Returns list of column ids that are primary keys.
        '''
        
        meta = self.metadata()
        pk_ids = []
        
        for pk in self.primary_keys():
            for m in meta:
                if m[1] == pk:
                    pk_ids.append(m[0])
            
        return pk_ids

    def show_image(self, img_col, pk_vals):
        '''
        Show image from column <img_col> identified by primary key
        values <pk_vals>.
        Raises NotConnectedError if database is not connected.
        
        @img_col -- column with stored image, int
        @pk_vals -- primary key values, list
        '''
        
        if self.is_connected():
            image_c = self.get_column_by_id(img_col)
            pks = self.primary_keys()
            pk_stmt = ""
            
            if len(pks) != len(pk_vals):
                raise InvalidParameterError(pk_vals, False)
            
            if len(pks) == 1:
                pk_stmt = "WHERE {0} = {1}".format(pks[0], pk_vals[0])
            else:
                pk_stmt = "WHERE "
                for i in range(len(pks)):
                    if i != len(pks) - 1:
                        pk_stmt = pk_stmt + "{0} = {1} AND ".format(pks[i], pk_vals[i])
                    else:
                        pk_stmt = pk_stmt + "{0} = {1}".format(pks[i], pk_vals[i])
                        
            if pk_stmt != "":
                stmt = "SELECT {0} FROM {1} {2}".format(image_c.name(), self.name(), pk_stmt)
                cur = self.database().connection().execute(stmt)
                img = cur.fetchone()[0]
                return img
            else:
                raise GenericError("Could not create SQL statement.")
        
        else:
            raise NotConnectedError(self.database_name())

    def get_column_by_name(self, col_name):
        '''
        Gets column with specified name <con_name> and returns it's object.
        If column does not exists returns None.

        @col_name -- name of the column, str
        '''

        cols = self.column_names()

        for col in cols:
            if col == col_name:
                return Column(col_name, self)
        raise ColumnNotFoundError("name", col_name, self.name())

    def get_column_by_id(self, col_id):
        '''
        Gets column with specified id <con_id> and returns it's object.
        If column does not exists returns None.

        @col_id -- id of the column, int
        '''

        meta = self.metadata()

        for m in meta:
            if m[0] == col_id:
                return Column(m[1], self)
        raise ColumnNotFoundError("id", col_id, self.name())

    def get_columns(self):
        '''
        Returns list of all columns in the table.
        '''

        meta = self.metadata()
        cols = []

        if len(meta) > 0:
            for m in meta:
                cols.append(Column(m[1], self))
            return cols
        else:
            return None

class Column:

    def __init__(self, col_name, table):
        '''
        Creates an object representation of the column with
        <col_name> from <table>.
        
        @col_name -- name of the column, str
        @table -- table it belongs to, Table
        '''
        
        if type(table) != Table or type(col_name) != str:
            raise InstanceCreationError(col_name)

        self._name = col_name
        self._table = table
        self._id = self._id_by_name(col_name)

    def table(self):
        '''
        Returns table which column belongs to.
        '''

        return self._table

    def __str__(self):
        '''
        Returns name of the column.
        '''

        return self.name()

    def name(self):
        '''
        Returns name of the column.
        '''

        return self._name

    def id(self):
        '''
        Returns id of the column.
        '''

        return self._id

    def database(self):
        '''
        Returns database object which it belongs to.
        '''

        return self.table().database()

    def is_connected(self):
        '''
        Returns True if is connected otherwise returns False.
        '''

        return self.table().is_connected()

    def is_primary_key(self):
        '''
        Returns True if column is primary key,
        otherwise returns False.
        '''
        
        meta = self.table().metadata()
        
        for m in meta:
            if m[0] == self.id() and m[5] == 1:
                return True
        return False
            
    def is_not_null(self):
        '''
        Returns True if column can not by null,
        otherwise returns False.
        '''
       
        meta = self.table().metadata()
        
        for m in meta:
            if m[0] == self.id() and m[3] == 1:
                return True
        return False     
        
    def default_value(self):
        '''
        Returns default value for the column. 
        '''
        
        meta = self.table().metadata()
        
        for m in meta:
            if m[0] == self.id():
                return m[4]
            
    def data_type(self):
        '''
        Returns data type of the column. 
        '''
     
        meta = self.table().metadata()
        
        for m in meta:
            if m[0] == self.id():
                return m[2]

    def _id_by_name(self, col_name):
        '''
        Returns ID of the column <col_name>. Returns None if column
        with specified name does not exists.
        
        @col_name -- name of the column, str
        '''
        

        meta = self.table().metadata()
        
        for m in meta:
            if m[1] == col_name:
                return m[0]
        return None

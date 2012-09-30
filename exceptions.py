#!/usr/bin/python3
# -*- coding: utf-8 -*-

class GenericError(Exception):
    '''Something happend.'''
    
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

class NotConnectedError(Exception):
    '''Database is not connected.'''
    
    def __init__(self, db_name):
        self.msg = "Database {0} is not connected".format(db_name)
        
    def __str__(self):
        return self.msg
        
class TableNotFoundError(Exception):
    '''Table does not exist in connected database.'''
    
    def __init__(self, table_name, db_name):
        self.msg = "{0} does not exists in {1}".format(table_name, db_name)
        
    def __str__(self):
        return self.msg
        
class ConnectionError(Exception):
    '''Could not connect database.'''
    
    def __init__(self, msg, db_name):
        self.msg = "Could not connect: {0} \"{1}\"".format(msg, db_name)
        
    def __str__(self):
        return self.msg
        
class InstanceCreationError(Exception):
    '''Could not create class instance.'''
    
    def __init__(self, instance_name):
        self.msg = "Could not create class instance \"{0}\". Wrong parameter type.".format(instance_name)
        
    def __str__(self):
        return self.msg
        
class InvalidFileError(Exception):
    '''Attempt to open invalid file type.'''
    
    def __init__(self, msg, fname):
        self.msg = "Invalid file {0}: {1}".format(fname, msg)
        
    def __str__(self):
        return self.msg
        
class InvalidParameterError(Exception):
    '''Invalid parameter in function call.'''
    
    def __init__(self, param, type_err):
        if type_err:
            self.msg = "Invalid type of parameter: \"{0}\".".format(param)
        else:
            self.msg = "Invalid value of parameter: \"{0}\".".format(param)
        
    def __str__(self):
        return self.msg
        
class ColumnNotFoundError(Exception):
    '''Could not found column with specified id.'''
    
    def __init__(self, what, val, tname):
            self.msg = "Column with {0} \"{1}\" colud not be found in \"{2}\".".format(what, val, tname)
        
    def __str__(self):
        return self.msg
     

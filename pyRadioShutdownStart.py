def parser( ):
... # when error found
... raise formatError, {'line':42, 'file':'spam.txt'}
try:
... parser( )
... except formatError, X:
... print 'Error at', X['file'], X['line']

__all__ = ("FileReader", )

from inspect import EndOfBlock


class FileReader:
    __slots__ = ("file_name",  "line_no", "pos", "_file", "line")

    def __init__(self, file_name: str):
        self.file_name = file_name
        self.line_no = 1
        self.pos  = 0
        self._file = open(file_name, "rb") 
        self.line = bytearray()
    
    def __repr__(self):
        return f"File:{self.file_name},Line:{self.line_no}, pos:self._pos"

    def close(self):
        if self._file != None:
            self._file.close()
        
    @property
    def ch(self):
        # this is a getter for the reader function
        # the job of the reader is to read the data byte at a time
        # and update position and charector as required
        ch = self._file.read(1)
        if ch == b'\n':
            self.line_no += 1
            self.pos = 0
            self.line = bytearray()
        self.pos += 1
        self.line.extend(ch)
        return ch

    def read_line(self):
        while  1:
            ch = self._file.read(1)
            if ch == b'\n' or ch == b'\r':
                break
            self.line.extend(ch)


class interfaceState():
    def __init__(self):
        self.status = None
        self.PARENT_DIRECTORY = None
        self.PROJECT = None

    def set_PARENT_DIRECTORY(self,direc):
        self.PARENT_DIRECTORY = direc
    
    def get_PARENT_DIRECTORY(self):
        return self.PARENT_DIRECTORY
    
    def set_PROJECT(self,projectName):
        self.PROJECT = projectName
    
    def get_PROJECT(self):
        return self.PROJECT
        
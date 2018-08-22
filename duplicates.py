'''
a wrapper to keep track of posts that have already been logged.
'''


class Duplicates:
    '''
    keeps track of duplicates DB
    '''

    def __init__(self, filename):
        self.__duplicates_db = set()
        self.__filename = filename
        self.__refresh()

    def __refresh(self):
        with open(self.__filename, 'r') as file:
            for line in file:
                self.__duplicates_db.add(line.strip())

    def duplicate_check(self, post_id):
        '''
        Checks the 'db' to see if this has already been posted
        '''
        return post_id in self.__duplicates_db

    def add_id(self, post_id):
        '''
        adds an entry to the 'db' to track what has been posted
        '''
        with open(self.__filename, 'a') as file:
            file.write(post_id + "\n")
            self.__duplicates_db.add(post_id)

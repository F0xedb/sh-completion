import argparse
import re

parser = argparse.ArgumentParser(description='Generate Bash and zsh completion scripts')
parser.add_argument('input', help='The file to generate bash and zsh scripts from', nargs=1)
parser.add_argument('--bash', "-b" , help='Generate bash only', action='store_true')
parser.add_argument('--zsh', '-z', help='Generate zsh only', action='store_true')

class Options:
    def __init__(self, file, bGenBash, bGenZsh):
        self.file = file
        self.bGenBash = bGenBash
        self.bGenZsh = bGenZsh

class Config:
    """
    Contains all fields present in the config file eg the root, all submodules and functions
    """
    def __init__(self):
        self.name = ""
        self.root = []
        self.sections = []
        self.functions = []
    
    def populate(self, stringList):
        self._pullName(stringList)
        self._pullRoot(stringList)
        self._pullSections(stringList)
        self._pullFunctions(stringList)

    def _pullName(self, stringList):
        string = stringList[0]
        if(string[0] != "#"):
            raise Exception("Could not determin the program name. Make sure the first line followes this format # <name>")
        self.name = string[1:]

    def _getCharOccurrenceInstr(self, string, char="("):
        occurrence = 0
        for i in string:
            if i == char:
                occurrence += 1
        return occurrence
    
    def _getSection(self, stringList, startIndex):
        """
        Find all given list in the config and return a list of all newlines.
        The first entry of the list contains the name of said list
        """
        index = startIndex
        openBrace = self._getCharOccurrenceInstr(stringList[index])
        section = [stringList[index].replace("=(","")]
        # gather everything that belongs to the given section
        while not openBrace == 0:
            index +=1
            openBrace += self._getCharOccurrenceInstr(stringList[index])
            openBrace -= self._getCharOccurrenceInstr(stringList[index], ")")
            section.append(stringList[index])
        # filter out the assignment and the end
        section = section[:-1]
        # filter all beginning whitespace and ending whitespace
        for index, item in enumerate(section):
            section[index] = item.strip().replace('"', '')
        return section

    
    def _pullRoot(self, stringList):
        for index, part in enumerate(stringList):
            if "root=" in part:
                self.root = self._getSection(stringList, index)
                return
    
    def _pullSections(self, stringList):
        for index, item in enumerate(stringList):
            if(re.match("^.*=\(", item) and not re.match("^root=\(", item)):
                self.sections.append(self._getSection(stringList, index))

    def _getFunction(self, stringlist, startIndex):
        """
        Return a list containing the function.
        The first element is the name of said function.
        This is followed by a list of all elements in the function
        """
        openBraces = self._getCharOccurrenceInstr(stringlist[startIndex], char="{")
        index = startIndex
        function = [stringlist[startIndex].replace("function", "").replace("{", "").strip()]
        while openBraces > 0:
            index += 1
            openBraces += self._getCharOccurrenceInstr(stringlist[index], char="{") 
            openBraces -= self._getCharOccurrenceInstr(stringlist[index], char="}") 
            function.append(stringlist[index])
        # return the function body
        # we discard the closing brace (which must be at the closing brace)
        return function[:-1]

    def _pullFunctions(self, stringList):
        for index, item in enumerate(stringList):
            if(re.match("^function .*\{", item)):
                self.functions.append(self._getFunction(stringList, index))
        

class Parse:
    def __init__(self, file):
        """
        Read the input file and put it in the data field
        """
        with open(file[0], 'r') as config:
            self.data = config.readlines()
            for index, item in enumerate(self.data):
                self.data[index] = item.replace("\n", "")

    def log(self):
        """
        Print the config file out
        """
        for item in self.data:
            print(item)


if __name__ == '__main__':
    args = parser.parse_args()
    options = Options(args.input, args.bash, args.zsh)
    parser = Parse(options.file)
    config = Config()
    config.populate(parser.data)
    for func in config.functions:
        print(func)

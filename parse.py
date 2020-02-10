import argparse
import re

parser = argparse.ArgumentParser(description='Generate Bash and zsh completion scripts')
parser.add_argument('input', help='The file to generate bash and zsh scripts from', nargs=1)
parser.add_argument('--bash', "-b" , help='Generate bash only', action='store_true')
parser.add_argument('--zsh', '-z', help='Generate zsh only', action='store_true')

def function_match(functions, elements, prefix="", delimiter="-"): 
    """
    Check if an element if found in a function.
    Returns the function list if found otherwise None
    """
    if (len(functions) == 0 or len(elements) == 0):
        return None
    matches = []
    for function in functions:
        name = function[0]
        # check if name is equal to an element with prefix
        # This check must run first because the naming is more specific thus more important
        for element in elements:
            element = prefix + delimiter + element
            bare_element = prefix + element
            if element == name or bare_element == name:
                matches.append((function, element))
        if name in elements:
            matches.append((function, name))
                # look at the match that is the most verbose
    func, Name = None, ""
    for function,name in matches:
        if len(name) > len(Name):
            Name = name
            func = function
    if not func == None:
        return func

    return None

def subcommand_match(sections, section):
    """
    Check if a section required by another section.
    Returns the section list if found otherwise None
    """
    # it performs the same as a function match
    return function_match(sections, section)

def getCommands(string):
    return string.split(",")

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
    
    def clean(self, list):
        """
        Remove all empty lines and comments
        """
        out = []
        for item in list:
            if(not item.strip() == "" and not item.strip()[0] == "#"):
                out.append(re.sub(r'#.*$', '', item))
        return out


    def populate(self, stringList):
        self._pullName(stringList)
        stringList = self.clean(stringList)
        self._pullRoot(stringList)
        self._pullSections(stringList)
        self._pullFunctions(stringList)

    def _pullName(self, stringList):
        string = stringList[0]
        if(string[0] != "#"):
            raise Exception("Could not determin the program name. Make sure the first line followes this format # <name>")
        self.name = string[1:].strip()

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
            if(re.match("^[a-zA-Z\-]*=\(", item) and not re.match("^root=\(", item)):
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

class zshGen:
    """
    Generate the zsh completion script
    """
    def __init__(self, config):
        self.config  = config

    def _generateConfigLine(self, line):
        line = line.split(":")
        # list of possible comments
        commands = line[0]
        # generate string that holds the comment of a command
        line = "".join(line[1:])
        commands = getCommands(commands)
        commands = [x.strip() for x in commands]
        if len(commands) > 1:
            commands = ",".join(commands)
            return '{}{}{}":{}"'.format("{",commands,"}",line)
        commands = "".join(commands)
        return '"{}:{}"'.format(commands, line)

    def _generateSubCommand(self, section):
        name = "_{}_{}_subcommands".format(self.config.name, section[0].replace("-","").strip())
        section = section[1:]
        payload = "\tlocal commands; commands=(\n"
        for item in section:
            payload += "\t\t" + self._generateConfigLine(item) + "\n"
        payload += "\t)\n"
        payload += "\t_describe -t commands 'subcommands' commands \"$@\""
        return "{}(){}\n".format(name, "{") + payload + "\n}\n"

    def _generateFunctionSubCommand(self, section):
        name = "_{}_{}".format(self.config.name, section[0].replace("-","").strip())
        short_name = section[0].replace("-","").strip()
        section = section[1:]
        payload = "\tlocal context curcontext=\"$curcontext\" state line\n"
        payload += "\ttypeset -A opt_args\n"
        payload += "\tlocal ret=1\n"
        payload += "\t_arguments -C '1: :{}_subcommands' '*::arg:->args'\n".format(name)
        case = ""
        # functions used by this subcommand
        functions = []
        for item in section:
            commands = item.split(":")[0]
            items = getCommands(commands)
            commands = []
            for command in items:
                commands.append('"{}"'.format(command.strip()))
            # check if we need to include functions into our subcommand
            if(function_match(self.config.functions, items, short_name)):
                case += "\t\t" + "|".join(commands) + ")\n"
                # generate function for current case
                function_name = "{}_{}".format(name, max(items, key=len).replace("-","").strip())
                function = function_match(self.config.functions, items, short_name)
                if not function:
                    raise Exception("No function signature found for {}".format(items))
                else:
                    functions.append(self._generateFunction(function, function_name))
                case += "\t\t\t{}\n".format(function_name)
                case += "\t\t;;\n"
            if(subcommand_match(self.config.sections, items)):
                case += "\t\t" + "|".join(commands) + ")\n"
                command_name = "_{}_{}".format(self.config.name, max(items, key=len).replace("-","").strip())
                case += "\t\t\t{}\n".format(command_name)
                case += "\t\t;;\n"
        if not case == "":
            payload += "\tcase $line[1] in\n"
            payload += case
            payload += "\tesac\n"
        stringifiedFunctions = ""
        for function in functions:
            stringifiedFunctions += function + "\n"
        return "function {} {}\n".format(name, "{") + payload + "\n}\n" + stringifiedFunctions
    
    def _generateFunction(self, function, name):
        payload = ""
        for line in function[1:]:
            payload += "\t" + line.strip() + "\n"
        payload += "\t_arguments -C \"1: :($list)\""
        return "function {} {}\n".format(name, "{") + payload + "\n}\n"

    def _AppendFunctions(self, functions):
        out = []
        for function in functions:
            if function[0][0] == "_":
                out.append(self._generateFunction(function, function[0]))
        return out


    def generate(self):
        name = self.config.name
        root = "_{}_{}".format(name.replace(".",""), self.config.root[0].replace("-","").strip())
        content = "#compdef {} {}\n\n".format(root, name)
        # make sure no functions are generated with invalid syntax
        self.config.name = self.config.name.replace(".", "")
        content += self._generateSubCommand(self.config.root)
        content += self._generateFunctionSubCommand(self.config.root)
        for section in self.config.sections:
            content += self._generateSubCommand(section)
            content += self._generateFunctionSubCommand(section)
        for func in self._AppendFunctions(self.config.functions):
            content += func
        return content

if __name__ == '__main__':
    args = parser.parse_args()
    options = Options(args.input, args.bash, args.zsh)
    parser = Parse(options.file)
    config = Config()
    config.populate(parser.data)
    zsh = zshGen(config)
    print(zsh.generate())

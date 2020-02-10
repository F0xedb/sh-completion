# name.sh
# the first line must be a comment containing the name of program for which this completion function exists)

# root is the start of your completion function.
# It are all possible completions of your root command
root=(
    "-h, --help: Show the help menu"
    "-s, --show: Show some arguments"
    "-v, --verbose: Be more verbose"
    "ps: Show all processes"
)

# override the ps subcommand with even more options
ps=(
  "-h, --help: Show the process help menu"
  "-a, --all: Show all processes"
  "-k, --kill: Kill a process"
  "name: Kill a process by its name"
)

name=(
    "-f,--full: kill a process by its full name"
)

# you can even have subcommands for "dashed" options
-v=(
  "-vv: Be even more verbose"
  "-vvv: Be super verbose"
)

# when calling a function by the name of your option you declare a completion list
# use the longest name that is present in the list
function -k {
    # list must be present in each function call it contains the list of possible completion functions
    list="$(pgrep bash)"
}

# reference by name and option combined
# the name here is name and the option is -f or --full
function name-f {
    list="$(ps -ax | awk '{print $5}')"
}

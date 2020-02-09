# tos
# the line above is the name of program for which to generate the completion script


root=(
    "-iso:Install TOS onto your system"
    "-S:Install a package"
    "-R:Remove a package"
    "-Q:Query package database"
    "-h,--help:Show help imformation"
    "-u,--update:Update the system to the latest version"
    "-c,--crypto:Add a ssh key, when a user@ip is specified add current key to that host"
    "-rs,--repair-system:Perform a system repair (this will take a long time)" 
    "gpg,g: Show pgp (Gnu pg) related commands"
    "network,n: Show network related commands"
    "theme,t: Show theme related commands"
    "bluetooth,b: Show bluetooth related commands"
    "volume,v: Show volume related commands"
    "screen,s: Show screen related commands"
)

gpg=(
    "info,in: Get general information"
    "key,k: List all keys"
    "export,e: Export a key to a file"
    "import,i: Import a key from a file"
    "upload,u: Upload a key to a keyserver"
    "generate,ge: Generate a gpg key"
    "git,gi: Add a gpg key to your git config"
)

network=(
    "metric,m: Show the metric of an interface"
    "device,d: Show the network devices"
    "restart,r: Restart the network stack"
    "connect,c: Connect to a wireless network"
    "list,l: List the network interfaces"
)

theme=(
    "set,s: Set the theme"
    "add,a: Add a theme to the database"
    "delete,d: Delete a theme"
    "random,r: enable or disable a theme"
    "list,l: List database"
    "time,t: Set the time"
)

bluetooth=(
    "set,s: Enable or disable bluetooth"
    "list,l: List all bluetooth devices (add scan option to enable scanning)"
    "connect,c: Connect to a bluetooth device"
    "disconnect,d: Disconnect from a bluetooth device"
    "pair,p: Pair with a device"
    "full,f: Go into full interactive mode"
)

volume=(
    "get,g: Get the current audio config"
    "c,change: Change the volume in percentage"
    "set,s: Set the current volume in percentage"
    "toggle,t: toggle the volume"
)

screen=(
    "get,g: Get information about current screen config"
    "add,a: Add a new resolution config to the screen modes"
    "duplicate,d: Duplicate your screen"
    "toggle,t: Turn screen on or off"
    "reset,r: Reset screen to original version"
    "res,resolution: Change resolution"
    "rate,refresh: Change refresh rate"
)

# reference to every subcommand that is called set
function set {
    list={1..50}
}

# specific set implementation 
function bluetooth-set {
    list={1..100}
}

function screen-toggle {
    list=$(xrandr | awk '$1 !~ /Screen|[0-9]*x[0-9]*/ {print $1}')
}

function screen-refresh {
    list=$(xrandr | awk '$1 !~ /Screen|[0-9]*x[0-9]*/ {print $1}')
}

function screen-res {
    list=$(xrandr | awk '$1 !~ /Screen|[0-9]*x[0-9]*/ {print $1}')
}

function screen-add {
    list=$(xrandr | awk '$1 !~ /Screen|[0-9]*x[0-9]*/ {print $1}')
}

function screen-duplicate {
    list=$(xrandr | awk '$1 !~ /Screen|[0-9]*x[0-9]*/ {print $1}')
}

function bluetooth-connect {
    _blue_list_available
}

function bluetooth-pair {
    _blue_list_available
}

# functions prefixed with a _ automatically get injected in the end code (usefull for references to other functions)
function _blue_list_available {
    list=$(bluetoothctl devices | awk '{print "\""$0"\"" }' |  sed -E 's/Device ([0-9ABCDEF]{2}:)*[0-9ABCDEF]{2} //g')
}
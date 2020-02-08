#compdef _namesh name.sh


function _namesh_subcommands {
	local commands; commands=(
    "ps: Show all processes"
	{-h,--help}": Show the help menu" \
	{-s,--show}": Show some arguments" \
	{-v,--verbose}": Be more verbose"
	)
	_describe -t commands 'subcommands' commands "$@"
}

function _namesh {
	local context curcontext="$curcontext" state line
    typeset -A opt_args

    local ret=1
    
    _arguments -C \
        '1: :_namesh_subcommands' \
        '*::arg:->args'
	case $line[1] in
		"ps")
			_namesh_ps
		;;
	esac
}

_namesh_ps_subcommands(){
	local commands; commands=(
		{-h,--help}": Show the process help menu"
		{-a,--all}": Show all processes"
		{-k,--kill}": Kill a process"
	)
	_describe -t commands 'subcommands' commands "$@"
}
function _namesh_ps {
	local context curcontext="$curcontext" state line
	typeset -A opt_args
	local ret=1
	_arguments -C '1: :_namesh_ps_subcommands' '*::arg:->args'
	case $line[1] in
		"-k"|"--kill")
			_namesh_ps_kill
		;;
	esac

}
function _namesh_ps_kill {
	list="$(pgrep bash)"
	_arguments -C "1: :($list)"
}

_namesh_v_subcommands(){
	local commands; commands=(
		-vv: Be even more verbose
		-vvv: Be super verbose
	)
	_describe -t commands 'subcommands' commands "$@"
}
function _namesh_v {
	local context curcontext="$curcontext" state line
	typeset -A opt_args
	local ret=1
	_arguments -C '1: :_namesh_v_subcommands' '*::arg:->args'

}


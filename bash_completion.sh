# this snippet enables flow-parameter completion via the tabulator key
# for bash. it can be used by adding the following
#
#   source /usr/share/bash-completion/bash_completion
#   export DEFAULT_COMPLETION_LOADER="_completion_loader"
#   source $PATH_TO_OPM_UTILITIES/bash_completion.sh
#
# to the ~/.bashrc file. (Actually this works for any eWoms based
# simulator, not just for flow!) Note that, depending on how your
# operating system implements bash parameter completion, the first and
# the second lines of the snippet above might need to be changed. The
# above has been verfied to work with Debian based linux distributions
# (i.e., Ubuntu >= 16.04) and openSUSE.
#
_ewomsParameterCompletions() 
{
    if test "$COMP_WORDS" == ""; then 
        return 0
    fi

    local cmd cur ALL_OPTS
    COMPREPLY=()
    cmd="${COMP_WORDS[0]}"
    cur="${COMP_WORDS[COMP_CWORD]}"

    fullcmd="$(which "$cmd")"
    if test -z "$fullcmd" || \
       ! test -x "$fullcmd" || \
       (! test -f "$fullcmd" && ! test -h "$fullcmd" ) || \
       ! test -r "$fullcmd" || \
       ! grep -q "Ewoms[a-zA-Z0-9]*Simulator[a-zA-Z0-0]" "$fullcmd"
    then
        "$DEFAULT_COMPLETION_LOADER" $@
        return $?
    fi

    ALL_OPTS=$("$fullcmd" --help 2> /dev/null | grep '^ *--' | sed 's/ *\(--[a-zA-Z0-9\-]*\)=.*/\1=/')
    ALL_OPTS=$(echo "$ALL_OPTS" | sed 's/^ *--help.*/--help/')
    COMPREPLY=( $(compgen -A file -W "$ALL_OPTS" -- "${cur}") )
    
    return 0
}

complete -D -o nospace -F _ewomsParameterCompletions

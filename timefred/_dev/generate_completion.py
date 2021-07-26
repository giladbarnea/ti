from timefred.store import store


def generate_completion():
    data = store.load()
    work = data['work']
    tags = set([x.get('tags')[0] for x in work if x.get('tags')])
    print(f"""function completion.tf(){{
    current=${{COMP_WORDS[COMP_CWORD]}}
    prev=${{COMP_WORDS[$COMP_CWORD - 1]}}
    possible_completions=''
    case "$prev" in
        tf)
            possible_completions='l h e on f'
            ;;
    esac
    if [[ "$prev" == -t ]]; then
        possible_completions="{" ".join(tags)}"
    fi
    COMPREPLY=($(compgen -W "$possible_completions" -- "${{current}}"))
}}
complete -o default -F completion.tf tf
    """)


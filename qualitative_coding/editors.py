editors = {
    "code": {
        "name": "Visual Studio Code",
        "command": 'code "{corpus_file_path}" "{codes_file_path}"'
    },
    "vim": {
        "name": "Vim",
        "command": 'vim "{codes_file_path}" -c :set scrollbind -c :83vsplit|view {corpus_file_path}|set scrollbind'
    },
    "nvim": {
        "name": "Neovim",
        "command": 'nvim "{codes_file_path}" -c :set scrollbind -c :83vsplit|view {corpus_file_path}|set scrollbind'
    },
    "emacs": {
        "name": "Emacs",
        "command": "emacs -Q --eval (progn (find-file \"{corpus_file_path}\") (split-window-right) (other-window 1) (find-file \"{codes_file_path}\") (scroll-all-mode))"
    },
}

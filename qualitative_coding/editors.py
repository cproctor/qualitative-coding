editors = {
    "code": {
        "name": "Visual Studio Code",
        "code_command": 'code "{corpus_file_path}" "{codes_file_path}" --wait',
        "memo_command": 'code "{memo_file_path}"',
    },
    "vim": {
        "name": "Vim",
        "code_command": 'vim -O "{corpus_file_path}" "{codes_file_path}" -c \'windo set scb!\'',
        "memo_command": 'vim "{memo_file_path}"',
    },
    "nvim": {
        "name": "Neovim",
        "code_command": 'nvim -O "{corpus_file_path}" "{codes_file_path}" -c \'windo set scb!\'',
        "memo_command": 'nvim "{memo_file_path}"',
    },
    "emacs": {
        "name": "Emacs",
        "code_command": "emacs -Q --eval (progn (find-file \"{corpus_file_path}\") (split-window-right) (other-window 1) (find-file \"{codes_file_path}\") (scroll-all-mode))",
        "memo_command": 'emacs "{memo_file_path}"',
    },
}

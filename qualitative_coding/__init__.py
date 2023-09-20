from pathlib import Path
from qualitative_coding.corpus import QCCorpus
from qualitative_coding.viewer import QCCorpusViewer
from qualitative_coding.cli import (
    build_arg_parser,
    check_incompatible,
    Truthy, 
    Falsy, 
)

def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    check_incompatible(args, invert=True, pattern=None)
    if args.command == "init":
        if not Path(args.settings).exists():
            QCCorpus.initialize(args.settings)
            return 
        else:
            QCCorpus.initialize(args.settings)
    corpus = QCCorpus(args.settings)
    viewer = QCCorpusViewer(corpus)
    if hasattr(args, 'filenames') and args.filenames:
        file_list = Path(args.filenames).read_text().split("\n")
    else:
        file_list = None
    if args.command == "check":
        corpus.validate()
    if args.command == "code":
        check_incompatible(args, first=True, random=True)
        if args.first:
            choice = "first"
        elif args.random:
            choice = "random"
        else:
            choice = None
        viewer.open_for_coding(
            pattern=args.pattern, 
            file_list=file_list,
            invert=args.invert,
            coder=args.coder, 
            choice=choice
        )
    if args.command == "init":
        check_incompatible(args, prepare_corpus=False, preformatted=True)
        check_incompatible(args, prepare_codes=True, coder=None)
        check_incompatible(args, prepare_codes=False, coder=True)
        if args.prepare_corpus:
            corpus.prepare_corpus(
                pattern=args.pattern, 
                file_list=file_list,
                invert=args.invert,
                preformatted=args.preformatted)
        if args.prepare_codes:
            corpus.prepare_code_files(args.coder, pattern=args.pattern)
    if args.command in ["codebook", "cb"]:
        corpus.update_codebook()
    if args.command in ["list", "ls"]:
        viewer.list_codes(args.expanded, depth=args.depth)
    if args.command in ["rename", "rn"]:
        corpus.rename_codes(
            old_codes=args.old_codes, 
            new_code=args.new_code, 
            pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            coder=args.coder,
            update_codebook=args.update_codebook,
        )
    if args.command == "find":
        viewer.show_coded_text(
            args.code, 
            before=args.before, 
            after=args.after, 
            recursive_codes=args.recursive_codes,
            depth=args.depth,
            unit=args.unit,
            pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            coder=args.coder,
            show_codes=not args.no_codes,
        )
    if args.command == "stats":
        check_incompatible(args, recursive=False, depth=Truthy())
        check_incompatible(args, recursive_counts=False, total_only=True)
        viewer.show_stats(
            args.code, 
            max_count=args.max, 
            min_count=args.min, 
            depth=args.depth, 
            recursive_codes=args.recursive_codes,
            recursive_counts=args.recursive_counts,
            expanded=args.expanded, 
            format=args.format, 
            pattern=args.pattern,
            file_list=file_list,
            invert=args.invert,
            coder=args.coder,
            unit=args.unit,
            outfile=args.outfile,
            total_only=args.total_only,
        )
    if args.command in ["crosstab", "ct"]:
        check_incompatible(args, code=Truthy(), depth=Truthy(), recursive_codes=False)
        check_incompatible(args, tidy=True, compact=True)
        check_incompatible(args, tidy=True, probs=True)
        check_incompatible(args, tidy=False, min=Truthy())
        check_incompatible(args, tidy=False, max=Truthy())
        if args.tidy:
            viewer.tidy_codes(
                args.code, 
                depth=args.depth, 
                recursive_codes=args.recursive_codes,
                recursive_counts=args.recursive_counts,
                expanded=args.expanded, 
                format=args.format, 
                pattern=args.pattern,
                file_list=file_list,
                invert=args.invert,
                coder=args.coder,
                unit=args.unit,
                outfile=args.outfile,
                minimum=args.min,
                maximum=args.max,
            )
        else:
            viewer.crosstab(
                args.code, 
                depth=args.depth, 
                recursive_codes=args.recursive_codes,
                recursive_counts=args.recursive_counts,
                expanded=args.expanded, 
                format=args.format, 
                pattern=args.pattern,
                file_list=file_list,
                invert=args.invert,
                coder=args.coder,
                unit=args.unit,
                outfile=args.outfile,
                probs=args.probs,
                compact=args.compact,
            )
    if args.command == "memo":
        if args.list_memos:
            print(viewer.list_memos())
        else:
            viewer.memo(args.coder, args.message)


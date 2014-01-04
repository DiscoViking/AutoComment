if !has('python')
    finish
endif

function! DoAutoComment()
    pyfile autocomment.py
endfunc

function! FormatComment()
    pyfile formatcomment.py
endfunc

command! AutoComment call DoAutoComment()

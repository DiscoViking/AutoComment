if !has('python')
    finish
endif

python import sys; sys.path.append('/home/ryan/.vim/plugin/AutoComment')

function! DoAutoComment()

python << EOF
import vim
from autocomment import *
b = getCommentBlock()
if b != None:
    formatCommentBlock(b)
else:
    createCommentBlock()
EOF

endfunc

function! DoFormatComment()

python << EOF
import vim
from autocomment import *
b = getCommentBlock()
if b != None:
    formatCommentBlock(b)
EOF

endfunc

command! AutoComment call DoAutoComment()
command! FormatComment call DoFormatComment()
inoremap <silent> <Space> <Space><C-\><C-o>:FormatComment<CR>

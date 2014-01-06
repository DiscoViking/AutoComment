if !has('python')
    finish
endif

let s:plugin_path = escape(expand('<sfile>:p:h'), '\')

exe 'python import sys; sys.path.append("' . s:plugin_path . '")'

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
    formatBlockFromCurrentLine(b)
EOF

endfunc

command! AutoComment call DoAutoComment()
command! FormatComment call DoFormatComment()
"inoremap <silent> <Space> <Space><C-\><C-o>:FormatComment<CR>

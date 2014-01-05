import vim

LINE_WIDTH = 80
COMMENT_STYLES = {
        'python':('#','#','#'),
        'c':('/*','*','*/'),
        'scheme':(';;','-',';;')
        }

################################################################################
# Find the correct comment style for the file we are in. If we don't           #
# recognise the filetype, default to python-style comments.                    #
################################################################################
filetype = vim.eval('&filetype')
if filetype not in COMMENT_STYLES:
    filetype = 'python'

(COMMENT_START, COMMENT_LINE, COMMENT_END) = COMMENT_STYLES[filetype]

def isCommentLine(line):
    if len(line) > 0 and line[:len(COMMENT_START)] == COMMENT_START:
        return True
    return False

def getCommentBlock():
    w = vim.current.window
    b = vim.current.buffer
    (y, x) = w.cursor
    y -= 1
    currentLine = b[y].strip()
    if not isCommentLine(currentLine):
        return None

    start = end = y
    
    line = b[start-1].strip()
    while isCommentLine(line):
        start -= 1
        line = b[start-1].strip()

    line = b[end+1].strip()
    while isCommentLine(line):
        end += 1
        line = b[end+1].strip()

    return b.range(start+1,end+1)

def createCommentBlock(text=None):
    w = vim.current.window
    b = vim.current.buffer
    (y, x) = w.cursor
    r = b.range(y,y)
    
    blockWidth = LINE_WIDTH - x
    innerWidth = blockWidth - len(COMMENT_START) - len(COMMENT_END)
     
    r[0] = ' ' * x + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END
    r.append(' ' * x + COMMENT_START + innerWidth * ' ' + COMMENT_END)
    r.append(' ' * x + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END)

    w.cursor = (y+1, x+2)
    vim.command('startinsert')

def formatCommentBlock(block):
    lines = [line.replace(COMMENT_START, '').replace(COMMENT_END, '').replace(COMMENT_LINE,'').strip().split() for line in block][1:-1]
    indent = len(block[0].split(COMMENT_START)[0])
    blockWidth = LINE_WIDTH - indent
    innerWidth = blockWidth - len(COMMENT_START) - len(COMMENT_END)

    del block[:]

    block.append(' ' * indent + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END)

    while len(lines) > 0:
        line = ' '
        words = lines.pop(0)

        ########################################################################
        # Add words onto the current line until it no longer fits inside the   #
        # comment block. We add the first word on automatically to prevent a   #
        # crash when there is only one super long word in the line.            #
        ########################################################################
        if len(words) > 0:
            line += words.pop(0) + ' '
        while (len(words) > 0) and (len(line + words[0]) < innerWidth):
            line += words.pop(0) + ' '

        block.append(' ' * indent + COMMENT_START + line.ljust(innerWidth) + COMMENT_END)

        ########################################################################
        # Add any left over words to the next line, unless it's a blank line,  #
        # in which case create a new line for them. We want to preserve        #
        # paragraphs.                                                          #
        ########################################################################
        if len(words) > 0:
            if len(lines) > 0 and len(lines[0]) == 0:
                lines.insert(0, words)
            elif len(lines) > 0:
                lines[0] = words + lines[0]
            else:
                lines.append(words)

    block.append(' ' * indent + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END)

    vim.current.window.cursor = (block.start + len(block) - 1, indent + len(COMMENT_START) + len(line))

def formatBlockFromCurrentLine(block):
    lines = [line.replace(COMMENT_START, '').replace(COMMENT_END, '').replace(COMMENT_LINE,'').strip().split() for line in block][1:-1]
    indent = len(block[0].split(COMMENT_START)[0])
    blockWidth = LINE_WIDTH - indent
    innerWidth = blockWidth - len(COMMENT_START) - len(COMMENT_END)

    (currentLine, x) = vim.current.window.cursor
    blockLine = currentLine - block.start - 1

    lines = lines[blockLine-1:]
    del block[blockLine:-1]
    
    firstLine = True
    while len(lines) > 0:
        line = ' '
        words = lines.pop(0)

        ########################################################################
        # Add words onto the current line until it no longer fits inside the   #
        # comment block. We add the first word on automatically to prevent a   #
        # crash when there is only one super long word in the line.            #
        ########################################################################
        if len(words) > 0:
            line += words.pop(0) + ' '
        while (len(words) > 0) and (len(line + words[0]) < innerWidth):
            line += words.pop(0) + ' '

        block.append(' ' * indent + COMMENT_START + line.ljust(innerWidth) + COMMENT_END, (block.end-block.start))

        ########################################################################
        # Add any left over words to the next line, unless it's a blank line,  #
        # in which case create a new line for them. We want to preserve        #
        # paragraphs.                                                          #
        ########################################################################
        if len(words) > 0:
            if len(lines) > 0 and len(lines[0]) == 0:
                lines.insert(0, words)
            elif len(lines) > 0:
                lines[0] = words + lines[0]
            else:
                lines.append(words)
        ########################################################################
        # If the line we were on wrapped, move the cursor to the next line, in #
        # front of the word that wrapped.                                      #
        ########################################################################
        if firstLine:
            firstLine = False
            if len(words) > 0 and x >= LINE_WIDTH - len(COMMENT_END):
                vim.current.window.cursor = (currentLine + 1, indent + len(COMMENT_START) + len(' '.join(words)) + 2)


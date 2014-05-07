import vim

LINE_WIDTH = 79
COMMENT_STYLES = {
        'python':('#','-',''),
        'sh':('#','#',''),
        'c':('/*','*','*/'),
        'cpp':('/*','*','*/'),
        'scheme':(';;','-',';;')
        }
IGNORE_HEADERS = ["PROC", "STRUCT"]

def loadCommentStyle():
    global COMMENT_START, COMMENT_LINE, COMMENT_END
    filetype = vim.eval('&filetype')
    if filetype not in COMMENT_STYLES:
        return False

    (COMMENT_START, COMMENT_LINE, COMMENT_END) = COMMENT_STYLES[filetype]
    return True

loadCommentStyle()

def isCommentLine(line):
    if len(line) > 0 and line[:len(COMMENT_START)] == COMMENT_START:
        return True
    return False

def getText(line):
    return line.replace(COMMENT_START,'').replace(COMMENT_END,'').replace(COMMENT_LINE,'').strip()

def buildLine(text, indent):
    innerWidth = LINE_WIDTH - indent - len(COMMENT_START) - len(COMMENT_END) - 2
    innards =  text.ljust(innerWidth) if COMMENT_END != '' else text
    return ' '*indent + COMMENT_START + ' ' + innards + ' ' + COMMENT_END

def blockStart(indent):
    innerWidth = LINE_WIDTH - indent - len(COMMENT_START) - len(COMMENT_END)
    return ' '*indent + COMMENT_START + COMMENT_LINE*innerWidth + COMMENT_END

def blockEnd(indent):
    innerWidth = LINE_WIDTH - indent - len(COMMENT_START) - len(COMMENT_END)
    return ' '*indent + COMMENT_START + COMMENT_LINE*innerWidth + COMMENT_END

def getCommentBlockAt(row):
    if not loadCommentStyle():
        return

    b = vim.current.buffer

    line = b[row-1].strip()
    if not isCommentLine(line):
        return None

    start = end = row-1

    line = b[start-1].strip()
    while isCommentLine(line):
        start -= 1
        line = b[start-1].strip()

    #--------------------------------------------------------------------------
    # If the top line of the block contains one of the specified headers, do
    # not return the block.
    # This is a hack to make sure we don't mess up function headers etc,
    # since AutoComment does not currently handle their more advanced
    # formatting.
    #--------------------------------------------------------------------------
    firstLine = getText(b[start])
    if reduce(lambda b, s: True if b else firstLine.startswith(s),
              IGNORE_HEADERS, False):
        return None

    line = b[end+1].strip()
    while isCommentLine(line):
        end += 1
        line = b[end+1].strip()

    return b.range(start+1, end+1)

def createCommentBlock(text=None):
    if not loadCommentStyle():
        return

    w = vim.current.window
    b = vim.current.buffer
    (y, x) = w.cursor
    r = b.range(y, y)

    blockWidth = LINE_WIDTH - x
    innerWidth = blockWidth - len(COMMENT_START) - len(COMMENT_END)

    r[0] = ' ' * x + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END

    innards = innerWidth * ' ' if COMMENT_END != '' else '  '
    r.append(' ' * x + COMMENT_START + innards + COMMENT_END)

    r.append(' ' * x + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END)

    w.cursor = (y+1, x+2)
    vim.command('startinsert')

def formatBlockFrom(block, row):
    if not loadCommentStyle():
        return

    b = vim.current.buffer
    indent = len(block[0].split(COMMENT_START)[0])
    innerWidth = LINE_WIDTH - indent - len(COMMENT_START) - len(COMMENT_END) - 2

    #--------------------------------------------------------------------------
    # Only format until we get to a blank row. This formats one paragraph.
    #--------------------------------------------------------------------------
    end = row
    while (end <= block.end - block.start):# and len(getText(block[end])) > 0:
        end += 1

    p = b.range(row + block.start, end + block.start)

    startOfBlock = (p.start == block.start)
    endOfBlock = (p.end == block.end)

    lines = [getText(line).split() for line in p]
    if startOfBlock:
        lines = lines[1:]
    if endOfBlock:
        lines = lines[:-1]

    (y,x) = vim.current.window.cursor

    del p[:]
    firstLine = True
    carriedChars = 0
    while len(lines) > 0:
        words = lines.pop(0)
        line = ''
        while len(words) > 0 and (len(line + words[0]) < innerWidth or len(line) == 0):
            line += words.pop(0) + ' '

        p.append(buildLine(line, indent))

        if len(lines) > 0:
            lines[0] = words + lines[0]
        elif len(words) > 0:
            lines.append(words)
        if len(words) > 0 and firstLine:
            carriedChars = indent + len(COMMENT_START) + 1 + len(words[0])

    if startOfBlock:
        p.append(blockStart(indent), 0)
        if row == end:
            p.append(buildLine("", indent))
            y += 1
    if endOfBlock:
        p.append(blockEnd(indent))

    if carriedChars == 0 or x < LINE_WIDTH - len(COMMENT_END) - 1:
        vim.current.window.cursor = (y, min(x, len(p[0])))
    else:
        vim.current.window.cursor = (y+1, carriedChars + 1)

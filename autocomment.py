import vim

LINE_WIDTH = 80
COMMENT_START = '/*'
COMMENT_END = '*/'
COMMENT_LINE = '*'
  
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
    text = ' '.join([line.replace(COMMENT_START, '').replace(COMMENT_END, '').replace(COMMENT_LINE,'').strip() for line in block])
    indent = len(block[0].split(COMMENT_START)[0])
    blockWidth = LINE_WIDTH - indent
    innerWidth = blockWidth - len(COMMENT_START) - len(COMMENT_END)

    del block[:]

    block.append(' ' * indent + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END)

    words = [w.strip() for w in text.split()]
    line = (' ' * indent) + COMMENT_START + ' '
    while len(words) > 0:
        if len(line + words[0] + ' ') < LINE_WIDTH - len(COMMENT_END):
            line += words[0] + ' '
            words = words[1:]
        else:
            block.append(line.ljust(LINE_WIDTH - len(COMMENT_END)) + COMMENT_END)
            line = (' ' * indent) + COMMENT_START + ' '

    block.append(line.ljust(LINE_WIDTH - len(COMMENT_END)) + COMMENT_END)
    block.append(' ' * indent + COMMENT_START + innerWidth * COMMENT_LINE + COMMENT_END)

    vim.current.window.cursor = (block.start + len(block) - 1, len(line))

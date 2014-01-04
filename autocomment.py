import vim

LINE_WIDTH = 80
COMMENT_CHAR = '#'

def getCommentBlock():
    w = vim.current.window
    b = vim.current.buffer
    (y, x) = w.cursor
    y -= 1
    currentLine = b[y].strip()
    if len(currentLine) == 0 or currentLine[0] != COMMENT_CHAR:
        return None

    start = end = y
    
    line = b[start-1].strip()
    while len(line) > 0 and line[0] == COMMENT_CHAR:
        start -= 1
        line = b[start-1].strip()

    line = b[end+1].strip()
    while len(line) > 0 and line[0] == COMMENT_CHAR:
        end += 1
        line = b[end+1].strip()

    return b.range(start+1,end+1)

def create_block(text=None):
    w = vim.current.window
    b = vim.current.buffer
    (y, x) = w.cursor
    r = b.range(y,y)
    
    blockWidth = LINE_WIDTH - x

    r[0] = ' ' * x + blockWidth * COMMENT_CHAR
    r.append(' ' * x + COMMENT_CHAR + ' ' * 2)
    r.append(' ' * x + blockWidth * COMMENT_CHAR)

    w.cursor = (y+1, x+2)
    vim.command('startinsert!')

def formatCommentBlock(block):
    text = ' '.join([line.replace(COMMENT_CHAR, '').strip() for line in block])
    indent = len(block[0].split(COMMENT_CHAR)[0])
    blockWidth = LINE_WIDTH - indent

    del block[:]

    block.append(' ' * indent + COMMENT_CHAR * blockWidth)

    words = [w.strip() for w in text.split()]
    line = (' ' * indent) + COMMENT_CHAR
    while len(words) > 0:
        if len(line + ' ' + words[0]) < LINE_WIDTH:
            line += ' ' + words[0]
            words = words[1:]
        else:
            block.append(line)
            line = (' ' * indent) + COMMENT_CHAR

    block.append(line)
    block.append(' ' * indent + COMMENT_CHAR * blockWidth)

b = getCommentBlock()
if b == None:
    create_block()
else:
    formatCommentBlock(b)

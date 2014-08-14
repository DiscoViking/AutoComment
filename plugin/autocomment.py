import vim
import re

LINE_WIDTH = 79
COMMENT_STYLES = {
        'python':('#','-',''),
        'sh':('#','#',''),
        'c':('/*','*','*/'),
        'cpp':('/*','*','*/'),
        'scheme':(';;','-',';;'),
        'vim':('"','-','')
        }
IGNORE_HEADERS = []
COMMENT_START, COMMENT_LINE, COMMENT_END = ("", "", "")

SENTENCE_ENDERS = ["?", ".", "!"]

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
    regex = "^\s*"+re.escape(COMMENT_START)+re.escape(COMMENT_LINE)+"*"
    if COMMENT_END != "":
        regex += "|"+re.escape(COMMENT_END)+"\s*$"
    r = re.compile(regex)
    text = r.sub("", line)
    if text.startswith(" "):
        text = text[1:]
    return text

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

    r = re.compile("\\S+|\\s+")
    lines = [r.findall(getText(line)) for line in p]

    #--------------------------------------------------------------------------
    # Work out if this is a 1 line block or not. If it isn't, then we will
    # have blank lines at the top and bottom from where the big lines are, so
    # remove them.
    #--------------------------------------------------------------------------
    newBlock = block.start == block.end
    if not newBlock:
        if startOfBlock:
            lines = lines[1:]
        if endOfBlock:
            lines = lines[:-1]

    (y,x) = vim.current.window.cursor

    #--------------------------------------------------------------------------
    # Delete everything, we will rebuild it from scratch.
    #--------------------------------------------------------------------------
    del p[:]
    firstLine = True
    carriedChars = 0
    while len(lines) > 0:
        words = lines.pop(0)
        line = ''

        leading_spaces = ""
        if len(words) > 0:
            if words[0].startswith(" "):
                leading_spaces = words[0]
            elif words[0].endswith(":"):
                if len(words) > 1:
                    leading_spaces = " " * (len(words[0]) + len(words[1]))
                else:
                    leading_spaces = " " * (len(words[0]) + 1)

        #----------------------------------------------------------------------
        # Add words to this line until it no longer fits in one LINE_WIDTH.
        #----------------------------------------------------------------------
        while len(words) > 0 and (words[0].startswith(" ") or
                                  len(line + words[0]) <= innerWidth or
                                  len(line) == 0):
            line += words.pop(0)

        #----------------------------------------------------------------------
        # Strip any trailing spaces unless they are before the cursor on the
        # first line.
        # (i.e. being typed right now).
        #----------------------------------------------------------------------
        if firstLine:
            relative_cursor = x - (indent + len(COMMENT_START) + 1)
            stripped_len = len(line.rstrip())
            if stripped_len < relative_cursor:
                line = line[:relative_cursor+1]
            else:
                line = line.rstrip()
        else:
            line = line.rstrip()

        p.append(buildLine(line, indent))

        #----------------------------------------------------------------------
        # Move any leftover words to the beginning of the next line.
        # If there is no next line, add one.
        # Never carry trailing spaces.
        #----------------------------------------------------------------------
        while len(words) > 0 and words[-1].startswith(" "):
            words = words[:-1]
        if len(words) > 0:
            words.append("  " if words[-1][-1] in SENTENCE_ENDERS else " ")
            if len(lines) > 0 and len(lines[0]) > 1:
                if lines[0][0].startswith(" "):
                    leading_spaces = lines[0].pop(0)
                lines[0] = [leading_spaces] + words + lines[0]
            else:
                if leading_spaces == "":
                    lines.insert(0, words)
                else:
                    lines.insert(0, [leading_spaces] + words)

        #----------------------------------------------------------------------
        # If we carried characters over on the first line, record how many.
        # This is used later to move the cursor to the correct place when
        # wrapping text.
        #----------------------------------------------------------------------
        if len(words) > 0 and firstLine:
            carriedChars = indent + len(COMMENT_START) + len(words[0]) + len(leading_spaces)
            if len(words) > 1:
                carriedChars += len(words[1])
        elif newBlock:
            #------------------------------------------------------------------
            # Move the cursor to the end of the line to force it to be placed
            # on the next line later.
            #------------------------------------------------------------------
            x = LINE_WIDTH
            carriedChars = indent + len(COMMENT_START) + len(line)

        firstLine = False

    #--------------------------------------------------------------------------
    # If we're formatting from the beginning, add in the top block line since
    # we will have erased it earlier.
    #--------------------------------------------------------------------------
    if startOfBlock:
        p.append(blockStart(indent), 0)

    #--------------------------------------------------------------------------
    # Similarly add in an end block line if necessary.
    #--------------------------------------------------------------------------
    if endOfBlock:
        p.append(blockEnd(indent))

    #--------------------------------------------------------------------------
    # Move the cursor to a sensible place.
    #--------------------------------------------------------------------------
    if carriedChars == 0 or x < LINE_WIDTH - len(COMMENT_END) - 1:
        y, x = (y, min(x, len(p[0])))
    else:
        y, x = (y+1, carriedChars + 1)

    vim.current.window.cursor = (y, x)

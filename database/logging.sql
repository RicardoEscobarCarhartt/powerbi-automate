CREATE TABLE IF NOT EXISTS log_record ( /*
The LogRecord has a number of attributes, most of which are derived from the parameters to the constructor. (Note that the names do not always correspond exactly between the LogRecord constructor parameters and the LogRecord attributes.) These attributes can be used to merge data from the record into the format string. The following table lists (in alphabetical order) the attribute names, their meanings and the corresponding placeholder in a %-style format string.

If you are using {}-formatting (str.format()), you can use {attrname} as the placeholder in the format string. If you are using $-formatting (string.Template), use the form ${attrname}. In both cases, of course, replace attrname with the actual attribute name you want to use.

In the case of {}-formatting, you can specify formatting flags by placing them after the attribute name, separated from it with a colon. For example: a placeholder of {msecs:03.0f} would format a millisecond value of 4 as 004. Refer to the str.format() documentation for full details on the options available to you.
*/
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    args            TEXT, -- The tuple of arguments merged into msg to produce message, or a dict whose values are used for the merge (when there is only one argument, and it is a dictionary).
    asctime         TEXT, -- Human-readable time when the LogRecord was created. By default this is of the form ‘2003-07-08 16:49:45,896’ (the numbers after the comma are millisecond portion of the time).
    created         REAL, -- Time when the LogRecord was created (as returned by time.time()).
    exc_info        TEXT, -- Exception tuple (à la sys.exc_info) or, if no exception has occurred, None.
    filename        TEXT, -- Filename portion of pathname.
    funcName        TEXT, -- Name of function containing the logging call.
    levelname       TEXT, -- Text logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
    lineno          INTEGER, -- Source line number where the logging call was issued (if available).
    message         TEXT, -- The logged message, computed as msg % args. This is set when Formatter.format() is invoked.
    module          TEXT, -- Module (name portion of filename).
    msecs           REAL, -- Millisecond portion of the time when the LogRecord was created.
    msg             TEXT, -- The format string passed in the original logging call. Merged with args to produce message, or an arbitrary object (see Using arbitrary objects as messages).
    name            TEXT, -- Name of the logger used to log the call.
    pathname        TEXT, -- Full pathname of the source file where the logging call was issued (if available).
    process         INTEGER, -- Process ID (if available).
    processName     TEXT, -- Process name (if available).
    relativeCreated REAL, -- Time in milliseconds when the LogRecord was created, relative to the time the logging module was loaded.
    stack_info      TEXT, -- Stack frame information (where available) from the bottom of the stack in the current thread, up to and including the stack frame of the logging call which resulted in the creation of this record.
    thread          INTEGER, -- Thread ID (if available).
    threadName      TEXT, -- Thread name (if available).
    taskName        TEXT -- asyncio.Task name (if available).
);
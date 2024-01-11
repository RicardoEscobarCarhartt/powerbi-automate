2024-01-11 16:14:42

# TASK 172717: Logging and Reporting

The system must log the results of each data check, recording both successful checks and instances where data accuracy issues are detected.

Generate detailed reports summarizing the results of scheduled data checks, including any identified discrepancies.

# Logging

I'll use the `logging` built-in Python module to create a new module to help me generate loggers easier.

These loggers will handle logging of every other module they are imported in.

The individual logger will handle saving the log messages into their respective log files, console and even a database using the SQL lite database engine.
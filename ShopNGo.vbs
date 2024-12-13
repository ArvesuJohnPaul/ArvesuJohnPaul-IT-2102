Set WShell = CreateObject("WScript.Shell")
strPath = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
WShell.CurrentDirectory = strPath

' Start MySQL using the XAMPP batch file
WShell.Run "C:\xampp\mysql_start.bat", 0, False

' Wait a moment to ensure MySQL has started
WScript.Sleep 2000

' Run the Python script
WShell.Run "pythonw main.py", 0, False
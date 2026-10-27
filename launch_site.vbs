Option Explicit
Dim sh, fso, dir, http, arg, i, opened
Set sh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
dir = fso.GetParentFolderName(WScript.ScriptFullName)
arg = ""
If WScript.Arguments.Count > 0 Then arg = LCase(WScript.Arguments(0))
opened = (arg = "browser")

Function ServerUp()
  On Error Resume Next
  Set http = CreateObject("MSXML2.ServerXMLHTTP")
  http.setTimeouts 700, 700, 700, 700
  http.Open "GET", "http://127.0.0.1:8765/demo.html", False
  http.Send
  ServerUp = (Err.Number = 0 And http.Status = 200)
  Err.Clear
End Function

If Not ServerUp() Then
  sh.CurrentDirectory = dir
  sh.Run "cmd /c python -m http.server 8765", 0, False
  For i = 1 To 25
    WScript.Sleep 200
    If ServerUp() Then Exit For
  Next
End If

If opened Then sh.Run "http://127.0.0.1:8765/demo.html", 1, False

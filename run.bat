:createVenv
@ IF EXIST .\env (
goto runMain
)

set /p pathToPython=Please Enter Python Install Path(folder):

%pathToPython%\python.exe -m venv env

:installLib
.\env\Scripts\pip.exe install numpy pandas opencv-python pydicom

:runMain
.\env\Scripts\python.exe -m main
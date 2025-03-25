@echo off
REM This script sets up the environment and runs the Inno Setup compiler

REM Get the root directory (parent of build_tools)
FOR %%G IN ("%~dp0..") DO SET "BuildRootDir=%%~fG"
echo Root directory: %BuildRootDir%

REM Create Output directory in the root directory
IF NOT EXIST "%BuildRootDir%\Output" mkdir "%BuildRootDir%\Output"

REM Find Inno Setup compiler
SET "InnoSetupPath="
IF EXIST "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    SET "InnoSetupPath=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) ELSE (
    IF EXIST "C:\Program Files\Inno Setup 6\ISCC.exe" (
        SET "InnoSetupPath=C:\Program Files\Inno Setup 6\ISCC.exe"
    )
)

IF "%InnoSetupPath%"=="" (
    echo Inno Setup not found! Please install Inno Setup 6.
    exit /b 1
)

echo Using Inno Setup at: %InnoSetupPath%

REM Set environment variable for the Inno Setup script
SET "BuildRootDir=%BuildRootDir%"

REM Run Inno Setup compiler
echo Running Inno Setup compiler...
"%InnoSetupPath%" /O"%BuildRootDir%\Output" "%~dp0installer_script.iss"

REM Inno Setup can return exit code 1 for warnings, but the installer still builds
IF %ERRORLEVEL% NEQ 0 (
    IF EXIST "%BuildRootDir%\Output\LocalAIChat_Setup.exe" (
        echo Warning: Inno Setup reported warnings but the installer was built successfully.
        exit /b 0
    ) ELSE (
        echo Installer build failed with error code %ERRORLEVEL%!
        exit /b %ERRORLEVEL%
    )
) ELSE (
    echo Installer built successfully!
)

exit /b 0 
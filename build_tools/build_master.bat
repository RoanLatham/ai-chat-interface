@echo off
REM Master build script for Local AI Chat
echo Starting Local AI Chat build process...

REM Get the root directory (parent of build_tools)
FOR %%G IN ("%~dp0..") DO SET "BuildRootDir=%%~fG"
echo Root directory: %BuildRootDir%

REM Change current directory to the root directory
cd /d "%BuildRootDir%"
echo Current directory set to: %CD%

REM Create Output directory in the root directory
IF NOT EXIST "%BuildRootDir%\Output" mkdir "%BuildRootDir%\Output"
echo Created output directory: %BuildRootDir%\Output

REM Process command line arguments
SET SKIP_APP_BUILD=0
SET SKIP_INSTALLER=0
SET BUILD_ARGS=

:parse_args
IF "%~1"=="" GOTO end_parse_args
IF /I "%~1"=="--no-app-build" (
    SET SKIP_APP_BUILD=1
) ELSE IF /I "%~1"=="--no-installer" (
    SET SKIP_INSTALLER=1
) ELSE (
    REM Collect all other arguments to pass to build.py
    SET BUILD_ARGS=%BUILD_ARGS% %1
)
SHIFT
GOTO parse_args
:end_parse_args

echo Build arguments: %BUILD_ARGS%

REM Build the application
IF %SKIP_APP_BUILD%==0 (
    echo Building Python application...
    REM Use absolute paths for the build script
    python "%BuildRootDir%\build_tools\build.py" --clean %BUILD_ARGS%
    IF %ERRORLEVEL% NEQ 0 (
        echo Application build failed with error code %ERRORLEVEL%!
        echo Check the error messages above for details.
        IF %SKIP_INSTALLER%==0 (
            echo Skipping installer build due to application build failure.
            exit /b %ERRORLEVEL%
        )
    ) ELSE (
        echo Application built successfully.
    )
) ELSE (
    echo Skipping application build...
)

REM Create the installer
IF %SKIP_INSTALLER%==0 (
    echo Building installer...
    
    REM Explicitly call the build_installer.bat in the build_tools directory with absolute path
    CALL "%BuildRootDir%\build_tools\build_installer.bat"
    
    IF %ERRORLEVEL% NEQ 0 (
        echo Installer build failed with error code %ERRORLEVEL%!
        echo Check the error messages above for details.
        exit /b %ERRORLEVEL%
    ) ELSE (
        echo Installer built successfully.
    )
) ELSE (
    echo Skipping installer build...
)

echo Build process completed successfully!
echo.
echo Output directories:
echo Application: %BuildRootDir%\dist\LocalAIChat
echo Installer: %BuildRootDir%\Output\LocalAIChat_Setup.exe
echo.

exit /b 0 
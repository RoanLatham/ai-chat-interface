#define MyAppName "Local AI Chat"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "RoanLatham"
#define MyAppURL "https://github.com/RoanLatham/ai-chat-interface"
#define MyAppExeName "LocalAIChat.exe"
#define RootDir GetEnv('BuildRootDir')

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
AppId={{F4A28639-55E4-4CB3-A519-7579E2B2B5D4}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir={#RootDir}\Output
OutputBaseFilename=LocalAIChat_Setup
Compression=lzma
SolidCompression=yes
DisableDirPage=no
DisableProgramGroupPage=no
; Set a custom icon for the installer if it exists
SetupIconFile={#RootDir}\icon\AII-icon.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
PrivilegesRequired=admin
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; App files
Source: "{#RootDir}\dist\LocalAIChat\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Dirs]
; Create and ensure directories are writable
Name: "{app}\ai_models"; Permissions: users-modify
Name: "{app}\conversations"; Permissions: users-modify
Name: "{app}\logs"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\logs"

[Code]
function InitializeSetup(): Boolean;
begin
  // Add any initialization logic here
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Add any post-installation steps here
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
begin
  // Check for any special conditions before installation
  Result := '';
end;

procedure DeinitializeSetup();
begin
  // Add any cleanup logic here
end; 
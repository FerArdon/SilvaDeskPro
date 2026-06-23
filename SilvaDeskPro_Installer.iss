; ============================================================
;  SilvaDesk Pro - Script de Instalador (Inno Setup 6)
;  SEDCAF - Sistema de Gestion Forestal Profesional
;  v1.1.0 - Incluye sistema de licencias con periodo de prueba
; ============================================================

#define AppName      "SilvaDesk Pro"
#define AppVersion   "1.1.0"
#define AppPublisher "SEDCAF - Servicios de Consultoria y Asesoria Forestal"
#define AppExeName   "SilvaDesk Pro.exe"
#define AppURL       "https://github.com/frardonr6/SilvaDeskPro"

[Setup]
AppId={{B3F1A2D4-5C7E-4F8A-9B0C-1D2E3F4A5B6C}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} v{#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}

; Instala en AppData\Local - no requiere UAC
DefaultDirName={localappdata}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes

; Salida del instalador
OutputDir=dist\Installer
OutputBaseFilename=SilvaDeskPro_v{#AppVersion}_Setup
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes

WizardStyle=modern
WizardSizePercent=110
WizardResizable=no

PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
MinVersion=10.0.17763

; Permite actualizar sobre instalacion existente
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "Crear icono en el &Escritorio"; GroupDescription: "Iconos adicionales:"; Flags: checkedonce

[Files]
; Ejecutable principal (compilado con PyInstaller --onefile)
Source: "dist\SilvaDesk Pro.exe"; DestDir: "{app}"; Flags: ignoreversion

; Icono para accesos directos
Source: "assets\icon.ico"; DestDir: "{app}\assets"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}";             Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\assets\icon.ico"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}";       Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\assets\icon.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Iniciar {#AppName} ahora"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Solo borra el ejecutable y assets — NO borra la base de datos ni los documentos generados
; Los datos del usuario (.db, Actas/, Facturas/, BitacorasTFC/) se conservan en {app}
Type: files; Name: "{app}\{#AppExeName}"
Type: files; Name: "{app}\assets\icon.ico"
Type: dirifempty; Name: "{app}\assets"

; NOTA: La clave de licencia se guarda en el Registro de Windows en:
; HKCU\Software\SEDCAF\SilvaDeskPro
; NO se elimina al desinstalar para que sobreviva una reinstalacion.

[Messages]
BeveledLabel=SilvaDesk Pro v{#AppVersion} - SEDCAF

[CustomMessages]
spanish.WelcomeLabel2=Este asistente instalara [name/ver] en tu equipo.%n%nSilvaDesk Pro incluye un periodo de prueba de 15 dias con acceso completo. Despues del periodo, los modulos de Facturador, Protocolo y Bitacora se limitan a 5 registros hasta activar una licencia.%n%nSe recomienda cerrar todas las aplicaciones antes de continuar.

$ErrorActionPreference = 'Continue'
$base  = 'C:\Users\Dev Marinho\clinica-odontologica\database'
$bin   = 'C:\Program Files\MySQL\MySQL Server 8.4\bin'
$data  = 'C:\ProgramData\MySQL\MySQL Server 8.4\Data'
$out   = "$base\init_stdout.log"
$err   = "$base\init_stderr.log"
$estado = "$base\init_estado.log"

Set-Content -Path $estado -Value "=== initialize-insecure $(Get-Date -Format s) ===" -Encoding utf8
New-Item -ItemType Directory -Force -Path $data | Out-Null

$p = Start-Process -FilePath "$bin\mysqld.exe" -ArgumentList '--initialize-insecure','--console' `
     -Wait -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
"mysqld exit code: $($p.ExitCode)" | Out-File -FilePath $estado -Append -Encoding utf8
"arquivos no data dir: $((Get-ChildItem $data -Force | Measure-Object).Count)" | Out-File -FilePath $estado -Append -Encoding utf8

if (-not (Test-Path "$data\mysql")) {
    "INSTALACAO FALHOU - ver init_stderr.log" | Out-File -FilePath $estado -Append -Encoding utf8
    exit 1
}

$svc = Get-Service -Name 'MySQL84' -ErrorAction SilentlyContinue
if (-not $svc) {
    $pi = Start-Process -FilePath "$bin\mysqld.exe" -ArgumentList '--install','MySQL84' `
          -Wait -PassThru -RedirectStandardOutput "$base\install_stdout.log" -RedirectStandardError "$base\install_stderr.log"
    "install exit code: $($pi.ExitCode)" | Out-File -FilePath $estado -Append -Encoding utf8
}

Start-Service MySQL84
Start-Sleep -Seconds 3
"servico status: $((Get-Service MySQL84).Status)" | Out-File -FilePath $estado -Append -Encoding utf8
"=== FIM ===" | Out-File -FilePath $estado -Append -Encoding utf8

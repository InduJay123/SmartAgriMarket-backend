$imports = Get-Content .\_dep_imports.json -Raw | ConvertFrom-Json

$packages = @(
    @{pkg='asgiref'; mods=@('asgiref')},
    @{pkg='Django'; mods=@('django')},
    @{pkg='django-cors-headers'; mods=@('corsheaders')},
    @{pkg='djangorestframework'; mods=@('rest_framework')},
    @{pkg='mysqlclient'; mods=@('MySQLdb','mysqlclient')},
    @{pkg='pdfplumber'; mods=@('pdfplumber')},
    @{pkg='firebase-admin'; mods=@('firebase_admin')},
    @{pkg='openpyxl'; mods=@('openpyxl')},
    @{pkg='sqlparse'; mods=@('sqlparse')},
    @{pkg='tzdata'; mods=@('tzdata')},
    @{pkg='scikit-learn'; mods=@('sklearn')},
    @{pkg='pandas'; mods=@('pandas')},
    @{pkg='numpy'; mods=@('numpy')},
    @{pkg='joblib'; mods=@('joblib')},
    @{pkg='tensorflow'; mods=@('tensorflow')},
    @{pkg='xgboost'; mods=@('xgboost')},
    @{pkg='statsmodels'; mods=@('statsmodels')},
    @{pkg='matplotlib'; mods=@('matplotlib')},
    @{pkg='seaborn'; mods=@('seaborn')},
    @{pkg='jupyter'; mods=@('jupyter')},
    @{pkg='ipykernel'; mods=@('ipykernel')},
    @{pkg='python-dotenv'; mods=@('dotenv')},
    @{pkg='drf-yasg'; mods=@('drf_yasg')},
    @{pkg='djangorestframework-simplejwt'; mods=@('rest_framework_simplejwt')},
    @{pkg='requests'; mods=@('requests')},
    @{pkg='scipy'; mods=@('scipy')}
)

$out = @()
$out += 'package|import_modules|direct_import_count'

foreach($p in $packages){
    $count = 0
    foreach($m in $p.mods){
        if($imports.PSObject.Properties.Name -contains $m){
            $count += @($imports.$m).Count
        }
    }
    $out += ('{0}|{1}|{2}' -f $p.pkg, ($p.mods -join ','), $count)
}

Set-Content -Path .\_dep_target_counts.txt -Value $out -Encoding utf8
Write-Output 'WROTE _dep_target_counts.txt'

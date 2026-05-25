# Sistema de Impressão de Etiquetas

Aplicativo desktop Windows para impressão de etiquetas de produtos a partir de um banco de dados Firebird. Gera comandos EPL para impressoras de etiquetas (ex: Elgin, Zebra).

## Funcionalidades

- Conexão com banco de dados Firebird local ou em rede
- Pesquisa de produtos por número de nota, código ou descrição
- Seleção de múltiplos itens com quantidade de etiquetas por item
- Impressão direta ou via fila de impressão
- Configuração persistente de banco de dados e impressora

## Requisitos

- Windows 10 ou superior
- Python 3.10+
- Firebird Client instalado ([download](https://firebirdsql.org/en/firebird-3-0/))
- Visual Studio Build Tools (necessário para compilar com Nuitka)

## Instalação das dependências

```bash
pip install -r requirements.txt
```

## Configuração

Copie `config.template.json` para `config.json` e ajuste os valores:

```json
{
  "ultimo_banco": "C:\\caminho\\para\\banco.fdb",
  "impressora_etiquetas": "Nome da Impressora"
}
```

O aplicativo também salva a configuração automaticamente ao selecionar banco e impressora pela interface.

## Executar em modo desenvolvimento

```bash
python etiquetas_key_v5.py
```

## Gerar executável (.exe)

O projeto usa **Nuitka** para compilar o Python em código nativo, o que evita falsos positivos em antivírus (diferente do PyInstaller, que usa um bootloader frequentemente flagrado).

### Pré-requisitos para o build

- [Nuitka](https://nuitka.net) — `pip install nuitka`
- Visual Studio Build Tools com "Desenvolvimento para desktop com C++" ([download](https://visualstudio.microsoft.com/visual-cpp-build-tools/))

### Gerar o ícone

O ícone é gerado por um script Python (requer Pillow):

```bash
python gerar_icone.py
```

Isso cria `icone.ico` com 7 resoluções (16 até 256 px).

### Comando de build

Execute dentro da pasta do projeto:

```bash
python -m nuitka ^
    --standalone ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --include-package=fdb ^
    --include-package=firebird ^
    --windows-icon-from-ico=icone.ico ^
    --windows-company-name="EtiquetasKey" ^
    --windows-product-name="Sistema de Impressao de Etiquetas" ^
    --windows-file-version=5.0.0.0 ^
    --windows-product-version=5.0.0.0 ^
    --windows-file-description="Sistema de Impressao de Etiquetas" ^
    --output-filename=EtiquetasApp.exe ^
    --output-dir=dist ^
    etiquetas_key_v5.py
```

> **Nota:** O `config.json` é salvo automaticamente na mesma pasta do `.exe` ao configurar banco e impressora pela interface. Não é necessário embutir o arquivo no build.

### Parâmetros explicados

| Parâmetro | Descrição |
|---|---|
| `--standalone` | Gera uma pasta autocontida (menos suspeito para antivírus que `--onefile`) |
| `--windows-console-mode=disable` | Remove a janela de console (modo GUI) |
| `--enable-plugin=tk-inter` | Inclui o Tkinter e dependências Tcl/Tk |
| `--include-package=fdb` | Inclui o driver Firebird |
| `--include-package=firebird` | Inclui dependências do fdb |
| `--windows-company-name` / `--windows-product-name` | Metadados do exe (reduzem falsos positivos em antivírus) |
| `--windows-file-version` | Versão do arquivo incorporada nos metadados do exe |

### Por que `--standalone` em vez de `--onefile`?

O modo `--onefile` gera um único `.exe` que se auto-extrai no `%TEMP%` a cada execução — comportamento idêntico ao de malware, por isso é constantemente flagrado por antivírus. O modo `--standalone` cria uma pasta com o executável e seus arquivos de suporte, sem extração em tempo de execução.

### Resultado

Gerado em `dist\EtiquetasApp.exe.dist\` (~pasta com dependências).

Distribua a pasta inteira. As configurações de banco e impressora são salvas em `config.json` na mesma pasta do `.exe`.

## Estrutura do projeto

```
etiquetas_key_v5.py      # Código-fonte principal
config.template.json     # Template de configuração
requirements.txt         # Dependências Python
```

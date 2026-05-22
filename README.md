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

### Comando de build

Execute dentro da pasta do projeto:

```bash
python -m nuitka ^
    --onefile ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --include-package=fdb ^
    --include-package=firebird ^
    --include-data-files=config.json=config.json ^
    --output-filename=EtiquetasApp.exe ^
    --output-dir=dist ^
    etiquetas_key_v5.py
```

> **Nota:** `config.json` precisa existir na pasta para ser embutido no executável. Crie-o a partir do `config.template.json` antes de buildar.

### Parâmetros explicados

| Parâmetro | Descrição |
|---|---|
| `--onefile` | Gera um único `.exe` autocontido |
| `--windows-console-mode=disable` | Remove a janela de console (modo GUI) |
| `--enable-plugin=tk-inter` | Inclui o Tkinter e dependências Tcl/Tk |
| `--include-package=fdb` | Inclui o driver Firebird |
| `--include-package=firebird` | Inclui dependências do fdb |
| `--include-data-files=...` | Embute o `config.json` no executável |

### Resultado

O executável é gerado em `dist\EtiquetasApp.exe` (~11 MB).

Na primeira execução, o `config.json` é extraído para a pasta do `.exe`. As configurações de banco e impressora são salvas automaticamente pela interface.

## Estrutura do projeto

```
etiquetas_key_v5.py      # Código-fonte principal
config.template.json     # Template de configuração
requirements.txt         # Dependências Python
```

# Update requirements.txt

Uma ferramenta de desktop simples para verificar as versões mais recentes de pacotes Python listados em um arquivo `requirements.txt` e gerar um novo arquivo atualizado e organizado.

## Descrição

Com GUI simples do TKInter para seleção do arquivo `requirements.txt`, se consulta o site oficial do PyPI ([pypi.org](https://pypi.org/)) para encontrar a última versão estável de cada pacote. Ao final do processo, ele gera um novo arquivo de `requirements` com as versões atualizadas e em ordem alfabética, além de um arquivo de log detalhado da execução.

## Funcionalidades Principais

  - **Mecanismo de Verificação Híbrido:**
    1.  Utiliza um método rápido (`requests` + `BeautifulSoup`) para a maioria das verificações (Fast Check).
    2.  Recorre ao `Selenium` para pacotes que exigem renderização de JavaScript, entre outras dependências (Slow Check).
  - **Log Detalhado:** Para cada execução, um arquivo `log_[data_hora].txt` é criado, registrando cada passo do processo com timestamps e níveis de severidade (INFO, WARNING, ERROR), facilitando a depuração e o acompanhamento.

## Pré-requisitos

Antes de começar:

  - [Python 3.8](https://www.python.org/downloads/) ou superior
  - `pip` (gerenciador de pacotes do Python, geralmente já vem com o Python)
  - Google Chrome (necessário para o funcionamento do Selenium)
  - pip install requests beautifulsoup4 selenium

## Como Usar

1.  Clique no executavel da pasta /dist/
2.  A janela principal do "Verificador Híbrido de Versões PyPI" será exibida.
3.  Clique no botão **"Procurar requirements.txt"** para procurar o arquivo.
4.  O caminho completo do arquivo selecionado aparecerá no campo de texto.
5.  Clique no botão **"Atualizar"** para iniciar o processo.
6.  Aguarde a conclusão. Você pode acompanhar o progresso em tempo real pelo console.
7.  Ao final, uma mensagem de "Concluído" será exibida e o log gerado.

## Saídas do Programa

- `requirements_atualizado.txt`: Contém a lista de pacotes com suas versões mais recentes, formatados como `pacote==versao` e ordenados alfabeticamente.
- `log_AAAA-MM-DD_HH-MM-SS.txt`: Um arquivo de log detalhado para registro e depuração.

## Licença

T2C Group

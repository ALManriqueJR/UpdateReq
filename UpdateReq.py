import re, requests
import tkinter as tk
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional
from tkinter import filedialog, messagebox
from selenium import webdriver as wb
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
import logging
from datetime import datetime

# Exclusivos para Type Hints
from re import Pattern
from requests.models import Response
from selenium.webdriver.chrome.webdriver import WebDriver
from bs4.element import Tag, PageElement
from selenium.webdriver.remote.webelement import WebElement
from tkinter import Tk, Frame, Label, Button, Text

var_strCaminho = ""
var_strPypiUrl = "https://pypi.org/project/"
var_dictReqUpdated = {}

log_filename = f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_filename, "w", "utf-8"), logging.StreamHandler()],
)


def procurar_arquivo() -> None:
    """
    Abre um diálogo para selecionar o arquivo requirements.txt e exibe o caminho selecionado.
    """
    global var_strCaminho
    filepath = filedialog.askopenfilename(filetypes=[("Arquivos de Texto", "*.txt")])
    if filepath:
        var_strCaminho = filepath
        var_txtCampo.config(state=tk.NORMAL)
        var_txtCampo.delete("1.0", tk.END)
        var_txtCampo.insert(tk.END, var_strCaminho)
        var_txtCampo.config(state=tk.DISABLED)


def salvar_requirements(
    arg_dictVersoesAtualizadas: dict,
    arg_strCaminho: str,
    arg_strNomeNovoReq: str = "requirements_atualizado.txt",
):
    """
    Salva um dicionário em um arquivo .txt, no mesmo diretório do arquivo original.
    """
    try:

        var_pathCaminhoOriginal: Path = Path(arg_strCaminho)

        var_pathDiretorioPai: Path = var_pathCaminhoOriginal.parent

        var_pathCaminhoFinal: Path = var_pathDiretorioPai / arg_strNomeNovoReq

        with open(var_pathCaminhoFinal, "w", encoding="utf-8") as file:
            for pacote, versao in sorted(
                arg_dictVersoesAtualizadas.items(), key=lambda item: item[0].lower()
            ):
                linha = f"{pacote}=={versao}\n"
                file.write(linha)

        logging.info(f"Arquivo '{var_pathCaminhoFinal}' criado com sucesso.")

        return str(var_pathCaminhoFinal)

    except Exception as e:
        logging.critical(f"Erro ao salvar o arquivo: {e}")
        return None


def verificar_versoes_hibrido():
    """
    Checagem das versões com requests/bs4 (Fast), e em último caso Selenium (Slow).
    """
    global var_dictReqUpdated
    global var_dictReqOld
    var_dictReqOld = {}
    var_dictReqUpdated = {}

    if not var_strCaminho:
        messagebox.showwarning(
            "Aviso", "Selecione um arquivo de requirements.txt primeiro."
        )
        return

    try:

        with open(var_strCaminho, "r", encoding="utf-8") as file:
            content = file.read()

        var_patternNomePacote: Pattern = re.compile(
            r"^\s*([A-Za-z][A-Za-z0-9_-]*)(?:[<>=!~]+([\d.a-zA-Zrc]+))?", re.MULTILINE
        )

        var_lstMatchs: list = var_patternNomePacote.findall(content)

        for var_lstNomePacote, var_lstVersaoPacote in var_lstMatchs:
            var_lstNomePacote = var_lstNomePacote.strip()
            var_lstVersaoPacote = (
                var_lstVersaoPacote.strip() if var_lstVersaoPacote else "-"
            )
            var_dictReqOld[var_lstNomePacote] = var_lstVersaoPacote

        var_lstPacotesSelenium = []

        logging.info("*** CHECKING REQUIREMENTS ***")

        for var_strNomePacote in var_dictReqOld.keys():
            try:
                var_strUrl: str = f"{var_strPypiUrl}{var_strNomePacote}/"
                var_responsePypi: Response = requests.get(var_strUrl, timeout=10)
                if var_responsePypi.status_code == 200:
                    var_bsPagina: BeautifulSoup = BeautifulSoup(
                        var_responsePypi.content, "html.parser"
                    )

                    var_tagHeaderElement: Optional[PageElement] = var_bsPagina.find(
                        "h1", class_="package-header__name"
                    )

                    if var_tagHeaderElement and isinstance(var_tagHeaderElement, Tag):
                        var_strNomeVersaoPacote: str = var_tagHeaderElement.get_text(
                            strip=True
                        )
                        var_strVersaoPacote: str = var_strNomeVersaoPacote.replace(
                            var_strNomePacote, "", 1
                        ).strip()

                        var_strMsg: str = (
                            f"{var_strNomePacote:<30} | Versão Usada é a mais atual: {var_dictReqOld[var_strNomePacote]} (Fast Check)"
                            if var_strVersaoPacote == var_dictReqOld[var_strNomePacote]
                            else f"{var_strNomePacote:<30} | Versão Usada: {var_dictReqOld[var_strNomePacote]:<30}| Versão Atualizada: {var_strVersaoPacote} (Fast Check)"
                        )
                        logging.info(var_strMsg)

                        var_dictReqUpdated[var_strNomePacote] = var_strVersaoPacote

                    else:
                        var_lstPacotesSelenium.append(var_strNomePacote)
                else:
                    var_strMsg: str = (
                        f"Pacote: {var_strNomePacote:<30} | Status retornado diferente de 200. [Erro {var_responsePypi.status_code}] (Fast Check Failed)"
                    )
                    logging.error(var_strMsg)

            except requests.exceptions.RequestException:
                logging.critical(
                    f"Pacote: {var_strNomePacote:<30} | Erro de Rede (Fast Check Fatal Error)"
                )
                var_lstPacotesSelenium.append(var_strNomePacote)

        if var_lstPacotesSelenium:
            var_wbNav: Optional[WebDriver] = None
            try:
                chrome_options: Options = Options()
                chrome_options.add_argument(
                    "--user-data-dir=C:/Selenium/ChromeProfile"
                )  # Perfil provisorio para o robo
                var_wbNav = wb.Chrome(options=chrome_options)
                wait: WebDriverWait = WebDriverWait(var_wbNav, 10)

                for var_strNomePacote in var_lstPacotesSelenium:
                    try:
                        var_strUrl: str = f"{var_strPypiUrl}{var_strNomePacote}/"
                        var_wbNav.get(var_strUrl)
                        var_weHeaderElement: WebElement = wait.until(
                            EC.presence_of_element_located(
                                (By.CLASS_NAME, "package-header__name")
                            )
                        )
                        var_strNomeVersaoPacote: str = var_weHeaderElement.text
                        var_strVersaoPacote: str = var_strNomeVersaoPacote.replace(
                            var_strNomePacote, "", 1
                        ).strip()

                        var_strMsg: str = (
                            f"{var_strNomePacote:<30} | Versão usada é a mais atual: {var_dictReqOld[var_strNomePacote]} (Slow Check)"
                            if var_strVersaoPacote == var_dictReqOld[var_strNomePacote]
                            else f"{var_strNomePacote:<30} | Versão Usada: {var_dictReqOld[var_strNomePacote]:<30}| Versão Atualizada: {var_strVersaoPacote} (Slow Check)"
                        )

                        logging.info(var_strMsg)

                        var_dictReqUpdated[var_strNomePacote] = var_strVersaoPacote

                    except TimeoutException:
                        logging.critical(
                            f"Pacote: {var_strNomePacote:<30} | Pacote não encontrado no PyPI ou Tempo de espera excedido (Slow Check)"
                        )
                    except Exception as e:
                        logging.critical(
                            f"Pacote: {var_strNomePacote:<30} | Erro com Selenium: {e} (Slow Check Fatal Error)"
                        )
            finally:
                if var_wbNav:
                    var_wbNav.quit()

        logging.info("*** REQUIREMENTS CHECKED ***")

        if var_dictReqUpdated:
            var_NovoReq = salvar_requirements(var_dictReqUpdated, var_strCaminho)

            if var_NovoReq:
                messagebox.showinfo(
                    "Concluído",
                    f"Verificação finalizada.\nNovo arquivo foi criado em:\n{var_NovoReq}",
                )
            else:
                messagebox.showerror(
                    "Erro",
                    "A verificação foi concluída, mas houve um erro ao salvar o novo arquivo.",
                )
        else:
            messagebox.showwarning(
                "Aviso", "Sem sucesso em gerar o requirements atualizado."
            )
            logging.error("Sem sucesso em gerar o requirements atualizado.")

    except Exception as e:
        messagebox.showerror("Erro Crítico", f"Ocorreu um erro inesperado: {e}")
        logging.critical(f"Erro Crítico: {e}")


var_tkJanela: Tk = Tk()
var_tkJanela.title("Atualizador de requirements.txt")
var_tkJanela.geometry("600x210")
var_tkJanela.resizable(False, False)
var_frameEcra: Frame = Frame(var_tkJanela, padx=10, pady=10)
var_frameEcra.pack(expand=True, fill=tk.BOTH)

var_strDisclaimer: str = (
    "Este programa verifica a versão estável mais recente de cada pacote no site PyPI. Em casos raros, pode se tratar de uma pre-release (alpha, beta, etc)."
)

var_Paragrafo: Label = Label(
    var_frameEcra,
    text=var_strDisclaimer,
    wraplength=400,
    justify=tk.CENTER,
)

var_Paragrafo.pack(pady=(0, 5))

var_btnProcurar: Button = Button(
    var_frameEcra, text="Procurar requirements.txt", command=procurar_arquivo
)

var_btnProcurar.pack(pady=5)

var_txtCampo: Text = Text(
    var_frameEcra, height=1, width=70, wrap=tk.NONE, state=tk.DISABLED
)
var_txtCampo.pack(pady=10)

var_strTip: str = (
    "Caso caminho do arquivo seja muito longo, ao clicar e arrastar para os lados é possivel visualizá-lo."
)

var_Help: Label = Label(
    var_frameEcra,
    text=var_strTip,
    wraplength=400,
    justify=tk.CENTER,
)

var_Help.pack(pady=(0, 10))

var_btnAtualizar: Button = Button(
    var_frameEcra,
    text="Atualizar",
    command=verificar_versoes_hibrido,
)

var_btnAtualizar.pack(pady=1)

var_tkJanela.mainloop()

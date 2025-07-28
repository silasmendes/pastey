### ✅ **Objetivo principal**

Criar uma aplicação local que:

* Monitore continuamente o clipboard do Windows,
* Armazene o histórico de itens copiados (textos),
* Permita acessar rapidamente esse histórico com um atalho (Ctrl+Shift+V),
* Exiba os itens em uma janela com interface simples (Tkinter),
* Permita ao usuário **fixar** itens que devem ser mantidos no histórico para sempre,
* Utilize **SQLite** para persistência local dos dados (itens fixados e histórico).

---

### 🧱 Requisitos técnicos

#### 📦 Tecnologias/libraries:

* Python 3.x (ja configurei o venv: (venv) PS X:\Repos\pastey>)
* `pyperclip` (acesso ao clipboard)
* `keyboard` (atalhos globais)
* `tkinter` (interface gráfica)
* `sqlite3` (persistência local)
* `pyautogui` (colagem automática com Ctrl+V)

ATENÇÃO: caso alguns dessas libraries tenho sido descontinuada ou nao seja adequada, fique a vontade para usar outra. 

---

### 💾 Especificações do banco de dados (SQLite)

Tabela: `clipboard_items`

| Campo      | Tipo     | Descrição              |
| ---------- | -------- | ---------------------- |
| id         | INTEGER  | Chave primária         |
| content    | TEXT     | Conteúdo copiado       |
| is_pinned | BOOLEAN  | `1` se item for fixado |
| timestamp  | DATETIME | Data/hora da cópia     |

Regras:

* Itens fixados (`is_pinned = 1`) nunca são removidos automaticamente.
* Itens não fixados são limitados a, por exemplo, 100 entradas (FIFO).

---

### 🖱️ Funcionalidade da UI

* Janela é aberta com **Ctrl+Shift+V**
* Mostra a lista com os últimos itens copiados (fixados sempre no topo)
* Permite:

  * Selecionar e colar com duplo clique ou Enter
  * Fixar/desafixar um item (ex: botão ao lado ou atalho)
  * Limpar itens não fixados 

---

### 🔐 Segurança

* Nenhum dado é enviado para a nuvem.
* Tudo fica salvo localmente em um arquivo `.db`.
* Se possível, evite duplicatas consecutivas.

---

### 🚀 Entregáveis esperados:

1. Código-fonte funcional do MVP
2. Script `requirements.txt`
3. Instruções para rodar (README simples)
4. Interface gráfica mínima, funcional e clara
# Tutorial: Scripts Externos para o JAM

[![Tutorial Original](https://img.shields.io/badge/Tutorial_Original-blue)](https://redsquirrel87.com/manga-downloader-external-scripts-tutorial)

Nesta página você pode encontrar um tutorial passo a passo para criar um script externo customizado compatível com o [JAM](/manga-downloader).

### Índice

* [Introdução](#introdução)
* [1) Análise do site](#1-análise-do-site)
* [2) Criando o script](#2-criando-o-script)
  + [Usando JAVA](#usando-java)
  + [Usando Python](#usando-python)
* [3) Configuração do JAM](#3-configuração-do-jam)

## Introdução

Para criar um script, você precisa escolher qual linguagem de programação usar. Sim, infelizmente *você precisa saber pelo menos uma linguagem de programação*, não importa qual. Hoje em dia, além de existirem guias de aprendizado totalmente gratuitos na web, há IAs que ajudam enormemente a escrever e verificar o código de qualquer linguagem. Portanto, mesmo que você esteja começando do zero, saiba que não é mais tão difícil quanto costumava ser.

Felizmente, não há limitação de qual linguagem pode ser usada; o importante é que o script final seja executável no seu sistema (seja Windows, Linux ou Mac). Tenha em mente que seu script terá que fazer essencialmente três coisas:

1. Baixar o código-fonte HTML de uma página da web (do site que você quer suportar).
2. Analisar (Fazer o *parse*) do código HTML baixado (para encontrar a lista de capítulos ou as páginas de um capítulo individual).
3. Criar um objeto JSON e imprimi-lo na tela para que o JAM possa ler e interpretar.

Isso é tudo: 3 passos simples. Muitas linguagens de programação possuem bibliotecas que permitem fazer essas coisas facilmente (download, parsing HTML, JSON), mas nada o impede de usar métodos manuais (como *regex*). No entanto, recomendo sempre usar bibliotecas para maior segurança e economia de tempo.

Neste tutorial, mostrarei como criar um script usando as 2 linguagens mais populares: **Java** e **Python**. O site que usaremos como exemplo será o [weebcentral.com](https://weebcentral.com).

## 1) Análise do site

O primeiro passo é analisar o código HTML do site que você deseja suportar para extrair as informações necessárias.

Para ver o código-fonte, recomendo usar o navegador **Google Chrome**, pois ele possui um recurso útil chamado **Inspecionar**, que permite verificar com um clique o código HTML de qualquer parte da página.

1. Abra no navegador o site que você deseja suportar e procure por um mangá (exemplo: `https://weebcentral.com/series/01J76XYDRMXQ5NEQNT4R3B0Z2N/...`).
2. Selecione o título do mangá, clique com o botão direito e escolha **Inspecionar**.

![Developer Console](https://redsquirrel87.com/_media/md/fl4waetwkl.png)

3. O painel de *Desenvolvedor* se abrirá mostrando a tag HTML correspondente (por exemplo, dentro de um `<h1>`).

![H1 Tag](https://redsquirrel87.com/_media/md/5d3wizraqh.png)

4. Da mesma forma, para a lista de capítulos, clique com o botão direito em um deles e selecione **Inspecionar**. 

![Inspect Chapter](https://redsquirrel87.com/_media/md/zfd3ybidem.png)

![Highlighted Chapter](https://redsquirrel87.com/_media/md/uuw8giuijp.png)

Suba o cursor no código HTML até que a lista inteira de capítulos seja selecionada (ex: uma `div` com id `chapters-list`).

![Chapters List](https://redsquirrel87.com/_media/md/twixlnn956.png)

5. Ao expandir o bloco dessa lista, você notará os padrões repetitivos para cada capítulo. 

![Chapters Blocks](https://redsquirrel87.com/_media/md/z1yocke3is.png)

![Expanded Chapter](https://redsquirrel87.com/_media/md/ijjx4covrm.png)

Geralmente, você encontrará o link (`href`) dentro de uma tag `<a>`, o título dentro de um `<span>` e a data em um `<time>`.

![URL href](https://redsquirrel87.com/_media/md/eizobwiudv.png)
![Chapter Title](https://redsquirrel87.com/_media/md/cgmjbusbfw.png)
![Chapter Date](https://redsquirrel87.com/_media/md/ae9jvzfuel.png)

6. Para capturar as páginas, entre em um capítulo e inspecione uma imagem. 

![Inspect Page Image](https://redsquirrel87.com/_media/md/hxnyfaee7i.png)

Você verá as tags `<img>` e precisará capturar seus respectivos atributos `src`.

![Image SRC](https://redsquirrel87.com/_media/md/kvn3cx5apr.png)

**Nota Importante:** Este é apenas um exemplo genérico. Cada site possui uma estrutura HTML única. Além disso, muitos sites modernos ofuscam o código ou injetam conteúdo via Javascript. Nesses casos, o código HTML puro não conterá as informações, exigindo técnicas mais avançadas como interpretadores Javascript externos (ex: Selenium).

## 2) Criando o script

Uma vez que descobrimos como extrair a informação, é hora de criar o script.

### Usando JAVA

Em JAVA, utilizaremos 2 bibliotecas simples: [jsoup](https://jsoup.org) (para download e parse de HTML) e [gson](https://github.com/google/gson) (para manipulação de JSON).

Abaixo está o código-fonte comentado em JAVA que adiciona suporte para o site Weebcentral:

```java
// Importamos as bibliotecas necessárias
import com.google.gson.JsonArray;
import com.google.gson.JsonObject;
import org.jsoup.jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;

public class Weebcentral {
    
    // Método principal que será executado ao iniciar o script
    public static void main(String[] args) {
        JsonObject output_json = new JsonObject(); // Cria o objeto JSON de retorno
        if (args.length != 2) { // Verifica se os argumentos estão corretos
            output_json.addProperty("error", "Quantidade de argumentos inválida."); 
        } else {
            if (args[1].equalsIgnoreCase("CHAPTERS")) { // Para adquirir a lista de capítulos
                GetChapters(args[0]);
                return;
            } else if (args[1].equalsIgnoreCase("PAGES")) { // Para adquirir a lista de páginas
                GetPages(args[0]);
                return;
            } else {
                output_json.addProperty("error", "Segundo argumento desconhecido (deve ser CHAPTERS ou PAGES).");
            }
        }
        System.out.println(output_json.toString()); // Imprime erros, se houverem
    }

    // Função que extrai os capítulos de um mangá
    private static void GetChapters(String u) {
        JsonObject output_json = new JsonObject(); 
        Document doc;
        try {
            doc = Jsoup.connect(u).timeout(10*1000).get(); // Conecta e baixa o HTML
            Elements content = doc.getElementsByTag("h1"); 
            if (content.isEmpty()) {
                output_json.addProperty("manga", "ERRO"); 
            } else {
                output_json.addProperty("manga", content.first().ownText().trim()); 
            }
            JsonArray out_chapters = new JsonArray(); 
            Element div = doc.getElementById("chapter-list"); 
            Elements as = div.getElementsByTag("a"); 
            
            for (Element a : as) {
                JsonObject out_chapter = new JsonObject(); 
                out_chapter.addProperty("title", a.select("span[class='']").text().trim()); 
                out_chapter.addProperty("url", a.attr("href")); 
                out_chapter.addProperty("date", a.getElementsByTag("time").attr("datetime").trim()); 
                out_chapter.addProperty("language", "English"); 
                
                // Valores vazios para o que não está disponível no site
                out_chapter.addProperty("group", ""); 
                out_chapter.addProperty("uploader", "");
                out_chapter.addProperty("views", "");
                out_chapters.add(out_chapter); 
            }
            output_json.add("chapters", out_chapters); 
        } catch (Exception e) {
            output_json.addProperty("error", "Erro obtendo capítulos (" + e.getMessage() + ")"); 
        }
        System.out.println(output_json.toString()); // Retorna o JSON final para o JAM
    }

    // Função que extrai a lista de páginas de um capítulo
    private static void GetPages(String u) {
        JsonObject output_json = new JsonObject(); 
        output_json.addProperty("user-agent", ""); 
        output_json.add("cookies", new JsonArray()); 
        
        try {
            // Nota: Adicionamos os parâmetros finais no link específicos para este site mostrar tudo
            Document doc = Jsoup.connect(u + "imagesis_prev=False&reading_style=long_strip").timeout(10 * 1000).get();

            String link;
            JsonArray out_pages = new JsonArray(); 
            Elements imgs = doc.getElementsByTag("img"); 
            for (int i = 0; i < imgs.size(); i++) { 
                link = imgs.get(i).attr("src").trim(); 
                out_pages.add(link); 
            }
            output_json.add("pages", out_pages); 
        } catch (Exception e) {
            output_json.addProperty("error", "Erro obtendo páginas (" + e.getMessage() + ")"); 
        }
        System.out.println(output_json.toString()); 
    }    
}
```

### Usando Python

Para mostrar que você não precisa saber JAVA para criar scripts, o exemplo abaixo escrito em Python faz exatamente as mesmas coisas. Utilizaremos **requests** para baixar páginas, **BeautifulSoup** para o parse e **json**.

```python
import sys
import requests
import json
from bs4 import BeautifulSoup

def get_chapters(url):
    output_json = {}
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        title_element = soup.find('h1')
        if title_element:
            output_json["manga"] = title_element.text.strip()
        else:
            output_json["manga"] = "ERROR"

        chapters = []
        chapter_list_div = soup.find(id="chapter-list")
        if chapter_list_div:
            for a in chapter_list_div.find_all('a'):
                chapter_info = {
                    "title": a.find('span', class_='').text.strip(),
                    "url": a.get('href'),
                    "date": a.find('time').get('datetime').strip(),
                    "language": "English",
                    "group": "",
                    "uploader": "",
                    "views": ""
                }
                chapters.append(chapter_info)

        output_json["chapters"] = chapters
    except Exception as e:
        output_json["error"] = f"Erro obtendo a lista de capítulos ({str(e)})"

    print(json.dumps(output_json, indent=4))

def get_pages(url):
    output_json = {
        "user-agent": "",
        "cookies": []
    }
    try:
        response = requests.get(f"{url}/images?is_prev=False&reading_style=long_strip", timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        pages = []
        for img in soup.find_all('img'):
            src = img.get('src').strip()
            pages.append(src)
        output_json["pages"] = pages
    except Exception as e:
        output_json["error"] = f"Erro obtendo as páginas ({str(e)})"

    print(json.dumps(output_json, indent=4))

def main():
    if len(sys.argv) != 3:
        print(json.dumps({"error": "Quantidade de argumentos inválida."}, indent=4))
        return

    url, mode = sys.argv[1], sys.argv[2].upper()
    if mode == "CHAPTERS":
        get_chapters(url)
    elif mode == "PAGES":
        get_pages(url)
    else:
        print(json.dumps({"error": "Segundo argumento desconhecido."}, indent=4))

if __name__ == "__main__":
    main()
```

## 3) Configuração do JAM

Agora que você criou seu script, é necessário configurar o JAM para usá-lo corretamente.

Como os scripts nestes exemplos não envolvem a criação direta de um arquivo `.exe` nativo no Windows, teremos que criar um **Launcher** (Iniciador) manualmente para eles. Basta criar um arquivo de texto e escrever o comando completo.

Para iniciar um script Java no Windows, crie um arquivo de texto e insira:

```bat
@echo off
java -jar seu_script.jar %*
```
*(Renomeie a extensão do arquivo de `.txt` para `.bat` para torná-lo executável).*

![Bat File](https://redsquirrel87.com/_media/md/hru8aien4m.png)

Para iniciar no Linux ou Mac, edite o arquivo assim:

```bash
#!/bin/bash
java -jar seu_script.jar "$@"
```
*(Dê permissão de execução com o comando `chmod +x arquivo.sh`).*

Se o seu script for em **Python**, o launcher no Windows deve ser assim:

```bat
@echo off
python seu_script.py %*
```

### Inserindo no JAM

Tendo criado o inicializador, para garantir que o script funcione, podemos abri-lo pelo terminal passando o argumento `CHAPTERS` para ver o array JSON impresso na tela.

![Terminal Test](https://redsquirrel87.com/_media/md/sa1ud3tvet.png)

E com o comando `PAGES` para as imagens:

![Terminal Pages](https://redsquirrel87.com/_media/md/n7x6rhuwbx.png)

Para inseri-lo de vez no JAM:

1. Certifique-se de que o inicializador gerado (`.bat` ou `.sh`) esteja na mesma pasta do arquivo principal.
2. Inicie o JAM, clique no menu **Edit** e escolha **External Scripts**.

![Edit Menu](https://redsquirrel87.com/_media/md/3tctuxoxgb.png)

3. Na tela exibida, clique no botão **Add**.
4. Insira o domínio do site (ex: `weebcentral.com`).

![Domain Input](https://redsquirrel87.com/_media/md/tjbswrxwe2.png)

5. Selecione o arquivo inicializador (`.bat` ou `.sh`) que você criou.
6. Clique em **OK** para salvar.

![Config Saved](https://redsquirrel87.com/_media/md/q8w3w6iihg.png)

Pronto! Ao tentar adicionar um link no programa, certifique-se de marcar a caixa **External Script** como *Generic Framework*, e o JAM chamará automaticamente o seu código. 

![Add Series](https://redsquirrel87.com/_media/md/xg1jdnepb1.png)

O JAM fará a leitura através do script perfeitamente.

![Chapter List Loaded](https://redsquirrel87.com/_media/md/39wsaz1pep.png)
![Downloading](https://redsquirrel87.com/_media/md/zv5rgo3klv.png)

Se a página mudar no futuro, basta atualizar o seu script sem precisar esperar uma atualização oficial do JAM.
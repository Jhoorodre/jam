# JAM - Java Manga Downloader

[![Site Oficial](https://img.shields.io/badge/Site_Oficial-blue)](https://redsquirrel87.com/jam)
[![Releases do GitHub](https://img.shields.io/github/v/release/RedSquirrel87/jam)](https://github.com/RedSquirrel87/jam/releases/tag/Release)

O **JAM** é um aplicativo simples baseado em Java que permite baixar e arquivar capítulos de uma ampla variedade de sites e fontes de mangás suportados. Originalmente, o programa se chamava *Manga Downloader*, mas como o nome poderia ser facilmente interpretado como algo relacionado à pirataria, ele foi completamente alterado. Isso evita qualquer mal-entendido, pois o programa tem a intenção de ser puramente uma ferramenta legal de arquivamento.

Até o momento, o programa suporta **mais de 50 sites diferentes**! Você pode encontrar a lista completa dentro do próprio aplicativo.

O programa também suporta diversos frameworks de mangá amplamente utilizados, o que significa que ele pode funcionar com muitos sites construídos sobre essas plataformas — mesmo que não estejam listados oficialmente como suportados. Os frameworks suportados incluem:
- Foolslide
- My Manga Reader CMS
- WordPress (Basic)
- WordPress Manga (Madara)
- Coreview
- Genkan
- Flat Manga
- Cruzers
- Pizza Reader
- Clone do Madara (não-WordPress)
- Manga Stream

## 📥 Instalação

1. Instale (ou atualize) o [JDK](https://www.oracle.com/it/java/technologies/downloads/) (v23 ou superior) e reinicie o seu PC (é muito importante para configurar as variáveis de ambiente corretamente!).
2. Baixe o pacote ZIP na [página oficial de releases do GitHub](https://github.com/RedSquirrel87/jam/releases/tag/Release) e extraia-o.
3. Execute o arquivo JAR:
   - **No Windows**: geralmente, basta dar um duplo clique nele. Se isso não funcionar, clique com o botão direito no arquivo JAR, escolha a opção "Abrir com" e selecione "JAVA(TM) Platform SE binary".
   - **Em distribuições Unix ou Mac**: abra uma janela de terminal na mesma pasta que o arquivo JAR e digite o seguinte comando:
     ```bash
     java -jar JAM.jar
     ```

## ⚙️ Opções da JVM
A partir da versão v50, você pode configurar opções/parâmetros customizados para a JVM ao iniciar o programa. Para fazer isso, abra o arquivo `vmoptions.txt` (criado automaticamente na primeira inicialização, na mesma pasta do executável principal) e adicione as opções/parâmetros customizados no arquivo (apenas um por linha).

## 🔌 Suporte a Scripts Externos
A partir da versão v70, o programa agora suporta o uso de scripts externos personalizados para expandir a compatibilidade com qualquer site que você desejar. Você pode encontrar um tutorial passo a passo sobre como criar e implementar esses scripts [AQUI](https://redsquirrel87.com/manga-downloader-external-scripts-tutorial).

## 🐛 Bugs, Problemas, Melhorias e Sugestões
Você pode relatar quaisquer bugs ou problemas, bem como dar sugestões de melhorias e propostas, utilizando a [página oficial do projeto no GitHub](https://github.com/RedSquirrel87/jam/issues).

---

### Aviso de Isenção de Responsabilidade (Disclaimer)
O JAM (doravante "este aplicativo") foi desenvolvido inteiramente por Red Squirrel (doravante "o criador"), também conhecido como @redsquirrel87 ([https://redsquirrel87.com](https://redsquirrel87.com)). Este é um projeto completamente não oficial e não possui suporte, endosso ou qualquer afiliação com a equipe, proprietários ou comunidades de nenhum dos sites de origem. Dessa forma, pede-se expressamente que os usuários não reportem bugs, problemas ou dúvidas relacionadas a este aplicativo para esses sites.

Este aplicativo é fornecido exclusivamente como uma ferramenta de automação para facilitar a criação de backups pessoais apenas para uso privado, com o único propósito de preservar o conteúdo para consultas futuras. Ele não tem a intenção de ser usado para violação de direitos autorais ou qualquer outra atividade ilegal.

### Agradecimentos
- À Oracle, pela linguagem Java.
- A todos os sites suportados, pelos seus incríveis bancos de dados de mangás online.
- A todos os patronos que apoiam este programa no [Patreon](https://www.patreon.com/redsquirrel87).

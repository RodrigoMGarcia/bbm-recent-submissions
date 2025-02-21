import requests
from bs4 import BeautifulSoup
import base64

# Função para coletar itens
def coletar_itens(url_base, itens_por_pagina=50, total_itens=100):
    itens = []
    offset = 0
    
    while len(itens) < total_itens:
        url = f"{url_base}?offset={offset}"
        print(f"Acessando: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Erro: Status {response.status_code}")
            break
        
        soup = BeautifulSoup(response.text, "html.parser")
        entradas = soup.find_all("div", class_="artifact-title")
        if not entradas:
            print("Nenhum item encontrado nesta página.")
            break
        
        for entrada in entradas:
            link_tag = entrada.find("a")
            if link_tag:
                titulo = link_tag.text.strip()
                link = link_tag["href"]
                full_link = f"https://digital.bbm.usp.br{link}"
                
                # Tentar encontrar o autor
                autor_div = entrada.find_next("span", class_="author")
                autor = autor_div.text.strip() if autor_div else "Autor não disponível"
                
                itens.append({"autor": autor, "titulo": titulo, "link": full_link})
        
        offset += 10
        if offset >= total_itens:
            break
    
    return itens[:total_itens]

# Função para gerar o HTML com paginação, estilização e imagem
def gerar_html(itens, nome_arquivo="index.html", itens_por_pagina=50):
    # Dividir itens em páginas
    paginas = [itens[i:i + itens_por_pagina] for i in range(0, len(itens), itens_por_pagina)]
    
    # Codificar a imagem em base64 com o caminho relativo
    with open("BBM_DIGITAL.png", "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Submissões Recentes - BBM</title>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 30px;
                background-color: #f5f5f5;
                color: #333;
            }}
            .header {{
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
            }}
            .header img {{
                height: 80px;
                margin-right: 20px;
            }}
            h1 {{
                color: #2c3e50;
                font-size: 2em;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            }}
            p {{
                text-align: center;
                font-size: 1.1em;
                color: #7f8c8d;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                background-color: #fff;
            }}
            th, td {{
                padding: 15px;
                border: 1px solid #ddd;
                text-align: left;
            }}
            th {{
                background-color: #3498db;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #ecf0f1;
            }}
            a {{
                color: #e74c3c;
                text-decoration: none;
                font-weight: 500;
            }}
            a:hover {{
                text-decoration: underline;
                color: #c0392b;
            }}
            .pagination {{
                text-align: center;
                margin: 20px 0;
            }}
            .pagination button {{
                padding: 10px 20px;
                margin: 0 5px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
            }}
            .pagination button:disabled {{
                background-color: #bdc3c7;
                cursor: not-allowed;
            }}
            .pagination button:hover:not(:disabled) {{
                background-color: #2980b9;
            }}
            .author {{
                font-style: italic;
                color: #666;
            }}
            /* Ajustar largura das colunas */
            th:nth-child(1), td:nth-child(1) {{ /* Coluna Autor */
                width: 25%; /* Mantido em 25% */
            }}
            th:nth-child(2), td:nth-child(2) {{ /* Coluna Título */
                width: 65%; /* Aumentado para 65% */
            }}
            th:nth-child(3), td:nth-child(3) {{ /* Coluna Link */
                width: 10%; /* Reduzido para 10% */
            }}
            @media (max-width: 600px) {{
                table, th, td {{
                    font-size: 0.9em;
                    padding: 10px;
                }}
                .header img {{
                    height: 60px;
                }}
                h1 {{
                    font-size: 1.5em;
                }}
                th:nth-child(1), td:nth-child(1) {{ width: 25%; }}
                th:nth-child(2), td:nth-child(2) {{ width: 60%; }}
                th:nth-child(3), td:nth-child(3) {{ width: 15%; }}
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <img src="data:image/png;base64,{img_base64}" alt="BBM Digital Logo">
            <h1>Submissões Recentes</h1>
        </div>
        <p>Mostrando até 50 itens por página</p>
    """
    
    # Adicionar tabelas para cada página
    for i, pagina in enumerate(paginas):
        display = "block" if i == 0 else "none"
        html += f"""
        <table id="pagina-{i}" style="display: {display};">
            <tr><th>Autor</th><th>Título</th><th>Link</th></tr>
        """
        for item in pagina:
            html += f"""
            <tr>
                <td><span class="author"><span>{item['autor']}</span></span></td>
                <td>{item['titulo']}</td>
                <td><a href='{item['link']}' target='_blank'>Acessar</a></td>
            </tr>
            """
        html += "</table>"
    
    # Adicionar controles de paginação
    html += """
        <div class="pagination">
            <button onclick="mudarPagina(-1)" id="anterior">Anterior</button>
            <span id="pagina-atual">Página 1 de """ + str(len(paginas)) + """</span>
            <button onclick="mudarPagina(1)" id="proxima">Próxima</button>
        </div>
        
        <script>
            let paginaAtual = 0;
            const totalPaginas = """ + str(len(paginas)) + """;
            
            function mudarPagina(direcao) {
                const novaPagina = paginaAtual + direcao;
                if (novaPagina >= 0 && novaPagina < totalPaginas) {
                    document.getElementById(`pagina-${paginaAtual}`).style.display = 'none';
                    document.getElementById(`pagina-${novaPagina}`).style.display = 'block';
                    paginaAtual = novaPagina;
                    
                    document.getElementById('pagina-atual').innerText = `Página ${paginaAtual + 1} de ${totalPaginas}`;
                    document.getElementById('anterior').disabled = paginaAtual === 0;
                    document.getElementById('proxima').disabled = paginaAtual === totalPaginas - 1;
                }
            }
            
            // Inicializar botões
            document.getElementById('anterior').disabled = true;
            document.getElementById('proxima').disabled = totalPaginas <= 1;
        </script>
    </body>
    </html>
    """
    
    with open(nome_arquivo, "w", encoding="utf-8") as arquivo:
        arquivo.write(html)
    print(f"Arquivo HTML gerado: {nome_arquivo} com {len(itens)} itens em {len(paginas)} páginas.")

# Executar
if __name__ == "__main__":
    url_base = "https://digital.bbm.usp.br/xmlui/recent-submissions"
    itens = coletar_itens(url_base, 50, 100)  # Coletar até 100 itens para 2 páginas
    gerar_html(itens)
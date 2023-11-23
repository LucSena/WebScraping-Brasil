from flask import Flask, render_template, request
from flask import jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Lista de lojas disponíveis
lojas = ['Filtro Loja', 'Mercado Livre', 'Magazine Luiza']

# Função para fazer scraping do Mercado Livre
def scrape_mercado_livre(pesquisa):
    produtos = []
    url = f"https://lista.mercadolivre.com.br/{pesquisa}"
    resposta = requests.get(url)
    soup = BeautifulSoup(resposta.text, 'html.parser')
    produtos_list = soup.find_all('li', class_='ui-search-layout__item')

    for produto in produtos_list:
        nome_produto_elemento = produto.find('h2', class_='ui-search-item__title')
        link_produto_elemento = produto.find('a', class_='ui-search-link')
        precos_produto_elemento = produto.find('div', class_='ui-search-price ui-search-price--size-medium')

        if nome_produto_elemento and precos_produto_elemento and link_produto_elemento:
            nome_produto = nome_produto_elemento.text
            imagem_produto = link_produto_elemento.img['data-src']

            precos = precos_produto_elemento.find_all('span', class_='andes-money-amount__fraction')
            if len(precos) > 1:
                preco_sem_desconto = precos[0].text
                preco_com_desconto = precos[1].text
            else:
                preco_sem_desconto = precos[0].text
                preco_com_desconto = None

            produtos.append({'nome': nome_produto + ' - Mercado Livre', 'preco_sem_desconto': preco_sem_desconto, 'preco_com_desconto': preco_com_desconto, 'imagem': imagem_produto})

    return produtos

# Função para fazer scraping da Magazine Luiza
def scrape_magazine_luiza(pesquisa):
    produtos = []
    url = f"https://www.magazineluiza.com.br/busca/{pesquisa}"
    resposta = requests.get(url)
    soup = BeautifulSoup(resposta.text, 'html.parser')
    produtos_list = soup.find_all('li', class_='sc-APcvf')

    for produto in produtos_list:
        img_produto_elemento = produto.find('img', {'data-testid': 'image'})
        info_produto = produto.find('div', {'data-testid': 'product-card-content'})

        if info_produto and img_produto_elemento:
            nome_produto_elemento = info_produto.find('h2', {'data-testid': 'product-title'})
            preco_produto_elemento = info_produto.find('p', {'data-testid': 'price-value'})
            preco_original_elemento = info_produto.find('p', {'data-testid': 'price-original'})

            if nome_produto_elemento and preco_produto_elemento and preco_original_elemento:
                nome_produto = nome_produto_elemento.text.strip()
                preco_produto = preco_produto_elemento.text.strip()
                preco_original = preco_original_elemento.text.strip()
                img_produto = img_produto_elemento['src']

                produtos.append({'nome': nome_produto + ' - Magazine Luiza', 'preco_sem_desconto': preco_original, 'preco_com_desconto': preco_produto, 'imagem': img_produto})

    return produtos

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', lojas=lojas)

@app.route('/pesquisar', methods=['POST'])
def pesquisar():
    produtos = []
    pesquisa = request.form.get('pesquisa')
    loja = request.form.get('loja')

    # Chama a função correspondente à loja escolhida
    if loja == 'Mercado Livre':
        produtos += scrape_mercado_livre(pesquisa)
    elif loja == 'Magazine Luiza':
        produtos += scrape_magazine_luiza(pesquisa)
    elif loja == 'Filtro Loja':
        produtos += scrape_mercado_livre(pesquisa) + scrape_magazine_luiza(pesquisa)

    return jsonify(produtos=produtos)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

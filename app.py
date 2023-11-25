from flask import Flask, render_template, request
from flask import jsonify
import requests
import random
from bs4 import BeautifulSoup

app = Flask(__name__)

# Lista de lojas disponíveis
lojas = ['Filtro Loja', 'Mercado Livre', 'Magazine Luiza', 'Amazon']

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

        produtos.append({
            'nome': nome_produto,
            'preco_sem_desconto': preco_sem_desconto,
            'preco_com_desconto': preco_com_desconto,
            'imagem': imagem_produto,
            'loja': 'Mercado Livre',
            'cor': '#f6aa1d',
            'link': link_produto_elemento['href']  # Adicione esta linha para obter o link do produto
        })

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
        link_produto_elemento = produto.find('a', {'data-testid': 'product-card-container'})

        if info_produto and img_produto_elemento:
            nome_produto_elemento = info_produto.find('h2', {'data-testid': 'product-title'})
            preco_produto_elemento = info_produto.find('p', {'data-testid': 'price-value'})
            preco_original_elemento = info_produto.find('p', {'data-testid': 'price-original'})

            if nome_produto_elemento and preco_produto_elemento and preco_original_elemento:
                nome_produto = nome_produto_elemento.text.strip()
                preco_produto = preco_produto_elemento.text.strip()
                preco_original = preco_original_elemento.text.strip()
                img_produto = img_produto_elemento['src']

            produtos.append({
                'nome': nome_produto,
                'preco_sem_desconto': preco_original,
                'preco_com_desconto': preco_produto,
                'imagem': img_produto,
                'loja': 'Magazine Luiza',
                'cor': 'blue',
                'link': f"https://www.magazineluiza.com.br{link_produto_elemento['href']}"
            })

    return produtos

# def scrape_amazon(pesquisa):
#  url = f"https://www.amazon.com.br/s?k={pesquisa}"
#  error_message = None

#  try:
#     # Fazendo a requisição para a página
#     resposta = requests.get(url)

#     # Verificando se a requisição foi bem-sucedida
#     resposta.raise_for_status()

#     soup = BeautifulSoup(resposta.text, 'html.parser')
#     produtos_list = soup.find_all('div', {'class': 's-asin'})

#     produtos = []
#     for produto in produtos_list:
#         # Obtendo o Nome do Produto
#         product_name_element = produto.find('span', {'class': 'a-size-base-plus'})
#         if product_name_element:
#             product_name = product_name_element.text.strip()
#         else:
#             # Se o nome do produto não estiver disponível, você pode tratar isso da maneira que preferir
#             product_name = "Nome não disponível"

#         # Obtendo o Preço do Produto
#         price_element = produto.find('span', {'class': 'a-price'})
#         if price_element:
#             product_price = price_element.find('span', {'class': 'a-offscreen'}).text.strip()
#         else:
#             # Se o preço do produto não estiver disponível, você pode tratar isso da maneira que preferir
#             product_price = "Preço não disponível"

#         # Obtendo o Preço Original (sem promoção) se estiver presente
#         original_price_element = produto.find('span', {'class': 'a-text-price'})
#         if original_price_element:
#             original_price = original_price_element.find('span', {'class': 'a-offscreen'}).text.strip()
#         else:
#             # Se o preço original do produto não estiver disponível, você pode tratar isso da maneira que preferir
#             original_price = "Preço original não disponível"

#         # Obtendo a Imagem do Produto
#         image_element = produto.find('img', {'class': 's-image'})
#         if image_element:
#             product_image = image_element['src']
#         else:
#             # Se a imagem do produto não estiver disponível, você pode tratar isso da maneira que preferir
#             product_image = "Imagem não disponível"

#         # Obtendo o Link do Produto
#         link_element = produto.find('a', {'class': 'a-link-normal'})
#         if link_element:
#             product_link = 'https://www.amazon.com.br' + link_element['href']
#         else:
#             # Se o link do produto não estiver disponível, você pode tratar isso da maneira que preferir
#             product_link = "Link não disponível"
#         # Adicionando os detalhes do produto à lista de produtos
#         produtos.append({
#             'nome': product_name,
#             'preco_sem_desconto': original_price,
#             'preco_com_desconto': product_price,
#             'imagem': product_image,
#             'loja': 'Amazon',
#             'cor': '#a6611e',
#             'link': product_link
#         })

#  except requests.exceptions.HTTPError as errh:
#     if resposta.status_code == 503:
#         # Adicione um tratamento para indicar um erro 503
#         error_message = {
#             'error': 'Amazon está temporariamente indisponível. Tente novamente mais tarde.'
#         }
#         return {'error': error_message, 'status': resposta.status_code}
#     else:
#         print(f"Erro HTTP: {errh}")
#  except requests.exceptions.ConnectionError as errc:
#     print(f"Erro de Conexão: {errc}")
#  except requests.exceptions.Timeout as errt:
#     print(f"Erro de Timeout: {errt}")
#  except requests.exceptions.RequestException as err:
#     print(f"Erro ao acessar a página: {err}")

#  return {'produtos': produtos, 'error': error_message, 'status': resposta.status_code if resposta else None}


def scrape_amazon(pesquisa):
    produtos = []
    url = f"https://www.amazon.com.br/s?k={pesquisa}"
    resposta = requests.get(url)
    soup = BeautifulSoup(resposta.text, 'html.parser')
    produtos_list = soup.find_all('div', {'class': 's-asin'})

    for produto in produtos_list:
        # Obtendo o Nome do Produto
        product_name_element = produto.find('span', {'class': 'a-size-base-plus'})
        if product_name_element:
            product_name = product_name_element.text.strip()
        else:
            # Se o nome do produto não estiver disponível, você pode tratar isso da maneira que preferir
            product_name = "Nome não disponível"

        # Obtendo o Preço do Produto
        price_element = produto.find('span', {'class': 'a-price'})
        if price_element:
            product_price = price_element.find('span', {'class': 'a-offscreen'}).text.strip()
        else:
            # Se o preço do produto não estiver disponível, você pode tratar isso da maneira que preferir
            product_price = "Preço não disponível"

        original_price_element = produto.find('span', {'class': 'a-text-price'})
        if original_price_element:
            original_price = original_price_element.find('span', {'class': 'a-offscreen'}).text.strip()
        else:
            # Se o preço original do produto não estiver disponível, pule para o próximo produto
            continue

        # Obtendo a Imagem do Produto
        image_element = produto.find('img', {'class': 's-image'})
        if image_element:
            product_image = image_element['src']
        else:
            # Se a imagem do produto não estiver disponível, você pode tratar isso da maneira que preferir
            product_image = "Imagem não disponível"

        # Obtendo o Link do Produto
        link_element = produto.find('a', {'class': 'a-link-normal'})
        if link_element:
            product_link = 'https://www.amazon.com.br' + link_element['href']
        else:
            # Se o link do produto não estiver disponível, você pode tratar isso da maneira que preferir
            product_link = "Link não disponível"

        # Adicionando os detalhes do produto à lista de produtos
        produtos.append({
            'nome': product_name,
            'preco_sem_desconto': original_price,
            'preco_com_desconto': product_price,
            'imagem': product_image,
            'loja': 'Amazon',
            'cor': 'orange',  # Você pode escolher a cor desejada
            'link': product_link
        })

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
    elif loja == 'Amazon':
        produtos += scrape_amazon(pesquisa)
    elif loja == 'Filtro Loja':
        produtos += scrape_mercado_livre(pesquisa) + scrape_magazine_luiza(pesquisa) + scrape_amazon(pesquisa)
        random.shuffle(produtos)

    return jsonify(produtos=produtos)

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)

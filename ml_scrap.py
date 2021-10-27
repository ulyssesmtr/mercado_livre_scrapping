from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
import pandas as pd

response = urlopen('https://lista.mercadolivre.com.br/peso#D[A:peso]')
html = response.read().decode('utf-8')
soup = BeautifulSoup(html, 'html.parser')
products = soup.findAll('li', class_='ui-search-layout__item')

pages = soup.find('li', class_='andes-pagination__page-count').get_text().split()[1]
max_id = int(pages) * 50 + 2

products_list = []

for i in range(1, max_id, 50):
    print(i)
    if i == 1:
        index_fix = -1
    else:
        index_fix = 0
    response = urlopen('https://lista.mercadolivre.com.br/peso_Desde_' + str(i+index_fix) + '_NoIndex_True')
    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')
    products = soup.findAll('li', class_='ui-search-layout__item')
    for product in products:
        item = {}
        name = product.find('h2', class_='ui-search-item__title').get_text()
        item['name'] = name
        price = product.find('span', class_='price-tag-amount').get_text()[2:].replace(',', '.')
        if price.count('.') > 1:
            aux_list = list(price)
            aux_list.remove('.')
            price = ''.join(aux_list)
        item['price'] = float(price)
        try:
            shipping = product.find('p', class_='ui-search-item__shipping').get_text().replace('Frete grátis', 'Free')
            item['shipping'] = shipping
        except AttributeError:
            item['shipping'] = 'Paid'
        products_list.append(item)

output_df = pd.DataFrame(products_list)
free_shipping_count = output_df.shipping.value_counts().Free
paid_shipping_count = output_df.shipping.value_counts().Paid
new_row = {'name': '', 'price': f'Average Price: {output_df["price"].mean()}', 'shipping': f'Paid: {paid_shipping_count} - Free: {free_shipping_count}'}
output_df = output_df.append(new_row, ignore_index=True)
output_df.to_csv('product_list.csv', sep=';', index=False, encoding='utf-8-sig')


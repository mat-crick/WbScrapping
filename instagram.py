import scrapy
from scrapy.conf import settings
import pandas as pd
import requests
from bs4 import BeautifulSoup

class InstagramSpider(scrapy.Spider):
    name = "instagram"
    
    brands = {
        'Chanel': 'https://www.instagram.com/chanelofficial/?hl=en',
        'Hermes': 'https://www.instagram.com/hermes/?hl=en',
        'Gucci': 'https://www.instagram.com/gucci/?hl=en',
        'Dior': 'https://www.instagram.com/dior/?hl=en',
        'Prada': 'https://www.instagram.com/prada/'
    }
    
    start_date = '2013-01-01'
    end_date = '2023-04-30'

    def start_requests(self):
        for brand, url in self.brands.items():
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(brand=brand))
    

    def parse(self, response, brand):
        print(f"Scraping {brand}'s Instagram page...")
        script = response.xpath('//script[contains(text(),"sharedData")]/text()').extract_first()
        pattern = r"window\._sharedData\s*=\s*({.*?});"
        match = re.search(pattern, script)
        if not match:
            return []
        data = json.loads(match.group(1))
        posts = data['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
        filtered_posts = []
        for post in posts:
            date = post['node']['taken_at_timestamp']
            if self.start_date <= pd.to_datetime(date, unit='s').strftime('%Y-%m-%d') <= self.end_date:
                filtered_posts.append(post)
        for post in filtered_posts:
            yield {
                'brand': brand,
                'id': post['node']['id'],
                'link': f"https://www.instagram.com/p/{post['node']['shortcode']}",
                'image_link': post['node']['display_url'],
                'publication_date': pd.to_datetime(post['node']['taken_at_timestamp'], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
                'caption': post['node']['edge_media_to_caption']['edges'][0]['node']['text'],
                'likes': post['node']['edge_media_preview_like']['count'],
                'comments': post['node']['edge_media_to_comment']['count']
            }
            
    def closed(self, reason):
        # Write the scraped data to a CSV file
        df = pd.DataFrame(self.items)
        df.to_csv('post_data.csv', index=False, encoding='utf-8')
        # Write the total number of posts to a CSV file
        df2 = df.groupby('brand')['id'].count().reset_index()
        df2.columns = ['Brand Name', 'Number of Posts']
        df2.to_csv('total_posts_by_brand.csv', index=False)
        print('Scraping completed successfully!')
       
    ____________________________________________________________________________________________________________________________________
    
    
    
def brand_information(brand):
    url = f'https://www.instagram.com/{brand}/'

    # Send a GET request to the Instagram URL
    r = requests.get(url)

    # Use BeautifulSoup to parse the HTML content
    soup = BeautifulSoup(r.content, 'html.parser')

    # Extract the brand information
    brand_name = soup.find('h1', {'class': 'rhpdm'}).text
    num_followers = int(soup.find_all('span', {'class': 'g47SY'})[1]['title'].replace(',', ''))
    num_following = int(soup.find_all('span', {'class': 'g47SY'})[2].text.replace(',', ''))
    num_posts = int(soup.find_all('span', {'class': 'g47SY'})[0].text.replace(',', ''))

    print("Brand name:", brand_name)
    print("Number of followers:", num_followers)
    print("Number of following:", num_following)
    print("Number of posts:", num_posts)


# Scrape the hashtags for each luxury brand
brand_information('chanelofficial')
brand_information('hermes')
brand_information('gucci')
brand_information('dior')
brand_information('prada')
    
    
    
    

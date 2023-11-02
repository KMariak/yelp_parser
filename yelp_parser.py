import scrapy
from urllib.parse import quote

search = "Takeout"  # Here enter description
location = "Atlanta, GA"  # Here enter location

encoded_search = quote(search)
encoded_location = quote(location)


class YelpSpider(scrapy.Spider):
    name = 'yelp_spider'
    start_urls = [f'https://www.yelp.com/search?find_desc={encoded_search}&find_loc={encoded_location}']

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,)

    def parse(self, response, **kwargs):
        for link in response.css('h3.css-1agk4wl'):
            yelp_href = link.css('a.css-19v1rkv::attr(href)').get()
            yelp_url = f'https://www.yelp.com{yelp_href}'
            print(f'Here link: {yelp_url}')

            yield scrapy.Request(yelp_url, callback=self.parse_business_page)

    def parse_business_page(self, response):
        global review_info
        business_name = response.css('h1.css-1se8maq::text').get()
        reviews_count = response.css('a.css-19v1rkv::text').get()
        rating = response.css('span.css-1fdy0l5::text').get()
        website_link = response.css('a.css-1idmmu3::attr(href)').get()
        reviews = response.xpath('//*[@id="reviews"]/section/div[2]/ul/li[position() <= 5]/div')

        for review in reviews:
            reviewer_name = review.xpath('.//a/text()').get()
            reviewer_location = review.xpath('.//span/text()').get()
            review_date = review.xpath('.//div/span/text()').get()

            review_info = {
                'Reviewer Name': reviewer_name,
                'Reviewer Location': reviewer_location,
                'Review Date': review_date
            }

        yield {
            'Business name': business_name,
            'Business rating': rating,
            'Number of reviews': reviews_count,
            'Business website': website_link,
            'Reviewers': review_info,
            }
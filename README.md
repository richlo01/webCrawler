# Web Crawler
I worked with a group to scrape the UCI Information and Computer Science Repository. The main code is in scraper.py. We started with a seed URL and extracted its HTML for 
important text in specfic headings. This was also the way we extracted the next url. Additionally, we did some text processing such as stemming to make our index stronger. 
To avoid duplicate documennts, we introduced the use of SimHash.

<br/> To show some of the results, here are the following:
<p align="center">
          <img src="https://user-images.githubusercontent.com/47437080/121439231-5c5fcb00-c93a-11eb-8588-3ee44ba77f50.png" alt="drawin" width="500">
</p>

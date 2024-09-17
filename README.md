# Web Scraping Script for Product Data Extraction
This Python script scrapes product information from the website gojersey.co, specifically targeting a category page and retrieving details for each product, including title, images, video links, and attributes like league, team, and more. The collected data is then saved in a CSV format suitable for WooCommerce imports.

Features
Category Scraping: Navigate through product category pages to extract product links.
Product Details Extraction: Gather product-specific information such as:
Title
Main Image & Gallery Images
Video URL (if available)
Product categories like league, team, and product type
Additional attributes such as material, logo type, and design year.
Data Export: Export all collected product data into a CSV file for each page, structured in a format compatible with WooCommerce.

Purpose
I created this script to automate the process of extracting product information from the gojersey.co website. Managing a large catalog of products for e-commerce can be time-consuming, so this tool simplifies the task by collecting product data and exporting it in a WooCommerce-compatible format. This saves hours of manual data entry and ensures consistency across product listings.

Requirements
Python 3.x

Required Libraries: Install these libraries using pip:
pip install requests beautifulsoup4

How to Use
Clone the repository:
git clone https://github.com/your-username/repository-name.git
cd repository-name

Run the script:
python scrape.py
By default, the script starts scraping from page 1 of the category.

Modify Starting Page: To start scraping from a specific page number, pass the start_page parameter to the start_scraping function:

python
start_scraping(start_page=2)
CSV Output: The scraped data is saved as prodotti_woocommerce_pagina_X.csv where X is the page number. Each CSV contains the following columns:
Title
Main Image
Gallery Images (separated by |)
Video
Categories
Model Year
Country and League
Material
Type of Brand Logo
Type of Team Badge
Color
Version
Designed For


Configuration
You can adjust the following settings:

Headers: Customize the User-Agent in the headers dictionary if needed.
Delay Between Requests: The script pauses for 5 seconds between product page requests to avoid server overload. You can modify this in the time.sleep(5) statement.
Base URLs: Update base_url and start_url variables to scrape a different category or domain.

Important Notes
Legal Disclaimer: Ensure that you have permission to scrape the targeted website, and check its robots.txt file for scraping policies. Scraping without permission may lead to IP blocks or legal issues.


Dependencies
Install all required Python packages:
pip install requests beautifulsoup4

License
This project is licensed under the MIT License.





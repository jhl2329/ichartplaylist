from urllib.request import urlopen
from bs4 import BeautifulSoup

def main():

	html = urlopen("http://www.instiz.net/iframe_ichart_score.htm")

	soup = BeautifulSoup(html, 'html.parser')

	# # print(soup.prettify())
	# rankingPage = soup.find(rel="amphtml")
	# print(rankingPage.get('href'))

	# html = urlopen(rankingPage.get('href'))
	# soup = BeautifulSoup(html, 'html.parser')

	print(soup.prettify())


if __name__ == '__main__':
	main()
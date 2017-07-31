from urllib.request import urlopen
from bs4 import BeautifulSoup

def main():

	html = urlopen("http://www.instiz.net/iframe_ichart_score.htm")

	soup = BeautifulSoup(html, 'html.parser')

	divList = soup.find_all('div', {"class": "ichart_score2_song1"})
	for song in divList:
		print(song)


if __name__ == '__main__':
	main()
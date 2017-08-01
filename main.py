from urllib.request import urlopen
from bs4 import BeautifulSoup

def getSongList():
	"""
	Parses through DOM of instiz song list and returns a list of songs

	:return: a list of Strings in order of popularity for that day
	"""

	html = urlopen("http://www.instiz.net/iframe_ichart_score.htm")

	soup = BeautifulSoup(html, 'html.parser')

	songList = []
	divList = soup.find_all('div', class_="ichart_score2_song1")
	for song in divList:
		songList.append(song.string)
	return songList

def main():
	songList = getSongList()
	print(songList)


if __name__ == '__main__':
	main()
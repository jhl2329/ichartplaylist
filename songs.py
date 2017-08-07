from urllib.request import urlopen
from bs4 import BeautifulSoup

def get_song_list(*args, **kwargs):
	"""
	Parses through DOM of instiz song list and returns a list of songs

	:return: a list of Strings in order of popularity for that day
	"""

	html = urlopen("http://www.instiz.net/iframe_ichart_score.htm")

	soup = BeautifulSoup(html, 'html.parser')

	song_list = []
	divList = soup.find_all('div', class_="ichart_score2_song1")
	for song in divList:
		print('Found song: ', song.string)
		song_list.append(song.string)

	artist_list = []
	div_list = soup.find_all('div', class_="ichart_score2_artist1")
	for artist in div_list:
		artist_list.append(artist.string)

	# Combine two lists together so that each element will have song title + artist	
	new_list = [a + ' ' + b for a, b in zip(song_list, artist_list)]
	return new_list

def main():
	song_list = get_song_list()
	print(song_list)


if __name__ == '__main__':
	main()
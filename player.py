from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from difflib import SequenceMatcher
import sys
import time
import csv
import random


class BandCamp:

	def discover(self, page=0):
		try:
			self.driver = webdriver.Chrome()
			self.driver.get(f'https://bandcamp.com/?g=jazz&s=top&p={page}&gn=0&f=all&t=fusion')
			items = self.driver.find_elements_by_class_name('discover-item')
			rank = random.randint(0, len(items)-1)
			x = items[rank]
			a = x.find_element_by_tag_name('a')
			self.driver.execute_script("arguments[0].click();", a)
		except Exception as e:
			print('In driver:', e)

		WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.LINK_TEXT, "hear more"))).click()

		table = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.ID, "track_table")))

		tr_len = None
		try:
			tracks = table.find_elements_by_class_name('track_row_view')
			tr = tracks[random.randint(0, len(tracks)-1)]
			song = tr.find_elements_by_class_name('play-col')[0]
			sl = song.find_element_by_tag_name('a')
			sl.click()
			dis = tr.find_elements_by_class_name('disabled')
			print('dis', len(dis), dis)
			if dis:
				raise Exception('Song link Disabled')
			title = tr.find_elements_by_class_name('track-title')[0].text
			tr_len = tr.find_elements_by_class_name('time')[0].text
			print(title, f'\nTrack length : {tr_len}')
		except Exception as e:
			print('In album:', e)
			self.driver.quit()
			return

		try:
			dt = date.today() # YYYY-MM-DD
			self.write_csv([[title, rank, dt, tr_len]])
		except Exception as e:
			print('In writing csv:', e)
		if tr_len:
			try:
				m, s = tr_len.split(':')
				sec = 60*(int(m))+int(s)
				print(f'Gonna play for {sec} seconds.')
				time.sleep(sec)
			except Exception as e:
				print('In playing song:', e)
				time.sleep(30)
		else:
			time.sleep(30)
		self.driver.quit()


	def write_csv(self, rows):
		empty = False
		try:
			with open('band_data.csv', 'r') as fr:
				csv_dict = [row for row in csv.DictReader(fr)]
				if len(csv_dict) == 0:
					empty = True
		except:
			pass

		with open('band_data.csv', 'a+') as fw:
			csvw = csv.writer(fw)
			if empty:
				print('File was empty till now.')
				csvw.writerow(['Title', 'Rank', 'Date', 'Track Length'])  
			csvw.writerows(rows) 


	def query_songs(self, title=''):
		if title == '':
			return 'Please mention the song name.'
		with open('band_data.csv', 'r') as fr:
			csv_dict = [row for row in csv.DictReader(fr)]
		rel = []
		for x in csv_dict:
			if x['Title'].lower() == title.lower():
				#print(f'Song {title} found')
				rel.append(x)
			elif title.lower() in x['Title'].lower():
				rel.append(x)
			else:
				if SequenceMatcher(None, title.lower(), x['Title'].lower()).ratio() > 0.8:
					rel.append(x)
		return rel


	def playlist(self, pl=''):
		with open('band_data.csv', 'r') as fr:
			csv_dict = [row for row in csv.DictReader(fr)]
		play = {'Title': ['Count', 'Track Length']}
		for x in csv_dict:
			if x['Title'] == 'Title':
				continue
			if not play.get(x['Title']):
				play[x['Title']] = [1, x['Track Length']]
			else:
				print(type(play[x['Title']][0]), play[x['Title']])
				play[x['Title']][0] += 1

		pl = 'Playlist'+str(pl)
		pl_file = f'{pl}.csv'
		with open(pl_file, 'w') as fw:
			csvw = csv.writer(fw)
			csvw.writerows(play.items()) 
		return play


# Main

if __name__ == '__main__':
	reg = [f"'0'  to exit", f"'1 [page_number]'  for playing a song", f"'2 SongName'  to query for a song in the csv file", f"'3 [playlist_name]'  to create a playlist\n"]
	for x in reg:
		print(x)

	con = True
	while con:
		obj1 = BandCamp()
		print('\nEnter request in the format:')
		inp = input('Integer [argument]\n\n')
		inp = inp.split()
		if inp[0] == '0':
			con = False
			print('Exiting...')
		elif inp[0] == '1':
			if len(inp) == 2:
				obj1.discover(inp[1])
			elif len(inp) == 1:
				obj1.discover()
			else:
				print('Please give a correct input for discover function.')
		elif inp[0] == '2':
			if len(inp) >= 2:
				nm = ' '.join([x for x in inp[1:]])
				rel = obj1.query_songs(nm)
				print(f'{len(rel)} related songs found.')
				print(rel)
			else:
				print('Will need a name to query a song.')
		elif inp[0] == '3':
			if len(inp) == 2:
				p = obj1.playlist(inp[1])
			elif len(inp) == 1:
				p = obj1.playlist()
			else:
				print('Please give a correct input to create a playlist.')
			try:
				print(p)
			except:
				pass
		else:
			print('Incorrect Request')

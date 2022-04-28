import json

my_array = []

with open('cenz.txt', encoding='utf-8') as r:
	for i in r:
		n = i.lower().split('\n')[0]
		if n != '':
			my_array.append(n)


with open('cenz.json', 'w', encoding='utf-8') as e:
	json.dump(my_array, e)
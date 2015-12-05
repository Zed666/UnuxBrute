#!/usr/bin/python
# -*- coding: utf-8 -*-

#Модули
import time;
import argparse;
import crypt;
import threading;
import queue;
import curses;
import time; 
import random;

#Функция которая выводит прогрессбар
def bar(proshlo, vsego, dlinas):
	pr = int((proshlo * 100) / vsego);
	dlinas -= 45;  
	dlina = int(((dlinas) / 100) * pr);
	spase = int((dlinas - dlina)); 
	st = str(pr) + "% [" + ">" * dlina + " " * spase + "]";
	return(st);

#Обьект вывода таблицы
class PrintedTable():

	def __init__(self, ShadowFile, DicFile, Workers, DicLen, ShadowLen): 
		#Имя файла шо брутим
		self.ShadowFileName = ShadowFile
		#Имя словаря
		self.DicFileName = DicFile;
		#Гениратор, словаря где потоки
		self.PrintedWorkers = {0:"None" for x in range(POTOKOV)};
		#Длинна словаря
		self.DicLen = DicLen;
		#Сбрученные
		self.DoneCracked = {};
		#Количество хэшей для брута
		self.ShadowLenSize = ShadowLen;

	#Метод в котором добавляем/обновляем в словарь значение потока 
	def AddWorkerValue(self, Worker, Value):
		self.PrintedWorkers[Worker] = Value;
	#Метод добавления сбрученного логина и пасса
	def AddCrackedPassword(self, UserLogin,CrackedPass):
		self.DoneCracked[UserLogin] = CrackedPass;

	#Печатаем всю таблицу   
	def PrintTable(self):
		screen.clear();
		screen.addstr(0, 0, "-" * dims[1]);
		screen.addstr(1, center - len("Shadow Bruter"), "Shadow Bruter", curses.color_pair(1));
		screen.addstr(2, 0, "-" * dims[1]);
		screen.addstr(3, 0,"Shadow File: " + str(self.ShadowFileName), curses.color_pair(2));
		screen.addstr(4, 0,"Dictionary File: " + str(self.DicFileName), curses.color_pair(2));
		screen.addstr(5, 0,"Cracked : " + str(len(self.DoneCracked)) + " / " + str(self.ShadowLenSize));
		screen.addstr(6, 0, "-" * dims[1]);
		for f in range(len(self.PrintedWorkers)):
			WorkerData = self.PrintedWorkers[f].split(":");
			screen.addstr(f+7, 0, WorkerData[0] + " / " + WorkerData[1] + " / " + str(self.DicLen) + " / "  + str(bar(int(WorkerData[1]), self.DicLen, dims[1])), curses.A_BOLD);
		screen.refresh();

#Процедура крека
def cracking(ShadowList, WordList, i):
	while True:
		#Берем 1 строку из очереди
		ShadowLine = ShadowList.get();
		#Выдираем тип хэша
		HashType = ShadowLine[1].split("$")[1];   
		#Выдираем соль
		Salt = ShadowLine[1].split("$")[2]; 
		#Собираем в строку тип хэша и соль    
		HashSalt = "$" + HashType + "$" + Salt + "$";
		#Получаем имя пользователя 
		UserLogin = ShadowLine[0]; 
		#Начинаем перебор всех слов
		for n in range(len(WordList)): 
			#Удаляем конец строки
			Word = WordList[n].strip('\n');
			#Вызываем блокировку
			Lock.acquire();
			#Добавляем в обьект таблица, номер потока и Логин:Количество сбрученных строк 
			Table.AddWorkerValue(i, UserLogin + ":" + str(n)); 
			#Печатаем таблицу  
			Table.PrintTable();
			#Убираем блокировку
			Lock.release();
			#Хэшируем
			CryptWord = crypt.crypt(Word, HashSalt);
			#Если хэш подходит то
			if (CryptWord == ShadowLine[1]):
				#Опять вызываем блокировку
				Lock.acquire();
				#Добавляем в словарь, логин и его сбрученный пасс 
				Table.AddCrackedPassword(UserLogin, Word);
				#Убираем блокировку
				Lock.release();
				#Если найдено то прекращаем перебирать
				break;
		#Ждем завершения
		curses.endwin();
		ShadowList.task_done();  

def main():
	#Создаем парсер
	parse = argparse.ArgumentParser(description='Простой многопоточный брут /etc/shadow .')
	#Добавляем опцию, путь к файлу паролей
	parse.add_argument('-f', action='store', dest='sha', help='Путь к файлу паролей, пример: \'/etc/shadow\'');
	#Добавляем путь к словарю
	parse.add_argument('-d', action='store', dest='dic', help='Путь к файлу словаря, пример: \'/dic.txt\'');
	#Получаем аргументы
	args = parse.parse_args();
	#Если аргументов нет то
	if (args.sha == None) or (args.dic == None):
		#Выводим хэлп
		curses.endwin();
		print (parse.print_help());
		#Выход
		exit();
	#Иначе, если аргументы есть то
	else:
		#Создаем очередь
		ShadowList = queue.Queue(); 
		#Открываем файл с хэшми
		ShadowFile = open(args.sha,'r');
		#Читаем построчно файл
		for ShadowString in ShadowFile.readlines():
			#Удаляем перенос строки и делим по :
			ShadowString = ShadowString.replace("\n","").split(":");
			#Если пользователь с паролем то
			if  not ShadowString[1] in [ 'x', '*','!' ]:
				#Добавляем в очередь
				ShadowList.put(ShadowString);
		#Закрываем файл
		ShadowFile.close();
	#Заполняем список словами для брута
		WordList = open(args.dic).read().splitlines();
		#Глобальная переменная количество потоков 
		global POTOKOV;
		#Получаем количество потоков как случайное число, между 1 и длинной очереди
		POTOKOV = random.randint(1, ShadowList.qsize());        
		#Глобальный обьект талица, используется для вывода
		global Table;
		#Обьект принимает, Имя Шадов файла, Имя словаря, Количество потоков, Длинна словаря для брта, длинна очереди
		Table = PrintedTable(args.sha, args.dic, POTOKOV, len(WordList), ShadowList.qsize());
	#Создаем и запускаем потоки
		for i in range(POTOKOV):
			Worker = threading.Thread(target=cracking, args=(ShadowList, WordList, i));
			Worker.setDaemon(True);
			Worker.start();
		#Ждем их завершения
		ShadowList.join();
		#Когда, все сбрутиццо то выводим словарь то что сбрутилось
		for key, value in Table.DoneCracked.items():
			print(key, value)

#Если имя модуля майн то 
if __name__=="__main__":
	#Список со словами для брута
	WordsList = [];
	#Глобальный обьект блокировки, для записи в таблицу, надо блочить чтоб потоки не передрались
	Lock = threading.Lock();
	#Тут создаем экран курсес
	screen = curses.initscr();
	curses.start_color();
	curses.use_default_colors();
	dims = screen.getmaxyx();
	#Получаем центр экрана
	center = int(dims[1]/2);
	#Создаем цвета для вывода
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK);
	curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK);
	main();

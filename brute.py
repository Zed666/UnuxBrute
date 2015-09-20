#!/usr/bin/python
# -*- coding: utf-8 -*-


#Модули
import time;
import argparse;
import crypt;
import Queue;
from threading import Thread;



#Процедура крека
def cracking(UserPassW, WordList, i):
    while True:
        #Берем из очереди имя пользователя
        Name = UserPassW.get();
	#Выдираем тип хэша
	ctype = UserPassHash[Name].split("$")[1];
	#Выдираем соль
	salt = UserPassHash[Name].split("$")[2];
	#Собираем все вместе
	insalt = "$" + ctype + "$" + salt + "$";
	#Если тип хэша 6 то это SHA-512
	if ctype == "6":
		print "[+] Поток - " + str(i) + " " + Name + " тип хэша SHA-512 найдэн ...\n";
	#Если тип хэша 1 то это MD5
	if ctype == "1":
		print "[+] Поток - " + str(i) + " " + Name + " тип хэша MD5 найдэн... " + UserPassHash[Name] +"\n";
	#Если тип хэша 5 то это SHA-1
	if ctype == "5":
		print "[+] Поток - " + + str(i) + " " + Name + " тип хэша SHA-1 найдэн ...\n";
	for word in WordList:
            #Удалям перенос строки
	    word=word.strip('\n');
	    #Хэшируем
	    cryptWord = crypt.crypt(word, insalt);
	    #Сравниваем и выводим на консоль
	    if (cryptWord == UserPassHash[Name]):
	        print "[+] Найдэн !: " + Name + " ====> " + word + "\n";
		#Если найдено то прекращаем перебирать
		break;
	#Ждем завершения
        UserPassW.task_done();		
            
#Главная функция
def main():
    #Создаем парсер
    parse = argparse.ArgumentParser(description='Простой брут /etc/shadow .')
    #Добовляем опцию, путь к файлу паролей
    parse.add_argument('-f', action='store', dest='path', help='Путь к файлу паролей, пример: \'/etc/shadow\'');
    #Добовляем путь к словарю
    parse.add_argument('-d', action='store', dest='dic', help='Путь к файлу словаря, пример: \'/dic.txt\'');
    #Получаем аргументы
    args = parse.parse_args();
    #Если аргументов нет то
    if (args.path == None) or (args.dic == None):
        #Выводим хэлп
        print parse.print_help();
        #Выход
        exit();
    #Иначе, если аргументы есть то
    else:
 	#Создаем очередь
    	UserPass = Queue.Queue(); 
	#Открываем файл с пассами
        passFile = open(args.path,'r');
        #Читаем построчно файл
        for line in passFile.readlines():
            #Удаляем перенос строки и делим по :
            line = line.replace("\n","").split(":");
            #Если хэш есть то
            if  not line[1] in [ 'x', '*','!' ]:
                #Передаем в функцию крека
                #cracking(line[1], line[0], args.dic);
		#Наполняем словарь		
		UserPassHash[line[0]] = line[1];
		#Добовляем имя пользователя в очередь
		UserPass.put(line[0]);
	#Закрываем файл	
	passFile.close();
	#Заполняем список словами для брута
	WordList = open(args.dic).read().splitlines();
	#----------------------------------------------------
	#Заполнили очередь и словарь
	#----------------------------------------------------	    		  	
	#Создаем и запускаем потоки
	for i in range(3):
		WK = Thread(target=cracking, args=(UserPass, WordList, i));
		WK.setDaemon(True);
		WK.start();
    #Ждем их завершения
    UserPass.join();
	
	
#Если имя модуля майн то 
if __name__=="__main__":
		
    #Список со словами для брута
    WordList = [];			
    #Глобальный словарь с именами пользователей и хэшами 	
    UserPassHash = {}; 
    #Вызываем соответствующию функцию
    main();

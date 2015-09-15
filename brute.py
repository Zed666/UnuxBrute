#!/usr/bin/python
# -*- coding: utf-8 -*-


#Модули
import argparse;
import crypt;


#Процедура крека
def cracking(hashpas, username, dictionary):
    #Открываем файл со словарем
    dic = open (dictionary,'r');
    #Смотрим тип хэша
    ctype = hashpas.split("$")[1];
    
   #Если тип хэша 6 то это SHA-512
    if ctype == "6":
        print "[+] " + username + " тип хэша SHA-512 найдэн ...";
    
    #Если тип хэша 1 то это MD5
    if ctype == "1":
	print "[+] " + username + " тип хэша MD5 найдэн ...";
    #Если тип хэша 5 то это SHA-1
    if ctype == "5":
	print "[+] " + username + " тип хэша SHA-1 найдэн ...";	
		
	
    #Выдираем соль
    salt = hashpas.split("$")[2];
    #Собираем все вместе
    insalt = "$" + ctype + "$" + salt + "$";
    #Проходим по словарю
    for word in dic.readlines():
    	#Удалям перенос строки
    	word=word.strip('\n');
        #Хэшируем
        cryptWord = crypt.crypt(word, insalt);
        #Если хэши совпали то
        if (cryptWord == hashpas):
        	print "[+] Найдэн !: " + username + " ====> " + word + "\n";
	
	
            
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
        #Открываем файл с пассами
        passFile = open (args.path,'r');
        #Читаем построчно файл
        for line in passFile.readlines():
            #Удаляем перенос строки и делим по :
            line = line.replace("\n","").split(":");
            #Если хэш есть то
            if  not line[1] in [ 'x', '*','!' ]:
                #Передаем в функцию крека
                cracking(line[1], line[0], args.dic);



#Если имя модуля майн то 
if __name__=="__main__":
    #Вызываем соответствующию функцию
    main();

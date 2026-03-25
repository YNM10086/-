#将拓普康全站仪测出的数据自动转化成cass软件可用的格式

import os

old_file = r'E:\Python_file_Test\_4ZU_test.dat'
new_file = r'E:\Python_file_Test\_4ZU_test.txt'

os.rename(old_file,new_file)
#修改文件格式

for line in open('E:\Python_file_Test\_4ZU_test.txt', 'r'):

    file_line = []

    for i in line:
        file_line.append(i)

    file_line_one = file_line[:]

    Te_a = file_line_one.index(',')
    file_line_one.insert(Te_a, ',')

    file_line_two = file_line_one[::-1]

    file_line_two.remove(',')

    file_line_three = file_line_two[::-1]

    file_final = ''.join(file_line_three)


    with open('E:\Python_file_Test\_4ZU_test_fix.txt', 'a') as file_fix:
        file_fix.write(file_final)
#修改每一行内容并添加至新文件

os.rename(new_file,old_file)
#将源文件格式修改回去

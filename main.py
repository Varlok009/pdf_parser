from pdf_file_model import PdfFile
from sys import argv


if __name__ == '__main__':
    # Для простоты отладки можно вписать путь к файлу - ниже, иначе подтянется значение введенное в командной строке
    script_name, file_path = (argv[0], argv[1]) if len(argv) == 2 else (argv, 'files/standart.pdf')

    f = PdfFile(file_path)

    print(f'Словарь с параметрами файла - {f.get_params_from_pdf()}', end='\n\n')

    print(f'Файл {f.pdf_file_path} - {"соответствует" if f.compare_file_with_standart() else "не соответствует"} '
          f'эталонному файлу')
    # assert f.compare_file_with_standart(), 'Файлы не одинаковые'

from pathlib import Path
import fitz


class PdfFile:
    __slots__ = ('_pdf_file_path', '_pdf_blocks', '_data')

    def __init__(self, path: str) -> None:
        self.pdf_file_path = path
        self.pdf_blocks = self.pdf_file_path
        self.data = self.pdf_blocks

    @property
    def pdf_file_path(self) -> str:
        return self._pdf_file_path

    @pdf_file_path.setter
    def pdf_file_path(self, path: str) -> None:
        if not self._check_valid_file_path(path):
            raise FileNotFoundError(f'Значение path <{path}> - не валидное, убедитесь, '
                                    f'что по указанному пути есть файл')
        if not self._check_file_type(path):
            raise TypeError(f'Тип испльзуемого файла должен быть <pdf>')
        self._pdf_file_path = path

    @property
    def pdf_blocks(self) -> list[tuple]:
        return self._pdf_blocks

    @pdf_blocks.setter
    def pdf_blocks(self, pdf_file_path: str) -> None:
        self._pdf_blocks = self._get_pdf(pdf_file_path)

    @property
    def data(self) -> dict:
        return self._data

    @data.setter
    def data(self, pdf_blocks: list[tuple]) -> None:
        self._data = self._pdf_parse(pdf_blocks)

    @staticmethod
    def _get_pdf(file_path: str) -> list[tuple]:
        """Распарсим только первую страницу"""
        try:
            with fitz.open(file_path) as doc:
                page = next(doc.pages()).get_text("blocks")
                return page
        except fitz.FileDataError:
            raise fitz.FileDataError(f'Файл поврежден, попробуйте другой файл')

    @staticmethod
    def _check_valid_file_path(path: str) -> bool:
        return Path(path).is_file()

    @staticmethod
    def _check_file_type(path: str) -> bool:
        return Path(path).suffix == '.pdf'


    def _pdf_parse(self, blocks: list[tuple]) -> dict:
        """
        Создает словарь, ключами которого являются наименования парметров,
        а значением словарь описывающий значение параметра, его координаты
        и порядок расположения в файле
        """
        data = {}
        for block in blocks:
            coord = block[:4]
            position = block[5]
            list_params = block[4].strip('\n').split('\n')
            params = self._parse_params(list_params)
            for pos_in_row, k in enumerate(params):
                if k == 'not_key' and position == 0:
                    # Значение первой строки будем считать заголовком страницы
                    data['header'] = {'value': params[k], 'coord': coord, 'position': (position, pos_in_row)}
                elif k == 'not_key' and position == len(blocks) - 1:
                    # Допущение, что последним объектом всегда будет inspection notes
                    data['NOTES']['value'] = params[k]
                else:
                    data[k] = {'value': params[k], 'coord': coord, 'position': (position, pos_in_row)}
        return data

    def _parse_params(self, list_params: list, param_separator: str = ':') -> dict[str: any]:
        """
        Парсит переданный блок (строку текста), по умолчанию для разделения
        параметра и значения используется ':'
        """
        params = {}

        for param in list_params:
            if param.isspace():
                continue
            item = [self._parse_value(value) for value in param.split(param_separator)]

            if len(item) == 1:
                params['not_key'] = item[0]
            if len(item) == 2:
                params[item[0]] = item[1]
        return params

    def _parse_value(self, value: str) -> any:
        """
        В задании нет уточнений нужно ли форматировать полученные из пдф значения, например в int/datetime
        поэтому пока функция просто убирает лишние пробелы
        """
        return value.strip()

    def get_params_from_pdf(self) -> dict[str: any]:
        return {k: v.get('value') for k, v in self._data.items()}

    def compare_file_with_standart(self) -> bool:
        standart = PdfFile('files/standart.pdf')
        return self.__eq__(standart)

    @staticmethod
    def _compare_coord(coord_1: tuple[float], coord_2: tuple[float], allow_diff: float = 0.5) -> bool:
        """
        Сравнивает соответствующие координаты блоков
        При тестировании оказалось, что даже если ничего не менять в файле, но пересохранить его,
        то координаты немного двигаются. Для решения этой проблемы ввел параметр допустимой погрешности
        кооридинат - allow_diff
        """
        return all(abs(c1 - c2) < allow_diff for c1, c2 in zip(coord_1, coord_2))

    def __eq__(self, other: any) -> bool:
        """
        Для каждого параметра:
        1 Проверяется его наличие в каждом файле
        2 Проверяется, что для обоих файлов совпадает порядок его расположения
        3 Проверяется, что координаты расположения блоков, в которых находятся параметры совпадают
        """

        if not isinstance(other, PdfFile):
            return False

        for other_param in other._data.keys():
            if other_param not in self._data:
                print(f'Параметр {other_param} содержится не в обоих файлах')
                return False
            self_item = self._data.get(other_param)
            other_item = other._data.get(other_param)
            if not self_item.get('position') == other_item.get('position'):
                print(f'Порядок расположения параметра {other_param} отличается от эталонного')
                return False
            if not self._compare_coord(self_item.get('coord'), other_item.get('coord')):
                print(f'Координаты расположения блока с параметром {other_param} отличается от  эталонного')
                return False
        return True


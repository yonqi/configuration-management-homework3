import re
import sys
import yaml


class ConfigParser:
    def __init__(self):
        self.constants = {}  # Для хранения констант
    
    def parse(self, text):
        """Основной метод для обработки входного текста."""
        lines = text.splitlines()
        result = {}
        inside_dict = False  # Флаг для обработки словаря
        current_dict = None  # Словарь, который будем собирать
        # print("Parsing input...")  # Отладка
        for line in lines:
            line = line.strip()
            # print(f"Processing line: {line}")  # Отладка
            if not line or line.startswith('"') or line.startswith("'"):  # Пропускаем пустые строки и комментарии
                continue
            
            if ":=" in line:  # Обрабатываем константы
                name, value = self._parse_constant(line)
                result[name] = value  # Сохраняем константы в результирующий словарь
            elif line.startswith("{"):  # Обрабатываем начало словаря
                inside_dict = True
                current_dict = {}
                # print("Start of dictionary.")  # Отладка
            elif line.startswith("}"):  # Обрабатываем конец словаря
                if inside_dict:
                    result.update(current_dict)  # Добавляем собранный словарь в результат
                    inside_dict = False
                    current_dict = None
                else:
                    raise SyntaxError(f"Unexpected line: {line}")
            elif inside_dict:  # Обрабатываем записи внутри словаря
                key, value = self._parse_dictionary(line)
                current_dict[key] = value  # Сохраняем константы в результирующий словарь
            else:
                raise SyntaxError(f"Unexpected line: {line}")
        # print("Parsing completed.")  # Отладка
        return result
    
    def _parse_constant(self, line):
        """Обработка объявления константы."""
        match = re.match(r"^([_a-z]+)\s*:=\s*(.+);$", line)
        if not match:
            raise SyntaxError(f"Invalid constant declaration: {line}")
        name, value = match.groups()
        #print(f"Defining constant: {name} = {value}")  # Отладка
        value_result = None
        if value.startswith("[") and value.endswith("]"):  # Если значение в квадратных скобках
            expression = value[1:-1]  # Убираем квадратные скобки
            value_result = self._evaluate_expression(expression)
        elif value.isdigit():  # Если значение — число
            value_result = int(value)
        elif value.startswith('"') and value.endswith('"'):  # Если строка
            value_result = value.strip('"')
        elif value.startswith("'") and value.endswith("'"):  # Если строка в одинарных кавычках
            value_result = value.strip("'")
        else:
            raise SyntaxError(f"Unsupported constant value: {value}")
        
        self.constants[name] = value_result  # Сохраняем в константы
        return name, value_result  # Возвращаем имя и значение для сохранения в результирующий словарь

    
    def _evaluate_expression(self, expr):
        """Обработка постфиксных выражений."""
        tokens = expr.split()
        stack = []
        # print(f"Evaluating expression: {expr}")  # Отладка
        for token in tokens:
            if token.isdigit():
                stack.append(int(token))
            elif token in self.constants:
                stack.append(self.constants[token])
            elif token == "+":
                if len(stack) < 2:
                    raise ValueError(f"Invalid '+' operation in expression: {expr}")
                b, a = stack.pop(), stack.pop()
                stack.append(a + b)
            elif token == "mod":
                if len(stack) < 2:
                    raise ValueError(f"Invalid 'mod' operation in expression: {expr}")
                b, a = stack.pop(), stack.pop()
                stack.append(a % b)
            else:
                raise ValueError(f"Unknown token in expression: {token}")
        if len(stack) != 1:
            raise ValueError(f"Malformed expression: {expr}")
        result = stack[0]
        # print(f"Expression result: {result}")  # Отладка
        return result
    
    def _parse_dictionary(self, line):
        """Обработка словаря."""
        match = re.match(r"^([_a-z]+)\s*=\s*(.+);$", line)
        if not match:
            raise SyntaxError(f"Invalid dictionary entry: {line}")
        key, value = match.groups()
        # print(f"Processing dictionary entry: {key} = {value}")  # Отладка
        value_result = None
        # Обрабатываем значения, как и в случае с константами
        if value.isdigit():  # Числовое значение
            value_result = int(value)
        elif value in self.constants:  # Ссылка на константу
            value_result = self.constants[value]
        elif value.startswith("[") and value.endswith("]"):  # Постфиксное выражение
            value_result = self._evaluate_expression(value[1:-1])
        elif value.startswith('"') and value.endswith('"'):  # Строка
            value_result = value.strip('"')
        elif value.startswith("'") and value.endswith("'"):  # Строка в одинарных кавычках
            value_result = value.strip("'")
        else:
            raise SyntaxError(f"Unsupported value: {value}")
        return key, value_result  # Возвращаем имя и значение для сохранения в результирующий словарь


def main():
    input_text = sys.stdin.read()
    parser = ConfigParser()
    try:
        parsed_data = parser.parse(input_text)
        yaml_output = yaml.dump(parsed_data, sort_keys=False)
        print(yaml_output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

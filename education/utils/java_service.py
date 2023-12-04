def clear_java_comments(text: str) -> str:
    result = ''
    i = 0

    while i < len(text):
        # Пропуск содержимого строк
        if text[i] == '\"':
            result += text[i]
            i += 1
            while i < len(text):
                if text[i] == '\"' and text[i - 1] != '\\':
                    result += text[i]
                    i += 1
                    break
                result += text[i]
                i += 1

        # Пропуск содержимого однострочных комментариев
        elif i + 1 < len(text) and text[i:i + 2] == '//':
            i = text.find('\n', i + 2)
            if i < 0:
                break

        # Пропуск содержимого многострочных комментариев
        elif i + 1 < len(text) and text[i:i + 2] == '/*':
            i = text.find('*/', i + 2)
            if i < 0:
                break
            i += 2

        else:
            result += text[i]
            i += 1

    return result


def get_java_package(text: str) -> str | None:
    i_begin = text.find('package')
    if i_begin < 0:
        return None

    i_begin += len('package')
    i_end = text.find(';', i_begin)
    if i_end < 0:
        return None

    return ''.join(text[i_begin:i_end].split())


def get_java_class_name(text: str) -> str | None:
    i = text.find('class')
    if i < 0:
        return None

    i += len('class')
    while i < len(text) and text[i] <= ' ':
        i += 1

    class_name = ''
    while ('a' <= text[i] <= 'z' or 'A' <= text[i] <= 'Z' or
           '0' <= text[i] <= '9' or text[i] == '_'):
        class_name += text[i]
        i += 1

    return class_name


def join_text_by_java_files(text: str) -> list[tuple[str, str]]:
    def _is_sep(word_: str):
        for ch in word_:
            if ch != '=':
                return
        return len(word_) > 3

    text = clear_java_comments(text)
    files = [('', '')]

    for line in text.split('\n'):
        word = line[0]
        if _is_sep(word):
            files[-1][1] = files[-1][1].strip()
            files.append(('', ''))
        else:
            files[-1][1] += line + '\n'

    for i, file in enumerate(files):
        class_name = get_java_class_name(file[1]) or ''
        files[i][0] = class_name + '.java'

    return files

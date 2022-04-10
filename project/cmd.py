import sys
import argparse

from lib import cypher

parser = argparse.ArgumentParser(description="Шифрование")

group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-e', '--encrypt', action='store_true', help='Шифрование')
group.add_argument('-d', '--decrypt', action='store_true', help='Расшифрование')

parser.add_argument('-i', '--input', metavar='filename.txt', type=argparse.FileType('r'),
                    default='input.txt',
                    help='Путь к файлу, содержимое которого будет зашифровано')

parser.add_argument('-o', '--output', metavar='filename.txt', type=argparse.FileType('w'),
                    default='output.txt', help='Путь к файлу, куда будет сохранен зашифрованный текст')

parser.add_argument('-m', '--mode', metavar='modename', type=str, default='Caesar',
                    choices=['Caesar', 'Vernam', 'RSA'],
                    help='Режим шифрования')

parser.add_argument('-c', '--crack', action='store_true', default=False,
                    help='Провести взлом шифра Цезаря метод частотного анализа')

parser.add_argument('--offset', metavar='42', type=int, default=42, help='Сдвиг для шифра Цезаря')

parser.add_argument('--key', metavar='secret', type=str, default='secret', help='Ключ для шифра Вернама')

RSA_enc_requirement = ('-e' in sys.argv or '--encrypt' in sys.argv) and 'RSA' in sys.argv
parser.add_argument('--pubexp', metavar='e', type=int, required=RSA_enc_requirement,
                    help='Открытая экспонента публичного ключа RSA')

RSA_dec_requirement = ('-d' in sys.argv or '--decrypt' in sys.argv) and 'RSA' in sys.argv
parser.add_argument('--privexp', metavar='e', type=int, required=RSA_dec_requirement,
                    help='Секретная экспонента публичного ключа RSA')

parser.add_argument('--product', metavar='n', type=int, required='RSA' in sys.argv,
                    help='Модуль публичного ключа RSA')


if __name__ == '__main__':
    args = parser.parse_args()
    inputFile, outputFile, mode = args.input, args.output, args.mode

    assert (not args.crack or (mode == 'Caesar' and args.decrypt)), "Conflicting flags"  # incorrect crack

    m = cypher.Cypher(inputFile, outputFile)
    rsaPair = (None, None)
    if RSA_dec_requirement:
        rsaPair = (args.privexp, args.product)
    elif RSA_enc_requirement:
        rsaPair = (args.pubexp, args.product)
    m.load(mode, args.offset, args.key, rsaPair)
    if args.encrypt:
        m.encrypt()
    else:
        if args.crack:
            m.crack()
        else:
            m.decrypt()

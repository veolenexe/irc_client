SMILE_DICT = {':-)': '☺',
              '=( ': '☹',
              '<3': '♥',
              ':@': '(╯°□°）╯︵ ┻━┻',
              'XD': '☺',
              '8)': '(⌐■_■)',
              '=$': '◉_◉',
              ':star:': '★',
              ':triforce:': '  ▲\n▲ ▲',
              ';(': '(ಥ_ಥ)',
              '=*': '(づ￣ ³￣)づ',
              ' ;D': '(◕‿↼)',
              ':\')': '(ʘ‿ʘ)',
              'D:': '(ʘ_ʘ)',
              '=D': '♥‿♥',
              '(y)': '✌',
              ':]': '☺',
              '=#': '(⊙⊙)',
              ':O': '(ō_ō)',
              '=L': '(͡๏̯͡๏)'

              }


class SymbolsReplacer:
    @staticmethod
    def find_smile(string: str):
        for key, smile in SMILE_DICT.items():
            if key in string:
                string = string.replace(key, smile)
        return string


def main():
    sr = SymbolsReplacer()
    b = '☺'
    b = sr.find_smile(b)
    print(b)


if __name__ == '__main__':
    main()

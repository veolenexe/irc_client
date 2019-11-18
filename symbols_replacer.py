

class SymbolsReplacer:
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

    @staticmethod
    def find_smile(string: str):
        for key, smile in SymbolsReplacer.SMILE_DICT.items():
            if key in string:
                string = string.replace(key, smile)
        return string

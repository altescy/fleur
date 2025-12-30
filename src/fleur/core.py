from fleur.js.builder import Record, String


class Cmd(Record):
    @staticmethod
    def none() -> Record:
        return Record(type=String("none"))

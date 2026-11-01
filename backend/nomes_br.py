"""Primeiros nomes mais frequentes no Brasil (Censo IBGE, API de nomes, ranking por década e sexo).

Usado só como detector residual: texto com um destes nomes seguido de sobrenome é
bloqueado (fail-closed), nunca substituído. Lista parcial: nomes raros não são cobertos.
"""

PRIMEIROS_NOMES: frozenset[str] = frozenset({
    "adriana", "alessandra", "alexandre", "alice", "aline", "alzira", "amanda", "ana",
    "anderson", "andre", "andrea", "andreia", "antonia", "antonio", "aparecida", "beatriz",
    "benedita", "benedito", "bianca", "bruna", "bruno", "camila", "carla", "carlos", "claudia",
    "claudio", "cristiane", "daiane", "daniel", "daniela", "diego", "edson", "eduarda",
    "eduardo", "elaine", "eliane", "elza", "fabiana", "fabio", "fatima", "felipe", "fernanda",
    "fernando", "francisca", "francisco", "gabriel", "gabriela", "geovana", "geraldo",
    "guilherme", "gustavo", "helena", "isabel", "isabela", "jaqueline", "jessica", "joana",
    "joao", "joaquim", "jorge", "jose", "josefa", "julia", "juliana", "larissa", "leandro",
    "leonardo", "leticia", "luana", "lucas", "lucia", "luciana", "luciano", "luis", "luiz",
    "luiza", "luzia", "manoel", "manuel", "marcelo", "marcia", "marcio", "marcos", "maria",
    "mariana", "mario", "marlene", "marli", "mateus", "matheus", "miguel", "nair", "natalia",
    "nelson", "osvaldo", "patricia", "paulo", "pedro", "priscila", "rafael", "rafaela",
    "raimunda", "raimundo", "regina", "renata", "ricardo", "rita", "roberto", "rodrigo", "rosa",
    "rosangela", "sandra", "sara", "sebastiana", "sebastiao", "sergio", "severino", "silvana",
    "simone", "sonia", "sueli", "tania", "tatiane", "tereza", "terezinha", "tiago", "vanessa",
    "vera", "vicente", "vitor", "vitoria",
})

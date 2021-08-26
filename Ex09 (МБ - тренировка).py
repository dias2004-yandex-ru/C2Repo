# игра Морской Бой (sea мальчик = объект класса МорскиеЛюди)
# по мотивам учебной программы 20210826 Mike
# модернизация: игра - тренировка со случайной закрытой|открытой расстановкой кораблей.
# *****************************************************************************
# ЗАПУСК ИГРЫ:
# Game(True).start() - игра "почти настоящая", корабли не видны
# Game(False).start() - игра "сильно тренировочная", корабли видны
# параметр у объекта Game необязательный, по умолчанию игра - почти настоящая

from random import randint


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Выстрел вне доски не учитывается, сделайте выстрел в поле на доске.'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Поле бито, выстрел не учитывается, сделайте выстрел в другое поле.'


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, bow, length, o, lives):
        self.bow = bow
        self.length = length
        self.o = o
        self.lives = lives

    @property
    def dots(self):
        ship_dots = []
        cur_x = self.bow.x
        cur_y = self.bow.y
        ship_dots.append(Dot(cur_x, cur_y))
        for i in range(self.length - 1):
            if self.o == 0:  # горизонтальный корабль
                cur_y += 1
            elif self.o == 1:  # вертикальный корабль
                cur_x += 1
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooted(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hidden=False, size=6):
        self.hidden = hidden
        self.size = size
        self.destroyed = 0  # количество поражённых кораблей
        self.field = [[' '] * size for _ in range(size)]  # список символов в полях доски
        self.busy = []  # список занятых полей доски
        self.ships = []  # список кораблей на доске

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'
        if self.hidden:
            res = res.replace('■', ' ')
        return res

    def out(self, d):
        return not ((0 < d.x <= self.size) and (0 < d.y <= self.size))

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x - 1][cur.y - 1] = '∙'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException
        for d in ship.dots:
            self.busy.append(d)
            self.field[d.x - 1][d.y - 1] = '■'

        self.ships.append(ship)
        self.contour(ship, False)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooted(d):
                ship.lives -= 1
                self.field[d.x - 1][d.y - 1] = 'X'
                if ship.lives == 0:
                    self.destroyed += 1
                    self.contour(ship, True)
                    print('Корабль уничтожен.')
                    return False
                else:
                    print('Корабль ранен.')
                    return True
        self.field[d.x - 1][d.y - 1] = '¤'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []  # инициализация списка для для хранения обстрелянных в ходе игры полей
        # (ранее список использовался при расстановке кораблей)


class Player:
    def __init__(self, board):
        self.board = board
        self.shots = 0      # количество выстрелов

    @staticmethod
    def ask():
        while True:
            cords = input('Ваш  выстрел: ').split()
            if len(cords) != 2:
                print('Введите две цифры - координаты поля')
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print('Введены недопустимые для указания координат символы.')
                continue
            return Dot(int(x), int(y))

    def move(self):
        while True:
            try:
                self.board.shot(self.ask())
                return
            except BoardException as e:
                print(e)

    def add_shot(self):
        self.shots += 1


class Game:
    def __init__(self, test=True, size=6):
        self.test = test
        self.size = size
        b = self.random_board()
        b.hidden = self.test

        self.plr = Player(b)

    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветствуем вас ")
        print("   на тренировке   ")
        print("перед морским боем!")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ", '\n')

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for le in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), le, randint(0, 1), le)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def loop(self):
        while True:
            if not self.plr.shots:
                print('*' * 54)
                if self.test:
                    print("Тренировочная доска со случайной закрытой расстановкой:")
                else:
                    print("Тренировочная доска со случайной открытой расстановкой:")
            else:
                print('*' * 27)
                print("Текущая диспозиция:")
            print('выполнено выстрелов ' + str(self.plr.shots))
            print('уничтожено целей ' + str(self.plr.board.destroyed))
            print(self.plr.board)
            print("-" * 27)
            self.plr.move()

            if self.plr.board.destroyed == len(self.plr.board.ships):
                print(self.plr.board)
                print("-" * 27)
                print("Чистый бескомпромиссный выигрыш!")
                print('Потрачено выстрелов: ' + str(self.plr.shots + 1))
                break

            self.plr.add_shot()

    def start(self):
        self.greet()
        self.loop()


Game().start()

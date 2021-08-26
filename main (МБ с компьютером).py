# игра Морской Бой (sea мальчик = объект класса МорскиеЛюди)
# учебная программа 20210826 Mike
# *****************************************************************************
# ЗАПУСК ИГРЫ:
# Game().start()

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
        return 'Выстрел вне доски, сделайте выстрел в поле на доске.'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Поле бито, сделайте выстрел в другое поле.'


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
        for i in range(self.length-1):
            if self.o == 0:     # горизонтальный корабль
                cur_y += 1
            elif self.o == 1:   # вертикальный корабль
                cur_x += 1
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hidden=False, size=6):
        self.hidden = hidden
        self.size = size
        self.destroyed = 0  # количество поражённых кораблей
        self.field = [['o'] * size for _ in range(size)]    # список символов в полях доски
        self.busy = []      # список занятых полей доски
        self.ships = []     # список кораблей на доске

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'
        if self.hidden:
            res = res.replace('■', 'o')
        return res

    def out(self, d):
        return not((0 < d.x <= self.size) and (0 < d.y <= self.size))

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
                        self.field[cur.x-1][cur.y-1] = '∙'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException
        for d in ship.dots:
            self.busy.append(d)
            self.field[d.x-1][d.y-1] = '■'

        self.ships.append(ship)
        self.contour(ship, False)

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x-1][d.y-1] = 'X'
                if ship.lives == 0:
                    self.destroyed += 1
                    self.contour(ship, verb=True)
                    print('Корабль уничтожен.')
                    return False
                else:
                    print('Корабль ранен.')
                    return True
        self.field[d.x-1][d.y-1] = '¤'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []  # инициализация списка для для хранения обстрелянных в ходе игры полей
        # (ранее список использовался при расстановке кораблей)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(1, 6), randint(1, 6))
        print(f'Компьютер стреляет: {d.x} {d.y}')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()
            if len(cords) != 2:
                print('Введите две цифры - координаты поля')
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print('Введены недопустимые для указания координат символы.')
                continue
            return Dot(int(x), int(y))


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветствуем вас ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

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
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.destroyed == len(self.ai.board.ships):
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.us.board.destroyed == len(self.us.board.ships):
                print("-" * 20)
                print("Компьютер выиграл!")
                break

            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

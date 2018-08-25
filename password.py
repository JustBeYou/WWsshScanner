
class Password(object):
    """
        pass_type:
            0 -> username:password
            1 -> usernames file + passwords file
    """
    users = []
    passwords = []
    index = 0

    def __init__(self, pass_type, args):
        self.pass_type = pass_type
        if pass_type == 0:
            filename = args[0]
            with open(filename) as f:
                for line in f:
                    line = line.strip().split(':')
                    self.users.append(line[0])
                    self.passwords.append(line[1])
        elif pass_type == 1:
            self.second_index = 0
            user_file = args[0]
            password_file = args[1]

            with open(user_file) as f:
                for line in f:
                    self.users.append(line.strip())
            with open(password_file) as f:
                for line in f:
                    self.passwords.append(line.strip())
        else:
            raise Exception("Wrong type")

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.pass_type == 0:
            if self.index < len(self.users):
                to_return = (self.users[self.index], self.passwords[self.index])
                self.index += 1
                return to_return
            raise StopIteration()
        elif self.pass_type == 1:
            if self.index < len(self.users):
                to_return = (self.users[self.index], self.passwords[self.second_index])
                self.second_index += 1

                if self.second_index == len(self.passwords):
                    self.second_index = 0
                    self.index += 1

                return to_return
            raise StopIteration()

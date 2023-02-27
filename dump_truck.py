class DumpTruck:
    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    # def get_student_details(self):
    #     print("Your name is " + self.name + ".")
    #     print("You are studying " + self.course)

    def get_code(self):
        return 1

    def __repr__(self):
        return str(self.get_code())
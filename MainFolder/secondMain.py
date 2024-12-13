import sys
sys.path.insert(1, 'C://Users//User//Desktop//MyPythonProject')
from firstFolder import secondFile as sf

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

class Student(Person):
    def __init__(self, name, age, gender):
        Person.__init__(self, name, age)
        self.gender = gender

student1 = Student("Nicholas", 21, "Male")
print(student1.gender)
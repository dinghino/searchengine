from faker import Faker
import click
fake = Faker()
fake.seed(1)


class Person:
    def __init__(self, id, fname, lname, job):
        self.id = id
        self.fname = fname
        self.lname = lname
        self.job = job

    def toString(self):
        return '<{} {} ({})>'.format(self.fname, self.lname, self.job)

    def __repr__(self):
        return self.toString()

    def __str__(self):
        return self.toString()


class Profile:
    """
    Profile object to handle faker.simple_profile dictionaries.
    """

    def __init__(self, id, address, birthdate, mail, name, sex, username, job):
        self.id = id
        self.address = address
        self.birthdate = birthdate
        self.mail = mail
        self.name = name
        self.sex = sex
        self.username = username
        self.job = job

    def __repr__(self):
        s = '<Profile of `{u}` [{n} ({j})] >'.format(
            u=self.username,
            n=click.style(self.name, bold=True),
            j=self.job,
        )
        return s


people = sorted([Person(
    i,
    fake.first_name(),
    fake.last_name(),
    fake.job()
) for i in range(500)], key=lambda p: p.fname)

my_people = [
    Person(500, 'John', 'Doe', 'anarchyst'),
    Person(501, 'Jane', 'Doe', 'bitch'),
    Person(502, 'Pippo', 'Doe', 'cane'),
]
people.extend(my_people)

profiles = sorted(
    (Profile(id=i, job=fake.job(), **fake.simple_profile())
     for i in range(100)), key=lambda p: p.name)

lenprof = len(profiles)

my_profiles = [
    {
        'id': lenprof,
        'username': 'thebitch99',
        'name': 'Jane Doe',
        'sex': 'F',
        'address': '70669 Heather Grove\nNew Sierra, WI 00080-6360',
        'mail': 'jane.doe.bitch@hotmail.com',
        'birthdate': '1985-11-11',
        'job': fake.job(),
    }, {
        'id': lenprof + 1,
        'username': 'john68',
        'name': 'John Doe',
        'sex': 'M',
        'address': 'PSC 1241, Box 5868\nAPO AP 44978',
        'mail': 'john.doe@yahoo.com',
        'birthdate': '1986-07-09',
        'job': fake.job(),
    }, {
        'id': lenprof + 2,
        'username': 'christopher81',
        'name': 'Pippo Doe',
        'sex': 'M',
        'address': '7070 Warner Ridges Suite 228\nNorth Kaylee, NJ 68595',
        'mail': 'pippo.dog@hotmail.com',
        'birthdate': '2011-06-10',
        'job': fake.job(),
    }
]

profiles.extend([Profile(**p) for p in my_profiles])

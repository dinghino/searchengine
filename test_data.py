from faker import Faker
import click
fake = Faker()
fake.seed(1)


class Person:
    def __init__(self, fname, lname, job):
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
    """Profile object to handle faker.simple_profile dictionaries. """

    def __init__(self, address, birthdate, mail, name, sex, username, job):
        self.address = address
        self.birthdate = birthdate
        self.mail = mail
        self.name = name
        self.sex = sex
        self.username = username
        self.job = job

    def __repr__(self):
        s = '<Profile of `{u}` - {e} [{n} ({j})] >'.format(
            u=self.username,
            n=click.style(self.name, bold=True),
            j=self.job,
            e=self.mail,
        )
        return s


people = sorted([Person(
    fake.first_name(),
    fake.last_name(),
    fake.job()
) for _ in range(500)], key=lambda p: p.fname)

profiles = sorted(
    (Profile(**fake.simple_profile(), job=fake.job()) for _ in range(100)),
    key=lambda p: p.name)

from django.forms.models import model_to_dict
from random import randint, shuffle, choices
from collections import namedtuple
import json
import re

# PARSING DATA #

def get_attribute(questionnaire, attribute):
    return [dict_[attribute] for dict_ in questionnaire]

def to_csv(l, delim):
    string = ''
    for item in l:
        string += f"{item}{delim}"
    return string.rstrip(delim)

# GENERATING RANDOM ANSWERS #

NUMBERS = re.compile(r'([0-9]+)')

LESSTHAN12 = re.compile(r'([0-9]|10|11|12)')
LESSTHAN31 = re.compile(r'([1-2][0-9]|30|31)')

YEAR = re.compile(r'([1-3][0-9]{3})')
MTEN = re.compile(r'([0-9]*0)')
OTHER = re.compile(r'([0-9]+)')

def randomize_word(word):
    # This will almost never happen but if there's no choices for answers
    # we will give a slightly changed version of the real answer
    if word == '':
        return 'potatoe'
    newword = list(word)
    # Picks a random character and changes it to a random letter
    newword[randint(0, len(word)-1)] = chr(randint(97, 122))
    return ''.join(newword)

def get_pure_strings(l_of_strings, auto_randomize_ints, delim):

    list_ = []

    for string in l_of_strings:
        # split the answer and take the first one, the main answer
        if not NUMBERS.search(string.split(delim)[0]) or auto_randomize_ints == False:
            list_.append(string.split(delim)[0])

    return list_

def get_number_strings(l_of_strings, delim):

    list_ = []

    for string in l_of_strings:
        # split the answer and take the first one, the main answer
        if NUMBERS.search(string.split(delim)[0]):
            list_.append(string.split(delim)[0])

    return list_

def generate_randomized_strings(answer, string_answers, number_answers, apq):
    # Get n strings that are not answer

    # Make it a set so there's not duplicates
    list_ = [answer]

    while len(list_) < apq:
        for item in string_answers:
            if item not in list_:
                list_.append(item)
                break
        else:
            for s in number_answers:
                if s not in list_:
                    list_.append(s)
                    break
            else:
                newword = randomize_word(answer)
                if newword not in list_:
                    list_.append(newword)

    shuffle(list_)

    return list_

def generate_randomized_ints(answer, apq):

    list_ = [answer]

    while len(list_) < apq:
        item = randomize_int(answer)
        if item not in list_:
            list_.append(item)

    shuffle(list_)

    return list_

def randomize_int(string):

    def rando12(n):
        return str(randint(1,12))

    def rando31(n):
        return str(randint(1,31))

    def randoyear(n):
        n=int(n)-20+randint(0,40)
        return str(n)

    def randomten(n):
        n=int(n)-20+randint(0,4)*10
        return str(n)

    def randoother(n):
        return ''.join(tuple([str(randint(0,9)) for char in n]))

    list_ = re.split(NUMBERS, string)

    st = ''

    for item in list_:
        mo = re.fullmatch(LESSTHAN12, item)
        if mo:
            st += rando12(mo[0])
            continue
        mo = re.fullmatch(LESSTHAN31, item)
        if mo:
            st += rando31(mo[0])
            continue
        mo = re.fullmatch(YEAR, item)
        if mo:
            st += randoyear(mo[0])
            continue
        mo = re.fullmatch(MTEN, item)
        if mo:
            st += randomten(mo[0])
            continue
        mo = re.fullmatch(OTHER, item)
        if mo:
            st += randoother(mo[0])
            continue

        st+=item

    return st

def generate_answers(questionnaire, apq, auto_randomize_ints, delim, extra_answers):

    correct = get_attribute(questionnaire, 'answer')

    # Pool from which to pick fake answers. Removed duplicates.
    fake = list(set(get_pure_strings(correct, auto_randomize_ints, delim) + extra_answers))
    numberstrings = list(set(get_number_strings(correct, delim)))

    # Choices is what we will return
    choices = list()

    for i, item in enumerate(correct):
        if questionnaire[i]['choices'] == None:
            existing_choices = []
        else:
            existing_choices = questionnaire[i]['choices'].split(delim)

        # Check if the item already has fake answers, if it does don't randomize
        if len(existing_choices) < apq-1:
            if bool(NUMBERS.search(item)) & auto_randomize_ints:
                choices.append(to_csv(generate_randomized_ints(item, apq), delim))
            else:
                shuffle(fake)
                shuffle(numberstrings)
                choices.append(to_csv(generate_randomized_strings(item, fake, numberstrings, apq), delim))
        else:
            # maybe change from real_answers[0] to real_answers[randint(0,len(real_answers)-1)]
            real_answers = questionnaire[i]['answer'].split(delim)
            existing_choices.append(real_answers[0])
            shuffle(existing_choices)
            choices.append(to_csv(existing_choices, delim))

    # this list will be then added as the value "choices" in the dictionary that will be sent
    return choices

def import_only_answers(questionnaire, auto_randomize_ints, delim):

    answers = get_attribute(questionnaire, 'answer')

    return list(set(get_pure_strings(answers, auto_randomize_ints, delim)))

class ParsedQuestionnaire:

    def __init__(self, Q, delim=', '):
        self.ordered                       = Q.ordered
        # If it's 0, it picks all of them
        self.questions_per_test            = Q.questions_per_test or len(Q.questions.all())
        self.auto_randomize_ints           = Q.auto_randomize_ints
        self.include_answers_from_previous = Q.include_answers_from_previous
        self.choices_per_question          = Q.choices_per_question
        self.type_choice                   = Q.type_choice
        self.type_write                    = Q.type_write
        # Course from which questionnaire comes (parent)
        self.course                        = Q.course
        self.number                        = Q.number
        self.name                          = Q.name

        self.delim                         = delim

        # Gets the number of questions you want, turned to dictionaries
        if self.ordered:
            self.all_questions = (Q.questions.order_by('number') [:self.questions_per_test]).values()
        else:
            self.all_questions = (Q.questions.order_by('?') [:self.questions_per_test]).values()
    
    @property
    def questions(self):
        return json.dumps(get_attribute(self.all_questions, 'question'))
    
    @property
    def answers(self):
        return json.dumps(get_attribute(self.all_questions, 'answer'))
    
    @property
    def choices(self):
        # If you don't want any, just pass in the empty list
        extra_answers = []
        if self.include_answers_from_previous:
            for q in self.course.questionnaires.all():
                if q.number < self.number:
                    extra_answers += import_only_answers(q.questions.values(), q.auto_randomize_ints, self.delim)

        return json.dumps(generate_answers(self.all_questions, self.choices_per_question,
        self.auto_randomize_ints, self.delim, extra_answers))
    
    @property
    def types(self):
        ''' Edit this to add more types of question.
        Returns a tuple. Each value corresponds to a question and describes its type.
        E.g. ('type_choice', 'type_write', 'type_write', 'type_choice')'''

        # 'random.choices' takes a tuple with the probabilities in range 0—1
        chances = (self.type_choice/100, self.type_write/100)

        # Based on 'chances', it randomly chooses which type each question is gonna be.
        def generator():
            for _ in range(self.questions_per_test):
                yield choices(('type_choice', 'type_write'), chances)[0]

        return json.dumps(tuple(generator()))

class TxtCourse:
    def __init__(self, lines):
        brackets = re.compile(r'^\[(.*?)\]$')
        question = re.compile(r'^(.*?),(.*?)$')
        
        self.isvalid = False
        self.questionnaires = []

        for line in lines:
            # If it's a blank line, just ignore it
            if not line:
                continue

            mo = re.match(brackets, line)

            if mo:
                self.questionnaires.append(TxtQuestionnaire(mo[1]))

            else:
                mo = re.match(question, line)
                # Do strip to questions and answers just in case
                if not mo:
                    continue

                if not self.questionnaires:
                    print('ERROR file not valid')
                    break

                answers = ','.join([a.strip() for a in mo[2].split(',')])

                self.questionnaires[-1].add_question(mo[1], answers)

        else:
            for questionnaire in self.questionnaires:
                if not questionnaire:
                    self.isvalid = False
                    break
            else:
                self.isvalid = True

    def __getitem__(self, i):
        return self.questionnaires[i]

    def __len__(self):
        return len(self.questionnaires)

    def __str__(self):
        return ','.join([x.name for x in self])

class TxtQuestionnaire:

    def __init__(self, name):
        self.name = name
        self.questions = []
        self.answers = []

    def __getitem__(self, i):
        return (self.questions[i], self.answers[i])

    def __len__(self):
        return len(self.questions)

    def __str__(self):
        return '\n'.join([f'Question: {x[0]}\nAnswer: {x[1]}' for x in self])

    def add_question(self, question, answers):
        self.questions.append(question)
        self.answers.append(answers)


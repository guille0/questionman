from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from .algorithms import ParsedQuestionnaire, TxtCourse, TxtQuestionnaire
from .models import Course, Questionnaire, Question
from .helpers import cleanCSV
from django.contrib import messages
# pylint: disable=maybe-no-member

def home(request):
    courses = sorted(Course.objects.all(), key=lambda course: course.rating, reverse=True)
    return render(request, 'courses/home.html', context={'courses': courses})

def ErrorAccessDenied(request):
    return render(request, 'courses/access-denied.html')

def UploadInfo(request):
    return render(request, 'courses/upload-info.html')

@login_required
def AjaxLikeCourse(request):
    user = request.user
    course = Course.objects.get(id=int(request.GET.get('id')))

    if course in user.profile.courses_liked.all():
        user.profile.courses_liked.remove(course)
        liked = False
    else:
        user.profile.courses_liked.add(course)
        liked = True

    data = {
        'liked': liked,
        'likes_number': len(course.liked_by.all()),
    }
    return JsonResponse(data)

def AjaxQuestionnaireDone(request):
    user = request.user
    questionnaire = Questionnaire.objects.get(id=int(request.GET.get('id')))
    course = questionnaire.course

    if user.username:
        try:
            user.profile.questionnaires_done.add(questionnaire)
            # Checking if all questionnaires in course are done
            for item in course:
                if item not in user.profile.questionnaires_done.all():
                    break
            else:
                user.profile.courses_done.add(course)

        except Exception:
            # TODO logging not printing
            print('Error adding questionnaire to profile.questionnaires_done'
            '(perhaps user got logged out?)')

    return HttpResponse(1)

def Browse(request):
    # Sorted by rating TODO add different sortings
    courses = sorted(Course.objects.all(), key=lambda course: course.rating, reverse=True)
    # Sort by newest
    # courses = sorted(Course.objects.all(), key=lambda course: course.date, reverse=True)

    context = {'courses': courses}
    return render(request, 'courses/browse.html', context)

def BrowseCourse(request, course_id):
    course = Course.objects.get(id=course_id)
    questionnaires = course.questionnaires.all()

    context = {'course': course,
               'questionnaires': questionnaires}

    return render(request, 'courses/browsecourse.html', context)

def BrowseQuestionnaire(request, course_id, questionnaire_n):

    course = Course.objects.get(id=course_id)
    questionnaire = course.questionnaires.get(number=questionnaire_n)

    PQ = ParsedQuestionnaire(questionnaire)

    context = {
               'q':             PQ.questions,
               'a':             PQ.answers,
               'c':             PQ.choices,
               't':             PQ.types,
               'apq':           PQ.choices_per_question,
               'delim':         PQ.delim,
               'test' :         0,          # This should be 0 or 1
               'course':        course,
               'questionnaire': questionnaire,
              }

    return render(request, 'courses/questionnaire.html', context)

@login_required
def Edit(request):
    courses = Course.objects.filter(author=request.user)
    # Add Course, remove Course.
    if request.method == 'POST':
        if request.POST.get("new-course"):
            newcourse = Course.objects.create(author=request.user)
            # Also creates a default questionnaire and question
            newcourse.new_questionnaire()

        if request.POST.get("delete"):
            courses.get(id=request.POST.get("delete")).delete()
            return redirect('edit')

    context = {'courses': courses}

    return render(request, 'courses/edit.html', context)

@login_required
def EditCourse(request, course_id):
    course = Course.objects.get(id=course_id)
    questionnaires = course.questionnaires.all()

    if course.author != request.user:
        return redirect('error-access-denied')

    if request.method == 'POST':
        if request.POST.get("new-questionnaire"):
            course.new_questionnaire()

        if request.POST.get("delete"):
            course.delete_questionnaire(number=request.POST.get('delete'))

        if request.POST.get("moveup"):
            questionnaires.get(number=request.POST.get("moveup")).move_up()

        if request.POST.get("movedown"):
            questionnaires.get(number=request.POST.get("movedown")).move_down()

        if request.POST.get("upload-txt"):
            uploaded_file = request.FILES['file']

            lines = []
            for line in uploaded_file:
                lines.append(line.decode())

            file = TxtCourse(lines)

            if file.isvalid:

                for questionnaire in file:
                    if questionnaire:
                        tmp_q = Questionnaire.objects.create(course=course,
                            name=questionnaire.name, number=len(course)+1)

                        for question, answer in questionnaire:
                            Question.objects.create(questionnaire=tmp_q, 
                                question=question, answer=answer, number=len(tmp_q)+1)
            
            else:
                messages.warning(request, 'File not valid.')

        if request.POST.get("edit-values"):
            course.name = request.POST.get('name') or course.name
            course.save()
            # Redirects to the #options part of the page
            return redirect(reverse('edit-course', kwargs={'course_id': course.id}) + '#options')

    context = {'course': course,
               'questionnaires': questionnaires}

    return render(request, 'courses/editcourse.html', context)

@login_required
def EditQuestionnaire(request, course_id, questionnaire_n):
    course = Course.objects.get(id=course_id)
    questionnaire = course.questionnaires.get(number=questionnaire_n)
    questions = questionnaire.questions.all()

    if course.author != request.user:
        return redirect('error-access-denied')

    if request.method == 'POST':
        if request.POST.get("new-question"):
            questionnaire.new_question()

        if request.POST.get("delete"):
            questionnaire.delete_question(number=request.POST.get('delete'))

        if request.POST.get("moveup"):
            questions.get(number=request.POST.get("moveup")).move_up()

        if request.POST.get("movedown"):
            questions.get(number=request.POST.get("movedown")).move_down()

        if request.POST.get("edit-values"):
            # Parses data from html
            questionnaire.edit_values(request.POST.copy())
            questionnaire.save()
            # Redirects to the '#Options' part of the page
            return redirect(reverse('edit-questionnaire', kwargs={'course_id': course.id, 'questionnaire_n': questionnaire.number}) + '#options')

    context = {'course': course,
               'questionnaire': questionnaire,
               'questions': questions}

    return render(request, 'courses/editquestionnaire.html', context)

@login_required
def EditQuestion(request, course_id, questionnaire_n, question_n):
    course = Course.objects.get(id=course_id)
    questionnaire = course.questionnaires.get(number=questionnaire_n)
    questions = questionnaire.questions.all()
    question = questions.get(number=question_n)

    if course.author != request.user:
        return redirect('error-access-denied')

    if request.method == 'POST':
        if request.POST.get("action") == "delete":
            questionnaire.delete_question(number=question.number)
            return redirect('edit-questionnaire', course.id, questionnaire.number)

        # If it's not deleted, then it gets saved
        # question.question is the string of the actual question (e. g. 'What's the capital of France?')
        question.question = request.POST.get("question") or question.question
        question.answer = cleanCSV(request.POST.get("answer")) or question.answer
        question.choices = cleanCSV(request.POST.get("choices"))
        question.save()

        if request.POST.get("action") == "save":
            # Saving returns back to the questionnaire (save and exit, basically)
            return redirect('edit-questionnaire', course.id, questionnaire.number)

        if request.POST.get("action") == "saveandnew":
            questionnaire.new_question()
            return redirect('edit-question', course.id, questionnaire.number, len(questionnaire))

    context = {'course': course,
               'questionnaire': questionnaire,
               'questions': questions,
               'question': question}

    return render(request, 'courses/editquestion.html', context)


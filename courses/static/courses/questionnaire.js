/* eslint-disable no-unused-vars */
/* eslint-disable no-undef */

// DOM OBJECTS //
// QUESTION
const BoxQuestion = document.querySelector('.box-question')
const TextQuestion = document.querySelector('#text-question')
// Boxes containing the input
const BoxInputChoice = document.querySelector('#box-input-choice')
const BoxInputWrite = document.querySelector('#box-input-write')
// Actual input buttons and form
const InputChoice = document.querySelectorAll('.input-choice')
const InputWrite = document.querySelector('#input-write')
const TextNoValue = document.querySelector('#text-novalue')

const BtnConfirm = document.querySelector('#button-confirm')
const BtnSkip = document.querySelector('#button-skip')

// RESULT (correct or incorrect)
const BoxResult = document.querySelector('.box-result')
const TextResult = document.querySelector('#text-result')
const TextResultDetail = document.querySelector('#text-result-detail')
const BtnNext = document.querySelector('#button-next')

// OBJECTS AND FUNCTIONS //

// Max number of characters in buttons //
const MAXCHAR = 48
// This means 1 typo per 5 characters (starting at 0)
const TYPOSALLOWED = 5

// Tool Functions //

// Unescape html
function htmlUnescape (str) {
  return str
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
}

function moveToLast (index, array) {
  array.push(array.splice(index, 1)[0])
}

function deleteItem (index, array) {
  array.splice(index - 1, index)
}

// Check if there's a similar string in an array
function similarInArray (answer, array) {
  for (let i = 0; i < array.length; i++) {
    let a = answer.toLowerCase().replace(/[ .,/#!$%^&*;:{}=\-_`~()]/g, '')
    let b = array[i].toLowerCase().replace(/[ .,/#!$%^&*;:{}=\-_`~()]/g, '')
    let na = a.match(/\d+/g)
    let nb = b.match(/\d+/g)
    // Numbers have to be exactly the same
    if ((na === null || nb === null) || na.toString() === nb.toString()) {
      // Strings can be a little different though (1 error per 5 characters)
      // (0-4) allow 0 errors, (5-9) allow 1 error, etc.
      if (Levenshtein.get(a, b) <= Math.floor(array[i].length / TYPOSALLOWED)) {
        return true
      }
    }
  } // endfor
  return false
}

// Check if an exact string is in an array
function inArray (item, array) {
  return (array.indexOf(item) > -1)
}

// Dealing with questions //

function nextQuestion (del) {
  if (del === true) {
    deleteItem(1, questionnaire)
  } else {
    moveToLast(0, questionnaire)
  }
  currentQ = questionnaire[0]
}

// OBJECTS //

const questionObject = (question, a, c, type) => {
  const answer = a.split(',')
  const choices = c.split(',')
  return { question, answer, choices, type }
}

const arrayOfQuestions = (questiondata, answerdata, choicesdata, typedata) => {
  let array = []
  for (let i = 0; i < questiondata.length; i++) {
    array.push(questionObject(questiondata[i], answerdata[i], choicesdata[i], typedata[i]))
  }
  return array
}

// GUI //

const renderQuestion = (aq, n) => {
  BoxQuestion.style.display = 'block'
  BoxResult.style.display = 'none'
  if (test) {
    BtnSkip.style.display = 'none'
  } else {
    BtnSkip.style.display = 'inline-block'
  }

  TextQuestion.innerText = aq[n].question

  let totalamount = 0
  switch (aq[n].type) {
    case 'type_choice':

      BoxInputChoice.style.display = 'block'
      BoxInputWrite.style.display = 'none'

      for (let i = 0; i < apq; i++) {
        InputChoice[i].innerText = aq[n].choices[i]
        totalamount += InputChoice[i].innerText.length
      }

      // If the answers to choose from are too long
      // split them into one line each

      if (totalamount >= MAXCHAR) {
        for (let i = 0; i < apq; i++) {
          InputChoice[i].style.display = 'block'
          InputChoice[i].style.maxWidth = '100%'
        }
      } else {
        for (let i = 0; i < apq; i++) {
          InputChoice[i].style.display = 'inline-block'
          InputChoice[i].style.maxWidth = '26%'
        }
      }
      break

    case 'type_write':
      BoxInputChoice.style.display = 'none'
      BoxInputWrite.style.display = 'block'
      InputWrite.focus()
      break
  }
}

const renderCongrats = () => {
  BoxQuestion.style.display = 'none'
  // BoxResult.style.display = "block";
  $('.box-result').fadeIn()
  BoxResult.id = '1' // 1 = green, 0 = red
  TextResult.innerText = aq[currentQ].question
  TextResultDetail.innerText = ('Good job, it is ' + playersAnswer.trim() + '!')
}

const renderFailure = (skip = false) => {
  BoxQuestion.style.display = 'none'
  $('.box-result').fadeIn()
  BoxResult.id = '0' // 1 = green, 0 = red
  TextResult.innerText = aq[currentQ].question
  if (skip === true) {
    TextResultDetail.innerText = ('The correct answer was ' + aq[currentQ].answer.join(', or ') + '.')
  } else {
    TextResultDetail.innerText = ('Sorry, the correct answer was ' + aq[currentQ].answer.join(', or ') + '.')
  }
}

const renderEnding = () => {
  BoxQuestion.style.display = 'none'
  $('.box-result').fadeIn()
  BoxResult.id = '2' // 1 = green, 0 = red
  TextResult.innerText = 'You have completed this questionnaire!'
  TextResultDetail.innerText = ('')
  // sends back
  
}

const renderNoValue = () => {
  $('#text-novalue').stop(jumpToEnd = true)
  $('#text-novalue').fadeIn(400).delay(1200).fadeOut(400)
}

// TODO const finished. submits an invible form with POST info about hwo you completed the test

const resetButtons = () => {
  InputChoice.forEach(btn => { btn.id = '0' })
}
const resetForm = () => {
  InputWrite.value = ''
}

// EVENTS //

const triggerNext = () => {
  if (questionnaire.length === 0) {
    if (BoxResult.id === '2') {
      $.ajax({
        url: '/ajax/questionnaire-done/',
        data: { 'id': questionnaire_id },
        dataType: 'json',
        success: function () {
          window.location.replace(urlBack)
        }
      })
    }
    renderEnding()
  } else {
    renderQuestion(aq, currentQ)
    playersAnswer = ''
  }
}

// When the player confirms his guess //
const triggerConfirm = () => {
  switch (aq[currentQ].type) {
    case 'type_write':

      playersAnswer = InputWrite.value

      if (playersAnswer.trim() === '') {
        renderNoValue()
      } else {
        if (similarInArray(playersAnswer, aq[currentQ].answer)) {
          renderCongrats()
          nextQuestion(true)
        } else {
          renderFailure()
          nextQuestion(test)
        }
        resetForm()
      }

      break

    case 'type_choice':
      if (playersAnswer.trim() === '') {
        renderNoValue()
      } else {
        if (inArray(playersAnswer, aq[currentQ].answer)) {
          renderCongrats()
          nextQuestion(true)
        } else {
          renderFailure()
          nextQuestion(test)
        }
        resetButtons()
      }
  }
}

const triggerButton = (button) => {
  resetButtons()
  button.id = '1'
  playersAnswer = button.innerText
}

// ADDING EVENTS //

InputChoice.forEach(button => {
  button.addEventListener('click', (e) => {
    triggerButton(button)
  })
})

BtnNext.addEventListener('click', (e) => {
  triggerNext()
})

BtnConfirm.addEventListener('click', (e) => {
  triggerConfirm()
})

BtnSkip.addEventListener('click', (e) => {
  resetButtons()
  resetForm()
  renderFailure(skip = true)
  nextQuestion(false)
})

$(document).keypress(function (e) {
  // Pressing enter counts as confirming guess or skipping screen //
  if (e.which === 13) {
    if (BoxQuestion.style.display === 'block') {
      triggerConfirm()
    } else {
      triggerNext()
    }
  }
  // Pressing a number counts as selecing that answer //
  for (let i = 0; i < Math.min(9, apq); i++) {
    if (e.which === 49 + i) {
      if (BoxQuestion.style.display === 'block' && aq[currentQ].type === 'type_choice') {
        triggerButton(InputChoice[i])
      }
    }
  }
})
